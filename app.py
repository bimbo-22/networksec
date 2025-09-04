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
from typing import List

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
    having_ip_address: Optional[int]
    url_length: Optional[int]
    shortining_service: Optional[int]
    having_at_symbol: Optional[int]
    double_slash_redirecting: Optional[int]
    prefix_suffix: Optional[int]
    having_sub_domain: Optional[int]
    ssl_final_state: Optional[int]
    domain_registeration_length: Optional[int]
    favicon: Optional[int]
    port: Optional[int]
    https_token: Optional[int]
    request_url: Optional[int]
    url_of_anchor: Optional[int]
    links_in_tags: Optional[int]
    sfh: Optional[int]
    submitting_to_email: Optional[int]
    abnormal_url: Optional[int]
    redirect: Optional[int]
    on_mouseover: Optional[int]
    rightclick: Optional[int]
    popupwidnow: Optional[int]
    iframe: Optional[int]
    age_of_domain: Optional[int]
    dnsrecord: Optional[int]
    web_traffic: Optional[int]
    page_rank: Optional[int]
    google_index: Optional[int]
    links_pointing_to_page: Optional[int]
    statistical_report: Optional[int]





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
    
@app.post("/check-link")
def check_link(url:str, feature: Features):
    try:
        logging.info(f" check if the url: {url} is malicious or not")
        feature_extractor = FeatureExtractor(FeatureExtractorConfig())
        features_df = feature_extractor.extract_features(url)
        provided_features = feature.model_dump(exclude_unset=True)
        features_dict = features_df.iloc[0].to_dict()
        features_dict.update(provided_features)

        final_input_df = pd.DataFrame([features_dict])
        print(final_input_df)

        preprocessor = load_object("final_model/preprocessor.pkl")
        final_model = load_object("final_model/model.pkl")
        network_model = NetworkModel(preprocessor=preprocessor, model=final_model)
        y_pred = network_model.predict(final_input_df)
        if y_pred[0] == 1:
            return {"message": "The link is safe", "prediction": int(y_pred[0])}
        else:
            return {"message": "The link is malicious", "prediction": int(y_pred[0])}
    except Exception as e:
        raise NetworkSecurityException(e, sys)

# @app.get("/batch_prediction")
# async def
    
@app.post("/check-batch-link")
def check_batch_link(list_of_urls: List[str]):
    try:
        results = {}

        preprocessor = load_object("final_model/preprocessor.pkl")
        final_model = load_object("final_model/model.pkl")
        network_model = NetworkModel(preprocessor=preprocessor, model=final_model)
        feature_extractor = FeatureExtractor(FeatureExtractorConfig())

        for url in list_of_urls:
            logging.info(f" checking if url: {url} is malicious or not")

            features_df = feature_extractor.extract_features(url)
            features_dict = features_df.iloc[0].to_dict()

            input_df = pd.DataFrame([features_dict])
            y_pred = network_model.predict(input_df)

            print(y_pred)
            if y_pred[0] == 1:
                results[url] = {"message": "The link is safe", "prediction": int(y_pred[0])}
            else:
                results[url] = {"message": "The link is malicious", "prediction": int(y_pred[0])}

        return results
    except Exception as e:
        raise NetworkSecurityException(e, sys)


if __name__ == "__main__":
    app_run(app,host="0.0.0.0", port=8000)
















