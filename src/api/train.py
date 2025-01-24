import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from flask import Flask, request, jsonify
from flask_cors import CORS 
import requests 
import json
from io import StringIO 

# Load configuration for the CSV URL
with open("config.json", "r") as file:
    config = json.load(file)

Sales_url = config["csv_files"]["sales"]  
Orders_url = config["csv_files"]["orders"]  
Products_url = config["csv_files"]["products"]  
Customers_url = config["csv_files"]["customers"]  

app = Flask(__name__)

CORS(app, origins=["http://localhost:3000"])

@app.route("/countries", methods=["GET"])
def get_countries_list():
    response = requests.get(Customers_url)
    csv_content = response.text
    df = pd.read_csv(StringIO(csv_content))
    countries = df["Country"].unique()
    return jsonify({"countries": countries}) 

@app.route("/countries/<country_name>", methods=["GET"])
def get_country_data(country_name):
    response = requests.get(Customers_url)
    csv_content = response.text
    df = pd.read_csv(StringIO(csv_content))

    
    

@app.route("/train", methods=["POST"])
def train():
    try:
        response = requests.get(Sales_url)
        if response.status_code != 200:
            return jsonify({"error": f"Failed to fetch CSV file: {response.status_code}"}), 400

        csv_content = response.text 
        df = pd.read_csv(StringIO(csv_content))

        # Validate the required columns
        if "Sales" not in df.columns or "Profit" not in df.columns:
            return jsonify({"error": "CSV must contain 'Sales' and 'Profit' columns"}), 400

        # Prepare the data for ML training
        X = df[["Sales"]]
        y = df["Profit"]
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # Train a simple linear regression model
        model = LinearRegression()
        model.fit(X_train, y_train)

        # Calculate accuracy
        accuracy = model.score(X_test, y_test)

        return jsonify({"message": "Model trained successfully!", "accuracy": accuracy})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(port=5000)
