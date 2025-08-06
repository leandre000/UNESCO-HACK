import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
import joblib
import os

# Simulate data
def generate_data(n=100):
    df = pd.DataFrame({
        'region_id': [f'R{i}' for i in range(n)],
        'child_population': np.random.randint(500, 10000, n),
        'conflict_risk': np.random.randint(0, 10, n),
        'food_insecurity': np.random.choice(['Low', 'Medium', 'High'], n),
        'school_destruction_rate': np.random.rand(n) * 100,
        'water_access': np.random.choice(['Good', 'Medium', 'Poor'], n),
        'recent_aid_delivered': np.random.choice([0, 1], n),
        'displacement_level': np.random.randint(0, 5000, n),
    })
    # Map to numeric for ML
    df['food_insecurity'] = df['food_insecurity'].map({'Low': 0, 'Medium': 1, 'High': 2})
    df['water_access'] = df['water_access'].map({'Good': 0, 'Medium': 1, 'Poor': 2})
    # Generate synthetic urgency score
    df['urgency_score'] = (
        0.3 * (df['conflict_risk'] / 10) +
        0.2 * (df['food_insecurity'] / 2) +
        0.2 * (df['school_destruction_rate'] / 100) +
        0.1 * (df['water_access'] / 2) +
        0.2 * (df['displacement_level'] / df['child_population'].max())
    )
    return df

def train_and_save_model(df, model_path):
    X = df.drop(['region_id', 'urgency_score'], axis=1)
    y = df['urgency_score']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    preds = model.predict(X_test)
    print("MAE:", mean_absolute_error(y_test, preds))
    joblib.dump(model, model_path)
    print(f"Model saved to {model_path}")

def main():
    df = generate_data(100)
    os.makedirs(os.path.dirname("../model/aidnet_model.pkl"), exist_ok=True)
    train_and_save_model(df, "../model/aidnet_model.pkl")

if __name__ == "__main__":
    main() 