# train.py

import os
import time
import pandas as pd
import joblib
import mlflow
import mlflow.sklearn
import logging
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import GridSearchCV
from mlflow.tracking import MlflowClient
from mlflow.exceptions import MlflowException

# Silencing GitPython warning in containerized environment
os.environ["GIT_PYTHON_REFRESH"] = "quiet"

# --- Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
DATA_PATH = os.getenv("BTE_DATASET_PATH", "bte_dataset_cleaned.csv")
docker_path = "/app/mlruns"
local_path = "./mlruns"
mlruns_path = docker_path if os.path.exists(docker_path) else local_path
MLFLOW_TRACKING_URI = f"file:{mlruns_path}"
MLFLOW_EXPERIMENT_NAME = "Brake Thermal Efficiency Prediction"
REGISTERED_MODEL_NAME = "bte-ridge-model"
SCALER_ARTIFACT_PATH = "scaler.pkl"


def train_and_save_model() -> None:
    """Trains a model, logs it, registers it (if needed), and assigns a 'production' alias."""
    start_time = time.time()
    logging.info("🔁 Starting model training and registration process...")

    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    logging.info(f"Using MLflow tracking URI: {mlflow.get_tracking_uri()}")
    mlflow.set_experiment(MLFLOW_EXPERIMENT_NAME)
    client = MlflowClient()

    df = pd.read_csv(DATA_PATH)
    X = df.drop("BTE", axis=1)
    y = df["BTE"]

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    ridge = Ridge()
    params = {'alpha': [0.01, 0.1, 1.0, 10.0, 100.0]}
    grid = GridSearchCV(ridge, params, cv=5, scoring='r2')
    grid.fit(X_scaled, y)

    best_model = grid.best_estimator_
    best_score = grid.best_score_
    logging.info(f"✅ GridSearchCV found best alpha: {grid.best_params_['alpha']} with R² score: {best_score:.4f}")

    with mlflow.start_run(run_name="ridge_regression_run") as run:
        model_info = mlflow.sklearn.log_model(sk_model=best_model, artifact_path="ridge_model")

        # Ensure the registered model exists
        try:
            client.get_registered_model(REGISTERED_MODEL_NAME)
            logging.info(f"Registered model '{REGISTERED_MODEL_NAME}' already exists.")
        except MlflowException:
            logging.info(f"Creating registered model '{REGISTERED_MODEL_NAME}' since it does not exist.")
            client.create_registered_model(REGISTERED_MODEL_NAME)

        registered_model = client.create_model_version(
            name=REGISTERED_MODEL_NAME,
            source=model_info.model_uri,
            run_id=run.info.run_id
        )
        version_number = registered_model.version
        logging.info(f"✅ Model registered as Version {version_number} of '{REGISTERED_MODEL_NAME}'")

        client.set_registered_model_alias(
            name=REGISTERED_MODEL_NAME,
            alias="production",
            version=version_number
        )
        logging.info(f"✅ Assigned alias 'production' to Version {version_number}.")

        # Save and log the scaler
        joblib.dump(scaler, SCALER_ARTIFACT_PATH)
        mlflow.log_artifact(SCALER_ARTIFACT_PATH)

    logging.info(f"⏱️ Training finished in {time.time() - start_time:.2f} seconds.")


def predict_bte(input_dict: dict) -> float:
    """Loads the production model and scaler, then performs prediction."""
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    client = MlflowClient()

    try:
        mlflow.set_tracking_uri("file:/app/mlruns")
        model_uri = f"models:/{REGISTERED_MODEL_NAME}@production"
        logging.info(f"Loading production model from URI: {model_uri}")
        model = mlflow.sklearn.load_model(model_uri)

        model_version_details = client.get_model_version_by_alias(REGISTERED_MODEL_NAME, "production")
        run_id = model_version_details.run_id
        scaler_path = client.download_artifacts(run_id, SCALER_ARTIFACT_PATH)
        scaler = joblib.load(scaler_path)

    except Exception as e:
        logging.error(f"❌ Failed to load model or scaler: {e}", exc_info=True)
        raise ValueError("Could not load model with alias 'production'. Ensure a model has been trained and alias is set.")

    feature_order = ['engine_load', 'fuel_blend_percentage', 'nanoparticle_concentration', 'injection_pressure', 'engine_speed']
    input_df = pd.DataFrame([input_dict], columns=feature_order)
    input_scaled = scaler.transform(input_df)
    prediction = model.predict(input_scaled)

    logging.info(f"Prediction successful for input: {input_dict}. Result: {prediction[0]:.3f}")
    return prediction[0]


if __name__ == "__main__":
    train_and_save_model()