'''
========================================================================================================
predict.py - MODEL PREDICTIVE MODULE
========================================================================================================

'''

# --- Import libraries -----------------------------------------------------------------------------

import os
import joblib

# Data manipulation & visualization
import numpy as np
import pandas as pd

from .utils.split_data import split_data
from .utils.preprocessing import (
    allign_data, 
    drop_useless_columns, 
    add_new_features, 
    handle_missing_values, 
    encode_features, 
    standardize_data, 
    are_there_strings
)
from .utils.validation import calculate_metrics


# --- Constants ---------------------------------------------------------------------------------------

DEFAULT_MODEL_NAME = "xgboost_model.joblib"
WINNING_MODEL = "xgboost"


# --- Functions ---------------------------------------------------------------------------------------

def load_model(model_type="xgboost"):
    model_file_name = f"{model_type}_model.joblib"
    model_path = os.path.join(model_file_name)

    if not os.path.exists(model_path):
        raise FileNotFoundError(f"❌ Model not found in {model_path}.")
    
    print(f"Model loading in progress...")
    return joblib.load(model_path)

def predict_price(new_data, model, ohe, ordinal, scaler, bins_density, global_medians, density_mapping, geo_mapping):
    
    if isinstance(new_data, dict):
        df = pd.DataFrame([new_data])
    elif isinstance(new_data, pd.DataFrame):
        df = new_data.copy()
    else:
        raise TypeError(f"❌ Input data must be a Python dictionary or a Pandas DataFrame.")
    
    print(f"⏳ Preprocessing on {new_data} in progress...")
    # call preprocessing fuctions from utils.preprocessing
    X_live = df.copy()

    # print(f"START -> columns before preprocessing: {X_live.columns}")

    X_live = allign_data(X_live)
    # print(f"Columns after ALLIGN_DATA: {X_live.columns}")

    X_live = drop_useless_columns(X_live)
    # print(f"Columns after DROP_USELESS: {X_live.columns}")

    X_live, _, _ = add_new_features(X_live, density_mapping=density_mapping, geo_mapping=geo_mapping)
    # print(f"Columns after ADD_NEW_FEATURES: {X_live.columns}")
    
    X_live = handle_missing_values(X_live, global_medians=global_medians)
    # print(f"Columns after HANDLE_MISSING: {X_live.columns}")

    X_live, _, _, _= encode_features(X_live, ohe=ohe, ordinal=ordinal, bins_density=bins_density)
    # print(f"Columns after ENCODE: {X_live.columns}")

    X_live, _ = standardize_data(X_live, scaler=scaler)
    # print(f"after STD_DATA: columns before preprocessing: {X_live.columns}")

    # final parachute
    expected_features_model = model.feature_names_in_
    X_live = X_live[expected_features_model]

    are_there_strings(X_live)

    print("🔮 The model is predicting the price...")
    predictions = model.predict(X_live)

    if len(predictions) == 1:
           return float(predictions[0])
    return predictions




if __name__ == "__main__":

    dummy_data = {
        'living_area_m2': 120,
        'property_type': "apartment",
        'bedrooms': 3,
        'postal_code': 1000,
        'epc_score': 'B+',
        'total_area_m2': 250,
        'has_garden': None,
        'garden_area_m2': 50,
        'furnished': None,
        'has_terrace': True,
        'facades': 2,
        'building_year': 2015,
        'state_of_the_building': "Normal",
        'kitchen_equipped': "Fully equipped",
        'region': "Brussels",
        'province': "Brussels Capital Region",
        'floor_number': 8
    }

    try:
        model = load_model(model_type=WINNING_MODEL)
        
        scaler = joblib.load("scaler.joblib")
        ohe = joblib.load("ohe.joblib")
        ordinal = joblib.load("ordinal.joblib")
        bins_density = joblib.load("bins_density.joblib")
        density_mapping = joblib.load("density_mapping.joblib")
        geo_mapping = joblib.load("geo_mapping.joblib")

        global_medians = joblib.load("global_medians.joblib")

        estimated_price = predict_price(
            dummy_data, 
            model, 
            ohe, 
            ordinal, 
            scaler, 
            bins_density,
            global_medians,
            density_mapping, 
            geo_mapping
        )

        print(f"🏠 Estimated price for dummy property: {estimated_price:,.2f} €.")
         
    except Exception as e:
        print(f"❌ Error: {e}.")