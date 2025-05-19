import os 
import sys
import json

import pandas as pd
import numpy as np
import pymongo
from networksecurity.logging.logger import logging
from networksecurity.exception.exception import NetworkSecurityException

from dotenv import load_dotenv

load_dotenv()

MONGO_DB_URL = os.getenv("MONGO_DB_URL")

# ensure that the Https are certified 
import certifi
ca = certifi.where()




class NetworkDataExtraction():
    def __init__(self):
        try:
            pass
        except Exception as e:
            raise NetworkSecurityException(e, sys)
        
    def csv_to_json_converter(self,file_path):
        try:
            data = pd.read_csv(file_path)
            data.reset_index(drop=True, inplace=True)
            records = list(json.loads(data.T.to_json()).values())
            return records
        except Exception as e:
            raise NetworkSecurityException(e, sys)
        
    def push_data_to_mongo(self, records, database, collection):
        try:
            self.database = database
            self.collection = collection
            self.records = records
            self.mongo_client = pymongo.MongoClient(MONGO_DB_URL)
            self.database = self.mongo_client[self.database]
            self.collection = self.database[self.collection]
            self.collection.insert_many(self.records)
            
            return(len(self.records))
        except Exception as e:
            raise NetworkSecurityException(e, sys)  
        
if __name__ == "__main__":
    FILE_PATH = "Network_Data/phisingData.csv"
    DATABASE = "NetworkSec"
    COLLECTION = "NetworkData"
    networkobj = NetworkDataExtraction()
    records = networkobj.csv_to_json_converter(FILE_PATH)
    print(f"Number of records converted: {len(records)}")
    print(records)
    no_of_records = networkobj.push_data_to_mongo(records, DATABASE, COLLECTION)
    print(f"Number of records inserted: {no_of_records}")