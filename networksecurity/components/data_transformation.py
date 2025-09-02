from networksecurity.logging.logger import logging
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.entity.config_entity import DataTransformationConfig
from networksecurity.constants.training_pipeline import TARGET_COLUMN
from networksecurity.constants.training_pipeline import DATA_TRANSFORMATION_IMPUTER_PARAMS
from networksecurity.entity.artifact_entity import DataValidationArtifact, DataTransformationArtifact
from networksecurity.utils.main_utils.utils import save_numpy_array_data, save_object
from networksecurity.components.feature_extractor import FeatureExtractor

import os
import sys
import pandas as pd
import numpy as np
from sklearn.impute import KNNImputer
from sklearn.pipeline import Pipeline
import pickle


class DataTransformation:
    def __init__(self, data_validation_artifact: DataValidationArtifact, data_transformation_config: DataTransformationConfig):
        try:

            self.data_validation_artifact = data_validation_artifact
            self.data_transformation_config = data_transformation_config
        
        except Exception as e:
            raise NetworkSecurityException(e, sys)
        
        
    @staticmethod
    def read_data(file_path: str) -> pd.DataFrame:
        try:
            return pd.read_csv(file_path)
        except Exception as e:
            raise NetworkSecurityException(e, sys)
        
        
    def get_data_transformer_object(self) -> Pipeline:
        logging.info("Creating the data transformation pipeline")
        
        try:
            imputer = KNNImputer(**DATA_TRANSFORMATION_IMPUTER_PARAMS)
            logging.info(f"Initialized the KNN imputer with params: {DATA_TRANSFORMATION_IMPUTER_PARAMS}")
            processor: Pipeline = Pipeline(steps=[
                ('imputer', imputer)
            ])
            return processor
        except Exception as e:
            raise NetworkSecurityException(e, sys)
    def initiate_data_transformation(self) -> DataTransformationArtifact:
        logging.info("Starting the initiation of data transformation")
        try:
            # read the data
            train_df = self.read_data(self.data_validation_artifact.valid_train_file_path)
            test_df = self.read_data(self.data_validation_artifact.valid_test_file_path)
            
            # Extractiong features from the url trying to implement the feature extractor
            
            # drop columns for respective dataframes
            # training 
            input_feature_train_df = train_df.drop(columns=[TARGET_COLUMN], axis = 1)
            target_feature_train_df = train_df[TARGET_COLUMN]
            target_feature_train_df = target_feature_train_df.replace(-1,0)
            
            # testing
            input_feature_test_df = test_df.drop(columns=[TARGET_COLUMN], axis = 1)
            target_feature_test_df = test_df[TARGET_COLUMN]
            target_feature_test_df = target_feature_test_df.replace(-1,0)
            
            
            # implementing the knn imputer
            # only fit_transform on the training data
            # and transform on the test data
            preprocessor_object = self.get_data_transformer_object()
            transformed_input_train_feature = preprocessor_object.fit_transform(input_feature_train_df)
            transformed_input_test_feature = preprocessor_object.transform(input_feature_test_df)
            
            train_arr = np.c_[transformed_input_train_feature, np.array(target_feature_train_df)]
            test_arr = np.c_[transformed_input_test_feature, np.array(target_feature_test_df)]
            
            # transformed_data_dir = os.path.join(
            # self.data_transformation_config.data_transformation_dir,
            # self.data_transformation_config.
            # )
            # os.makedirs(transformed_data_dir, exist_ok=True)
            # save transformed data 
            save_numpy_array_data(self.data_transformation_config.transformed_train_file_path, array = train_arr,)
            save_numpy_array_data(self.data_transformation_config.transformed_test_file_path, array = test_arr,)
            save_object(self.data_transformation_config.transformed_object_file_path, obj = preprocessor_object,)
            
            save_object("final_model/preprocessor.pkl", preprocessor_object)
            
            # prepare artifacts
            data_transformation_artifact = DataTransformationArtifact(
             transformed_object_file_path= self.data_transformation_config.transformed_object_file_path,
             transformed_train_file_path =  self.data_transformation_config.transformed_train_file_path,
             transformed_test_file_path = self.data_transformation_config.transformed_test_file_path, 
            )
            return data_transformation_artifact
        except Exception as e:
            raise NetworkSecurityException(e, sys)