import os
from src.logger import get_logger
from src.custom_exceptions import CustomExceptions
import yaml

logger = get_logger(__name__)

def read_yaml(file_path):
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"{file_path} File is not in the given path")

        with open(file_path, "r") as yaml_file:
            config = yaml.safe_load(yaml_file)
            logger.info("Successfully read the YAML File")
            return config
        
    except Exception as e:
        logger.error("Error while reading YAML File")
        raise CustomExceptions("Failed to read the YAML File", e)

