# config.py

# Each product is a dictionary with:
# - url: the Amazon product page URL
# - name: human readable label
# - target_price: alert when price drops below this

# config.py
PRODUCTS = [
    {
        "name": "Silent Hill Townfall PS5",
        "url": "https://www.amazon.com/dp/B0GMPN17CC",
        "target_price": 50000.00
    },
    {
        "name": "Silent Hill Townfall PS5 — Copy",
        "url": "https://www.amazon.com/dp/B0GMPN17CC",
        "target_price": 70000.00
    },
    {
        "name": "Silent Hill Townfall PS5 — Copy 2",
        "url": "https://www.amazon.com/dp/B0GMPN17CC",
        "target_price": 80000.00
    },
    {
        "name": "Silent Hill Townfall PS5 — Copy 3",
        "url": "https://www.amazon.com/dp/B0GMPN17CC",
        "target_price": 40000.00
    },
]

NUM_CONTEXTS = 2
CURRENCY = "₦"