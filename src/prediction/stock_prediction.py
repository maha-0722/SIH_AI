import time
from collections import defaultdict, deque

HISTORY_SIZE = 20
LOW_STOCK_LIMIT = 2

history = defaultdict(lambda: deque(maxlen=HISTORY_SIZE))

def add_reading(product, quantity):
    history[product].append(
        (time.time(), quantity)
    )

def calculate_removal_rate(product):
    readings = history[product]

    if len(readings) < 2:
        return 0

    first_time, first_quantity = readings[0]
    last_time, last_quantity = readings[-1]

    elapsed_hours = (last_time - first_time) / 3600

    if elapsed_hours <= 0:
        return 0

    removed = first_quantity - last_quantity

    if removed <= 0:
        return 0

    return removed / elapsed_hours

def predict_depletion(product):
    readings = history[product]

    if not readings:
        return {
            "product": product,
            "status": "NO_DATA",
            "hours_remaining": None
        }

    current_quantity = readings[-1][1]
    rate = calculate_removal_rate(product)

    if current_quantity <= 0:
        status = "OUT_OF_STOCK"
        hours_remaining = 0

    elif current_quantity <= LOW_STOCK_LIMIT:
        status = "LOW_STOCK"
        hours_remaining = (
            current_quantity / rate
            if rate > 0 else None
        )

    elif rate > 0:
        hours_remaining = current_quantity / rate
        status = "DEPLETION_PREDICTED"

    else:
        hours_remaining = None
        status = "NORMAL"

    return {
        "product": product,
        "current_quantity": current_quantity,
        "removal_rate_per_hour": round(rate, 2),
        "hours_remaining": (
            round(hours_remaining, 2)
            if hours_remaining is not None
            else None
        ),
        "status": status
    }

def display_prediction(result):
    print(
        f"{result['product']:18} | "
        f"Qty: {result.get('current_quantity', '-'):>3} | "
        f"Rate: {result.get('removal_rate_per_hour', '-'):>6} | "
        f"Hours: {result.get('hours_remaining', '-'):>6} | "
        f"{result['status']}"
    )

def demo():
    print("\nSIH26179 - STOCK DEPLETION PREDICTION")
    print("=" * 75)

    product = "water_bottle"

    quantities = [12, 11, 10, 9, 8, 7, 6]

    for quantity in quantities:
        add_reading(product, quantity)
        time.sleep(0.1)

    result = predict_depletion(product)

    print("\nPREDICTION")
    print("-" * 75)
    display_prediction(result)

    print("\nSTOCK DEPLETION PREDICTION COMPLETED")

if __name__ == "__main__":
    demo()