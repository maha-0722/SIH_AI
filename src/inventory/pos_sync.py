import time
import sqlite3

DB_PATH = "retail_inventory.db"

PRODUCTS = {
    "water_bottle": {
        "total_stock": 50,
        "shelf_stock": 10
    },
    "jinthaa_juice": {
        "total_stock": 50,
        "shelf_stock": 10
    },
    "lifebuoy": {
        "total_stock": 50,
        "shelf_stock": 10
    },
    "dhal": {
        "total_stock": 50,
        "shelf_stock": 10
    }
}


def create_database():
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventory_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product TEXT,
            event_type TEXT,
            quantity INTEGER,
            shelf_stock INTEGER,
            total_stock INTEGER,
            timestamp REAL
        )
    """)

    connection.commit()
    connection.close()


def save_event(
    product,
    event_type,
    quantity,
    shelf_stock,
    total_stock
):
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO inventory_events
        (product, event_type, quantity, shelf_stock, total_stock, timestamp)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        product,
        event_type,
        quantity,
        shelf_stock,
        total_stock,
        time.time()
    ))

    connection.commit()
    connection.close()


def process_sale(product, quantity):
    if product not in PRODUCTS:
        return False

    if quantity <= 0:
        return False

    if PRODUCTS[product]["total_stock"] < quantity:
        return False

    PRODUCTS[product]["total_stock"] -= quantity

    if PRODUCTS[product]["shelf_stock"] >= quantity:
        PRODUCTS[product]["shelf_stock"] -= quantity

    save_event(
        product,
        "SALE",
        quantity,
        PRODUCTS[product]["shelf_stock"],
        PRODUCTS[product]["total_stock"]
    )

    return True


def process_shelf_removal(product, quantity):
    if product not in PRODUCTS:
        return False

    if quantity <= 0:
        return False

    if PRODUCTS[product]["shelf_stock"] < quantity:
        return False

    PRODUCTS[product]["shelf_stock"] -= quantity

    save_event(
        product,
        "SHELF_REMOVAL",
        quantity,
        PRODUCTS[product]["shelf_stock"],
        PRODUCTS[product]["total_stock"]
    )

    return True


def process_refill(product, quantity):
    if product not in PRODUCTS:
        return False

    if quantity <= 0:
        return False

    PRODUCTS[product]["shelf_stock"] += quantity

    save_event(
        product,
        "REFILL",
        quantity,
        PRODUCTS[product]["shelf_stock"],
        PRODUCTS[product]["total_stock"]
    )

    return True


def process_delivery(product, quantity):
    if product not in PRODUCTS:
        return False

    if quantity <= 0:
        return False

    PRODUCTS[product]["total_stock"] += quantity

    save_event(
        product,
        "DELIVERY",
        quantity,
        PRODUCTS[product]["shelf_stock"],
        PRODUCTS[product]["total_stock"]
    )

    return True


def process_return(product, quantity):
    if product not in PRODUCTS:
        return False

    if quantity <= 0:
        return False

    PRODUCTS[product]["total_stock"] += quantity

    save_event(
        product,
        "RETURN",
        quantity,
        PRODUCTS[product]["shelf_stock"],
        PRODUCTS[product]["total_stock"]
    )

    return True


def process_adjustment(product, quantity):
    if product not in PRODUCTS:
        return False

    PRODUCTS[product]["total_stock"] += quantity

    if PRODUCTS[product]["total_stock"] < 0:
        PRODUCTS[product]["total_stock"] = 0

    save_event(
        product,
        "ADJUSTMENT",
        quantity,
        PRODUCTS[product]["shelf_stock"],
        PRODUCTS[product]["total_stock"]
    )

    return True


def display_inventory():
    print("\nCURRENT INVENTORY")
    print("-" * 55)

    for product, data in PRODUCTS.items():
        print(
            f"{product:<20} "
            f"Shelf: {data['shelf_stock']:<5} "
            f"Total: {data['total_stock']}"
        )


def display_events():
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT product, event_type, quantity,
               shelf_stock, total_stock
        FROM inventory_events
        ORDER BY id
    """)

    events = cursor.fetchall()

    connection.close()

    print("\nINVENTORY EVENTS")
    print("-" * 70)

    for event in events:
        print(
            f"Product: {event[0]} | "
            f"Event: {event[1]} | "
            f"Qty: {event[2]} | "
            f"Shelf: {event[3]} | "
            f"Total: {event[4]}"
        )


def simulate_ai_pos_flow():
    print("\nAI + POS INVENTORY SYNCHRONIZATION")

    process_shelf_removal(
        "water_bottle",
        2
    )

    process_sale(
        "water_bottle",
        2
    )

    process_refill(
        "water_bottle",
        5
    )

    process_delivery(
        "jinthaa_juice",
        20
    )

    process_return(
        "lifebuoy",
        2
    )

    process_adjustment(
        "dhal",
        -1
    )


create_database()

simulate_ai_pos_flow()

display_inventory()

display_events()