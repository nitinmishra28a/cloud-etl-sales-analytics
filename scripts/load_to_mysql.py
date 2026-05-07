import pandas as pd
from sqlalchemy import create_engine

# MySQL connection details
username = "root"
password = "nitin1234"   # <-- your password
host = "localhost"
database = "sales_etl"

# Create connection
engine = create_engine(f"mysql+pymysql://{username}:{password}@{host}/{database}")

# Load cleaned data
df = pd.read_csv("data/clean/sales_clean.csv")

# Upload to MySQL
df.to_sql("sales_data", con=engine, if_exists="append", index=False)

print("Data loaded successfully into MySQL!")