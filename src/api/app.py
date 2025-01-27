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
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from mlxtend.frequent_patterns import apriori, association_rules
from mlxtend.preprocessing import TransactionEncoder
import matplotlib.pyplot as plt
import seaborn as sns

# Load configuration for the CSV URL
with open("config.json", "r") as file:
    config = json.load(file)

Sales_url = config["csv_files"]["sales"]  
Orders_url = config["csv_files"]["orders"]  
Products_url = config["csv_files"]["products"]  
Customers_url = config["csv_files"]["customers"]  

app = Flask(__name__)

CORS(app, origins=["https://intern-project-liart.vercel.app"])

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
        return obj.tolist()  
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")

@app.route("/countries", methods=["GET"])
def get_countries_list():
    countries = customers_df["Country"].unique()
    countries_list = countries.tolist()
    return jsonify({"countries": countries_list}) 

@app.route("/products" , methods=["GET"])
def get_products_list():
    products = products_df["Product Name"].unique()
    products_list = products.tolist()
    countries = customers_df["Country"].unique()
    countries_list = countries.tolist()
    cities = customers_df["City"].unique()
    cities_list = cities.tolist()
    return jsonify({"products": products_list, "countries": countries_list, "cities": cities_list})

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

@app.route("/products/<product_name>/<country>/<city>", methods=["GET"])
def get_product_data(product_name, country, city):
    if product_name != "all":
        product_data = order_sales_customers_products[(order_sales_customers_products["Product Name"] == product_name)]
    else: 
        product_data = order_sales_customers_products
    if country != "all": 
        product_data = product_data[product_data["Country"] == country]
    if city != "all":
        product_data = product_data[product_data["City"] == city]
    countries_product = product_data["Country"].unique()
    countries_list = countries_product.tolist()
    cities_product = product_data["City"].unique()
    cities_list = cities_product.tolist()
    len_customers = product_data["Customer.ID"].nunique()
    len_orders = product_data["Order.ID"].nunique()
    len_products = product_data["Product.ID"].nunique()
    total_sales = product_data["Sales"].sum()
    total_profit = product_data["Profit"].sum()
    total_profit = math.ceil(total_profit)
    # Sales over time
    sales_over_time = product_data.groupby('Order.Date')['Sales'].sum().reset_index()
    fig_sales_over_time = px.line(
        sales_over_time,
        x='Order.Date',
        y='Sales',
        title=f'Sales Over Time for {product_name} in {city}, {country}',
        labels={'Sales': 'Total Sales', 'Order.Date': 'Date'}
    )
    fig_sales_over_time_json = fig_sales_over_time.to_plotly_json()
    fig_sales_over_time_json_serializable = json.loads(json.dumps(fig_sales_over_time_json, default=convert_to_serializable))
    # Profit over time
    profit_over_time = product_data.groupby('Order.Date').agg({
        'Profit': 'sum',
        'Shipping.Cost': 'sum',
        'Sales': 'sum'
    }).reset_index()
    fig_profit_over_time = px.line(
        profit_over_time,
        x='Order.Date',
        y=['Profit', 'Shipping.Cost', 'Sales'],
        title=f'Profit, Shipping Cost, and Sales Over Time for {product_name} in {country}',
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
    return jsonify({
        "countries_list": countries_list,
        "cities_list"  : cities_list,
        "customers": len_customers,
        "orders": len_orders,
        "products": len_products,
        "total_sales": total_sales,
        "total_profit": total_profit,
        "sales_over_time": fig_sales_over_time_json_serializable,
        "profit_over_time": fig_profit_over_time_json_serializable
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

@app.route("/advanced_metrics", methods=["GET"])    
def advanced_metrics_func(): 
    features = ["Sales", "Profit", "Shipping.Cost"]
    X = order_sales_customers_products[features] 
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    kmeans = KMeans(n_clusters=5, random_state=42)
    kmeans.fit(X_scaled)
    order_sales_customers_products["Cluster"] = kmeans.labels_
    cluster_summary = order_sales_customers_products.groupby("Cluster")[features].mean().reset_index()
    print(cluster_summary)
    fig = px.scatter(
        order_sales_customers_products,
        x="Profit",
        y="Shipping.Cost",
        color="Cluster",
        color_continuous_scale="viridis",
        size=None,
        title="Optimization of Sales using KMeans Clustering",
        labels={"Cluster": "Cluster", "Profit": "Profit", "Shipping.Cost": "Shipping Cost"}
    )
    fig_kmeans_json = fig.to_plotly_json()
    fig_kmeans_serializable = json.loads(json.dumps(fig_kmeans_json, default=convert_to_serializable))
    # to see the seasionality 
    seasonal_df = order_sales_customers_products[["Order.Date", "Product Name", "Sales", "Profit", "Shipping.Cost"]]
    seasonal_df["Order.Date"] = pd.to_datetime(seasonal_df["Order.Date"])
    seasonal_df["Month"] = seasonal_df["Order.Date"].dt.month
    seasonal_df["Year"] = seasonal_df["Order.Date"].dt.year
    seasonal = seasonal_df.groupby(["Product Name", "Month"])["Sales"].sum().unstack()
    seasonal_normalized = seasonal.div(seasonal.sum(axis=1), axis=0)
    seasonal_products = seasonal_normalized.idxmax(axis=1)
    print(seasonal_products)
    seasonal_temp = seasonal.max(axis=1) / seasonal.sum(axis=1)
    seasonal_df = seasonal_df.merge(seasonal_temp.rename("Seasonality.Index"), how="left", left_on="Product Name", right_index=True)
    features_seasonal = ["Sales", "Profit", "Shipping.Cost", "Seasonality.Index"]
    # there is nan somewhere
    # replacing nan values with mean value 
    X_seasonal = seasonal_df[features_seasonal]
    scaler = StandardScaler()
    X_seasonal_scaled = scaler.fit_transform(X_seasonal)
    kmeans_seasonal = KMeans(n_clusters=5, random_state=42)
    seasonal_df["Cluster"] = kmeans_seasonal.fit_predict(X_seasonal_scaled)
    seasonal_summary = seasonal_df.groupby("Cluster")[features].mean()
    print(seasonal_summary)
    fig_seasonal = px.scatter(
        seasonal_df,
        x="Profit",
        y="Seasonality.Index",
        color="Cluster",
        color_continuous_scale="viridis",
        size=None,
        title="Seasonality Index and Profit Optimization",
        labels={"Cluster": "Cluster", "Profit": "Profit", "Shipping.Cost": "Shipping Cost"}
    )
    fig_seasonal_json = fig_seasonal.to_plotly_json()
    fig_seasonal_serializable = json.loads(json.dumps(fig_seasonal_json, default=convert_to_serializable))
    # Define the 5 most and least trending product (using 365 days data)
    # Compare the trending between the year_before and now 
    order_sales_customers_products["Order.Date"] = pd.to_datetime(order_sales_customers_products["Order.Date"])
    end_date = order_sales_customers_products["Order.Date"].max()
    start_date = end_date - pd.Timedelta(days=365)
    recent_sales = order_sales_customers_products[order_sales_customers_products["Order.Date"].between(start_date, end_date)]
    product_sales = recent_sales.groupby("Product Name")["Sales"].sum().reset_index()
    # The trending of the previosu year 
    previous_start_date = start_date - pd.Timedelta(days=365)
    previous_sales = order_sales_customers_products[order_sales_customers_products["Order.Date"].between(previous_start_date, start_date)]
    previous_product_sales = previous_sales.groupby("Product Name")["Sales"].sum().reset_index()
    growing = pd.merge(
        product_sales,
        previous_product_sales,
        on="Product Name",
        suffixes=("_recent", "_previous"),
    )
    growing["Growth"] = (growing["Sales_recent"] - growing["Sales_previous"])
    growing["Growth"].fillna(0, inplace=True)
    grow_sort = growing.sort_values(by="Growth", ascending=False)
    top_5 = grow_sort.head(5)
    bottom_5 = grow_sort.tail(5)
    trending_prod = pd.concat([top_5, bottom_5])
    trending_prod["Trend"] = ["Trending"] * 5 + ["Non-Trending"] * 5
    fig_trending = px.bar(
        trending_prod,
        x="Product Name",
        y="Growth",
        color="Trend",
        title="top 5 most trending and least trending product (Comapred with last year)",
        labels={"Growth": "Sales Growth (%)", "Product Name": "Product"},
        color_discrete_map={"Trending": "green", "Non-Trending": "red"},
    )
    fig_trending.update_layout(
        xaxis_title="Product",
        yaxis_title="Sales Growth (%)",
        showlegend=True,
    )
    fig_trending_json = fig_trending.to_plotly_json()
    fig_trending_serial = json.loads(json.dumps(fig_trending_json, default=convert_to_serializable))
    # Goal: To find the most profitable country, emerging country, decling country, not profitable coountry
    group_country_sales = recent_sales.groupby("Country")["Sales"].sum().reset_index()
    previous_group_country_sales = previous_sales.groupby("Country")["Sales"].sum().reset_index()
    growth_by_country = pd.merge(
        group_country_sales, previous_group_country_sales, on="Country", suffixes=("_recent", "_previous")
    )
    # current sales - previous sales dividde by previous sales to see the correlation between previous year and current year
    growth_by_country["Growth"] = ((growth_by_country["Sales_recent"] - growth_by_country["Sales_previous"]) / growth_by_country["Sales_previous"])*100
    growth_by_country["Growth"].fillna(0, inplace=True)
    most_sold_country = growth_by_country.loc[growth_by_country["Sales_recent"].idxmax()]
    least_sold_country = growth_by_country.loc[growth_by_country["Sales_recent"].idxmin()]
    emerging_country = growth_by_country.loc[growth_by_country["Growth"].idxmax()]
    decling_country = growth_by_country.loc[growth_by_country["Growth"].idxmin()]
    visualization_data = pd.DataFrame({
        "Country": [most_sold_country["Country"], least_sold_country["Country"], emerging_country["Country"], decling_country["Country"]],
        "Category": ["Most Sold", "Least Sold", "Emerging", "Decreasing"],
        "Sales": [most_sold_country["Sales_recent"], least_sold_country["Sales_recent"], emerging_country["Sales_recent"], decling_country["Sales_recent"]],
        "Growth": [most_sold_country["Growth"], least_sold_country["Growth"], emerging_country["Growth"], decling_country["Growth"]],
    })
    fig_sales = px.bar(
        visualization_data,
        x="Country",
        y="Sales",
        color="Category",
        title="Sales by Country (Last year)",
        labels={"Sales": "Total Sales", "Country": "Country"},
        text="Sales",
    )
    fig_sales.add_scatter(
        x=visualization_data["Country"],
        y=visualization_data["Growth"],
        mode="lines+markers+text",
        name="Growth percentage",
        text=visualization_data["Growth"],
        textposition="top center",
        line=dict(color="red", width=2),
        yaxis="y2",
    )
    fig_sales.update_layout(
        xaxis_title="Country",
        yaxis_title="Total Sales",
        yaxis2=dict(title="Growth percentage", overlaying="y", side="right"),
        showlegend=True,
    )
    fig_sales_json = fig_sales.to_plotly_json()
    fig_sales_serial = json.loads(json.dumps(fig_sales_json, default=convert_to_serializable))
    # calculate
    customer_data = order_sales_customers_products.groupby("Customer.ID").agg({
        "Sales": "sum",               
        "Order.ID": "nunique",        
        "Order.Date": "max"           
    }).reset_index()
    customer_data.columns = ["Customer.ID", "Total_Sales", "Count_Orders", "last_purchase_date"]
    # Calculate recency (days since last purchase)
    customer_data["last_purchase_date"] = pd.to_datetime(customer_data["last_purchase_date"])
    current_date = pd.to_datetime(order_sales_customers_products["Order.Date"].max())
    customer_data["Recency"] = (current_date - customer_data["last_purchase_date"]).dt.days
    high_value_threshold = customer_data["Total_Sales"].quantile(0.8)
    high_value_customers = customer_data[customer_data["Total_Sales"] >= high_value_threshold]
    frequent_buyer_threshold = customer_data["Count_Orders"].quantile(0.8)
    frequent_buyers = customer_data[customer_data["Count_Orders"] >= frequent_buyer_threshold]
    at_risk_customers = customer_data[customer_data["Recency"] > 180]
    at_risk_threshold = 180
    customer_data["Segment"] = "Regular"
    customer_data.loc[customer_data["Total_Sales"] >= high_value_threshold, "Segment"] = "High-Value"
    customer_data.loc[customer_data["Count_Orders"] >= frequent_buyer_threshold, "Segment"] = "Frequent Buyer"
    customer_data.loc[customer_data["Recency"] > at_risk_threshold, "Segment"] = "At-Risk"
    fig_high_value = px.scatter(
        customer_data,
        x="Count_Orders",
        y="Total_Sales",
        color="Segment",
        size="Recency",
        hover_name="Customer.ID",
        title="Risk evaluation",
        labels={
            "Count_Orders": "Number of Orders",
            "Total_Sales": "Sales Total",
            "Segment": "Customer Segment"
        }
    )
    fig_high_value.update_layout(
        xaxis_title="Number of Orders",
        yaxis_title="Sales Total",
        legend_title="Customer Segment",
        hovermode="closest"
    )
    fig_high_json = fig_high_value.to_plotly_json()
    fig_high_serializable = json.loads(json.dumps(fig_high_json, default=convert_to_serializable))
    return jsonify({"kmeans": fig_kmeans_serializable, "seasonal": fig_seasonal_serializable, "trending": fig_trending_serial, "sales_growth": fig_sales_serial, "high_value": fig_high_serializable})

@app.route("/comparison/<country_1>/<country_2>", methods=["GET"])
def get_comparison(country_1, country_2):
    if country_1 != "all":
        country1_df = order_sales_customers_products[order_sales_customers_products["Country"] == country_1]
    else: 
        country1_df = order_sales_customers_products
    if country_2 != "all":
        country2_df = order_sales_customers_products[order_sales_customers_products["Country"] == country_2]
    else:
        country2_df = order_sales_customers_products
    def calculate_metrics_sales_profit_shipping(df, country): 
        return {
            "country": country, 
            "total_sales": df["Sales"].sum(),
            "total_profit": df["Profit"].sum(),
            "total_shipping_costs": df["Shipping.Cost"].sum(),
        }
    country1_metric_high = calculate_metrics_sales_profit_shipping(country1_df, country_1)
    country2_metric_high = calculate_metrics_sales_profit_shipping(country2_df, country_2)
    def calculate_metrics_customers_orders_products(df, country):
        return {
            "country": country,
            "total_customers": df["Customer.ID"].nunique(),
            "total_orders": df["Order.ID"].nunique(),
            "total_products": df["Product.ID"].nunique()
        }
    country1_metric = calculate_metrics_customers_orders_products(country1_df, country_1)
    country2_metric = calculate_metrics_customers_orders_products(country2_df, country_2)
    # generate bar chart for sales, profit, shipping cost 
    def generate_charts_sales_profit_shipping(metrics_country1, metrics_country2, country1_name, country2_name):
        bar_chart_data = {
            "Metrics": ["Total Sales", "Total Profit", "Total Shipping Cost"],
            country1_name: [
                metrics_country1["total_sales"], metrics_country1["total_profit"], metrics_country1["total_shipping_costs"],
            ],
            country2_name: [
                metrics_country2["total_sales"], metrics_country2["total_profit"], metrics_country2["total_shipping_costs"],
            ]
        }
        df = pd.DataFrame(bar_chart_data)
        df_melted = df.melt(id_vars="Metrics", var_name="Country", value_name="Value")
        fig = px.bar(
            df_melted,
            x="Metrics", y="Value",
            color="Country", barmode="group",  
            title=f"Comparison of Sales, Profit, and Shipping Cost in {country1_name} and {country2_name}",
            labels={"Value": "Values", "Metrics": "Metrics", "Country": "Country"},
        )
        fig_bar_json = fig.to_plotly_json()
        return json.loads(json.dumps(fig_bar_json, default=convert_to_serializable))
    # generate bar chart for customers, orders, products
    def generate_charts_customers_orders_products(metrics_country1, metrics_country2, country1_name, country2_name):
        bar_chart_data_2 = {
            "Metrics": ["Customers", "Orders", "Products"],
            country1_name: [
                metrics_country1["total_customers"], metrics_country1["total_orders"], metrics_country1["total_products"]
            ],
            country2_name: [
                metrics_country2["total_customers"], metrics_country2["total_orders"], metrics_country2["total_products"]
            ]
        }
        df_2 = pd.DataFrame(bar_chart_data_2)
        df_melted_2 = df_2.melt(id_vars="Metrics", var_name="Country", value_name="Value")
        fig_2 = px.bar(
            df_melted_2,
            x="Metrics", y="Value",
            color="Country", barmode="group", 
            title=f"Comparison of Customers, Orders, and Products in {country1_name} and {country2_name}",
            labels={"Value": "Values", "Metrics": "Metrics", "Country": "Country"},
        )
        fig_bar_2_json = fig_2.to_plotly_json()
        return json.loads(json.dumps(fig_bar_2_json, default=convert_to_serializable))
    def generate_line_chart(metrics_country1, metrics_country2, country1_name, country2_name):
        sales_over_time_country1 = metrics_country1.groupby('Order.Date')['Sales'].sum().reset_index()
        sales_over_time_country2 = metrics_country2.groupby('Order.Date')['Sales'].sum().reset_index()
        fig_line_sales = px.line(
            sales_over_time_country1,
            x='Order.Date',
            y='Sales',
            title=f'Sales over Time: {country1_name} vs {country2_name}',
            labels={'Sales': 'Total Sales', 'Order.Date': 'Date'},
            line_shape="spline"
        )
        fig_line_sales.add_scatter(
            x=sales_over_time_country2['Order.Date'],
            y=sales_over_time_country2['Sales'],
            mode='lines',
            name=f'{country2_name} Sales',
            line=dict(dash='dash') 
        )
        fig_line_sales.update_layout(
            legend=dict(
                title='Countries',
                itemsizing='trace'
            )
        )
        fig_line_sales_json = fig_line_sales.to_plotly_json()
        return json.loads(json.dumps(fig_line_sales_json, default=convert_to_serializable))
    return jsonify({"bar_1_chart": generate_charts_sales_profit_shipping(country1_metric_high, country2_metric_high, country_1, country_2), 
                    "bar_2_chart": generate_charts_customers_orders_products(country1_metric, country2_metric, country_1, country_2), 
                    "line_sales_chart" : generate_line_chart(country1_df, country2_df, country_1, country_2)})


@app.route("/train", methods=["POST"])
def train():
    try:
        response = requests.get(Sales_url)
        if response.status_code != 200:
            return jsonify({"error": f"Failed to fetch CSV file: {response.status_code}"}), 400
        csv_content = response.text 
        df = pd.read_csv(StringIO(csv_content))
        if "Sales" not in df.columns or "Profit" not in df.columns:
            return jsonify({"error": "CSV must contain 'Sales' and 'Profit' columns"}), 400
        X = df[["Sales"]]
        y = df["Profit"]
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        model = LinearRegression()
        model.fit(X_train, y_train)
        accuracy = model.score(X_test, y_test)

        return jsonify({"message": "Model trained successfully!", "accuracy": accuracy})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
