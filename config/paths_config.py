import os

############################### DATA INGESTION ###########################

RAW_DIR = "artifacts/raw"

RAW_FILE_PATH = os.path.join(RAW_DIR, "raw.csv")
TRAIN_FILE_PATH = os.path.join(RAW_DIR, "train.csv")
TEST_FILE_PATH = os.path.join(RAW_DIR, "test.csv")

CONFIG_PATH = "config/config.yaml"

############################### DATA PREPROCESSING ###########################

PREPROCESSED_DIR = "artifacts/preprocessed"
PREPROCESSED_TRAIN_PATH = os.path.join(PREPROCESSED_DIR, "train_preprocessed.csv")
PREPROCESSED_TEST_PATH = os.path.join(PREPROCESSED_DIR, "test_preprocessed.csv")
PREPROCESSOR_OBJ_PATH = os.path.join(PREPROCESSED_DIR, "preprocessor.pkl")

__all__ = [
    "RAW_DIR",
    "RAW_FILE_PATH",
    "TRAIN_FILE_PATH",
    "TEST_FILE_PATH",
    "CONFIG_PATH",
    "PREPROCESSED_DIR",
    "PREPROCESSED_TRAIN_PATH",
    "PREPROCESSED_TEST_PATH",
    "PREPROCESSOR_OBJ_PATH",
]