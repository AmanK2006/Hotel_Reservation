from __unknown__ import RAW_FILE_PATH
from __unknown__ import RAW_DIR
import os
import pandas as pd
from google.cloud import storage
from src.logger import get_logger
from src.custom_exceptions import CustomException
from utils.common_functions import read_yaml
from config.paths_config import *

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
            raise CustomException("Failed to download CSV from GCP", e)



