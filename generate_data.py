import os
import random
import datetime
import pandas as pd
from faker import Faker

# Set seed for reproducibility
random.seed(42)
fake = Faker()

# Create data directory if it doesn't exist
os.makedirs("data", exist_ok=True)

# 1. Generate 20 Products
categories = ["Carbonated", "Juice", "Water", "Energy", "Dairy"]
product_details = [
    # Carbonated
    {"product_name": "Cola Classic", "brand": "FizzCo", "category": "Carbonated", "sub_category": "Cola", "pack_size_ml": 500, "unit_price": 1.99},
    {"product_name": "Diet Cola", "brand": "FizzCo", "category": "Carbonated", "sub_category": "Diet Cola", "pack_size_ml": 500, "unit_price": 1.99},
    {"product_name": "Lemon Lime Fizz", "brand": "FizzCo", "category": "Carbonated", "sub_category": "Lemon Lime", "pack_size_ml": 330, "unit_price": 1.49},
    {"product_name": "Ginger Beer Elite", "brand": "FizzCo", "category": "Carbonated", "sub_category": "Ginger", "pack_size_ml": 330, "unit_price": 2.49},
    # Juice
    {"product_name": "Premium Orange Juice", "brand": "Juicy", "category": "Juice", "sub_category": "Orange", "pack_size_ml": 1000, "unit_price": 4.49},
    {"product_name": "Apple Orchard Delight", "brand": "Juicy", "category": "Juice", "sub_category": "Apple", "pack_size_ml": 1000, "unit_price": 3.99},
    {"product_name": "Mango Passion Nectar", "brand": "Juicy", "category": "Juice", "sub_category": "Mango", "pack_size_ml": 500, "unit_price": 2.99},
    {"product_name": "Ruby Cranberry Splash", "brand": "Juicy", "category": "Juice", "sub_category": "Cranberry", "pack_size_ml": 1000, "unit_price": 4.99},
    # Water
    {"product_name": "Pure Spring Water", "brand": "AquaFit", "category": "Water", "sub_category": "Still", "pack_size_ml": 500, "unit_price": 0.99},
    {"product_name": "Sparkling Mineral Water", "brand": "AquaFit", "category": "Water", "sub_category": "Sparkling", "pack_size_ml": 750, "unit_price": 1.79},
    {"product_name": "Electrolyte Active Water", "brand": "AquaFit", "category": "Water", "sub_category": "Enhanced", "pack_size_ml": 1000, "unit_price": 2.29},
    {"product_name": "Peach Infused Water", "brand": "AquaFit", "category": "Water", "sub_category": "Flavored", "pack_size_ml": 500, "unit_price": 1.29},
    # Energy
    {"product_name": "Energy Rush Original", "brand": "Charge", "category": "Energy", "sub_category": "Original", "pack_size_ml": 250, "unit_price": 2.99},
    {"product_name": "Zero Sugar Charge", "brand": "Charge", "category": "Energy", "sub_category": "Sugarfree", "pack_size_ml": 250, "unit_price": 2.99},
    {"product_name": "Blue Raspberry Boost", "brand": "Charge", "category": "Energy", "sub_category": "Berry", "pack_size_ml": 355, "unit_price": 3.49},
    {"product_name": "Coffee Monster Energy", "brand": "Charge", "category": "Energy", "sub_category": "Coffee", "pack_size_ml": 330, "unit_price": 3.79},
    # Dairy
    {"product_name": "Organic Whole Milk", "brand": "DairyDelight", "category": "Dairy", "sub_category": "Milk", "pack_size_ml": 1000, "unit_price": 2.49},
    {"product_name": "Double Chocolate Shake", "brand": "DairyDelight", "category": "Dairy", "sub_category": "Flavored Milk", "pack_size_ml": 500, "unit_price": 2.19},
    {"product_name": "Strawberry Yogurt Drink", "brand": "DairyDelight", "category": "Dairy", "sub_category": "Yogurt Drink", "pack_size_ml": 250, "unit_price": 1.89},
    {"product_name": "Probiotic Kefir Classic", "brand": "DairyDelight", "category": "Dairy", "sub_category": "Kefir", "pack_size_ml": 500, "unit_price": 3.29}
]

products = []
for idx, prod in enumerate(product_details):
    prod["product_id"] = f"PROD{idx+1:03d}"
    products.append(prod)

df_products = pd.DataFrame(products)
df_products.to_csv("data/products.csv", index=False)
print(f"Generated {len(df_products)} products in data/products.csv")

# 2. Generate 40 Stores
regions = ["North", "South", "East", "West"]
cities_by_region = {
    "North": ["New York", "Chicago", "Boston", "Detroit", "Minneapolis"],
    "South": ["Houston", "Miami", "Atlanta", "Dallas", "Nashville"],
    "East": ["Philadelphia", "Washington", "Atlanta", "Charlotte", "Baltimore"],
    "West": ["Los Angeles", "San Francisco", "Seattle", "Denver", "Phoenix"]
}
formats = ["Supermarket", "Hypermarket", "Convenience", "Wholesale"]

stores = []
for i in range(1, 41):
    store_id = f"STORE{i:03d}"
    region = random.choice(regions)
    city = random.choice(cities_by_region[region])
    store_format = random.choice(formats)
    store_name = f"{fake.company()} {store_format}"
    stores.append({
        "store_id": store_id,
        "store_name": store_name,
        "region": region,
        "city": city,
        "store_format": store_format
    })

df_stores = pd.DataFrame(stores)
df_stores.to_csv("data/stores.csv", index=False)
print(f"Generated {len(df_stores)} stores in data/stores.csv")

# 3. Generate 24 weeks of data
start_date = datetime.date(2026, 1, 5) # Monday
weeks = [start_date + datetime.timedelta(weeks=w) for w in range(24)]

sales_data = []
inventory_data = []

# Define format multipliers for sales volume
format_multipliers = {
    "Wholesale": 3.5,
    "Hypermarket": 2.0,
    "Supermarket": 1.2,
    "Convenience": 0.5
}

# Pre-calculate base demand parameters per store-product pair
base_demands = {}
for store in stores:
    s_id = store["store_id"]
    s_format = store["store_format"]
    for prod in products:
        p_id = prod["product_id"]
        p_price = prod["unit_price"]
        # Demand is inversely proportional to price, scaled by store format
        base_qty = (120 / p_price) * format_multipliers[s_format]
        base_qty = max(5, int(base_qty * random.uniform(0.8, 1.2)))
        base_demands[(s_id, p_id)] = base_qty

# Initialize inventory trackers: {(store_id, product_id): current_stock}
current_stocks = {}
for store in stores:
    s_id = store["store_id"]
    for prod in products:
        p_id = prod["product_id"]
        # Start with a healthy opening stock
        current_stocks[(s_id, p_id)] = int(base_demands[(s_id, p_id)] * random.uniform(3, 5))

# Generate weekly transactions chronologically
for week in weeks:
    week_str = week.strftime("%Y-%m-%d")
    for store in stores:
        s_id = store["store_id"]
        s_region = store["region"]
        for prod in products:
            p_id = prod["product_id"]
            p_price = prod["unit_price"]
            
            base_qty = base_demands[(s_id, p_id)]
            
            # 12% probability of promotion
            promo_flag = 0
            promo_type = "None"
            discount_pct = 0.0
            promo_multiplier = 1.0
            
            if random.random() < 0.12:
                promo_flag = 1
                promo_type = random.choice(["BOGO", "Discount", "Display Space"])
                if promo_type == "BOGO":
                    discount_pct = 50.0
                    promo_multiplier = random.uniform(1.6, 2.0)
                elif promo_type == "Discount":
                    discount_pct = random.choice([10.0, 15.0, 20.0, 25.0])
                    promo_multiplier = random.uniform(1.3, 1.7)
                elif promo_type == "Display Space":
                    discount_pct = 0.0
                    # Just eye-level shelf placement increases sales
                    promo_multiplier = random.uniform(1.2, 1.4)
            
            # Expected demand
            demand = int(base_qty * promo_multiplier * random.uniform(0.9, 1.1))
            demand = max(1, demand)
            
            # Inventory management: replenishment logic
            opening_stock = current_stocks[(s_id, p_id)]
            reorder_point = int(base_qty * 1.5)
            
            if opening_stock < reorder_point:
                # Order enough to restock up to 4 weeks of base demand plus buffer
                units_received = int(base_qty * random.uniform(3, 4))
            else:
                units_received = 0
                
            available_stock = opening_stock + units_received
            
            # Stockout check
            stockout_flag = 0
            if demand > available_stock:
                stockout_flag = 1
                # Stockout curtails the actual units sold (simulating lost customers or partial stock duration)
                units_sold = int(demand * 0.5)
                # But cannot exceed what we actually have in stock
                units_sold = min(units_sold, available_stock)
            else:
                units_sold = demand
                
            closing_stock = available_stock - units_sold
            current_stocks[(s_id, p_id)] = closing_stock
            
            # Calculate financials
            revenue = round(units_sold * p_price * (1.0 - discount_pct / 100.0), 2)
            
            # Record inventory transaction
            inventory_data.append({
                "week_start_date": week_str,
                "product_id": p_id,
                "store_id": s_id,
                "opening_stock": opening_stock,
                "units_received": units_received,
                "units_sold": units_sold,
                "closing_stock": closing_stock,
                "stockout_flag": stockout_flag
            })
            
            # Record sales & promotions transaction
            sales_data.append({
                "week_start_date": week_str,
                "product_id": p_id,
                "store_id": s_id,
                "region": s_region,
                "units_sold": units_sold,
                "revenue": revenue,
                "promotion_flag": promo_flag,
                "promotion_type": promo_type,
                "discount_pct": discount_pct
            })

df_sales = pd.DataFrame(sales_data)
df_sales.to_csv("data/sales_promotions.csv", index=False)
print(f"Generated {len(df_sales)} sales rows in data/sales_promotions.csv")

df_inventory = pd.DataFrame(inventory_data)
df_inventory.to_csv("data/inventory.csv", index=False)
print(f"Generated {len(df_inventory)} inventory rows in data/inventory.csv")

print("All synthetic datasets generated successfully!")
