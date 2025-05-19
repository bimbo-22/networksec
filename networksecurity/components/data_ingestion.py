from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
from networksecurity.entity.config_entity import DataIngestionConfig
from networksecurity.entity.artifact_entity import DataIngestionArtifact


import os
import sys
import numpy as np
import pandas as pd
import pymongo
from pymongo import MongoClient
from typing import List
from sklearn.model_selection import train_test_split

from dotenv import load_dotenv
load_dotenv()

MONGO_DB_URL = os.getenv("MONGO_DB_URL")


class DataIngestion:
    def __init__(self,data_ingestion_config:DataIngestionConfig):
        try: 
            self.data_ingestion_config = data_ingestion_config
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def export_collection_as_dataframe(self):
        try:
            if not MONGO_DB_URL:
                raise NetworkSecurityException(
                    Exception(f"Environment variable MONGO_DB_URL not set (got {MONGO_DB_URL!r})."),
                    sys
                )

            client = MongoClient(MONGO_DB_URL, serverSelectionTimeoutMS=5000)
            client.server_info()  # verify connection

            # debug output
            logging.info(f"Databases available: {client.list_database_names()}")
            db = client[self.data_ingestion_config.database_name]
            logging.info(f"Collections in {db.name!r}: {db.list_collection_names()}")

            collection = db[self.data_ingestion_config.collection_name]
            df = pd.DataFrame(list(collection.find()))
            if "_id" in df.columns:
                df.drop(columns=["_id"], inplace=True)
            
            df.replace({"na": np.nan}, inplace=True)
            return df
        except Exception as e:
            raise NetworkSecurityException(e, sys)
        
        
    def export_data_to_feature_store(self,dataframe: pd.DataFrame):
        try:
            feature_store_file_path = self.data_ingestion_config.feature_store_file_path
            # create folder
            dir_path = os.path.dirname(feature_store_file_path)
            os.makedirs(dir_path, exist_ok=True)
            dataframe.to_csv(feature_store_file_path, index=False, header=True)
            return dataframe
        except Exception as e:
            raise NetworkSecurityException(e, sys)
        
    def split_data_into_train_test(self, dataframe: pd.DataFrame):
        try: 
            train_set, test_set = train_test_split(dataframe, test_size=self.data_ingestion_config.train_test_split_ratio, random_state=self.data_ingestion_config.train_test_split_random_state)
            logging.info("performing train test split on the dataframe")
            
            logging.info("train test split completed")
            
            dir_path =  os.path.dirname(self.data_ingestion_config.training_file_path)
            os.makedirs(dir_path, exist_ok=True)
            
            logging.info("exporting train and test file path ")
            
            train_set.to_csv(self.data_ingestion_config.training_file_path, index=False, header=True)
            
            test_set.to_csv(self.data_ingestion_config.testing_file_path, index=False, header=True)
            
            logging.info("train and test file path exported")
            
        except Exception as e:
            raise NetworkSecurityException(e, sys)
    
    def initiate_data_ingestion(self):
        try:
            dataframe = self.export_collection_as_dataframe() #get data from mongodb
            dataframe = self.export_data_to_feature_store(dataframe) # export the features 
            self.split_data_into_train_test(dataframe) # split the data into train and test
            dataingestionartifact = DataIngestionArtifact(
                training_file_path=self.data_ingestion_config.training_file_path,
                testing_file_path=self.data_ingestion_config.testing_file_path
            ) # create the artifact
            return dataingestionartifact
        except Exception as e:
            raise NetworkSecurityException(e, sys)
    