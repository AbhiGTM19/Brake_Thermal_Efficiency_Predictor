import os
import time
import pandas as pd
import joblib
import mlflow
import mlflow.sklearn
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import GridSearchCV

DATA_PATH = os.getenv("BTE_DATASET_PATH", "bte_dataset_cleaned.csv")
MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "mlruns")  # Local folder

mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
mlflow.set_experiment("Brake Thermal Efficiency Prediction")


def train_and_save_model():
    start_time = time.time()
    print("🔁 Starting model training...")

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
    best_alpha = grid.best_params_['alpha']

    with mlflow.start_run(run_name="ridge_regression_run") as run:
        mlflow.log_params({"alpha": best_alpha})
        mlflow.sklearn.log_model(best_model, "ridge_model")
        mlflow.log_artifact("bte_dataset_cleaned.csv")  # Optional

        # Save scaler manually
        scaler_path = "scaler.pkl"
        joblib.dump(scaler, scaler_path)
        mlflow.log_artifact(scaler_path)

        print(f"✅ Model logged to MLflow (run_id: {run.info.run_id})")

    print(f"⏱️ Training time: {time.time() - start_time:.2f} seconds")


def predict_bte(input_dict):
    from mlflow.tracking import MlflowClient

    client = MlflowClient()
    
    # Get experiment by name
    experiment = client.get_experiment_by_name("Brake Thermal Efficiency Prediction")
    if experiment is None:
        raise ValueError("Experiment not found. Ensure the model has been trained and logged.")
    
    runs = client.search_runs(experiment_ids=[experiment.experiment_id], order_by=["start_time DESC"])
    if not runs:
        raise ValueError("No runs found in MLflow experiment. Train the model first.")

    latest_run = runs[0]
    run_id = latest_run.info.run_id

    model_uri = f"runs:/{run_id}/ridge_model"
    model = mlflow.sklearn.load_model(model_uri)

    artifacts_uri = latest_run.info.artifact_uri
    scaler_path = os.path.join(artifacts_uri.replace("file://", ""), "scaler.pkl")
    if not os.path.exists(scaler_path):
        raise FileNotFoundError("Scaler not found in MLflow artifacts.")

    scaler = joblib.load(scaler_path)

    feature_order = ['engine_load', 'fuel_blend_percentage', 'nanoparticle_concentration',
                     'injection_pressure', 'engine_speed']
    input_df = pd.DataFrame([input_dict], columns=feature_order)

    input_scaled = scaler.transform(input_df)
    prediction = model.predict(input_scaled)
    return prediction[0]


if __name__ == "__main__":
    train_and_save_model()