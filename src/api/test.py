import pandas as pd
import os
import plotly.graph_objects as go
import plotly.express as px
from mlxtend.frequent_patterns import apriori, association_rules
from mlxtend.preprocessing import TransactionEncoder

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
frequent_buyer_threshold = customer_data["Order_Count"].quantile(0.8)
frequent_buyers = customer_data[customer_data["Order_Count"] >= frequent_buyer_threshold]
at_risk_customers = customer_data[customer_data["Recency"] > 180]
at_risk_threshold = 180
customer_data["Segment"] = "Regular"
customer_data.loc[customer_data["Total_Sales"] >= high_value_threshold, "Segment"] = "High-Value"
customer_data.loc[customer_data["Order_Count"] >= frequent_buyer_threshold, "Segment"] = "Frequent Buyer"
customer_data.loc[customer_data["Recency"] > at_risk_threshold, "Segment"] = "At-Risk"
fig = px.scatter(
    customer_data,
    x="Order_Count",
    y="Total_Sales",
    color="Segment",
    size="Recency",
    hover_name="Customer.ID",
    title="Customer Segments: Total Sales vs. Order Count",
    labels={
        "Order_Count": "Number of Orders",
        "Total_Sales": "Sales Total",
        "Segment": "Customer Segment"
    }
)
fig.update_layout(
    xaxis_title="Number of Orders",
    yaxis_title="Sales Total",
    legend_title="Customer Segment",
    hovermode="closest"
)
fig.show()



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