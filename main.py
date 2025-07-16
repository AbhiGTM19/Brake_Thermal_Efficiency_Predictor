from flask import Flask, request, jsonify, render_template
from train import predict_bte
import joblib
import os

MODEL_DIR = "models"
MODEL_PATH = os.path.join(MODEL_DIR, "model.pkl")
SCALER_PATH = os.path.join(MODEL_DIR, "scaler.pkl")

app = Flask(__name__)

@app.route("/")
@app.route("/home", methods=["GET"])
def index():
    return render_template('index.html')

@app.route("/predict", methods=["POST"])
def predict():
    try:
        input_data = request.get_json()

        # Validate all required keys
        expected_keys = ['engine_load', 'fuel_blend_percentage', 'nanoparticle_concentration',
                         'injection_pressure', 'engine_speed']
        if not all(key in input_data for key in expected_keys):
            return jsonify({"error": "Missing one or more required fields."}), 400

        prediction = predict_bte(input_data)
        return jsonify({"predicted_BTE": round(prediction, 3)})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
