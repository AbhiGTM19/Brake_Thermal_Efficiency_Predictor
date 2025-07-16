# main.py
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from train import predict_bte
import os


MODEL_DIR = "models"
MODEL_PATH = os.path.join(MODEL_DIR, "model.pkl")
SCALER_PATH = os.path.join(MODEL_DIR, "scaler.pkl")

app = Flask(__name__)
CORS(app)

@app.route("/")
@app.route("/home", methods=["GET"])
def index():
    return render_template('index.html')

# NEW ROUTE for status check
@app.route("/status", methods=["GET"])
def status_check():
    try:
        if os.path.exists(MODEL_PATH) and os.path.exists(SCALER_PATH):
            return jsonify({"status": "ok"}), 200
        else:
            return jsonify({"message": "⚠️ Backend is running, but models not found.", "status": "warning"}), 200
    except Exception as e:
        return jsonify({"message": f"❌ Backend encountered an error: {str(e)}", "status": "error"}), 500

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
    app.run(host="0.0.0.0", port=5000, debug=False)