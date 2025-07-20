import logging
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from train import predict_bte

# --- Configuration ---
# Set up basic logging to see output in your console
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize the Flask app
app = Flask(__name__)
CORS(app)


@app.route("/")
def index() -> str:
    """Renders the main HTML page."""
    return render_template('index.html')


@app.route("/status", methods=["GET"])
def status_check() -> tuple[str, int]:
    """Provides a health check endpoint for monitoring."""
    logging.info("Status check endpoint was called.")
    return jsonify({"message": "✅ App is running and ready to serve predictions."}), 200


@app.route("/predict", methods=["POST"])
def predict() -> tuple[str, int]:
    """
    Handles the prediction requests.

    Expects a JSON payload with engine parameters, validates the input,
    calls the prediction function, and returns the result.
    """
    try:
        input_data = request.get_json()
        logging.info(f"Received prediction request with data: {input_data}")

        # Validate that the input is a dictionary
        if not isinstance(input_data, dict):
            logging.warning("Prediction failed: Invalid input format (not a JSON object).")
            return jsonify({"error": "Invalid input format. Please send a JSON object."}), 400

        # Validate that all required keys are present
        expected_keys = [
            'engine_load', 'fuel_blend_percentage', 'nanoparticle_concentration',
            'injection_pressure', 'engine_speed'
        ]
        if not all(k in input_data for k in expected_keys):
            logging.warning(f"Prediction failed: Missing one or more required keys. Expected: {expected_keys}")
            return jsonify({
                "error": "Missing one or more required fields. Please include all fields."
            }), 400

        # Call the prediction function from train.py
        prediction = predict_bte(input_data)
        
        # Return the successful prediction
        return jsonify({"predicted_BTE": round(prediction, 3)})

    except ValueError as ve:
        # Catch specific errors raised from predict_bte (e.g., model not found)
        logging.error(f"Prediction ValueError: {ve}", exc_info=True)
        return jsonify({"error": str(ve)}), 500
        
    except Exception as e:
        # Catch any other unexpected errors
        logging.error(f"An unexpected error occurred during prediction: {e}", exc_info=True)
        return jsonify({"error": "An unexpected internal error occurred. Please check the server logs."}), 500


if __name__ == "__main__":
    # The debug=True is great for development, but should be False in production
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=True)