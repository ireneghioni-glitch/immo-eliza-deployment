'''
========================================================================================================
app.py
========================================================================================================

'''

# import libraries
import joblib
import os

from typing import Literal, Union
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# from predict.py
from predict import load_model, predict_price, WINNING_MODEL



PORT = os.environ.get("PORT", 8000)
app = FastAPI() 



# LOADING ARTIFACTS
# =================

print("🔄 Loading model and transformers in memory...")

MODEL = load_model(model_type=WINNING_MODEL)
OHE = joblib.load("ohe.joblib")
ORDINAL = joblib.load("ordinal.joblib")
SCALER = joblib.load("scaler.joblib")
BINS_DENSITY = joblib.load("bins_density.joblib")
GLOBAL_MEDIANS = joblib.load("global_medians.joblib")
DENSITY_MAPPING = joblib.load("density_mapping.joblib")
GEO_MAPPING = joblib.load("geo_mapping.joblib")


print("✅ All artifacts are now ready in RAM.")



# PYDANTIC SCHEMA
# ===============

# entrance schema
class PropertyData(BaseModel):
    living_area_m2: float
    property_type: Union[Literal["House", "Apartment"], None] = None
    bedrooms: int
    postal_code: str
    epc_score: Literal['G', 'F', 'E-', 'E', 'E+', 'D-', 'D', 'D+', 'C-', 'C', 'C+', 'B-', 'B', 'B+', 'A-', 'A', 'A+', 'A++']
    total_area_m2: Union[int, None] = None
    has_garden: Union[bool, None] = None
    garden_area_m2: Union[int, None] = None
    furnished: Union[bool, None] = None
    has_terrace: Union[bool, None] = None
    facades: Union[int, None] = None
    building_year: Union[int, None] = None
    state_of_the_building: Union[Literal['To demolish', 'To restore', 'To renovate', 'Normal', 'Fully renovated', 'under construction', 'New'], None] = None
    kitchen_equipped: Union[Literal['Not equipped', 'Partially equipped', 'Fully equipped', 'Super equipped'], None] = None
    region: Union[Literal['Wallonia', 'Flanders', 'Brussels'], None] = None
    province: Union[Literal['Namur', 'Antwerp', 'Hainaut', 'Limburg', 'Brussels Capital Region', 'Walloon Brabant', 'East Flanders', 'Luxembourg', 'West Flanders', 'Liège', 'Flemish Brabant'], None] = None
    floor_number: Union[int, None] = None
    bathrooms: Union[int, None] = None
    

    
# GET route (Status check)
@app.get("/")
def read_root():
    return {"status": "API is working"}



# ENPOINT POST
# ============

# POST route for data Injection and Elaboration
# creating an endpoint that listens to POST requests
@app.post("/predict") # "/predict"
def predict_property_price(sale_expectation: PropertyData):
    # data from user is still in JSON format

    # access to Pydantic obj values
    data = sale_expectation.model_dump()
    # obj of PropertyData class (with data from user) is now a Python dictionary

    try:

        estimated_price = predict_price(
            data, 
            MODEL, 
            OHE, 
            ORDINAL, 
            SCALER, 
            BINS_DENSITY, 
            GLOBAL_MEDIANS, 
            DENSITY_MAPPING, 
            GEO_MAPPING
        ) 

        return {
            "prediction": estimated_price,
            "status_code": 200
        }
    
    except Exception as e: 

        raise HTTPException(
            status_code=400,
            detail=f"Error in prediction pipeline: {str(e)}"
        )


# .get() for asking rapidly infos to the server (querying the url)

# .post() for sending complex data to elaborate
    # params are inside request body in JSON format (how data travel across internet)
    # packed and validated inside pydantic class