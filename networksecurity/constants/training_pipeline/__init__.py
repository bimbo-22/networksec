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

# starting with DATA INGESTION

DATA_INGESTION_COLLECTION_NAME: str = "NetworkData" # From mongodb
DATA_INGESTION_DATABASE_NAME: str = "NetworkSec" # from mongodb
DATA_INGESTION_DIR_NAME: str = "data_ingestion"
DATA_INGESTION_FEATURE_STORE_DIR: str = "feature_store"
DATA_INGESTION_INGESTED_DIR: str = "ingested"
DATA_INGESTION_TRAIN_TEST_SPLIT_RATIO: float = 0.2
DATA_INGESTION_TRAIN_TEST_SPLIT_RANDOM_STATE: int = 42


