from flask import Flask, request, jsonify
from flask_cors import CORS  # Import flask-cors

app = Flask(__name__)

CORS(app, origins=["https://intern-project-liart.vercel.app"])

@app.route("/train", methods=["POST"])
def train():
    return jsonify({"message": "CORS is enabled!"})

if __name__ == "__main__":
    app.run(debug=True)
    #app.run(port=5000)