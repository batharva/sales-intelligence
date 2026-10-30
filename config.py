from pathlib import Path
ROOT = Path(__file__).parent
P = dict(bg="#F3F3EF", surface="#FFFFFF", text="#191B1A", muted="#6B706D", border="#D9DDD7",
         accent="#285C48", steel="#637D8A", pos="#2E7D55", neg="#A64B3A", grid="#E6E8E3")
REQUIRED = ["order_id", "order_date", "customer_id", "segment", "region", "category",
            "subcategory", "product", "quantity", "sales"]
