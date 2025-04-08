from flask import Flask, jsonify
from logs_prediction import logs_prediction

app = Flask(__name__)

@app.route("/api/v1/ml/logs-prediction", methods=["GET"])
def get_logs_prediction():
    return jsonify(logs_prediction())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=False)