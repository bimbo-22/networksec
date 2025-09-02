import sys,os

import certifi
ca = certifi.where()

from dotenv import load_dotenv
load_dotenv()
mongo_db_url = os.getenv("MONGO_DB_URL")
print(mongo_db_url)

import pymongo
import pandas as pd
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
from networksecurity.pipeline.training_pipeline import TrainingPipeline
from networksecurity.components.feature_extractor import FeatureExtractor
from networksecurity.entity.config_entity import FeatureExtractorConfig
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, File, UploadFile, Request
from uvicorn import run as app_run
from fastapi.responses import Response
from starlette.responses import RedirectResponse
from fastapi.templating import Jinja2Templates # for rendering HTML templates
from typing import Optional

import pandas as pd

from networksecurity.utils.main_utils.utils import load_object
from networksecurity.utils.ml_utils.model.estimator import NetworkModel
from networksecurity.constants.training_pipeline import DATA_INGESTION_COLLECTION_NAME
from networksecurity.constants.training_pipeline import DATA_INGESTION_DATABASE_NAME

# get mongoclient 

client = pymongo.MongoClient(mongo_db_url, tlsCAFile=ca)


logging.info("Starting training pipeline via /train endpoint")
database = client[DATA_INGESTION_DATABASE_NAME]
collection = database[DATA_INGESTION_COLLECTION_NAME]

app = FastAPI()
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins = origins,
    allow_credentials =True,
    allow_methods = ["*"],
    allow_headers=["*"]
)

features = {

}
# create a basemodel for the features
class Features(BaseModel):
    having_IP_Address: Optional[int]
    URL_Length: Optional[int]
    Shortining_Service: Optional[int]
    having_At_Symbol: Optional[int]
    double_slash_redirecting: Optional[int]
    Prefix_Suffix: Optional[int]
    having_Sub_Domain: Optional[int]
    SSL_final_state: Optional[int]
    Domain_registeration_length: Optional[int]
    Favicon: Optional[int]
    port: Optional[int]
    HTTPS_token: Optional[int]
    Request_URL: Optional[int]
    URL_of_Anchor: Optional[int]
    Links_in_tags: Optional[int]
    SFH: Optional[int]
    Submitting_to_email: Optional[int]
    Abnormal_URL: Optional[int]
    Redirect: Optional[int]
    on_mouseover: Optional[int]
    RightClick: Optional[int]
    popUpWidnow: Optional[int]
    Iframe: Optional[int]
    age_of_domain: Optional[int]
    DNSRecord: Optional[int]
    web_traffic: Optional[int]
    Page_Rank: Optional[int]
    Google_Index: Optional[int]
    Links_pointing_to_page: Optional[int]
    Statistical_report: Optional[int]




@app.get("/", tags=["authentication"])
async def index():
    return RedirectResponse(url="/docs")

@app.get("/train")
async def train_route():
    try:
        train_pipeline = TrainingPipeline()
        train_pipeline.run_pipeline()
        return Response("Training Successful")
    except Exception as e :
        raise NetworkSecurityException (e,sys)
    
    
templates = Jinja2Templates(directory="./templates")
@app.get("/predict")
async def predict_route(request: Request, file: UploadFile = File(...)):
    try:
        df = pd.read_csv(file.file)
        
        preprocessor = load_object("final_model/preprocessor.pkl")
        final_model = load_object("final_model/model.pkl")
        network_model = NetworkModel(preprocessor=preprocessor, model=final_model)
        print(df.iloc[0])
        y_pred = network_model.predict(df)
        df["prediction_column"] = y_pred
        print(df["prediction_column"])
        # df["predicted_column"].replace(-1,0)
        # return df.to_json()
        df.to_csv("prediction_output/output.csv")
        table_html = df.to_html(classes='table table-striped', index=False)
        return templates.TemplateResponse("predict.html", {"request": request, "table_html": table_html})
    except Exception as e:
        raise NetworkSecurityException(e, sys)
    

# testing the feature extractor
@app.post("/create-new-feature")
def create_new_feature_route(url: str, feature: Features):
    try:
        logging.info(f"Extracting features from the url: {url}")
        feature_extractor = FeatureExtractor(FeatureExtractorConfig())
        features_df = feature_extractor.extract_features(url)

        provided_features = feature.dict(exclude_unset=True)
        features_dict = features_df.iloc[0].to_dict()
        features_dict.update(provided_features)
        return features_dict
        # return features_df.to_dict(orient="records")[0]
    except Exception as e:
        raise NetworkSecurityException(e, sys)

# @app.get("/batch_prediction")
# async def
    
if __name__ == "__main__":
    app_run(app,host="0.0.0.0", port=8000)
















