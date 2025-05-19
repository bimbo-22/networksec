from networksecurity.components.data_ingestion import DataIngestion
from networksecurity.components.data_validation import DataValidation
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
from networksecurity.entity.config_entity import DataIngestionConfig,DataValidationConfig
from networksecurity.entity.config_entity import TrainingPipelineConfig

import sys 

if __name__ == "__main__":
    try:
        logging.info("Initializing the configuration")
        # Initialize the configuration
        training_pipeline_config = TrainingPipelineConfig()
        data_ingestion_config = DataIngestionConfig(training_pipeline_config)
        logging.info("Starting the data ingestion process")
        data_ingestion = DataIngestion(data_ingestion_config)
        data_ingestion_artifact = data_ingestion.initiate_data_ingestion()
        logging.info("Data ingestion process completed successfully")
        
        logging.info("==========================")
        
        logging.info("Starting the data validation process")
        data_validation_config = DataValidationConfig(training_pipeline_config)
        data_validation = DataValidation(data_validation_config, data_ingestion_artifact)
        logging.info("Data validation Initiated")
        data_validation_artifact = data_validation.initiate_data_validation()
        print(data_validation_artifact)
        logging.info("Data validation process completed successfully")
        
        
        
        
    except Exception as e:
        raise NetworkSecurityException(e, sys)