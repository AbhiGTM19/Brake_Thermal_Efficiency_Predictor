import logging
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from train import predict_bte

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)
CORS(app)

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/status", methods=["GET"])
def status_check():
    logging.info("✅ Status check hit.")
    return jsonify({"message": "✅ App is running and ready to serve predictions."}), 200

@app.route("/predict", methods=["POST"])
def predict():
    try:
        input_data = request.get_json()
        logging.info(f"Received input: {input_data}")

        expected_keys = ['engine_load', 'fuel_blend_percentage', 'nanoparticle_concentration', 'injection_pressure', 'engine_speed']
        if not all(k in input_data for k in expected_keys):
            return jsonify({"error": f"Missing fields. Required: {expected_keys}"}), 400

        prediction = predict_bte(input_data)
        return jsonify({"predicted_BTE": round(prediction, 3)})

    except ValueError as ve:
        logging.error(f"ValueError during prediction: {ve}", exc_info=True)
        return jsonify({"error": str(ve)}), 500
    except Exception as e:
        logging.error(f"Unexpected error during prediction: {e}", exc_info=True)
        return jsonify({"error": "An unexpected error occurred. Please try again later."}), 500

if __name__ == "__main__":
    import os
    try:
        from huggingface_hub import hf_hub_download, snapshot_download
        logging.info("Downloading MLflow models from HF Hub...")
        # Download only the necessary model files to avoid overwriting README.md
        snapshot_download(repo_id="abhshkgtm19/BTE-Predictor-Models", allow_patterns=["mlruns/**", "scaler.pkl"], local_dir="/app", local_dir_use_symlinks=False)
        logging.info("Models downloaded successfully!")
    except Exception as e:
        logging.error(f"Failed to download models from HF Hub: {e}")

    port = int(os.environ.get("PORT", 7860))
    app.run(host="0.0.0.0", port=port, debug=False)