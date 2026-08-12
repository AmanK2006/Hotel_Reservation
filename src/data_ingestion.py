import os
import pandas as pd
from google.cloud import storage
from src.logger import get_logger
from src.custom_exceptions import CustomExceptions
from utils.common_functions import read_yaml
from config.paths_config import RAW_DIR, RAW_FILE_PATH, TRAIN_FILE_PATH, TEST_FILE_PATH, CONFIG_PATH
from sklearn.model_selection import train_test_split

logger = get_logger(__name__)

class DataIngestion:
    def __init__(self, config):
        self.config = config["data_ingestion"]
        self.bucket_name = self.config["bucket_name"]
        self.bucket_file_name = self.config["bucket_file_name"]

        os.makedirs(RAW_DIR, exist_ok=True)

        logger.info(f"Data Ingestion has started with {self.bucket_name} and the file name is {self.bucket_file_name}")

    def download_csv_from_gcp(self):
        try: 
            client = storage.Client()
            bucket = client.bucket(self.bucket_name)
            blob = bucket.blob(self.bucket_file_name)
            
            blob.download_to_filename(RAW_FILE_PATH)
            logger.info("Successfully downloaded CSV from GCP")

        except Exception as e:
            logger.error("Error while downloading CSV from GCP")
            raise CustomExceptions("Failed to download CSV from GCP", e)
        
    def split_data(self):
        try:
            logger.info("Splitting process has started")
            df = pd.read_csv(RAW_FILE_PATH)
            train_data, test_data = train_test_split(df, test_size = 1 - self.config["train_ratio"], random_state = 42)
            train_data.to_csv(TRAIN_FILE_PATH, index=False)
            test_data.to_csv(TEST_FILE_PATH, index=False)
            logger.info("Successfully split data")

            return TRAIN_FILE_PATH, TEST_FILE_PATH

        except Exception as e:
            logger.error("Error while splitting data")
            raise CustomExceptions("Failed to split data", e)

    def run(self):
        try:
            logger.info("The Data Ingestion process has started")

            self.download_csv_from_gcp()
            self.split_data()

            logger.info("The Data Ingestion process has ended")

        except CustomExceptions as ce:
            logger.error(f"{CustomExceptions, str(ce)}") 
        
        finally:
            logger.info("Data Ingestion finally completed")

if __name__ == "__main__":
    config = read_yaml(CONFIG_PATH)
    data_ingestion_obj = DataIngestion(config)
    data_ingestion_obj.run()


