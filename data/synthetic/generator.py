"""
Synthetic Data Generator
========================
Uses Faker to generate ~9,400 synthetic rows that mirror the real
ecommerce_churn.xlsx schema, then combines them with the original
dataset to produce ~15,000 rows.

Output: data/synthetic/synthetic_data.csv
        data/synthetic/combined_data.csv
"""

import os
import random
import pandas as pd
from faker import Faker

# ── Paths ────────────────────────────────────────────────────────────────────
RAW_PATH       = "data/raw/ecommerce_churn.xlsx"
SYNTH_PATH     = "data/synthetic/synthetic_data.csv"
COMBINED_PATH  = "data/synthetic/combined_data.csv"

TARGET_TOTAL   = 15_000   # desired final row count
RANDOM_SEED    = 42

fake = Faker()
random.seed(RANDOM_SEED)
Faker.seed(RANDOM_SEED)


# ── Helpers ──────────────────────────────────────────────────────────────────
CITIES            = ["Tier1", "Tier2", "Tier3"]
PREFERRED_LOGIN   = ["Mobile", "Computer"]
PAYMENT_MODES     = ["Debit Card", "Credit Card", "UPI", "Cash on Delivery",
                     "E wallet", "COD"]
GENDER_OPTS       = ["Male", "Female"]
MARITAL_OPTS      = ["Single", "Married", "Divorced"]
COMPLAINT_OPTS    = [0, 1]
PREFERRED_CAT     = ["Fashion", "Electronics", "Grocery", "Mobile",
                     "Laptop & Accessory", "Others"]


def generate_row():
    tenure          = random.randint(0, 61)
    order_count     = random.randint(1, 16)
    cashback        = round(random.uniform(0, 325), 2)
    satisfaction    = random.randint(1, 5)
    day_since_order = random.randint(0, 46)
    complain        = random.choice(COMPLAINT_OPTS)
    coupon_used     = random.randint(0, 16)
    days_since_reg  = random.randint(0, 3700)
    num_devices     = random.randint(1, 6)
    num_address     = random.randint(1, 22)
    hour_on_app     = round(random.uniform(0, 5), 1)
    warehouse_to_home = random.randint(5, 127)
    order_amount_hike = round(random.uniform(11, 26), 0)

    # Churn probability influenced by real-world signals
    churn_prob = 0.15
    if complain == 1:
        churn_prob += 0.2
    if satisfaction <= 2:
        churn_prob += 0.15
    if tenure < 6:
        churn_prob += 0.1
    if coupon_used > 10:
        churn_prob += 0.05
    churn = 1 if random.random() < churn_prob else 0

    return {
        "CustomerID":                  random.randint(50001, 99999),
        "Churn":                       churn,
        "Tenure":                      tenure,
        "PreferredLoginDevice":        random.choice(PREFERRED_LOGIN),
        "CityTier":                    random.choice(CITIES),
        "WarehouseToHome":             warehouse_to_home,
        "PreferredPaymentMode":        random.choice(PAYMENT_MODES),
        "Gender":                      random.choice(GENDER_OPTS),
        "HourSpendOnApp":              hour_on_app,
        "NumberOfDeviceRegistered":    num_devices,
        "PreferedOrderCat":            random.choice(PREFERRED_CAT),
        "SatisfactionScore":           satisfaction,
        "MaritalStatus":               random.choice(MARITAL_OPTS),
        "NumberOfAddress":             num_address,
        "Complain":                    complain,
        "OrderAmountHikeFromlastYear": order_amount_hike,
        "CouponUsed":                  coupon_used,
        "OrderCount":                  order_count,
        "DaySinceLastOrder":           day_since_order,
        "CashbackAmount":              cashback,
    }


# ── Main ─────────────────────────────────────────────────────────────────────
def generate_synthetic_data():
    os.makedirs("data/synthetic", exist_ok=True)

    # Load original to find actual row count
    print("Loading original dataset...")
    df_original = pd.read_excel(RAW_PATH, sheet_name="E Comm")
    original_rows = len(df_original)
    print(f"  Original rows : {original_rows}")

    rows_needed = max(0, TARGET_TOTAL - original_rows)
    print(f"  Rows to generate: {rows_needed}")

    # Generate synthetic rows
    print("Generating synthetic rows...")
    synthetic_records = [generate_row() for _ in range(rows_needed)]
    df_synthetic = pd.DataFrame(synthetic_records)

    # Align columns with original dataset
    df_synthetic = df_synthetic[df_original.columns]

    # Save synthetic-only file
    df_synthetic.to_csv(SYNTH_PATH, index=False)
    print(f"  Synthetic data saved → {SYNTH_PATH}")

    # Merge and save combined dataset
    df_combined = pd.concat([df_original, df_synthetic], ignore_index=True)
    df_combined.to_csv(COMBINED_PATH, index=False)
    print(f"  Combined data saved → {COMBINED_PATH}")
    print(f"  Total rows: {len(df_combined)}")

    return df_combined


if __name__ == "__main__":
    generate_synthetic_data()
