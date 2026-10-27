"""
Generate synthetic retail sales data and seed the SQLite database.
Creates a dataset modeled after the Superstore schema with ~10,000 rows.
"""

import sqlite3
import random
import string
from datetime import datetime, timedelta
import pathlib

import numpy as np

PROJECT_ROOT = pathlib.Path(__file__).parent.parent.resolve()
DATA_DIR = PROJECT_ROOT / "data"
DB_PATH = DATA_DIR / "sales_intelligence.db"

random.seed(42)
np.random.seed(42)

# ── Configuration ───────────────────────────────────────────────────────────────

NUM_CUSTOMERS = 800
NUM_PRODUCTS = 1800
NUM_ORDERS = 5000
MAX_LINE_ITEMS_PER_ORDER = 5
START_DATE = datetime(2020, 1, 1)
END_DATE = datetime(2024, 12, 31)

REGIONS = ["East", "West", "Central", "South"]
SEGMENTS = ["Consumer", "Corporate", "Home Office"]
SHIP_MODES = ["Standard Class", "Second Class", "First Class", "Same Day"]
CATEGORIES = {
    "Furniture": ["Bookcases", "Chairs", "Furnishings", "Tables"],
    "Office Supplies": [
        "Appliances", "Art", "Binders", "Envelopes", "Fasteners",
        "Labels", "Paper", "Storage", "Supplies",
    ],
    "Technology": ["Accessories", "Copiers", "Machines", "Phones"],
}

STATES_BY_REGION = {
    "East": ["New York", "New Jersey", "Pennsylvania", "Massachusetts", "Connecticut", "Maryland"],
    "West": ["California", "Washington", "Oregon", "Nevada", "Arizona", "Colorado"],
    "Central": ["Illinois", "Texas", "Ohio", "Michigan", "Indiana", "Missouri"],
    "South": ["Florida", "Georgia", "North Carolina", "Virginia", "Tennessee", "Alabama"],
}

CITIES = {
    "New York": ["New York City", "Buffalo", "Rochester"],
    "New Jersey": ["Newark", "Jersey City", "Trenton"],
    "Pennsylvania": ["Philadelphia", "Pittsburgh", "Harrisburg"],
    "Massachusetts": ["Boston", "Cambridge", "Springfield"],
    "Connecticut": ["Hartford", "New Haven", "Stamford"],
    "Maryland": ["Baltimore", "Annapolis", "Silver Spring"],
    "California": ["Los Angeles", "San Francisco", "San Diego", "Sacramento"],
    "Washington": ["Seattle", "Spokane", "Tacoma"],
    "Oregon": ["Portland", "Salem", "Eugene"],
    "Nevada": ["Las Vegas", "Reno", "Carson City"],
    "Arizona": ["Phoenix", "Tucson", "Mesa"],
    "Colorado": ["Denver", "Colorado Springs", "Aurora"],
    "Illinois": ["Chicago", "Springfield", "Naperville"],
    "Texas": ["Houston", "Dallas", "Austin", "San Antonio"],
    "Ohio": ["Columbus", "Cleveland", "Cincinnati"],
    "Michigan": ["Detroit", "Grand Rapids", "Ann Arbor"],
    "Indiana": ["Indianapolis", "Fort Wayne", "South Bend"],
    "Missouri": ["St. Louis", "Kansas City", "Springfield"],
    "Florida": ["Miami", "Jacksonville", "Tampa", "Orlando"],
    "Georgia": ["Atlanta", "Savannah", "Augusta"],
    "North Carolina": ["Charlotte", "Raleigh", "Greensboro"],
    "Virginia": ["Richmond", "Virginia Beach", "Norfolk"],
    "Tennessee": ["Nashville", "Memphis", "Knoxville"],
    "Alabama": ["Birmingham", "Montgomery", "Mobile"],
}

PRODUCT_ADJECTIVES = [
    "Premium", "Classic", "Modern", "Compact", "Deluxe", "Essential",
    "Professional", "Standard", "Executive", "Basic", "Advanced", "Ergonomic",
]
PRODUCT_NOUNS = [
    "Desk", "Chair", "Table", "Shelf", "Lamp", "Organizer", "Cabinet",
    "Monitor", "Keyboard", "Mouse", "Printer", "Scanner", "Phone", "Charger",
    "Paper", "Pen Set", "Folder", "Binder", "Notebook", "Stapler",
    "Tape", "Scissors", "Calculator", "Clock", "Speaker", "Router",
]

FIRST_NAMES = [
    "James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael",
    "Linda", "William", "Elizabeth", "David", "Barbara", "Richard", "Susan",
    "Joseph", "Jessica", "Thomas", "Sarah", "Charles", "Karen", "Christopher",
    "Lisa", "Daniel", "Nancy", "Matthew", "Betty", "Anthony", "Margaret",
    "Mark", "Sandra", "Donald", "Ashley", "Steven", "Kimberly", "Paul",
    "Emily", "Andrew", "Donna", "Joshua", "Michelle",
]
LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
    "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez",
    "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin",
    "Lee", "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark",
    "Ramirez", "Lewis", "Robinson", "Walker", "Young", "Allen", "King",
    "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores",
]

# ── Generate Data ───────────────────────────────────────────────────────────────

def random_date(start, end):
    delta = (end - start).days
    return start + timedelta(days=random.randint(0, delta))


def generate_customers(num):
    customers = []
    for i in range(1, num + 1):
        cid = f"CU-{i:05d}"
        first = random.choice(FIRST_NAMES)
        last = random.choice(LAST_NAMES)
        name = f"{first} {last}"
        segment = random.choice(SEGMENTS)
        region = random.choice(REGIONS)
        state = random.choice(STATES_BY_REGION[region])
        city_options = CITIES.get(state, ["Unknown City"])
        city = random.choice(city_options)
        zip_code = str(random.randint(10000, 99999))
        customers.append((cid, name, segment, "United States", region, state, city, zip_code))
    return customers


def generate_products(num):
    products = []
    for i in range(1, num + 1):
        pid = f"PR-{i:05d}"
        cat = random.choice(list(CATEGORIES.keys()))
        subcat = random.choice(CATEGORIES[cat])
        adj = random.choice(PRODUCT_ADJECTIVES)
        noun = random.choice(PRODUCT_NOUNS)
        name = f"{adj} {noun}"
        products.append((pid, name, cat, subcat))
    return products


def generate_orders(customers, products, num_orders):
    orders = []
    line_items = []
    order_id_counter = 1

    for _ in range(num_orders):
        oid = f"OR-{order_id_counter:05d}"
        order_id_counter += 1
        order_date = random_date(START_DATE, END_DATE)
        ship_offset = random.randint(1, 7)
        ship_date = order_date + timedelta(days=ship_offset)
        ship_mode = random.choice(SHIP_MODES)
        customer = random.choice(customers)
        customer_id = customer[0]
        num_items = random.randint(1, MAX_LINE_ITEMS_PER_ORDER)

        for _ in range(num_items):
            product = random.choice(products)
            product_id = product[0]
            quantity = random.choice([1, 2, 3, 4, 5])
            # Base price depends on category
            if product[2] == "Technology":
                base_price = round(np.random.lognormal(mean=4.5, sigma=0.8), 2)
            elif product[2] == "Furniture":
                base_price = round(np.random.lognormal(mean=4.8, sigma=0.9), 2)
            else:
                base_price = round(np.random.lognormal(mean=3.5, sigma=0.7), 2)

            base_price = max(1.99, base_price)
            discount_roll = random.random()
            if discount_roll < 0.4:
                discount = round(random.choice([0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.45, 0.5, 0.6, 0.7]), 2)
            else:
                discount = 0.0

            sales = round(base_price * quantity * (1 - discount), 2)
            # Profit: roughly 10-40% margin, with a chance of loss on heavily discounted items
            margin = random.uniform(-0.15, 0.45) - (discount * 0.5)
            profit = round(sales * margin, 2)

            line_items.append((oid, order_date.strftime("%Y-%m-%d"), ship_date.strftime("%Y-%m-%d"),
                               ship_mode, customer_id, product_id, sales, quantity, discount, profit))

    return line_items


def seed_database(db_path=None):
    if db_path is None:
        db_path = DB_PATH

    db_path = pathlib.Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    # Load and execute schema
    schema_path = PROJECT_ROOT / "database" / "schema.sql"
    if schema_path.exists():
        schema_sql = schema_path.read_text(encoding="utf-8")
        cursor.executescript(schema_sql)
    else:
        print(f"Schema file not found at {schema_path}")
        conn.close()
        return False

    # Generate data
    print("Generating customers...")
    customers = generate_customers(NUM_CUSTOMERS)
    print("Generating products...")
    products = generate_products(NUM_PRODUCTS)
    print("Generating orders...")
    line_items = generate_orders(customers, products, NUM_ORDERS)

    # Insert customers
    print("Inserting customers...")
    cursor.executemany(
        "INSERT OR IGNORE INTO customers (customer_id, customer_name, segment, country, region, state, city, postal_code) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        customers,
    )

    # Insert products
    print("Inserting products...")
    cursor.executemany(
        "INSERT OR IGNORE INTO products (product_id, product_name, category, subcategory) VALUES (?, ?, ?, ?)",
        products,
    )

    # Insert orders (line items)
    print("Inserting order line items...")
    cursor.executemany(
        "INSERT OR IGNORE INTO orders (order_id, order_date, ship_date, ship_mode, customer_id, product_id, "
        "sales, quantity, discount, profit) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        line_items,
    )

    conn.commit()

    # Verify
    cursor.execute("SELECT COUNT(*) FROM customers")
    cust_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM products")
    prod_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM orders")
    ord_count = cursor.fetchone()[0]

    conn.close()

    print(f"\nDatabase seeded successfully at: {db_path}")
    print(f"  Customers: {cust_count}")
    print(f"  Products: {prod_count}")
    print(f"  Order line items: {ord_count}")
    return True


if __name__ == "__main__":
    seed_database()