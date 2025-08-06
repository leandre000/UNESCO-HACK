from fastapi import FastAPI
import pandas as pd
from aidnet_api.schemas import RegionData, BatchRegionData
import joblib
import numpy as np
import os
from fastapi import UploadFile, File, HTTPException
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
import shutil

app = FastAPI()

MODEL_PATH = os.path.join(os.path.dirname(__file__), 'model', 'aidnet_model.pkl')
model = joblib.load(MODEL_PATH)

@app.post("/predict")
def predict(data: RegionData):
    feature_names = [
    "child_population", "conflict_risk", "food_insecurity",
    "school_destruction_rate", "water_access",
    "recent_aid_delivered", "displacement_level"
]
    features = pd.DataFrame([data.dict()], columns=feature_names)
    score = model.predict(features)[0]
    return {"urgency_score": round(float(score), 3)}

@app.post("/predict_batch")
def predict_batch(batch: BatchRegionData):
    features = np.array([[v for v in region.dict().values()] for region in batch.regions])
    scores = model.predict(features)
    return {"urgency_scores": [round(float(s), 3) for s in scores]}

@app.post("/train")
def train_model(file: UploadFile = File(...)):
    # Save uploaded file to a temp location
    temp_path = os.path.join(os.path.dirname(__file__), 'model', 'uploaded_data.csv')
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    try:
        df = pd.read_csv(temp_path)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid CSV: {e}")
    # Check required columns
    required_cols = [
        'region_id', 'child_population', 'conflict_risk', 'food_insecurity',
        'school_destruction_rate', 'water_access', 'recent_aid_delivered', 'displacement_level', 'urgency_score'
    ]
    if not all(col in df.columns for col in required_cols):
        raise HTTPException(status_code=400, detail=f"CSV must contain columns: {required_cols}")
    # Train model
    X = df.drop(['region_id', 'urgency_score'], axis=1)
    y = df['urgency_score']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model_new = RandomForestRegressor(n_estimators=100, random_state=42)
    model_new.fit(X_train, y_train)
    preds = model_new.predict(X_test)
    mae = mean_absolute_error(y_test, preds)
    # Save and hot-reload model
    joblib.dump(model_new, MODEL_PATH)
    global model
    model = model_new
    return {"message": "Model retrained and reloaded.", "MAE": mae}

@app.get("/health")
def health_check():
    return {"status": "OK", "model": "AidNet v1"}

@app.get("/features")
def get_features():
    return {
        "features": [
            "child_population", "conflict_risk", "food_insecurity",
            "school_destruction_rate", "water_access",
            "recent_aid_delivered", "displacement_level"
        ]
    } 