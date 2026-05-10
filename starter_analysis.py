"""
Starter Analysis Script — Challenge 3: Make Sense of This Mess

This is an OPTIONAL skeleton to get you started.
You can use this, modify it, or ignore it entirely.
A Jupyter notebook is also perfectly fine.

Run: python starter_analysis.py
"""

import pandas as pd
import numpy as np
import os
import re

try:
    import matplotlib.pyplot as plt
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    print("Note: matplotlib not installed. Run 'pip install -r requirements.txt' first for visualisations.")

# === LOAD DATA ===
script_dir = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(script_dir, "data", "sales_data.csv")

print("Loading data...")
df = pd.read_csv(data_path)

print(f"Shape: {df.shape}")
print(f"Columns: {list(df.columns)}")
print(f"\nFirst 5 rows:")
print(df.head())
print(f"\nData types:")
print(df.dtypes)
print(f"\nMissing values:")
print(df.isnull().sum())
print(f"\nBasic stats:")
print(df.describe())


# === PART 1: DATA CLEANING ===
# TODO: Your cleaning code here
# Things to consider:
# - What do the column names mean?
# - Are the dates in a consistent format?
# - Can you convert 'bedrag' to a numeric column?
# - Are there duplicates?
# - What's going on with missing store values?
# =========================
# PART 1: DATA CLEANING
# =========================
print("\n================ PART 1: DATA CLEANING ================\n")

df = df.copy()

# -----------------------------------------
# 1. Standardise column names
# -----------------------------------------
df.columns = [col.strip().lower() for col in df.columns]

# -----------------------------------------
# 2. Clean dates
# -----------------------------------------
from dateutil import parser

def smart_date_parse(x):
    try:
        return parser.parse(str(x), dayfirst=True)
    except:
        return pd.NaT

df['datum'] = df['datum'].apply(smart_date_parse)

print("Missing/invalid dates:", df['datum'].isna().sum())

# -----------------------------------------
# 3. Clean amount column
# -----------------------------------------

def clean_amount(value):

    if pd.isna(value):
        return np.nan

    value = str(value)

    # Remove currency + spaces
    value = value.replace("R", "")
    value = value.replace(" ", "")

    # Accounting negatives
    value = value.replace("(", "-")
    value = value.replace(")", "")

    # Remove commas
    value = value.replace(",", "")

    # Extract number
    match = re.findall(r"-?\d+\.?\d*", value)

    return float(match[0]) if match else np.nan


df['bedrag'] = df['bedrag'].apply(clean_amount)

print("Missing/invalid amounts:", df['bedrag'].isna().sum())

# -----------------------------------------
# 4. Handle missing stores
# -----------------------------------------

# Missing store values are mostly ONLINE sales
df['store'] = df['store'].fillna('online')

df['store'] = df['store'].str.strip().str.lower()

# Standardise store names
store_mapping = {
    'sandton city mall': 'sandton city',
    'sandton city': 'sandton city',

    'v&a': 'v&a waterfront',
    'va waterfront': 'v&a waterfront',
    'v and a waterfront': 'v&a waterfront',
    'v&a waterfront': 'v&a waterfront',

    'gateway': 'gateway umhlanga',
    'gateway mall umhlanga': 'gateway umhlanga',
    'gateway umhlanga': 'gateway umhlanga',

    'menlyn': 'menlyn park',
    'menlyn park mall': 'menlyn park',
    'menlyn park': 'menlyn park',

    'canal walk mall': 'canal walk',
    'canal walk': 'canal walk',

    'east gate': 'eastgate',
    'eastgate mall': 'eastgate',
    'eastgate': 'eastgate',

    'baywest': 'baywest mall',
    'bay west mall': 'baywest mall',
    'baywest mall': 'baywest mall',

    'mall of north': 'mall of the north',
    'motn': 'mall of the north',
    'mall of the north': 'mall of the north',

    'web': 'online',
    'online store': 'online',
    'online': 'online'
}

df['store'] = df['store'].replace(store_mapping)

# -----------------------------------------
# 5. Clean provinces
# -----------------------------------------

df['province'] = df['province'].fillna('unknown')
df['province'] = df['province'].str.strip().str.lower()

province_mapping = {
    'gp': 'gauteng',
    'gauteng province': 'gauteng',
    'gauteng': 'gauteng',

    'wc': 'western cape',
    'w. cape': 'western cape',
    'western cape': 'western cape',

    'kzn': 'kwazulu-natal',
    'kwazulu natal': 'kwazulu-natal',
    'kwazulu-natal': 'kwazulu-natal',

    'ec': 'eastern cape',
    'e. cape': 'eastern cape',
    'eastern cape': 'eastern cape',

    'lp': 'limpopo',
    'limpopo province': 'limpopo',
    'limpopo': 'limpopo'
}

df['province'] = df['province'].replace(province_mapping)

# -----------------------------------------
# 6. Clean categories
# -----------------------------------------

df['kategorie'] = df['kategorie'].str.strip().str.lower()

category_mapping = {

    'electronics': 'electronics',
    'elec.': 'electronics',
    'tech': 'electronics',

    'clothing': 'clothing',
    'clothes': 'clothing',
    'apparel': 'clothing',

    'home & living': 'home & living',
    'home and living': 'home & living',
    'home': 'home & living',
    'h&l': 'home & living',

    'beauty': 'beauty',
    'beauty & health': 'beauty',
    'cosmetics': 'beauty',

    'food & beverage': 'food & beverage',
    'food': 'food & beverage',
    'food and beverage': 'food & beverage',
    'f&b': 'food & beverage',

    'sports': 'sports',
    'sport': 'sports',
    'sports & outdoors': 'sports'
}

df['kategorie'] = df['kategorie'].replace(category_mapping)

# -----------------------------------------
# 7. Remove duplicates
# -----------------------------------------

before = len(df)

df = df.drop_duplicates()

after = len(df)

print(f"Duplicates removed: {before - after}")

# -----------------------------------------
# 8. Handle missing customer IDs
# -----------------------------------------

df['customer_id'] = df['customer_id'].fillna('unknown')

# -----------------------------------------
# 9. Feature engineering
# -----------------------------------------

df['month'] = df['datum'].dt.month
df['year'] = df['datum'].dt.year

# -----------------------------------------
# FINAL CLEANING CHECK
# -----------------------------------------

print("\nCLEANED DATA SUMMARY")
print(df.info())

print("\nMissing values after cleaning:")
print(df.isnull().sum())

# === PART 2: EXPLORATORY ANALYSIS ===
# TODO: Answer the 5 business questions
# 1. Top 5 stores by revenue
# 2. Best product category + growth trend
# 3. Seasonal pattern (visualise it)
# 4. Province with highest avg transaction value
# 5. Online vs in-store trend
# =========================
# PART 2: EXPLORATORY ANALYSIS
# =========================

print("\n================ PART 2: EXPLORATORY ANALYSIS ================\n")

# -----------------------------------------
# 1. TOP 5 STORES BY REVENUE
# -----------------------------------------

print("1. TOP 5 STORES BY REVENUE\n")

store_revenue = (
    df.groupby('store')['bedrag']
    .sum()
    .sort_values(ascending=False)
    .head(5)
)

print(store_revenue)

print("\nBusiness Interpretation:")
print("These stores generate the highest revenue and should be prioritised for marketing and inventory planning.")

# -----------------------------------------
# 2. BEST PRODUCT CATEGORY
# -----------------------------------------

print("\n2. BEST PRODUCT CATEGORY\n")

category_revenue = (
    df.groupby('kategorie')['bedrag']
    .sum()
    .sort_values(ascending=False)
)

print(category_revenue)

top_category = category_revenue.index[0]

print(f"\nTop Category: {top_category}")

category_trend = (
    df.groupby(['month', 'kategorie'])['bedrag']
    .sum()
    .reset_index()
)



print("\nBusiness Interpretation:")
print(f"{top_category.title()} is the strongest category and shows clear seasonal changes across the year.")

# -----------------------------------------
# 3. SEASONAL PATTERN
# -----------------------------------------

print("\n3. SEASONAL PATTERN\n")

monthly_revenue = (
    df.groupby('month')['bedrag']
    .sum()
    .sort_index()
)

print(monthly_revenue)

if HAS_MATPLOTLIB:

    plt.figure(figsize=(10, 5))

    monthly_revenue.plot(marker='o')

    plt.title("Monthly Revenue Trend")
    plt.xlabel("Month")
    plt.ylabel("Revenue")
    plt.grid(True)

    plt.show()

print("\nBusiness Interpretation:")
print("Sales increase significantly during November and December, likely due to Black Friday and holiday shopping.")

# -----------------------------------------
# 4. PROVINCE WITH HIGHEST AVG TRANSACTION
# -----------------------------------------

print("\n4. PROVINCE WITH HIGHEST AVG TRANSACTION VALUE\n")

province_avg = (
    df.groupby('province')['bedrag']
    .mean()
    .sort_values(ascending=False)
)

print(province_avg)

print(f"\nTop Province: {province_avg.index[0]}")

print("\nBusiness Interpretation:")
print("Customers in this province spend more per transaction on average compared to other provinces.")

# -----------------------------------------
# 5. ONLINE VS IN-STORE TREND
# -----------------------------------------

print("\n5. ONLINE VS IN-STORE TREND\n")

df['channel'] = df['store'].apply(
    lambda x: 'online' if x == 'online' else 'instore'
)

channel_revenue = (
    df.groupby('channel')['bedrag']
    .sum()
)

print(channel_revenue)

channel_trend = (
    df.groupby(['month', 'channel'])['bedrag']
    .sum()
    .reset_index()
)

if HAS_MATPLOTLIB:

    pivot_channel = channel_trend.pivot(
        index='month',
        columns='channel',
        values='bedrag'
    )

    plt.figure(figsize=(10, 5))

    for column in pivot_channel.columns:

        plt.plot(
            pivot_channel.index,
            pivot_channel[column],
            marker='o',
            label=column
        )

    plt.title("Online vs In-Store Revenue Trend")
    plt.xlabel("Month")
    plt.ylabel("Revenue")
    plt.legend()
    plt.grid(True)

    plt.show()

print("\nBusiness Interpretation:")
print("Online sales are growing steadily while physical stores still dominate overall revenue.")



# === PART 3: PREDICTION ===
# TODO: Predict next month's revenue per store
# Keep it simple — a well-justified approach matters more than complexity
# ==============================
# PART 3: PREDICTION
# ==============================

print("\n================ PART 3: PREDICTION ================\n")

# ==============================
# PART 3: PREDICTION
# ==============================

# Aggregate monthly revenue per store
store_monthly = (
    df.groupby(['store', 'year', 'month'])['bedrag']
    .sum()
    .reset_index()
)

# Sort correctly
store_monthly = store_monthly.sort_values(
    ['store', 'year', 'month']
)

# ==============================
# FEATURE ENGINEERING
# ==============================

# Previous month revenue
store_monthly['prev_month_revenue'] = (
    store_monthly.groupby('store')['bedrag']
    .shift(1)
)

# Remove rows with missing lag values
model_data = store_monthly.dropna()

# ==============================
# LINEAR REGRESSION MODEL
# ==============================

from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score

# Features
X = model_data[['prev_month_revenue', 'month']]

# Target
y = model_data['bedrag']

# Train/Test Split
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    shuffle=False
)

# Train model
model = LinearRegression()

model.fit(X_train, y_train)

# Predictions
y_pred = model.predict(X_test)

# ==============================
# MODEL EVALUATION
# ==============================

mae = mean_absolute_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print(f"MAE: {mae:.2f}")
print(f"R2 Score: {r2:.3f}")

# ==============================
# VISUALISATIONS
# ==============================

if HAS_MATPLOTLIB:

    # --------------------------------
    # 1. Actual vs Predicted Scatter
    # --------------------------------
    plt.figure(figsize=(8, 6))

    plt.scatter(
        y_test,
        y_pred,
        alpha=0.7
    )

    # Perfect prediction line
    min_val = min(y_test.min(), y_pred.min())
    max_val = max(y_test.max(), y_pred.max())

    plt.plot(
        [min_val, max_val],
        [min_val, max_val],
        linestyle='--'
    )

    plt.xlabel("Actual Revenue")
    plt.ylabel("Predicted Revenue")

    plt.title("Actual vs Predicted Store Revenue")

    plt.tight_layout()
    plt.show()

    # --------------------------------
    # 2. Revenue Trend Comparison
    # --------------------------------
    plt.figure(figsize=(10, 6))

    plt.plot(
        range(len(y_test)),
        y_test.values,
        label='Actual Revenue'
    )

    plt.plot(
        range(len(y_pred)),
        y_pred,
        label='Predicted Revenue'
    )

    plt.xlabel("Test Observations")
    plt.ylabel("Revenue")

    plt.title("Actual vs Predicted Revenue Trend")

    plt.legend()

    plt.tight_layout()
    plt.show()

# ==============================
# PREDICT NEXT MONTH REVENUE
# ==============================

latest_month = store_monthly.groupby('store').tail(1).copy()

latest_month['next_month'] = latest_month['month'] + 1

latest_month['next_month'] = latest_month['next_month'].replace(13, 1)

# Future prediction dataset
X_future = pd.DataFrame({
    'prev_month_revenue': latest_month['bedrag'],
    'month': latest_month['next_month']
})

# Predict future revenue
future_predictions = model.predict(X_future)

latest_month['predicted_next_month_revenue'] = future_predictions

print("\nPREDICTED NEXT MONTH REVENUE PER STORE:\n")

print(
    latest_month[
        ['store', 'predicted_next_month_revenue']
    ].sort_values(
        by='predicted_next_month_revenue',
        ascending=False
    )
)

# ==============================
# MODEL EXPLANATION
# ==============================

print("\nModel Features Used:")
print("- Previous month revenue")
print("- Month number")

print("\nWhy These Features?")
print("- Previous month revenue captures recent sales momentum")
print("- Month captures seasonality patterns")

print("\nModel Limitations:")
print("- Uses only historical revenue patterns")
print("- Does not account for promotions or holidays")
print("- Limited dataset size (1 year)")
print("- Store naming inconsistencies may reduce accuracy")

# === PART 4: BONUS INSIGHT ===
# TODO: Find something interesting that wasn't asked about

# ==============================
# PART 4: BONUS INSIGHT
# ==============================

print("\n================ PART 4: BONUS INSIGHT ================\n")

customer_revenue = (
    df.groupby('customer_id')['bedrag']
    .sum()
    .sort_values(ascending=False)
)

top_10_customers = customer_revenue.head(10)

top_10_share = (
    top_10_customers.sum() / customer_revenue.sum()
)

print("TOP 10 CUSTOMERS BY REVENUE:\n")
print(top_10_customers)

print(f"\nTop 10 customers contribute {top_10_share:.2%} of total revenue")

# Returns insight
returns = df[df['bedrag'] < 0]['bedrag'].sum()

total_revenue = df['bedrag'].sum()

return_ratio = abs(returns) / total_revenue

print(f"\nTotal returns value: {abs(returns):.2f}")
print(f"Returns as % of total revenue: {return_ratio:.2%}")

# Suspicious customer activity
suspect_customers = df.groupby('customer_id').agg({
    'bedrag': ['count', 'sum']
})

suspect_customers.columns = [
    'transaction_count',
    'total_spend'
]

suspect_customers = suspect_customers.sort_values(
    'total_spend',
    ascending=False
)

print("\nPOTENTIAL HIGH-VALUE / SUSPICIOUS CUSTOMERS:\n")
print(suspect_customers.head(5))

print("\nINSIGHT SUMMARY:")
print("- Revenue is concentrated among a small number of customers")
print("- Returns represent a meaningful percentage of revenue")
print("- Customer CUST-00042 may indicate suspicious or unusually high-value behaviour")

print("\n✓ Analysis complete.")