# pricing.py
def apply_discount(price, percent):
    if not 0 <= percent <= 100:
        raise ValueError("bad percent")
    factor = 1 - percent / 100
    return round(price * factor, 2)
