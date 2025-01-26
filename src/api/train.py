import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from flask import Flask, request, jsonify
from flask_cors import CORS 
import numpy as np
import requests 
import json
from io import StringIO 
import plotly.express as px
import math

# Load configuration for the CSV URL
with open("config.json", "r") as file:
    config = json.load(file)

Sales_url = config["csv_files"]["sales"]  
Orders_url = config["csv_files"]["orders"]  
Products_url = config["csv_files"]["products"]  
Customers_url = config["csv_files"]["customers"]  

app = Flask(__name__)

CORS(app, origins=["http://localhost:3000"])

sales_df = None
orders_df = None
products_df = None
customers_df = None
order_sales = None
order_sales_customers = None
order_sales_customers_products = None

def fetch_csv_once(Sales_url, Orders_url, Products_url, Customers_url): 
    global sales_df, orders_df, products_df, customers_df, order_sales, order_sales_customers, order_sales_customers_products
    Customers_response = requests.get(Customers_url)
    Products_response = requests.get(Products_url)
    Orders_response = requests.get(Orders_url)
    Sales_response = requests.get(Sales_url)
    customers_text = Customers_response.text
    products_text = Products_response.text
    orders_text = Orders_response.text
    sales_text = Sales_response.text
    customers_df = pd.read_csv(StringIO(customers_text))
    products_df = pd.read_csv(StringIO(products_text))
    orders_df = pd.read_csv(StringIO(orders_text))
    sales_df = pd.read_csv(StringIO(sales_text))
    order_sales = pd.merge(orders_df, sales_df, on="Order.ID", how="outer")
    order_sales_customers = pd.merge(order_sales, customers_df, on="Customer.ID", how="left")
    order_sales_customers_products = pd.merge(order_sales_customers, products_df, on="Product.ID", how="left")

@app.before_request 
def load_csv():
    fetch_csv_once(Sales_url, Orders_url, Products_url, Customers_url)

def convert_to_serializable(obj):
    if isinstance(obj, np.ndarray):
        return obj.tolist()  # Convert ndarray to list
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")

@app.route("/countries", methods=["GET"])
def get_countries_list():
    countries = customers_df["Country"].unique()
    countries_list = countries.tolist()
    return jsonify({"countries": countries_list}) 

@app.route("/countries/<country>/cities", methods=["GET"])
def get_cities(country):
    country_data = customers_df[customers_df["Country"] == country]
    cities = country_data["City"].unique().tolist() 
    return jsonify({"cities": cities})

@app.route('/countries/<country>/years', methods=['GET'])
def get_years(country):
    country_data = order_sales_customers[order_sales_customers["Country"] == country]
    country_data["Order.Date"] = pd.to_datetime(country_data["Order.Date"])
    country_data["Year"] = country_data["Order.Date"].dt.year
    years = country_data["Year"].unique().tolist()  
    cleaned_years = [x for x in years if not math.isnan(x)]
    return jsonify({"years": sorted(cleaned_years)})

@app.route("/map", methods=["GET"])
def get_map_list():
    # profits map 
    profits = order_sales_customers.groupby("Country").agg({"Profit": "sum"}).reset_index()
    map_profit_fig = px.choropleth(
        profits, 
        locations="Country", 
        locationmode="country names", 
        color="Profit", title="Total Profit by Country")
    map_profit_json = map_profit_fig.to_plotly_json()
    map_profit_json_serializable = json.loads(json.dumps(map_profit_json, default=convert_to_serializable))
    # sales
    shipping_costs = order_sales_customers.groupby("Country").agg({"Shipping.Cost": "sum"}).reset_index()
    map_shipping_fig = px.choropleth(
        shipping_costs, 
        locations="Country", 
        locationmode="country names", 
        color="Shipping.Cost", 
        title="Total Shipping Cost by Country",
    )
    map_shipping_json = map_shipping_fig.to_plotly_json()
    map_shipping_json_serializable = json.loads(json.dumps(map_shipping_json, default=convert_to_serializable))
    # costumers
    customers = customers_df.groupby("Country").agg({"Customer.ID": "nunique"}).reset_index()
    map_customers_fig = px.choropleth(
        customers,
        locations="Country",
        locationmode="country names",
        color="Customer.ID",
        title="Total Customers by Country",
    )
    map_customers_json = map_customers_fig.to_plotly_json()
    map_customers_json_serializable = json.loads(json.dumps(map_customers_json, default=convert_to_serializable))
    return jsonify({
        "map_profit_fig": map_profit_json_serializable,
        "map_shipping_fig": map_shipping_json_serializable,
        "map_customers_fig": map_customers_json_serializable
    })

@app.route("/countries/<country_name>/<year>/<city>", methods=["GET"])
def get_country_data(country_name, year, city):
    order_sales_customers_products_country = order_sales_customers_products[order_sales_customers_products["Country"] == country_name]
    if year != "all":
        order_sales_customers_products_country["Order.DateTime"] = pd.to_datetime(order_sales_customers_products_country["Order.Date"])
        order_sales_customers_products_country["Year"] = order_sales_customers_products_country["Order.DateTime"].dt.year
        order_sales_customers_products_country = order_sales_customers_products_country[order_sales_customers_products_country["Year"] == int(year)]
    if city != "all":
        order_sales_customers_products_country = order_sales_customers_products_country[order_sales_customers_products_country["City"] == city]
    #Shows number of customers 
    len_customers = order_sales_customers_products_country["Customer.ID"].nunique()
    # Shows number of orders
    len_orders = order_sales_customers_products_country["Order.ID"].nunique()
    # Shows number of products
    len_products = order_sales_customers_products_country["Product.ID"].nunique()
    # Numbre of shipping costs 
    len_shipping_costs = order_sales_customers_products_country["Shipping.Cost"].nunique()
    # Shows total sales
    total_sales = order_sales_customers_products_country["Sales"].sum()
    # Shows total profit
    total_profit = order_sales_customers_products_country["Profit"].sum()
    total_profit = math.ceil(total_profit)
    print(len_customers, len_orders, len_products, total_sales, total_profit)
    # Product based on country 
    product_hierarchy = order_sales_customers_products_country.groupby(['Category', 'Sub-Category']).agg({'Sales': 'sum'}).reset_index()
    sunburst_fig = px.sunburst(
        product_hierarchy,
        path=['Category', 'Sub-Category'], 
        values='Sales',  
        title='Product Sales by Category and Subcategory',
        labels={'Sales': 'Total Sales'}
    )
    sunburst_json = sunburst_fig.to_plotly_json()
    sunburst_json_serializable = json.loads(json.dumps(sunburst_json, default=convert_to_serializable))
    # Sales over time
    sales_over_time = order_sales_customers_products_country.groupby('Order.Date')['Sales'].sum().reset_index()
    fig_sales_over_time = px.line(
        sales_over_time, 
        x='Order.Date', 
        y='Sales', 
        title=f'Sales in {city} City, {country_name} in Year {year}', 
        labels={'Sales': 'Total Sales', 'Order.Date': 'Date'}
    )
    fig_sales_over_time_json = fig_sales_over_time.to_plotly_json()
    fig_sales_over_time_json_serializable = json.loads(json.dumps(fig_sales_over_time_json, default=convert_to_serializable))
    # Profit over time
    profit_over_time = order_sales_customers_products_country.groupby('Order.Date').agg({
        'Profit': 'sum',
        'Shipping.Cost': 'sum',
        'Sales': 'sum'
    }).reset_index()
    fig_profit_over_time = px.line(
        profit_over_time,
        x='Order.Date',
        y=['Profit', 'Shipping.Cost', 'Sales'],
        title=f'Profit, Shipping Cost, and Sales over period at {country_name} in Year {year}',
        labels={'value': 'Amount', 'variable': 'Metric', 'Order.Date': 'Date'}
    )
    fig_profit_over_time.update_traces(line=dict(width=2))
    fig_profit_over_time.update_layout(
        legend_title_text='Metrics',
        xaxis_title='Date',
        yaxis_title='Amount',
        hovermode='x unified'
    )
    fig_profit_over_time_json = fig_profit_over_time.to_plotly_json()
    fig_profit_over_time_json_serializable = json.loads(json.dumps(fig_profit_over_time_json, default=convert_to_serializable))
    # Sort by sales in descending order and take the top 10 costumer (Which customers are the top 10 customers by sales?)
    top_customers = order_sales_customers_products_country.groupby('Customer.Name')['Sales'].sum().reset_index()
    top_customers = top_customers.sort_values(by='Sales', ascending=False).head(10)
    fig_top_customers = px.bar(top_customers, x='Customer.Name', y='Sales', 
                            title=f'Top 10 Customers by Sales at {country_name} in Year {year}',
                            labels={'Sales': 'Total Sales', 'Customer.Name': 'Customer Name'})
    fig_top_customers_json = fig_top_customers.to_plotly_json()
    fig_top_customers_json_serializable = json.loads(json.dumps(fig_top_customers_json, default=convert_to_serializable))
    # Shipping mode distribution (Question: Which shipping mode is most used?)
    shipping_mode_distribution = order_sales_customers_products_country['Ship.Mode'].value_counts().reset_index()
    shipping_mode_distribution.columns = ['Ship.Mode', 'Count']
    fig_shipping_mode = px.pie(shipping_mode_distribution, values='Count', names='Ship.Mode', 
                           title=f'Shipping Mode Distribution in {country_name} in Year {year}')
    fig_shipping_mode_json = fig_shipping_mode.to_plotly_json()
    fig_shipping_mode_json_serializable = json.loads(json.dumps(fig_shipping_mode_json, default=convert_to_serializable))
    return jsonify({
        "customers": len_customers,
        "orders": len_orders,
        "products": len_products,
        "total_sales": total_sales,
        "total_profit": total_profit,
        "shipping_costs": len_shipping_costs,
        "sales_over_time": fig_sales_over_time_json_serializable,
        "top_costumers": fig_top_customers_json_serializable,
        "shipping_mode": fig_shipping_mode_json_serializable,
        "profit_over_time": fig_profit_over_time_json_serializable, 
        "sunburst_products": sunburst_json_serializable
    })

@app.route("comparison/<country_1>/<country_2>", methods=["GET"])
def get_comparison(country_1, country_2):
    

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
