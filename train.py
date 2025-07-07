import os
import time
import pandas as pd
import joblib
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import GridSearchCV

# Dynamic path handling
DATA_PATH = os.getenv("BTE_DATASET_PATH", "bte_dataset_cleaned.csv")
MODEL_DIR = "models"


def train_and_save_model():
    start_time = time.time()
    print("🔁 Starting model training...")

    # Load dataset
    df = pd.read_csv(DATA_PATH)
    X = df.drop("BTE", axis=1)
    y = df["BTE"]

    # Scale input features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Ridge Regression + Hyperparameter Tuning
    ridge = Ridge()
    params = {'alpha': [0.01, 0.1, 1.0, 10.0, 100.0]}
    grid = GridSearchCV(ridge, params, cv=5, scoring='r2')
    grid.fit(X_scaled, y)

    # Create 'models' directory if it doesn't exist
    os.makedirs(MODEL_DIR, exist_ok=True)

    # Save model and scaler in 'models' directory
    joblib.dump(grid.best_estimator_, os.path.join(MODEL_DIR, "model.pkl"))
    joblib.dump(scaler, os.path.join(MODEL_DIR, "scaler.pkl"))

    end_time = time.time()
    duration = end_time - start_time
    print(f"✅ Model training complete. Best alpha: {grid.best_params_['alpha']}")
    print(f"📁 Artifacts saved in ./models/ directory")
    print(f"⏱️ Training time: {duration:.2f} seconds")


def predict_bte(input_dict):
    model = joblib.load(os.path.join(MODEL_DIR, "model.pkl"))
    scaler = joblib.load(os.path.join(MODEL_DIR, "scaler.pkl"))

    # Ensure input order matches training features
    feature_order = ['engine_load', 'fuel_blend_percentage', 'nanoparticle_concentration',
                     'injection_pressure', 'engine_speed']
    input_df = pd.DataFrame([input_dict], columns=feature_order)

    input_scaled = scaler.transform(input_df)
    prediction = model.predict(input_scaled)
    return prediction[0]


# Optional: Train on first run
if __name__ == "__main__":
    train_and_save_model()
