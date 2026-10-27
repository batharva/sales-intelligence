# Dataset

This directory contains the SQLite database file used by the Sales Intelligence dashboard.

## Automatic Generation

The database (`sales_intelligence.db`) is **automatically generated** when the application starts for the first time. The generation process:

1. Drops the existing database if present
2. Creates the schema from `database/schema.sql`
3. Generates ~10,000 synthetic order records
4. Creates ~800 customer records
5. Creates ~1,800 product records

## Manual Generation

To manually generate or regenerate the database:

```bash
cd sales-intelligence
python database/seed_database.py
```

## Dataset Schema

- **customers**: Customer dimension (customer_id, name, segment, region, etc.)
- **products**: Product dimension (product_id, name, category, subcategory)
- **orders**: Fact table (order_id, date, customer, product, sales, quantity, etc.)

## Notes

- The `sales_intelligence.db` file is in `.gitignore` and will not be committed
- Each run of `seed_database.py` regenerates the data with the same random seed for reproducibility
- The synthetic dataset is modeled after Tableau's Sample - Superstore schema
- No real customer data is used — all names and records are randomly generated