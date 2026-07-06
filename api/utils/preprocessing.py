import os
import joblib
import numpy as np
import pandas as pd
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder, StandardScaler, MinMaxScaler
from sklearn.linear_model import Ridge
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error


# --- Constants ---------------------------------------------------------------------------------------

MAP_JOBLIB_PATH = "density_mapping.joblib"
GEO_MAP_PATH = "geo_mapping.joblib"

DEFAULTS = {
    'parking_count': 0,
    'bathrooms': 1,
    'has_garden': 0,
    'garden_area_m2': 0,
    'has_terrace': 0,
    'facades': 1,
    'furnished': 0,
    'has_elevator': 0,
    'has_garage': 0,
    'state_of_the_building': 'Normal',
    'kitchen_equipped': 'Not equipped',
    'floors_total': 0,
    'total_area_m2': 0,
    'km_from_nearby_city': 0,
    'is_nearby_city_prestigious': 0,
    'property_subtype': 'Unknown'
}


# --- Functions ---------------------------------------------------------------------------------------


# ========== PREPROCESSING PHASES ==========

# --- Allign input data ---

def allign_data(df):
    '''
    This function returns input data from user with also required features for preprocessing.
    Features in the dictionary DEFAULTS stated above as constant are injected with correspondant
    default value if the feature is not given by the user.
    '''

    df_copy = df.copy()
    # in case input data from user is missing required features, I add them here below using DEFAULTS dict
    for col in DEFAULTS.keys():
        if col not in df_copy.columns:
            df_copy[col] = None

    # unspecified features are filled with None
    df_copy = df_copy.fillna(value=DEFAULTS)

    return df_copy


# --- Drop Columns ---

# use **kwargs for making it a flexible function for feature chenges on preprocessing
# config dictionary
def drop_useless_columns(df):
    '''
    This function returns the dataframe without features that are not relevant for the model.
    '''

    df_copy = df.copy()

    COLS_TO_DROP = {
        "property_url": "Unique for each property - no predictive power",
        "address": "Unique for each property - no predictive power",
        "city": "Too many values - would affect negatively predictive power",
        "nearby_city": "Too many values - would affect negatively predictive power"
    }

    df_copy = df_copy.drop(columns=COLS_TO_DROP, errors='ignore')

    return df_copy


# --- Feature Engineering ---

def add_new_features(df, density_mapping, geo_mapping):
    '''
    ===================
    Feature Engineering
    ===================

    This function adds new features to the dataset.
    '''

    df_copy = df.copy()

    # ===========================
    #       'urban_density'
    # ===========================

    # collecting postal_code of current record
    p_code = df_copy['postal_code'].iloc[0]

    # if postal code exists in geo_mapping received as argument
    if geo_mapping is not None and p_code in geo_mapping:
        # filling fields only if they have not been specified by the user
        if 'province' not in df_copy.columns or df_copy['province'].isnull().all() or df_copy['province'].iloc[0] == 'Unknown':
            df_copy['province'] = geo_mapping[p_code]['province']
        if 'region' not in df_copy.columns or df_copy['region'].isnull().all() or df_copy['region'].iloc[0] == 'Unknown':
            df_copy['region'] = geo_mapping[p_code]['region']
        if 'latitude' not in df_copy.columns or pd.isnull(df_copy['latitude'].iloc[0]):
            df_copy['latitude'] = geo_mapping[p_code]['latitude']
        if 'longitude' not in df_copy.columns or pd.isnull(df_copy['longitude'].iloc[0]):
            df_copy['longitude'] = geo_mapping[p_code]['longitude']
    
    if density_mapping is not None:
        df_copy['urban_density'] = df_copy['postal_code'].map(density_mapping)

    # ===============================
    #         'property_age'
    # ===============================
    # 2026 - df['building_year']

    df_copy['property_age'] = 2026 - df_copy['building_year']

    # ===============================
    #      'living_area_ratio'
    # ===============================
    # df['living_area_m2'] / df['total_area_m2']

    df_copy['living_area_ratio'] = df_copy['living_area_m2'].div(df_copy['total_area_m2'].replace(0, np.nan))

    # ===============================
    #        'bedroom_density'
    # ===============================
    # df['bedrooms'] / df['living_area_m2']

    df_copy['bedroom_density'] = df_copy['bedrooms'].div(df_copy['total_area_m2'].replace(0, np.nan))

    return df_copy, density_mapping, geo_mapping


# --- Handle NaNs ---

def handle_missing_values(df, global_medians=None):
    '''
    This function returns the dataframe without NaNs:
        - fills missing numerical data with global medians;
        - fills missing categorial data with 'Unknown'.
    '''

    df_copy = df.copy()

    if global_medians is None:
        return df_copy
    
    # extractions of the two levels from the dictionary passed
    by_province = global_medians.get('by_province', {})
    national = global_medians.get('national', {})
    # collecting province
    province = df_copy['province'].iloc[0] if 'province' in df_copy.columns else None

    # --- LATITUDE ---
    if 'latitude' in df_copy.columns and 'province' in df_copy.columns:
        prov_lat_series = df_copy['province'].map(by_province.get('latitude', {}))
        df_copy['latitude'] = df_copy['latitude'].fillna(prov_lat_series).fillna(national.get('latitude', df_copy['latitude'].median()))
    elif 'latitude' in df_copy.columns:
        df_copy['latitude'] = df_copy['latitude'].fillna(national.get('latitude', df_copy['latitude'].median()))
    
    # --- LONGITUDE ---
    if 'longitude' in df_copy.columns and 'province' in df_copy.columns:
        prov_lat_series = df_copy['province'].map(by_province.get('longitude', {}))
        df_copy['longitude'] = df_copy['longitude'].fillna(prov_lat_series).fillna(national.get('latitude', df_copy['latitude'].median()))
    elif 'longitude' in df_copy.columns:
        df_copy['longitude'] = df_copy['longitude'].fillna(national.get('longitude', df_copy['latitude'].median()))
    
    # --- OTHER NUMERICAL FEATURES ---
    for col in ['living_area_ratio', 'bedroom_density', 'urban_density', 'property_age']:
        if col in df_copy.columns and col in national:
            df_copy[col] = df_copy[col].fillna(national[col])
    
    # final fix against strings
    remaining_text_cols = df_copy.select_dtypes(exclude='number').columns
    df_copy[remaining_text_cols] = df_copy[remaining_text_cols].fillna('Unknown')

    return df_copy

def encode_features(df, ohe=None, ordinal=None, bins_density=None):
    '''
    This function return data encoded using OneHotEncoder (ohe), OrdinalEncoder (ordinal)
    and bins_density in joblib files.'''

    df_copy = df.copy()

    # property_type mapping
    type_mapping = {
        'house': 0,
        'apartment': 1
    }
    if 'property_type' in df_copy.columns:
        df_copy['property_type'] = df_copy['property_type'].astype(str).str.lower().map(type_mapping)
        df_copy['property_type'] = df_copy['property_type'].fillna(1).astype(int)
    
    # coord_swapped
    if 'coord_swapped' not in df_copy.columns:
        df_copy['coord_swapped'] = 0

    # 0. Pre-Encoding - urban density binning
    if 'urban_density' in df_copy.columns:
        if bins_density is None:
            df_copy['urban_density'], bins_density = pd.qcut(
                df_copy['urban_density'],
                q=3,
                labels=False,
                retbins=True,
                duplicates='drop'
            )
        else:
            df_copy['urban_density'] = pd.cut(
                df_copy['urban_density'],
                bins=bins_density,
                labels=False,
                include_lowest=True
            )
        df_copy['urban_density'] = df_copy['urban_density'].astype(str)

    # 1. Ordinal Encoding +  Dtype Fix
    if ordinal:
        categ_cols_ordinal = list(ordinal.feature_names_in_)
        if all(col in df_copy.columns for col in categ_cols_ordinal):
            df_copy[categ_cols_ordinal] = ordinal.transform(df_copy[categ_cols_ordinal])
            # forcing float type
            df_copy[categ_cols_ordinal] = df_copy[categ_cols_ordinal].astype(float)
    
    # 2. OneHot Encoding + Index Fix
    if ohe:
        categ_cols_ohe = list(ohe.feature_names_in_) 
        if all(col in df_copy.columns for col in categ_cols_ohe):
            ohe_encoded = ohe.transform(df_copy[categ_cols_ohe])
            all_ohe_features = ohe.get_feature_names_out(categ_cols_ohe)
            ohe_df = pd.DataFrame(ohe_encoded, columns=all_ohe_features, index=df_copy.index)
            df_copy = pd.concat([df_copy, ohe_df], axis=1)
            df_copy = df_copy.drop(columns=categ_cols_ohe)

    
    return df_copy, ohe, ordinal, bins_density
    

# --- Feature Scaling ---

def standardize_data(df, scaler=None):
    '''
    This function returns data with numerical features standard scaled and also scaler.
    '''

    df_copy = df.copy()

    if scaler is not None:
        cols_to_scale = [c for c in scaler.feature_names_in_ if c in df_copy.columns]
        if cols_to_scale:
            df_copy[cols_to_scale] = df_copy[cols_to_scale].astype(float)
            df_copy[cols_to_scale] = scaler.transform(df_copy[cols_to_scale])

    return df_copy, scaler


def are_there_strings(df):
    '''
    This functions returns True if data after preprocessing is compliant for model inference.
    '''

    string_columns = df.select_dtypes(include=['object', 'category']).columns.tolist()
    if string_columns:
        raise TypeError(
            f'❌ Preprocessing validation failed.\nThe following columns still contain non-numerical values:\n'
            f'\n{", ".join(string_columns)}.\nReview Preprocessing Pipeline.'
        )
    return True



