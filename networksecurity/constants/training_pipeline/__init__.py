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
