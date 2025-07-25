from datetime import datetime
from dataclasses import dataclass
import os 
from networksecurity.constants import training_pipeline 

print(training_pipeline.ARTIFACT_DIR)
print(training_pipeline.PIPELINE_NAME)

class FeatureExtractorConfig:
    def __init__(self):
        self.serpapi_key = training_pipeline.SERPAPI_KEY
        if not self.serpapi_key:
            raise ValueError("SERPAPI key is not set in the environment variables.")
        
        self.whois_timeout = training_pipeline.WHOIS_TIMEOUT 
        self.requests_timeout = training_pipeline.REQUEST_TIMEOUT
        self.url_length_threshold = training_pipeline.URL_LENGTH_THRESHOLD
        self.max_subdomains = training_pipeline.MAX_SUBDOMAINS
        
        self.ssl_check_enabled = training_pipeline.SSL_CHECK_ENABLED
        self.min_domain_age_days = training_pipeline.MIN_DOMAIN_AGE_DAYS
        
        self.max_links_in_tags = training_pipeline.MAX_LINKS_IN_TAGS
        self.max_iframes = training_pipeline.MAX_IFRAMES
        
        self.temp_feature_dir = training_pipeline.TEMP_FEATURE_DIR
        self.feature_cache_file = training_pipeline.TEMP_FEATURE_CACHE_FILE

class TrainingPipelineConfig:
    def __init__(self, timestamp=datetime.now()):
        timestamp = timestamp.strftime("%m-%d-%Y-%H-%M-%S")
        self.pipeline_name =  training_pipeline.PIPELINE_NAME
        self.artifact_name = training_pipeline.ARTIFACT_DIR
        self.artifact_dir = os.path.join(self.artifact_name, timestamp)
        self.timestamp: str = timestamp
        self.model_dir = os.path.join("final_model")
        
class DataIngestionConfig:
    def __init__(self, training_pipeline_config: TrainingPipelineConfig):
        self.data_ingestion_dir:str = os.path.join(
            training_pipeline_config.artifact_dir,
            training_pipeline.DATA_INGESTION_DIR_NAME,
        )
        self.feature_store_file_path: str = os.path.join(
            self.data_ingestion_dir,
            training_pipeline.DATA_INGESTION_FEATURE_STORE_DIR,
            training_pipeline.FILE_NAME
        )
        self.training_file_path: str = os.path.join(
            self.data_ingestion_dir,
            training_pipeline.DATA_INGESTION_INGESTED_DIR,
            training_pipeline.TRAIN_FILE_NAME
        )
        self.testing_file_path: str = os.path.join(
            self.data_ingestion_dir,
            training_pipeline.DATA_INGESTION_INGESTED_DIR,
            training_pipeline.TEST_FILE_NAME
        )
        self.train_test_split_ratio: float = training_pipeline.DATA_INGESTION_TRAIN_TEST_SPLIT_RATIO
        self.train_test_split_random_state: int = training_pipeline.DATA_INGESTION_TRAIN_TEST_SPLIT_RANDOM_STATE
        self.collection_name: str = training_pipeline.DATA_INGESTION_COLLECTION_NAME
        self.database_name: str = training_pipeline.DATA_INGESTION_DATABASE_NAME
        
class DataValidationConfig:
        def __init__(self, training_pipeline_config: TrainingPipelineConfig):
            self.data_validation_dir: str = os.path.join(
                training_pipeline_config.artifact_dir,
                training_pipeline.DATA_VALIDATION_DIR_NAME
            )
            self.valid_dir: str = os.path.join(
                self.data_validation_dir,
                training_pipeline.DATA_VALIDATION_VALID_DIR
            )
            self.invalid_dir: str = os.path.join(
                self.data_validation_dir,
                training_pipeline.DATA_VALIDATION_INVALID_DIR
            )
            self.valid_train_file_path: str = os.path.join(
                self.valid_dir,
                training_pipeline.TRAIN_FILE_NAME
            )
            self.valid_test_file_path: str = os.path.join(
                self.valid_dir,
                training_pipeline.TEST_FILE_NAME
            )
            self.invalid_train_file_path: str = os.path.join(
                self.invalid_dir,
                training_pipeline.TRAIN_FILE_NAME
            )
            self.invalid_test_file_path: str = os.path.join(
                self.invalid_dir,
                training_pipeline.TEST_FILE_NAME
            )
            self.drift_report_file_path: str = os.path.join(
                self.data_validation_dir,
                training_pipeline.DATA_VALIDATION_DRIFT_REPORT_DIR,
                training_pipeline.DATA_VALIDATION_DRIFT_REPORT_FILE_NAME
            )
            self.feature_extractor_config = FeatureExtractorConfig()
            

class DataTransformationConfig:
    def __init__(self,training_pipeline_config:TrainingPipelineConfig):
        self.data_transformation_dir: str = os.path.join( training_pipeline_config.artifact_dir,training_pipeline.DATA_TRANSFORMATION_DIR_NAME )
        self.transformed_train_file_path: str = os.path.join( self.data_transformation_dir,training_pipeline.DATA_TRANSFORMATION_TRANSFORMED_DATA_DIR,
            training_pipeline.TRAIN_FILE_NAME.replace("csv", "npy"),)
        self.transformed_test_file_path: str = os.path.join(self.data_transformation_dir,  training_pipeline.DATA_TRANSFORMATION_TRANSFORMED_DATA_DIR,
            training_pipeline.TEST_FILE_NAME.replace("csv", "npy"), )
        self.transformed_object_file_path: str = os.path.join( self.data_transformation_dir, training_pipeline.DATA_TRANSFORMATION_TRANSFORMED_OBJECT_DIR,
            training_pipeline.PREPROCESSING_OBJECT_FILE_NAME,)
        
class ModelTrainerConfig:
    def __init__(self, training_pipeline_config: TrainingPipelineConfig):
        self.model_trainer_dir: str = os.path.join(
            training_pipeline_config.artifact_dir, training_pipeline.MODEL_TRAINER_DIR_NAME
        )
        self.trained_model_file_path: str = os.path.join(
            self.model_trainer_dir, training_pipeline.MODEL_TRAINER_TRAINED_MODEL_DIR,training_pipeline.MODEL_TRAINER_TRAINED_MODEL_NAME
        )
        self.expected_accuracy: float = training_pipeline.MODEL_TRAINER_EXPECTED_SCORE
        self.overfitting_underfitting_threshold = training_pipeline.MODEL_TRAINER_OVER_FITTING_UNDER_FITTING_THRESHOLD