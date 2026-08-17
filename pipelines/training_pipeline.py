from src.data_ingestion import DataIngestion
from src.data_preprocessing import DataTransformation
from src.model_training import Model_Training
from utils.common_functions import read_yaml
from config.paths_config import PROCESSED_TEST_FILE, PROCESSED_TRAIN_FILE, CONFIG_PATH
from config.model_params import PARAM_DIST, RANDOM_SEARCH

if __name__ == "__main__":
    
    ########################################## DATA INGESTION ######################################
    
    config = read_yaml(CONFIG_PATH)
    data_ingestion_obj = DataIngestion(config)
    data_ingestion_obj.run()
    
    ########################################## DATA PROCESSING ######################################
    
    try:
        transformer = DataTransformation()
        transformer.initiate_data_transformation()
    except Exception as e:
        print(f"Pipeline Failed: {e}")
        
    ########################################## MODEL TRAINING #######################################
    
    Model_trainer = Model_Training(PROCESSED_TRAIN_FILE, PROCESSED_TEST_FILE, PARAM_DIST, RANDOM_SEARCH)
    Model_trainer.run_process()