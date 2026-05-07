import pandas as pd

# Step 1: Extract
df = pd.read_csv("data/raw/sales_raw.csv")

print("Raw Data Loaded:")
print(df.head())

# Step 2: Transform

# Remove duplicates
df.drop_duplicates(inplace=True)

# Handle missing values
df.fillna({
    "sales": 0,
    "cost": 0,
    "quantity": 1
}, inplace=True)

# Convert date column
df["order_date"] = pd.to_datetime(df["order_date"])

# Create new columns
df["profit"] = df["sales"] - df["cost"]

# Business KPI
df["profit_margin"] = (df["profit"] / df["sales"]) * 100

# Fix negative/invalid data
df = df[df["sales"] > 0]

# Step 3: Load (save clean file)
df.to_csv("data/clean/sales_clean.csv", index=False)

print("Clean Data Saved Successfully!")
print("\nSummary Stats:")
print(df.describe())