"""
Dataset Generator for Challenge 3: Make Sense of This Mess
Generates messy South African retail sales data.

DO NOT MODIFY THIS FILE — it's part of the challenge setup.
You may READ it to understand the data structure (but the challenge
is to figure it out from the data itself).
"""

import random
import os
import csv
from datetime import datetime, timedelta

random.seed(2024)

# === STORE CONFIGURATION ===
STORES = {
    "Sandton City": {"province": "Gauteng", "opened": "2023-01-01", "size": "large"},
    "V&A Waterfront": {"province": "Western Cape", "opened": "2023-01-01", "size": "large"},
    "Gateway Umhlanga": {"province": "KwaZulu-Natal", "opened": "2023-01-01", "size": "large"},
    "Menlyn Park": {"province": "Gauteng", "opened": "2023-01-01", "size": "medium"},
    "Canal Walk": {"province": "Western Cape", "opened": "2023-01-01", "size": "medium"},
    "Eastgate": {"province": "Gauteng", "opened": "2023-01-01", "size": "medium"},
    "Baywest Mall": {"province": "Eastern Cape", "opened": "2023-01-01", "size": "small"},
    "Mall of the North": {"province": "Limpopo", "opened": "2024-06-01", "size": "small"},  # NEW STORE
}

ONLINE_CHANNEL = "Online"

PRODUCT_CATEGORIES = ["Electronics", "Clothing", "Home & Living", "Beauty", "Food & Beverage", "Sports"]

PAYMENT_METHODS = ["Card", "Cash", "EFT", "Mobile Money"]

# Province name variations (intentional messiness)
PROVINCE_VARIATIONS = {
    "Gauteng": ["Gauteng", "GP", "gauteng", "Gauteng Province", "GAUTENG"],
    "Western Cape": ["Western Cape", "WC", "W. Cape", "western cape", "Western cape"],
    "KwaZulu-Natal": ["KwaZulu-Natal", "KZN", "Kwazulu-Natal", "kwazulu natal", "KwaZulu Natal"],
    "Eastern Cape": ["Eastern Cape", "EC", "E. Cape", "eastern cape"],
    "Limpopo": ["Limpopo", "LP", "limpopo", "Limpopo Province"],
}

# Store name variations (intentional messiness)
STORE_NAME_VARIATIONS = {
    "Sandton City": ["Sandton City", "sandton city", "Sandton city", "SANDTON CITY", "Sandton City Mall"],
    "V&A Waterfront": ["V&A Waterfront", "V&A waterfront", "VA Waterfront", "V and A Waterfront", "V&A"],
    "Gateway Umhlanga": ["Gateway Umhlanga", "Gateway", "gateway umhlanga", "Gateway Mall Umhlanga"],
    "Menlyn Park": ["Menlyn Park", "Menlyn", "menlyn park", "Menlyn Park Mall"],
    "Canal Walk": ["Canal Walk", "Canal walk", "canal walk", "Canal Walk Mall"],
    "Eastgate": ["Eastgate", "eastgate", "Eastgate Mall", "East Gate"],
    "Baywest Mall": ["Baywest Mall", "Baywest", "baywest mall", "Bay West Mall"],
    "Mall of the North": ["Mall of the North", "Mall of North", "mall of the north", "MOTN"],
}

# Category variations (intentional messiness)
CATEGORY_VARIATIONS = {
    "Electronics": ["Electronics", "electronics", "Elec.", "ELECTRONICS", "Tech"],
    "Clothing": ["Clothing", "clothing", "Clothes", "CLOTHING", "Apparel"],
    "Home & Living": ["Home & Living", "Home and Living", "home & living", "Home", "H&L"],
    "Beauty": ["Beauty", "beauty", "BEAUTY", "Beauty & Health", "Cosmetics"],
    "Food & Beverage": ["Food & Beverage", "Food", "food & beverage", "F&B", "Food and Beverage"],
    "Sports": ["Sports", "sports", "SPORTS", "Sports & Outdoors", "Sport"],
}

# Date format variations
DATE_FORMATS = [
    "%Y-%m-%d",          # 2024-03-15
    "%d/%m/%Y",          # 15/03/2024
    "%d %b %Y",          # 15 Mar 2024
    "%m-%d-%Y",          # 03-15-2024 (American format mixed in)
]

# === SEASONAL PATTERNS ===
# Monthly multipliers (December = holiday spike, Jan/March = load shedding dips for in-store)
MONTHLY_MULTIPLIERS = {
    1: 0.75,   # January - post-holiday slump + load shedding
    2: 0.85,   # February - recovery
    3: 0.80,   # March - load shedding
    4: 0.90,   # April - Easter boost
    5: 0.85,   # May
    6: 0.90,   # June - mid-year sales
    7: 0.95,   # July - winter
    8: 0.90,   # August
    9: 0.95,   # September - spring
    10: 1.00,  # October
    11: 1.15,  # November - Black Friday
    12: 1.40,  # December - holiday season
}

# Online gets BOOST during load shedding months (people shop from home)
ONLINE_LOAD_SHEDDING_BOOST = {1: 1.3, 3: 1.25}


def random_date_in_month(year: int, month: int) -> datetime:
    """Generate a random datetime within a given month."""
    if month == 12:
        max_day = 31
    elif month in (4, 6, 9, 11):
        max_day = 30
    elif month == 2:
        max_day = 29 if year % 4 == 0 else 28
    else:
        max_day = 31

    day = random.randint(1, max_day)
    hour = random.randint(8, 20)
    minute = random.randint(0, 59)
    return datetime(year, month, day, hour, minute)


def format_date_messy(dt: datetime) -> str:
    """Format a date using a randomly chosen format."""
    fmt = random.choice(DATE_FORMATS)
    return dt.strftime(fmt)


def format_amount_messy(amount: float) -> str:
    """Format a currency amount inconsistently."""
    style = random.random()
    if style < 0.3:
        return f"R{amount:.2f}"                    # R1500.00
    elif style < 0.5:
        return f"R {amount:,.2f}"                  # R 1,500.00
    elif style < 0.7:
        return f"{amount:.2f}"                     # 1500.00 (no currency symbol)
    elif style < 0.85:
        return f"R{int(amount)}"                   # R1500 (no decimals)
    else:
        # Afrikaans style with space as thousands separator
        int_part = int(amount)
        if int_part >= 1000:
            return f"R {int_part // 1000} {int_part % 1000:03d}.{int(amount * 100) % 100:02d}"
        return f"R{amount:.2f}"


def generate_base_amount(category: str) -> float:
    """Generate a realistic transaction amount based on category."""
    ranges = {
        "Electronics": (500, 15000),
        "Clothing": (150, 3500),
        "Home & Living": (200, 8000),
        "Beauty": (80, 2000),
        "Food & Beverage": (50, 800),
        "Sports": (200, 5000),
    }
    low, high = ranges[category]
    return round(random.uniform(low, high), 2)


def generate_transaction(month: int, year: int = 2024, is_online: bool = False) -> dict:
    """Generate a single transaction record."""

    # Pick store
    if is_online:
        store_name = ONLINE_CHANNEL
        province = random.choice(list(PROVINCE_VARIATIONS.keys()))
    else:
        store_name = random.choice(list(STORES.keys()))
        store_info = STORES[store_name]

        # Skip if store hasn't opened yet
        opened = datetime.strptime(store_info["opened"], "%Y-%m-%d")
        if datetime(year, month, 1) < opened:
            return None

        province = store_info["province"]

    # Pick category
    category = random.choice(PRODUCT_CATEGORIES)

    # Generate amount with seasonal adjustment
    base_amount = generate_base_amount(category)
    seasonal_mult = MONTHLY_MULTIPLIERS[month]

    # Online boost during load shedding
    if is_online and month in ONLINE_LOAD_SHEDDING_BOOST:
        seasonal_mult *= ONLINE_LOAD_SHEDDING_BOOST[month]

    amount = base_amount * seasonal_mult

    # Generate date
    dt = random_date_in_month(year, month)

    # Generate customer ID (some repeat customers)
    if random.random() < 0.3:
        # Repeat customer
        customer_id = f"CUST-{random.randint(1, 200):05d}"
    else:
        customer_id = f"CUST-{random.randint(1, 2000):05d}"

    # Payment method
    if is_online:
        payment = random.choice(["Card", "EFT", "Mobile Money"])
    else:
        payment = random.choice(PAYMENT_METHODS)

    # Quantity
    quantity = random.choices([1, 2, 3, 4, 5], weights=[50, 25, 15, 7, 3])[0]

    # === APPLY MESSINESS ===

    # Messy date
    date_str = format_date_messy(dt)

    # Messy amount
    amount_str = format_amount_messy(amount)

    # Messy store name (use variation)
    if is_online:
        messy_store = random.choice(["Online", "online", "ONLINE", "Online Store", "Web"])
    else:
        messy_store = random.choice(STORE_NAME_VARIATIONS[store_name])

    # Messy province
    messy_province = random.choice(PROVINCE_VARIATIONS[province])

    # Messy category
    messy_category = random.choice(CATEGORY_VARIATIONS[category])

    # Sometimes missing values
    if is_online and random.random() < 0.7:
        messy_store = ""  # Online orders often have no store (SYSTEMATIC MISSINGNESS)

    if random.random() < 0.05:
        messy_province = ""  # Random missing province

    if random.random() < 0.03:
        customer_id = ""  # Random missing customer ID

    record = {
        "transaction_id": None,  # Set later
        "datum": date_str,  # "datum" is Afrikaans for "date" — intentional column name
        "store": messy_store,
        "province": messy_province,
        "kategorie": messy_category,  # "kategorie" is Afrikaans for "category"
        "bedrag": amount_str,  # "bedrag" is Afrikaans for "amount"
        "quantity": quantity,
        "customer_id": customer_id,
        "payment_method": payment,
    }

    return record


def generate_returns(transactions: list) -> list:
    """Generate return transactions (negative amounts, not labelled as returns)."""
    returns = []
    for txn in random.sample(transactions, k=int(len(transactions) * 0.08)):
        # Create a return — same details but negative amount, slightly later date
        return_txn = txn.copy()
        return_txn["transaction_id"] = None

        # Make amount negative (but keep the messy formatting)
        original_amount = txn["_clean_amount"]
        return_amount = -abs(original_amount)

        # Format the negative amount messily
        style = random.random()
        if style < 0.4:
            return_txn["bedrag"] = f"-R{abs(return_amount):.2f}"
        elif style < 0.7:
            return_txn["bedrag"] = f"(R{abs(return_amount):.2f})"  # Accounting style
        else:
            return_txn["bedrag"] = f"R-{abs(return_amount):.2f}"

        returns.append(return_txn)

    return returns


def generate_duplicates(transactions: list) -> list:
    """Generate near-duplicate transactions (same data, slightly different timestamp)."""
    duplicates = []
    for txn in random.sample(transactions, k=int(len(transactions) * 0.04)):
        dup = txn.copy()
        dup["transaction_id"] = None
        # Slightly modify the timestamp (within 1-2 minutes)
        # Since dates are already formatted as strings, just keep the same date
        # The duplicate will have the same date string — making it a true duplicate
        duplicates.append(dup)

    return duplicates


def generate_fraud_cluster(month: int = 7) -> list:
    """Generate a suspicious cluster of high-value transactions from one 'customer'."""
    fraud_customer = "CUST-00042"
    fraud_records = []

    # 8 high-value electronics purchases across different stores on the same day
    dt = datetime(2024, month, 15, 10, 0)
    stores_used = random.sample(list(STORES.keys()), 5)

    for i, store in enumerate(stores_used):
        record = {
            "transaction_id": None,
            "datum": format_date_messy(dt + timedelta(hours=i)),
            "store": random.choice(STORE_NAME_VARIATIONS[store]),
            "province": random.choice(PROVINCE_VARIATIONS[STORES[store]["province"]]),
            "kategorie": random.choice(CATEGORY_VARIATIONS["Electronics"]),
            "bedrag": format_amount_messy(random.uniform(10000, 14999)),
            "quantity": random.randint(2, 5),
            "customer_id": fraud_customer,
            "payment_method": "Card",
            "_clean_amount": random.uniform(10000, 14999),
        }
        fraud_records.append(record)

    return fraud_records


def generate_dataset(n_target: int = 5000) -> list:
    """Generate the full messy dataset."""
    transactions = []

    # Generate transactions month by month
    for month in range(1, 13):
        # Number of transactions per month (varies seasonally)
        base_count = n_target // 12
        month_count = int(base_count * MONTHLY_MULTIPLIERS[month])

        # Split between online and in-store
        online_ratio = 0.15 + (month - 1) * 0.01  # Online growing throughout year
        online_count = int(month_count * online_ratio)
        instore_count = month_count - online_count

        # Generate in-store transactions
        for _ in range(instore_count):
            txn = generate_transaction(month, is_online=False)
            if txn:
                # Store clean amount for returns generation
                txn["_clean_amount"] = generate_base_amount(
                    random.choice(PRODUCT_CATEGORIES)
                ) * MONTHLY_MULTIPLIERS[month]
                transactions.append(txn)

        # Generate online transactions
        for _ in range(online_count):
            txn = generate_transaction(month, is_online=True)
            if txn:
                txn["_clean_amount"] = generate_base_amount(
                    random.choice(PRODUCT_CATEGORIES)
                ) * MONTHLY_MULTIPLIERS[month]
                transactions.append(txn)

    # Add returns (negative amounts, ~8% of transactions)
    returns = generate_returns(transactions)
    transactions.extend(returns)

    # Add near-duplicates (~4% of transactions)
    duplicates = generate_duplicates(transactions)
    transactions.extend(duplicates)

    # Add fraud cluster
    fraud = generate_fraud_cluster()
    transactions.extend(fraud)

    # Shuffle everything
    random.shuffle(transactions)

    # Assign transaction IDs
    for i, txn in enumerate(transactions):
        txn["transaction_id"] = f"TXN-{i+1:06d}"

    # Remove the internal _clean_amount field
    for txn in transactions:
        txn.pop("_clean_amount", None)

    return transactions


def main():
    # Create data directory relative to this script's location
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, "data")
    os.makedirs(data_dir, exist_ok=True)

    records = generate_dataset(5000)

    # Write to CSV
    output_path = os.path.join(data_dir, "sales_data.csv")
    fieldnames = [
        "transaction_id", "datum", "store", "province",
        "kategorie", "bedrag", "quantity", "customer_id", "payment_method"
    ]

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for record in records:
            # Only write the specified fields
            row = {k: record.get(k, "") for k in fieldnames}
            writer.writerow(row)

    print(f"✓ Generated {len(records)} transactions → {output_path}")
    print(f"\n  Dataset characteristics:")
    print(f"  - 12 months of data (Jan-Dec 2024)")
    print(f"  - 8 physical stores + online channel")
    print(f"  - 6 product categories")
    print(f"  - ~8% returns (negative amounts)")
    print(f"  - ~4% near-duplicate records")
    print(f"  - Intentionally messy formatting throughout")
    print(f"\n  Columns: {fieldnames}")
    print(f"  Note: Some column names are in Afrikaans (datum=date, kategorie=category, bedrag=amount)")


if __name__ == "__main__":
    main()
