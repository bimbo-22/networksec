import os
import sys
import numpy as np
import pandas as pd 


# common constant variable for training pipeline
TARGET_COLUMN: str = "Result"
PIPELINE_NAME: str = "NetworkSecurity"
ARTIFACT_DIR: str = "Artifact"
FILE_NAME: str = "PhishingData.csv"

TRAIN_FILE_NAME: str = "train.csv"
TEST_FILE_NAME: str = "test.csv"

SCHEMA_FILE_PATH = os.path.join("data_schema", "schema.yaml")

SAVED_MODEL_DIR = os.path.join("saved_model")
MODEL_FILE_NAME = "model.pkl"

# starting with DATA INGESTION

DATA_INGESTION_COLLECTION_NAME: str = "NetworkData" # From mongodb
DATA_INGESTION_DATABASE_NAME: str = "NetworkSec" # from mongodb
DATA_INGESTION_DIR_NAME: str = "data_ingestion"
DATA_INGESTION_FEATURE_STORE_DIR: str = "feature_store" # basically the folder where the data is stored from database
DATA_INGESTION_INGESTED_DIR: str = "ingested" # basically the folder where the data is stored after ingestion split into test and train
DATA_INGESTION_TRAIN_TEST_SPLIT_RATIO: float = 0.2
DATA_INGESTION_TRAIN_TEST_SPLIT_RANDOM_STATE: int = 42

# Data Validation
DATA_VALIDATION_DIR_NAME: str = "data_validation"
DATA_VALIDATION_VALID_DIR: str = "validated"
DATA_VALIDATION_INVALID_DIR: str = "invalid"
DATA_VALIDATION_DRIFT_REPORT_DIR: str = "drift_report"
DATA_VALIDATION_DRIFT_REPORT_FILE_NAME: str = "drift_report.yaml"

# Data Transformation
DATA_TRANSFORMATION_DIR_NAME: str = "data_transformation"
DATA_TRANSFORMATION_TRANSFORMED_DATA_DIR: str = "transformed"
DATA_TRANSFORMATION_TRANSFORMED_OBJECT_DIR: str = "transformed_object"

PREPROCESSING_OBJECT_FILE_NAME: str = "preprocessing.pkl"
# knn imputer to replace missing values
DATA_TRANSFORMATION_IMPUTER_PARAMS: dict = {
    "missing_values": np.nan,
    "n_neighbors": 3,
    "weights": "uniform",
}

DATA_TRANSFORMATION_TRAIN_FILE_PATH: str = "train.npy"

DATA_TRANSFORMATION_TEST_FILE_PATH: str = "test.npy"

# MODEL TRAINER

MODEL_TRAINER_DIR_NAME: str = "model_trainer"
MODEL_TRAINER_TRAINED_MODEL_DIR: str = "trained_model"
MODEL_TRAINER_TRAINED_MODEL_NAME: str = "model.pkl"
MODEL_TRAINER_EXPECTED_SCORE: float = 0.6
MODEL_TRAINER_OVER_FITTING_UNDER_FITTING_THRESHOLD: float = 0.05

# cloud
TRAINING_BUCKET_NAME: str = "network-security-mlops"

# LINK feature extracting
WHOIS_TIMEOUT: int = 10
REQUEST_TIMEOUT: int = 10
SERPAPI_KEY: str = os.getenv("SERPAPI")
URL_LENGTH_THRESHOLD: int = 100
MAX_SUBDOMAINS = 5
SSL_CHECK_ENABLED: bool = True
MIN_DOMAIN_AGE_DAYS: int = 90
MAX_LINKS_IN_TAGS = 100
MAX_IFRAMES = 5
TEMP_FEATURE_DIR: str = "temp_features"
TEMP_FEATURE_CACHE_FILE: str = "temp_features_cache.pkl"
