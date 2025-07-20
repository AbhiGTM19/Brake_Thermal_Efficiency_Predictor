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
    app.run(host="0.0.0.0", port=5000, debug=True)