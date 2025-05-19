from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import os 
import pymongo

from dotenv import load_dotenv
load_dotenv()

MONGO_DB_URL = os.getenv("MONGO_DB_URL")


# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)
def export_collection_as_dataframe(self):
    
    client = MongoClient(MONGO_DB_URL, serverSelectionTimeoutMS=5000)
    print("AVAILABLE DATABASES:", client.list_database_names())
    db = client[self.data_ingestion_config.database_name]
    print("AVAILABLE DATABASES:", client.list_database_names())
    print(f"AVAILABLE COLLECTIONS IN {db.name!r}:", db.list_collection_names())
    collection = db[self.data_ingestion_config.collection_name]
    
