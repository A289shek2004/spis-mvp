import pandas as pd
import numpy as np
import datetime
import random

# --- Config ---
NUM_PRODUCTS = 20
BATCHES_PER_PRODUCT = (3, 5)  # range (min, max)
SALES_PER_BATCH = (5, 10)

today = datetime.date.today()

# --- Products ---
products = [
    {
        "product_id": i,
        "name": f"Product{i}",
        "generic_name": f"Generic{i}",
        "unit": random.choice(["strip", "bottle", "tablet"]),
        "category": random.choice(["Painkiller", "Antibiotic", "Vitamin", "Cough Syrup"]),
    }
    for i in range(1, NUM_PRODUCTS + 1)
]
pd.DataFrame(products).to_csv("products.csv", index=False)

# --- Suppliers ---
suppliers = [
    {"id": i, "name": f"Supplier{i}", "lead_time_days": random.randint(2, 10)}
    for i in range(1, 6)
]
pd.DataFrame(suppliers).to_csv("suppliers.csv", index=False)

# --- Batches ---
batches = []
for p in products:
    for _ in range(random.randint(*BATCHES_PER_PRODUCT)):
        batches.append({
            "batch_id": len(batches) + 1,
            "product_id": p["product_id"],
            "batch_no": f"B{random.randint(1000,9999)}",
            "expiry_date": today + datetime.timedelta(days=random.randint(30, 365)),
            "qty": random.randint(20, 100),
            "purchase_price": round(random.uniform(5, 50), 2),
            "supplier_id": random.randint(1, len(suppliers))
        })
pd.DataFrame(batches).to_csv("batches.csv", index=False)

# --- Sales ---
sales = []
for b in batches:
    for _ in range(random.randint(*SALES_PER_BATCH)):
        sales.append({
            "sale_id": len(sales) + 1,
            "batch_id": b["batch_id"],
            "date": today - datetime.timedelta(days=random.randint(1, 90)),
            "qty_sold": random.randint(1, 10),
            "price": round(b["purchase_price"] * random.uniform(1.2, 1.8), 2),
            "pharmacist_id": random.randint(1, 3)
        })
pd.DataFrame(sales).to_csv("sales.csv", index=False)

print("✅ Sample data generated: products.csv, suppliers.csv, batches.csv, sales.csv")
