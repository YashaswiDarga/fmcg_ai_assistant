import os
import sqlite3
import pandas as pd

# Ensure the database directory exists
os.makedirs("database", exist_ok=True)

db_path = "database/fmcg.db"
conn = sqlite3.connect(db_path)

print("Loading products...")
pd.read_csv("data/products.csv").to_sql(
    "product_master",
    conn,
    if_exists="replace",
    index=False
)

print("Loading stores...")
pd.read_csv("data/stores.csv").to_sql(
    "store_master",
    conn,
    if_exists="replace",
    index=False
)

print("Loading sales & promotions...")
pd.read_csv("data/sales_promotions.csv").to_sql(
    "sales_promotions",
    conn,
    if_exists="replace",
    index=False
)

print("Loading inventory...")
pd.read_csv("data/inventory.csv").to_sql(
    "inventory",
    conn,
    if_exists="replace",
    index=False
)

conn.close()

print("Database created successfully at:", db_path)
