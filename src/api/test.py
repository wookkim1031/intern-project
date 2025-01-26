import pandas as pd
import os
import plotly.graph_objects as go
import plotly.express as px

base_dir = os.path.dirname(os.path.abspath(__file__)) 
customers_path = os.path.join(base_dir, "../csv/customers.csv")  
orders_path = os.path.join(base_dir, "../csv/orders.csv")  
products_path = os.path.join(base_dir, "../csv/products.csv")  
sales_path = os.path.join(base_dir, "../csv/sales.csv")

customers_df = pd.read_csv(customers_path)
orders_df = pd.read_csv(orders_path)
products_df = pd.read_csv(products_path)
sales_df = pd.read_csv(sales_path)

merged = pd.merge(orders_df, customers_df, on="Customer.ID")
order_sales = pd.merge(orders_df, sales_df, on="Order.ID", how="outer")
order_sales_customers = pd.merge(order_sales, customers_df, on="Customer.ID", how="left")
order_sales_customers_products = pd.merge(order_sales_customers, products_df, on="Product.ID", how="left")

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


profits = order_sales_customers.groupby("Country").agg({"Profit" : "sum"}).reset_index()

map_profit_fig = px.choropleth(
    profits,
    locations="Country",  # Column with country names or ISO-3 codes
    locationmode="country names",  # Use country names; alternatively, use "ISO-3"
    color="Profit",  # Values to plot (e.g., profit, sales, etc.)
    title="Profit Distribution by Country",
    color_continuous_scale="Viridis",  # Color scale
    labels={"Profit": "Total Profit"}
)

# Show the map
map_profit_fig.show()

# Profit based on country (others are country with less than 0.5% of the profit from total
total_profit = profits["Profit"].sum()
profits["Percentage"] = (profits["Profit"] / total_profit) * 100
filtered_profits = profits[profits["Percentage"] >= 0.5].copy()
others = profits[profits["Percentage"] < 0.5].sum(numeric_only=True)
others_row = pd.DataFrame([{
    "Country": "Others",
    "Profit": others["Profit"],
    "Percentage": (others["Profit"] / total_profit) * 100
}])
final_data = pd.concat([filtered_profits, others_row], ignore_index=True)

# Create the pie chart
fig2 = px.pie(
    final_data,
    names="Country",
    values="Profit",
    title="Profit Distribution (Countries with ≥ 0.5% Contribution)",
    labels={"Profit": "Total Profit", "Country": "Country"},
    hole=0.4  # Optional: Creates a donut chart
)
fig2.show()







# Sort by the number of customers in each country

grouped = customers_df.groupby(["Country", "City"]).size().reset_index(name="Count")

fig = px.bar(
    grouped,
    x="Country",
    y="Count",
    title="Orders by Country",
    labels={"Count": "Number of Customers", "Country": "Country"}
)
buttons = []
countries = grouped["Country"].unique()
for country in countries:
    filtered_df = grouped[grouped["Country"] == country]
    buttons.append(
        dict(
            label=country,
            method="update",
            args=[
                {"x": [filtered_df["City"]], "y": [filtered_df["Count"]], "type": "bar"},
                {"title": f"Orders in {country}"},
            ],
        )
    )

buttons.insert(
    0,
    dict(
        label="All",
        method="update",
        args=[
            {"x": [grouped["City"]], "y": [grouped["Count"]], "type": "bar"},
            {"title": "Orders by Country and City"},
        ],
    ),
)

fig.update_layout(
    updatemenus=[
        dict(
            active=0,
            buttons=buttons,
            direction="down",
            showactive=True,
        )
    ]
)
fig.show()

# customer # products
# Products: Product.ID there are duplicates