from flask import Flask, request, jsonify
from train import predict_bte

app = Flask(__name__)

@app.route("/predict", methods=["POST"])
def predict():
    input_data = request.get_json()
    try:
        result = predict_bte(input_data)
        return jsonify({"predicted_BTE": round(result, 3)})
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    app.run(debug=True)
