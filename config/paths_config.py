import os

############################### DATA INGESTION ###########################

RAW_DIR = "artifacts/raw"

RAW_FILE_PATH = os.path.join(RAW_DIR, "raw.csv")
RAW_TRAIN_PATH = os.path.join(RAW_DIR, "train.csv")
RAW_TEST_PATH = os.path.join(RAW_DIR, "test.csv")

CONFIG_PATH = "config/config.yaml"