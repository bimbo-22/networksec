import os,sys
from networksecurity.constants.training_pipeline import TRAINING_BUCKET_NAME
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
from networksecurity.components.data_ingestion import DataIngestion
from networksecurity.components.data_validation import DataValidation
from networksecurity.components.data_transformation import DataTransformation
from networksecurity.components.model_trainer import ModelTrainer
from networksecurity.components.feature_extractor import FeatureExtractor
from networksecurity.cloud.s3_syncer import S3Sync
from networksecurity.entity.config_entity import (
    TrainingPipelineConfig,
    DataIngestionConfig,
    DataTransformationConfig,
    DataValidationConfig,
    ModelTrainerConfig,
    FeatureExtractorConfig
)

from networksecurity.entity.artifact_entity import (
    DataIngestionArtifact,
    DataTransformationArtifact,
    DataValidationArtifact,
    ModelTrainerArtifact,
    FeatureExtractorArtifact

)

class TrainingPipeline:
    def __init__(self): 
        self.training_pipeline_config = TrainingPipelineConfig()
        self.s3_sync = S3Sync()
        
    def start_data_ingestion(self):
        try:
            self.data_ingestion_config = DataIngestionConfig(training_pipeline_config=self.training_pipeline_config)
            logging.info("Starting data ingestion")
            data_ingestion = DataIngestion(data_ingestion_config = self.data_ingestion_config)
            data_ingestion_artifact = data_ingestion.initiate_data_ingestion()
            logging.info(f"Data Ingestion completed and artifact: {data_ingestion_artifact}")
            return data_ingestion_artifact
        except Exception as e:
            raise NetworkSecurityException(e,sys)
        
    def start_data_validation(self,data_ingestion_artifact: DataIngestionArtifact):
        try:
            logging.info("Starting the data validation process")
            data_validation_config = DataValidationConfig(training_pipeline_config = self.training_pipeline_config)
            data_validation = DataValidation(data_validation_config=data_validation_config, data_ingestion_artifact=data_ingestion_artifact)
            logging.info("Data validation Initiated")
            data_validation_artifact = data_validation.initiate_data_validation()
            logging.info(f"Data validation process completed successfully {data_validation_artifact}")
            logging.info("==========================")
            
            return data_validation_artifact
        except Exception as e:
            raise NetworkSecurityException (e,sys)
        
    def start_feature_extraction(self):
        try:
            logging.info("Starting feature extraction process")
            feature_extractor_config = FeatureExtractorConfig(training_pipeline_config = self.training_pipeline_config)
            feature_extractor = FeatureExtractor(feature_extractor_config=feature_extractor_config)
            logging.info("Feature extraction initiated")
            feature_extractor_artifact = feature_extractor.initiate_feature_extraction()
            logging.info(f"Feature extraction process completed successfully {feature_extractor_artifact}")
            logging.info("==========================")
            
            return feature_extractor_artifact
        except Exception as e:
            raise NetworkSecurityException (e,sys)
    def start_data_transformation(self,data_validation_artifact:DataValidationArtifact ) -> DataTransformationArtifact:
        try:
            logging.info("Starting the data transformation process")
            data_transformation_config = DataTransformationConfig(training_pipeline_config = self.training_pipeline_config)
            data_transformation = DataTransformation(data_transformation_config = data_transformation_config, data_validation_artifact=data_validation_artifact)
            logging.info("Data transformation Initiated")
            data_transformation_artifact = data_transformation.initiate_data_transformation()
            logging.info("Data transformation process completed successfully")
            logging.info("==========================")
            return data_transformation_artifact
        except Exception as e:
            raise NetworkSecurityException (e,sys)
        
    def start_model_trainer(self,data_transformation_artifact: DataTransformationArtifact) -> ModelTrainerArtifact:
        try:
            logging.info("Starting Model Training")
            self.model_trainer_config =  ModelTrainerConfig(training_pipeline_config = self.training_pipeline_config)
            model_trainer = ModelTrainer(model_trainer_config = self.model_trainer_config, data_transformation_artifact=data_transformation_artifact)
            model_trainer_artifact = model_trainer.initiate_model_trainer()
            logging.info("Model Traning process completed successfully")
            logging.info("==========================")
            
            return model_trainer_artifact
        except Exception as e:
            raise NetworkSecurityException (e,sys)
        
        
        # pushing to aws s3 bucket or any other cloud storage using aws cli 
    def sync_artifact_dir_to_s3(self):
        try:
            aws_bucket_url = f"s3://{TRAINING_BUCKET_NAME}/artifact/{self.training_pipeline_config.timestamp}"
            self.s3_sync.sync_folder_to_s3(folder = self.training_pipeline_config.artifact_dir, aws_bucket_url=aws_bucket_url)
        except Exception as e:
            raise NetworkSecurityException(e, sys)
        
    def sync_saved_model_dir_to_s3(self):
        try:
            aws_bucket_url = f"s3://{TRAINING_BUCKET_NAME}/final_model/{self.training_pipeline_config.timestamp}"
            self.s3_sync.sync_folder_to_s3(folder = self.training_pipeline_config.model_dir, aws_bucket_url=aws_bucket_url)
        except Exception as e:
            raise NetworkSecurityException(e, sys)
            
        
    def run_pipeline(self):
        try:
            data_ingestion_artifact = self.start_data_ingestion()
            data_validation_artifact = self.start_data_validation(data_ingestion_artifact=data_ingestion_artifact)
            #feature_extractor_artifact= self.start_feature_extractor(feature_extractor_artifact=feature_exactor_artifact)
            data_transformation_artifact = self.start_data_transformation(data_validation_artifact=data_validation_artifact)
            model_trainer_artifact = self.start_model_trainer(data_transformation_artifact = data_transformation_artifact)
            
            self.sync_artifact_dir_to_s3()
            self.sync_saved_model_dir_to_s3()
            
            return model_trainer_artifact
        except Exception as e:
            raise NetworkSecurityException (e,sys)