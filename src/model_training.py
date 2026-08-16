import os
import pandas as pd
from sklearn.model_selection import RandomizedSearchCV
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from lightgbm import LGBMClassifier
from src.logger import get_logger
from src.custom_exceptions import CustomExceptions
from utils.common_functions import load_csv, save_csv
from config.paths_config import MODEL_DIR, PROCESSED_TRAIN_FILE, PROCESSED_TEST_FILE
from config.model_params import PARAM_DIST, RANDOM_SEARCH
import joblib
import mlflow

logger = get_logger(__name__)

class Model_Training:
    def __init__(self, train_path, test_path, param_dist, random_search):
        self.train_path = train_path
        self.test_path = test_path
        self.param_dist = param_dist
        self.random_search = random_search
        
    
    def loading_and_splitting(self):
        try:
            logger.info("Loading the Data")
            
            Train_data = load_csv(self.train_path)
            logger.info("The Training data has been successfully loaded")
            
            Test_data = load_csv(self.test_path)
            logger.info("The Testing data has been successfully loaded")
            
            logger.info("Now we are Splitting the Data")
            
            X_train = Train_data.drop(columns=['booking_status'])
            y_train = Train_data["booking_status"]
            
            X_test = Test_data.drop(columns=['booking_status'])
            y_test = Test_data["booking_status"]
            
            logger.info("The Data has been split successfully")
            
            return X_train, y_train, X_test, y_test
            
        except Exception as e:
            logger.error("Error in loading and splitting the data")
            raise CustomExceptions("Failed in loading and splitting the data", e)
    
    def model_training(self, X_train, y_train):
        try:
            logger.info("Model Training will start now")
            
            lgbm = LGBMClassifier(random_state=42)
            
            logger.info("Hyperparameter Tuning will start now")
            
            random_model = RandomizedSearchCV(
                estimator=lgbm,
                param_distributions=self.param_dist,
                scoring=self.random_search["scoring"],
                n_iter=self.random_search["n_iter"],
                n_jobs=self.random_search["n_jobs"],
                verbose=self.random_search["verbose"],
                cv=self.random_search["cv"],
                random_state=self.random_search["random_state"]
            )
            
            random_model.fit(X_train, y_train)
            
            logger.info("Hyperparamter tuning has been completed")
            
            best_params = random_model.best_params_
            best_model = random_model.best_estimator_
            
            logger.info(f"Best params are {best_params}")
            logger.info(f"Best model is {best_model}")
            
            return best_model
        
        except Exception as e:
            logger.error("Error in Training the Model")
            raise CustomExceptions("Failure in Training the Model", e)
        
    def evaluate_model(self, model, X_test, y_test):
        try:
            logger.info("Model Evaluation has started")
            
            y_pred = model.predict(X_test)
            
            accuracy = accuracy_score(y_test, y_pred)
            recall = recall_score(y_test, y_pred)
            precision = precision_score(y_test, y_pred)
            f1 = f1_score(y_test, y_pred)
            
            logger.info(f"Accuracy is {accuracy}")
            logger.info(f"Recall Score is {recall}")
            logger.info(f"Precision Score is {precision}")
            logger.info(f"f1 score is {f1}")
            
            return {
                "accuracy" : accuracy,
                "Recall_Score" : recall,
                "Precision_Score" : precision,
                "f1_Score" : f1
            }
        
        except Exception as e:
            logger.error("Error in Evaluating the model")
            raise CustomExceptions("Failed to evaluate the model", e)
        
    def save_model(self, model):
        try:
            logger.info("Now we are Saving the model")
            
            os.makedirs(os.path.dirname(MODEL_DIR), exist_ok=True)
            
            joblib.dump(model, MODEL_DIR)
            
            logger.info("Model has been successfully saved")
            
        except Exception as e:
            logger.error("Error in saving the model")
            raise CustomExceptions("Failure in saving the model", e)
    
    def run_process(self):
        try:
            mlflow.set_tracking_uri("http://127.0.0.1:5000")
            with mlflow.start_run():
                logger.info("Model Training starts here")
                
                logger.info("Starting our Experiment Tracking using MLFLOW")
                
                logger.info("Logging the training and testing data")
                mlflow.log_artifact(self.train_path, artifact_path="datasets")
                mlflow.log_artifact(self.test_path, artifact_path="datasets")
                        
                X_train, y_train, X_test, y_test = self.loading_and_splitting()
                best_model = self.model_training(X_train, y_train)
                metrics = self.evaluate_model(best_model, X_test, y_test)
                self.save_model(best_model)
                
                mlflow.log_artifact(MODEL_DIR)
                
                logger.info("Logging the model paramters and accuracy")
                mlflow.log_params(best_model.get_params())
                mlflow.log_metrics(metrics)
                
                logger.info("The Entire Process has been completed")
            
        except Exception as e:
            logger.error("Error in running the process")
            raise CustomExceptions("Failure in running the process", e)
    
if __name__ == "__main__":
    Model_trainer = Model_Training(PROCESSED_TRAIN_FILE, PROCESSED_TEST_FILE, PARAM_DIST, RANDOM_SEARCH)
    Model_trainer.run_process()