import pandas as pd
import random
from faker import Faker
from datetime import datetime, timedelta

fake = Faker()

products = ["Laptop", "Phone", "Mouse", "Keyboard", "Monitor", "Printer"]
categories = {
    "Laptop": "Electronics",
    "Phone": "Electronics",
    "Mouse": "Accessories",
    "Keyboard": "Accessories",
    "Monitor": "Electronics",
    "Printer": "Office"
}

regions = ["North", "South", "East", "West"]

rows = []

for i in range(1, 1001):
    product = random.choice(products)
    qty = random.randint(1, 5)
    sales = random.randint(500, 50000)
    cost = round(sales * random.uniform(0.5, 0.9), 2)

    rows.append({
        "order_id": i,
        "customer_id": random.randint(1000, 5000),
        "product": product,
        "category": categories[product],
        "region": random.choice(regions),
        "quantity": qty,
        "sales": sales,
        "cost": cost,
        "order_date": fake.date_between(start_date='-365d', end_date='today')
    })

df = pd.DataFrame(rows)
df.to_csv("data/raw/sales_raw.csv", index=False)

print("sales_raw.csv created successfully!")