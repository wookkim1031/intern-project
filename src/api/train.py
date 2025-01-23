import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
import json

with open("config.json", "r") as file:
    config = json.load(file)

CSV_URL = config["csv_files"]["default"]

def handler(event, context):
    try:
        response = requests.get(CSV_URL)
        if response.status_code != 200:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Failed to fetch the CSV file!"}),
            }

        # Load the CSV content into a Pandas DataFrame
        csv_data = response.content.decode('utf-8')
        df = pd.read_csv(pd.compat.StringIO(csv_data))

        if "Sales" not in df or "Profit" not in df:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "CSV must contain 'Sales' and 'Profit' columns"}),
            }

        # Prepare data for training
        X = df[["Sales"]]
        y = df["Profit"]

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # Train the model
        model = LinearRegression()
        model.fit(X_train, y_train)

        # Calculate model accuracy
        accuracy = model.score(X_test, y_test)

        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Model trained successfully", "accuracy": accuracy}),
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)}),
        }