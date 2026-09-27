import random
import time


UNIT_WEIGHTS = {
    "jinthaa_juice": 218,
    "dhal": 250,
    "water_bottle": 512,
    "lifebuoy": 118
}


def calculate_rack_weight(stock):
    total_weight = 0

    for product, quantity in stock.items():
        total_weight += UNIT_WEIGHTS[product] * quantity

    return total_weight


def simulate_rack_sensor(stock):
    ideal_weight = calculate_rack_weight(stock)

    variation = random.uniform(-0.01, 0.01)

    measured_weight = ideal_weight * (1 + variation)

    return round(measured_weight, 2)


def calculate_weight_change(previous_weight, current_weight):
    return round(current_weight - previous_weight, 2)


def get_rack_status(weight, previous_weight):
    change = calculate_weight_change(
        previous_weight,
        weight
    )

    if change < -500:
        return "SIGNIFICANT_REMOVAL"

    if change < -100:
        return "STOCK_REMOVAL"

    if change > 100:
        return "REFILL_DETECTED"

    return "STABLE"


def display_rack_reading(weight, previous_weight, status):
    change = calculate_weight_change(
        previous_weight,
        weight
    )

    print(
        f"Rack Weight: {weight:10.2f} g | "
        f"Change: {change:10.2f} g | "
        f"Status: {status}"
    )


def demo():
    print("\nSIH26179 - RACK LEVEL SENSOR SIMULATION")
    print("=" * 75)

    stock = {
        "jinthaa_juice": 10,
        "dhal": 8,
        "water_bottle": 12,
        "lifebuoy": 6
    }

    print("\nUNIT WEIGHTS")
    print("-" * 50)

    for product, weight in UNIT_WEIGHTS.items():
        print(f"{product:18} : {weight} g")

    initial_weight = calculate_rack_weight(stock)

    print("\nINITIAL RACK STOCK")
    print("-" * 50)

    for product, quantity in stock.items():
        print(f"{product:18} : {quantity} units")

    print(f"\nExpected rack weight: {initial_weight} g")

    previous_weight = initial_weight

    print("\nSIMULATED HX711 RACK READINGS")
    print("-" * 75)

    for _ in range(5):
        current_weight = simulate_rack_sensor(stock)

        status = get_rack_status(
            current_weight,
            previous_weight
        )

        display_rack_reading(
            current_weight,
            previous_weight,
            status
        )

        previous_weight = current_weight

        time.sleep(1)

    print("\nSIMULATING PRODUCT REMOVAL")
    print("-" * 75)

    stock["water_bottle"] -= 2

    current_weight = simulate_rack_sensor(stock)

    status = get_rack_status(
        current_weight,
        previous_weight
    )

    display_rack_reading(
        current_weight,
        previous_weight,
        status
    )

    previous_weight = current_weight

    print("\nSIMULATING REFILL")
    print("-" * 75)

    stock["jinthaa_juice"] += 5

    current_weight = simulate_rack_sensor(stock)

    status = get_rack_status(
        current_weight,
        previous_weight
    )

    display_rack_reading(
        current_weight,
        previous_weight,
        status
    )

    print("\nRACK SENSOR SIMULATION COMPLETED")


if __name__ == "__main__":
    demo()