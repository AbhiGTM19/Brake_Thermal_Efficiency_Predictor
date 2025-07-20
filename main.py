from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from train import predict_bte

app = Flask(__name__)
CORS(app)

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/status", methods=["GET"])
def status_check():
    return jsonify({"message": "✅ App running, model loaded via MLflow"}), 200

@app.route("/predict", methods=["POST"])
def predict():
    try:
        input_data = request.get_json()
        expected_keys = ['engine_load', 'fuel_blend_percentage', 'nanoparticle_concentration',
                         'injection_pressure', 'engine_speed']
        if not all(k in input_data for k in expected_keys):
            return jsonify({"error": "Missing one or more required fields."}), 400

        prediction = predict_bte(input_data)
        return jsonify({"predicted_BTE": round(prediction, 3)})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)