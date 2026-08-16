import sys
import pandas as pd
from sklearn.preprocessing import OrdinalEncoder, PowerTransformer
from imblearn.over_sampling import SMOTE
from sklearn.ensemble import RandomForestClassifier

from src.logger import get_logger
from src.custom_exceptions import CustomExceptions
from utils.common_functions import read_yaml, load_csv, save_csv
from config.paths_config import (
    TRAIN_FILE_PATH,
    TEST_FILE_PATH,
    PROCESSED_TRAIN_FILE,
    PROCESSED_TEST_FILE,
    CONFIG_PATH
)

logger = get_logger(__name__)

class DataTransformation:
    def __init__(self, config_path: str = CONFIG_PATH):
        try:
            logger.info("Initializing DataTransformation component...")
            config_data = read_yaml(config_path)
            self.config = config_data["data_processing"]

            self.cat_cols = self.config["categorical_cols"]
            self.num_cols = self.config["numerical_cols"]
            self.skewness_threshold = self.config["skewness_threshold"]
            self.num_important_features = self.config["num_important_features"]

            self.ordinal_encoder = OrdinalEncoder(handle_unknown='use_encoded_value', unknown_value=-1)
            self.power_transformer = PowerTransformer(method='yeo-johnson')

        except Exception as e:
            logger.error("Initialization error in DataTransformation.")
            raise CustomExceptions("Failed to initialize DataTransformation", sys) from e

    def _basic_preprocessing(self, df: pd.DataFrame) -> pd.DataFrame:
        try:
            df = df.copy()

            # 1. Drop identifiers
            if 'Booking_ID' in df.columns:
                df = df.drop(columns=['Booking_ID'])

            # 2. Target mapping (Defensive check for existing ints, floats, or strings)
            if 'booking_status' in df.columns:
                # Log raw values to verify what's inside
                logger.info(f"Raw booking_status unique values: {df['booking_status'].unique()}")
                
                # If already numeric (0 and 1)
                if pd.api.types.is_numeric_dtype(df['booking_status']):
                    df['booking_status'] = df['booking_status'].astype(int)
                else:
                    # Clean strings and map dynamically
                    status_str = df['booking_status'].astype(str).str.strip().str.lower()
                    
                    mapping = {
                        'canceled': 1,
                        '1': 1,
                        'not_canceled': 0,
                        'not canceled': 0,
                        '0': 0
                    }
                    
                    df['booking_status'] = status_str.map(mapping)

                # Verify target hasn't collapsed into 1 class
                unique_classes = df['booking_status'].nunique()
                if unique_classes < 2:
                    logger.error(f"Target column collapsed! Unique values found: {df['booking_status'].unique()}")
                    raise ValueError("Target mapping failed. Check raw values of booking_status in input CSV.")

            # 3. Clip negative price
            if 'avg_price_per_room' in df.columns:
                df['avg_price_per_room'] = pd.to_numeric(df['avg_price_per_room'], errors='coerce').clip(lower=0)

            # 4. Feature engineering
            if 'no_of_adults' in df.columns and 'no_of_children' in df.columns:
                adults = pd.to_numeric(df['no_of_adults'], errors='coerce').fillna(0)
                children = pd.to_numeric(df['no_of_children'], errors='coerce').fillna(0)
                df['total_guests'] = adults + children

            if 'no_of_weekend_nights' in df.columns and 'no_of_week_nights' in df.columns:
                w_nights = pd.to_numeric(df['no_of_weekend_nights'], errors='coerce').fillna(0)
                wk_nights = pd.to_numeric(df['no_of_week_nights'], errors='coerce').fillna(0)
                df['total_stay_nights'] = w_nights + wk_nights

            # 5. Drop component features
            drop_cols = ['no_of_weekend_nights', 'no_of_week_nights', 'no_of_adults', 'no_of_children']
            cols_to_drop = [col for col in drop_cols if col in df.columns]
            if cols_to_drop:
                df = df.drop(columns=cols_to_drop)

            return df

        except Exception as e:
            print(f"\n--> RAW BASIC PREPROCESSING ERROR: {e}\n")
            logger.error(f"Error in basic preprocessing helper: {e}")
            raise CustomExceptions("Error in basic preprocessing helper", sys) from e

    def preprocess_data(self, train_df: pd.DataFrame, test_df: pd.DataFrame):
        try:
            logger.info("Executing feature engineering and encoding...")
            train_df = self._basic_preprocessing(train_df)
            test_df = self._basic_preprocessing(test_df)

            # 1. Safe Categorical Ordinal Encoding
            valid_cat_cols = [col for col in self.cat_cols if col in train_df.columns]
            
            if valid_cat_cols:
                logger.info(f"Encoding categorical columns: {valid_cat_cols}")
                for col in valid_cat_cols:
                    train_df[col] = train_df[col].fillna("Missing").astype(str).str.strip()
                    test_df[col] = test_df[col].fillna("Missing").astype(str).str.strip()

                # Transform categorical columns safely
                train_encoded = self.ordinal_encoder.fit_transform(train_df[valid_cat_cols])
                test_encoded = self.ordinal_encoder.transform(test_df[valid_cat_cols])

                train_df[valid_cat_cols] = pd.DataFrame(train_encoded, columns=valid_cat_cols, index=train_df.index)
                test_df[valid_cat_cols] = pd.DataFrame(test_encoded, columns=valid_cat_cols, index=test_df.index)

            # 2. Dynamic Skewness Transformation
            skewed_features = [
                col for col in self.num_cols 
                if col in train_df.columns 
                and pd.api.types.is_numeric_dtype(train_df[col])
                and abs(train_df[col].skew()) > self.skewness_threshold
            ]

            if skewed_features:
                logger.info(f"Applying PowerTransformer to skewed features: {skewed_features}")
                
                # Ensure no NaNs exist in numeric columns before PowerTransformer
                train_df[skewed_features] = train_df[skewed_features].fillna(train_df[skewed_features].median())
                test_df[skewed_features] = test_df[skewed_features].fillna(train_df[skewed_features].median())

                train_pt = self.power_transformer.fit_transform(train_df[skewed_features])
                test_pt = self.power_transformer.transform(test_df[skewed_features])

                train_df[skewed_features] = pd.DataFrame(train_pt, columns=skewed_features, index=train_df.index)
                test_df[skewed_features] = pd.DataFrame(test_pt, columns=skewed_features, index=test_df.index)

            return train_df, test_df

        except Exception as e:
            logger.error(f"--> EXACT PREPROCESSING ERROR: {e}")
            print(f"\n--> EXACT ERROR CAUSE: {e}\n")
            raise CustomExceptions("Preprocessing execution failed", sys) from e

    def handle_imbalanced_data(self, X_train: pd.DataFrame, y_train: pd.Series):
        try:
            logger.info("Applying SMOTE on training dataset...")
            
            # 1. Defensively convert all features to numeric & fill missing values
            X_train = X_train.apply(pd.to_numeric, errors='coerce')
            X_train = X_train.fillna(X_train.median())

            # 2. Ensure y_train is integer type with no NaNs
            y_train = y_train.fillna(0).astype(int)

            # 3. Apply SMOTE
            smote = SMOTE(random_state=42)
            X_train_res, y_train_res = smote.fit_resample(X_train, y_train)

            logger.info(f"Original class distribution: {y_train.value_counts().to_dict()}")
            logger.info(f"Resampled class distribution: {pd.Series(y_train_res).value_counts().to_dict()}")

            return X_train_res, y_train_res

        except Exception as e:
            print(f"\n--> EXACT SMOTE ERROR: {e}\n")
            logger.error(f"Error applying SMOTE: {e}")
            raise CustomExceptions("SMOTE resampling failed", sys) from e

    def select_top_features(self, X_train: pd.DataFrame, y_train: pd.Series, X_test: pd.DataFrame):
        try:
            logger.info(f"Selecting top {self.num_important_features} features using RandomForest...")
            rf = RandomForestClassifier(n_estimators=100, random_state=42)
            rf.fit(X_train, y_train)

            importances = pd.Series(rf.feature_importances_, index=X_train.columns)
            top_features = importances.nlargest(self.num_important_features).index.tolist()

            logger.info(f"Selected Top Features: {top_features}")
            return X_train[top_features], X_test[top_features]

        except Exception as e:
            logger.error("Feature selection failed.")
            raise CustomExceptions("Failed to select top features", sys) from e

    def initiate_data_transformation(self):
        try:
            logger.info("--- Starting Data Transformation Stage ---")

            # Load Raw Datasets via Utility Function
            train_df = load_csv(TRAIN_FILE_PATH)
            test_df = load_csv(TEST_FILE_PATH)

            # Preprocess & Encode
            train_df, test_df = self.preprocess_data(train_df, test_df)

            X_train = train_df.drop(columns=['booking_status'])
            y_train = train_df['booking_status']
            
            X_test = test_df.drop(columns=['booking_status'])
            y_test = test_df['booking_status']

            # SMOTE (Train set only)
            X_train_res, y_train_res = self.handle_imbalanced_data(X_train, y_train)

            # Feature Selection
            X_train_selected, X_test_selected = self.select_top_features(X_train_res, y_train_res, X_test)

            # Combine Features and Targets
            processed_train = pd.concat([X_train_selected, y_train_res.reset_index(drop=True)], axis=1)
            processed_test = pd.concat([X_test_selected, y_test.reset_index(drop=True)], axis=1)

            # Save Processed Datasets via Utility Function
            save_csv(processed_train, PROCESSED_TRAIN_FILE)
            save_csv(processed_test, PROCESSED_TEST_FILE)

            logger.info("--- Data Transformation Completed Successfully ---")
            return PROCESSED_TRAIN_FILE, PROCESSED_TEST_FILE

        except Exception as e:
            logger.error("Data Transformation pipeline execution failed.")
            raise CustomExceptions(e, sys)


if __name__ == "__main__":
    try:
        transformer = DataTransformation()
        transformer.initiate_data_transformation()
    except Exception as e:
        print(f"Pipeline Failed: {e}")