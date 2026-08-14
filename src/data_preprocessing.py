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
            if 'Booking_ID' in df.columns:
                df = df.drop(columns=['Booking_ID'])

            if 'booking_status' in df.columns and df['booking_status'].dtype == 'object':
                df['booking_status'] = df['booking_status'].map({'Canceled': 1, 'Not_Canceled': 0})

            if 'avg_price_per_room' in df.columns:
                df['avg_price_per_room'] = df['avg_price_per_room'].clip(lower=0)

            if 'no_of_adults' in df.columns and 'no_of_children' in df.columns:
                df['total_guests'] = df['no_of_adults'] + df['no_of_children']

            if 'no_of_weekend_nights' in df.columns and 'no_of_week_nights' in df.columns:
                df['total_stay_nights'] = df['no_of_weekend_nights'] + df['no_of_week_nights']

            drop_cols = ['no_of_weekend_nights', 'no_of_week_nights', 'no_of_adults', 'no_of_children']
            df = df.drop(columns=[col for col in drop_cols if col in df.columns])

            return df

        except Exception as e:
            raise CustomExceptions("Error in basic preprocessing helper", sys) from e

    def preprocess_data(self, train_df: pd.DataFrame, test_df: pd.DataFrame):
        try:
            logger.info("Executing feature engineering and encoding...")
            train_df = self._basic_preprocessing(train_df)
            test_df = self._basic_preprocessing(test_df)

            # Ordinal Encoding
            train_df[self.cat_cols] = self.ordinal_encoder.fit_transform(train_df[self.cat_cols])
            test_df[self.cat_cols] = self.ordinal_encoder.transform(test_df[self.cat_cols])

            # Dynamic Skewness Transformation
            skewed_features = [
                col for col in self.num_cols 
                if col in train_df.columns and abs(train_df[col].skew()) > self.skewness_threshold
            ]

            if skewed_features:
                logger.info(f"Applying PowerTransformer to skewed features: {skewed_features}")
                train_df[skewed_features] = self.power_transformer.fit_transform(train_df[skewed_features])
                test_df[skewed_features] = self.power_transformer.transform(test_df[skewed_features])

            return train_df, test_df

        except Exception as e:
            logger.error("Failed during categorical/skewness transformation.")
            raise CustomExceptions("Preprocessing execution failed", sys) from e

    def handle_imbalanced_data(self, X_train: pd.DataFrame, y_train: pd.Series):
        try:
            logger.info("Applying SMOTE on training dataset...")
            smote = SMOTE(random_state=42)
            X_train_res, y_train_res = smote.fit_resample(X_train, y_train)
            return X_train_res, y_train_res
        except Exception as e:
            logger.error("Error applying SMOTE.")
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