import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import GridSearchCV
import joblib

def train_and_save_model():
    df = pd.read_csv("bte_dataset_cleaned.csv")
    X = df.drop("BTE", axis=1)
    y = df["BTE"]

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    model = Ridge()
    grid = GridSearchCV(model, {'alpha': [0.1, 1, 10]}, cv=5, scoring='r2')
    grid.fit(X_scaled, y)

    joblib.dump(grid.best_estimator_, "model.pkl")
    joblib.dump(scaler, "scaler.pkl")

def predict_bte(input_dict):
    model = joblib.load("model.pkl")
    scaler = joblib.load("scaler.pkl")
    input_df = pd.DataFrame([input_dict])
    input_scaled = scaler.transform(input_df)
    return model.predict(input_scaled)[0]
