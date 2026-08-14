import os
import sys
import yaml
import pandas as pd
from src.logger import get_logger
from src.custom_exceptions import CustomExceptions

logger = get_logger(__name__)

def read_yaml(file_path: str) -> dict:
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found at given path: [{file_path}]")

        with open(file_path, "r") as yaml_file:
            config = yaml.safe_load(yaml_file)
            logger.info(f"Successfully read YAML File from [{file_path}]")
            return config

    except Exception as e:
        logger.error(f"Error while reading YAML File from [{file_path}]")
        raise CustomExceptions(f"Failed to read the YAML File: {e}", sys) from e


def load_csv(file_path: str) -> pd.DataFrame:
    try:
        logger.info(f"Loading data from CSV: [{file_path}]")
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"CSV file not found at path: [{file_path}]")

        df = pd.read_csv(file_path)
        logger.info(f"Data successfully loaded into DataFrame with shape: {df.shape}")
        return df

    except Exception as e:
        logger.error(f"Failed to load CSV from path: [{file_path}]")
        raise CustomExceptions(f"Failed to load csv: {e}", sys) from e


def save_csv(df: pd.DataFrame, file_path: str, index: bool = False) -> None:
    try:
        logger.info(f"Saving DataFrame to CSV: [{file_path}]")
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        df.to_csv(file_path, index=index)
        logger.info(f"Successfully saved CSV to [{file_path}]")

    except Exception as e:
        logger.error(f"Failed to save CSV to path: [{file_path}]")
        raise CustomExceptions(f"Failed to save csv: {e}", sys) from e