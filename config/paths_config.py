import os

############################### DATA INGESTION ###########################

RAW_DIR = "artifacts/raw"

RAW_FILE_PATH = os.path.join(RAW_DIR, "raw.csv")
TRAIN_FILE_PATH = os.path.join(RAW_DIR, "train.csv")
TEST_FILE_PATH = os.path.join(RAW_DIR, "test.csv")

CONFIG_PATH = "config/config.yaml"

__all__ = [
    "RAW_DIR",
    "RAW_FILE_PATH",
    "TRAIN_FILE_PATH",
    "TEST_FILE_PATH",
    "CONFIG_PATH",
]