import sqlite3
import json
from datetime import datetime
from collections import deque

DB_FILE = "retail_events.db"

event_queue = deque()

def get_connection():
    return sqlite3.connect(DB_FILE)

def initialize_database():
    con = get_connection()

    con.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_type TEXT NOT NULL,
            source TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            data TEXT
        )
    """)

    con.commit()
    con.close()

def create_event(event_type, source, data):
    event = {
        "event_type": event_type,
        "source": source,
        "timestamp": datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
        "data": data
    }

    event_queue.append(event)

    return event

def save_event(event):
    con = get_connection()

    con.execute(
        """
        INSERT INTO events
        (event_type, source, timestamp, data)
        VALUES (?, ?, ?, ?)
        """,
        (
            event["event_type"],
            event["source"],
            event["timestamp"],
            json.dumps(event["data"])
        )
    )

    con.commit()
    con.close()

def process_event(event):
    save_event(event)

    print(
        f"[EVENT] {event['event_type']} | "
        f"{event['source']} | "
        f"{event['data']}"
    )

def process_queue():
    while event_queue:
        event = event_queue.popleft()
        process_event(event)

def inventory_event(product, quantity, status):
    return create_event(
        "INVENTORY",
        "YOLO",
        {
            "product": product,
            "quantity": quantity,
            "status": status
        }
    )

def queue_event(count, wait_time, status):
    return create_event(
        "QUEUE",
        "CAMERA",
        {
            "queue_count": count,
            "wait_time": wait_time,
            "status": status
        }
    )

def sensor_event(weight, change, status):
    return create_event(
        "SENSOR",
        "HX711",
        {
            "rack_weight": weight,
            "weight_change": change,
            "status": status
        }
    )

def pos_event(transaction_id, product, quantity):
    return create_event(
        "POS",
        "POS_SYSTEM",
        {
            "transaction_id": transaction_id,
            "product": product,
            "quantity": quantity
        }
    )

def staff_event(staff_id, task_id, status):
    return create_event(
        "STAFF",
        "STAFF_SYSTEM",
        {
            "staff_id": staff_id,
            "task_id": task_id,
            "status": status
        }
    )

def rfid_event(tag_id, product, payment_status):
    return create_event(
        "RFID",
        "EXIT_READER",
        {
            "tag_id": tag_id,
            "product": product,
            "payment_status": payment_status
        }
    )

def anomaly_event(anomaly_type, severity):
    return create_event(
        "ANOMALY",
        "AI_ENGINE",
        {
            "type": anomaly_type,
            "severity": severity
        }
    )

def task_event(task_id, task_type, priority):
    return create_event(
        "TASK",
        "TASK_ENGINE",
        {
            "task_id": task_id,
            "task_type": task_type,
            "priority": priority
        }
    )

def demo():
    print("\nSIH26179 - EVENT PROCESSOR")
    print("=" * 65)

    initialize_database()

    inventory_event(
        "water_bottle",
        8,
        "LOW_STOCK"
    )

    queue_event(
        6,
        4.5,
        "MODERATE"
    )

    sensor_event(
        6820.5,
        -512.0,
        "SIGNIFICANT_REMOVAL"
    )

    pos_event(
        "TXN1001",
        "water_bottle",
        1
    )

    staff_event(
        "STAFF001",
        "TASK001",
        "IN_PROGRESS"
    )

    rfid_event(
        "RFID001",
        "water_bottle",
        "PAID"
    )

    anomaly_event(
        "UNUSUAL_ACTIVITY",
        "MEDIUM"
    )

    task_event(
        "TASK001",
        "REFILL",
        "HIGH"
    )

    print("\nProcessing events...\n")

    process_queue()

    print("\nEVENT PROCESSING COMPLETED")

if __name__ == "__main__":
    demo()