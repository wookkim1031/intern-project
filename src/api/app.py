from flask import Flask, request, jsonify
from flask_cors import CORS  # Import flask-cors

app = Flask(__name__)

# Enable CORS for all routes and allow localhost:3000
CORS(app, origins=["http://localhost:3000"])

@app.route("/train", methods=["POST"])
def train():
    # Your existing code
    return jsonify({"message": "CORS is enabled!"})

if __name__ == "__main__":
    app.run(port=5000)