import sqlite3
import json
import uuid
from datetime import datetime
from collections import deque


DB_FILE = "retail_events.db"

event_queue = deque()


def get_timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def initialize_database():
    conn = sqlite3.connect(DB_FILE)

    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS events (
            event_id TEXT PRIMARY KEY,
            timestamp TEXT,
            event_type TEXT,
            source TEXT,
            severity TEXT,
            status TEXT,
            data TEXT
        )
    """)

    conn.commit()
    conn.close()


def create_event(event_type, source, data, severity="INFO", status="NEW"):
    event = {
        "event_id": str(uuid.uuid4()),
        "timestamp": get_timestamp(),
        "event_type": event_type,
        "source": source,
        "severity": severity,
        "status": status,
        "data": data
    }

    return event


def store_event(event):
    conn = sqlite3.connect(DB_FILE)

    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO events
        (event_id, timestamp, event_type, source, severity, status, data)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        event["event_id"],
        event["timestamp"],
        event["event_type"],
        event["source"],
        event["severity"],
        event["status"],
        json.dumps(event["data"])
    ))

    conn.commit()
    conn.close()


def add_event(event):
    event_queue.append(event)


def process_events():
    while event_queue:
        event = event_queue.popleft()
        store_event(event)

        print(
            f"[{event['timestamp']}] "
            f"{event['source']} -> "
            f"{event['event_type']} -> "
            f"{event['severity']}"
        )


def process_inventory_event(
    product,
    quantity,
    stock_status,
    shelf,
    source="YOLO"
):
    severity = "WARNING" if stock_status in ["Low", "Empty"] else "INFO"

    event = create_event(
        event_type="INVENTORY_UPDATE",
        source=source,
        data={
            "product": product,
            "quantity": quantity,
            "stock_status": stock_status,
            "shelf": shelf
        },
        severity=severity
    )

    add_event(event)


def process_queue_event(
    queue_count,
    estimated_wait,
    queue_status,
    source="QUEUE_AI"
):
    severity = "WARNING" if queue_status == "QUEUE CONGESTION" else "INFO"

    event = create_event(
        event_type="QUEUE_UPDATE",
        source=source,
        data={
            "queue_count": queue_count,
            "estimated_wait_minutes": estimated_wait,
            "queue_status": queue_status
        },
        severity=severity
    )

    add_event(event)


def process_sensor_event(
    product,
    sensor_quantity,
    shelf,
    sensor_status,
    source="HX711"
):
    severity = "WARNING" if sensor_status == "UNCERTAIN_CHECK_REQUIRED" else "INFO"

    event = create_event(
        event_type="SENSOR_UPDATE",
        source=source,
        data={
            "product": product,
            "sensor_quantity": sensor_quantity,
            "shelf": shelf,
            "sensor_status": sensor_status
        },
        severity=severity
    )

    add_event(event)


def process_pos_event(
    product,
    quantity,
    event_type,
    shelf_quantity,
    total_quantity,
    source="POS"
):
    event = create_event(
        event_type=event_type,
        source=source,
        data={
            "product": product,
            "quantity": quantity,
            "shelf_quantity": shelf_quantity,
            "total_quantity": total_quantity
        }
    )

    add_event(event)


def process_staff_event(
    staff_id,
    section,
    availability,
    task,
    source="STAFF_APP"
):
    event = create_event(
        event_type="STAFF_UPDATE",
        source=source,
        data={
            "staff_id": staff_id,
            "section": section,
            "availability": availability,
            "task": task
        }
    )

    add_event(event)


def process_rfid_event(
    tag_id,
    product,
    payment_status,
    outward_crossing,
    source="RFID"
):
    if payment_status == "UNRESOLVED" and outward_crossing:
        severity = "CRITICAL"
    else:
        severity = "INFO"

    event = create_event(
        event_type="EXIT_VERIFICATION",
        source=source,
        data={
            "tag_id": tag_id,
            "product": product,
            "payment_status": payment_status,
            "outward_crossing": outward_crossing
        },
        severity=severity
    )

    add_event(event)


def process_anomaly_event(
    anomaly_type,
    values,
    source="ANOMALY_AI"
):
    event = create_event(
        event_type="ANOMALY_DETECTED",
        source=source,
        data={
            "anomaly_type": anomaly_type,
            "values": values
        },
        severity="WARNING"
    )

    add_event(event)


def process_staff_task_event(
    task_id,
    task_type,
    staff_id,
    task_status,
    source="TASK_ENGINE"
):
    event = create_event(
        event_type="TASK_UPDATE",
        source=source,
        data={
            "task_id": task_id,
            "task_type": task_type,
            "staff_id": staff_id,
            "task_status": task_status
        }
    )

    add_event(event)


def get_recent_events(limit=20):
    conn = sqlite3.connect(DB_FILE)

    cursor = conn.cursor()

    cursor.execute("""
        SELECT event_id, timestamp, event_type, source,
               severity, status, data
        FROM events
        ORDER BY timestamp DESC
        LIMIT ?
    """, (limit,))

    rows = cursor.fetchall()

    conn.close()

    events = []

    for row in rows:
        events.append({
            "event_id": row[0],
            "timestamp": row[1],
            "event_type": row[2],
            "source": row[3],
            "severity": row[4],
            "status": row[5],
            "data": json.loads(row[6])
        })

    return events


def display_recent_events():
    events = get_recent_events()

    print("\nRECENT EVENTS")
    print("-" * 100)

    for event in events:
        print(
            f"{event['timestamp']} | "
            f"{event['source']} | "
            f"{event['event_type']} | "
            f"{event['severity']} | "
            f"{event['data']}"
        )


def demo():
    initialize_database()

    print("\nSIH26179 - REAL-TIME EVENT PROCESSING")
    print("=" * 70)

    process_inventory_event(
        product="water_bottle",
        quantity=4,
        stock_status="Low",
        shelf=1
    )

    process_sensor_event(
        product="water_bottle",
        sensor_quantity=4,
        shelf=1,
        sensor_status="CONFIRMED"
    )

    process_queue_event(
        queue_count=6,
        estimated_wait=8,
        queue_status="QUEUE CONGESTION"
    )

    process_pos_event(
        product="water_bottle",
        quantity=2,
        event_type="SALE",
        shelf_quantity=2,
        total_quantity=46
    )

    process_staff_event(
        staff_id="S001",
        section="Shelf 1",
        availability="Busy",
        task="Water bottle refill"
    )

    process_staff_task_event(
        task_id="T001",
        task_type="REFILL",
        staff_id="S001",
        task_status="Accepted"
    )

    process_anomaly_event(
        anomaly_type="Unexpected stock change",
        values={
            "people_count": 4,
            "queue_count": 2,
            "stock_change": -5,
            "dwell_time": 12
        }
    )

    process_rfid_event(
        tag_id="RFID001",
        product="water_bottle",
        payment_status="UNRESOLVED",
        outward_crossing=True
    )

    process_events()

    display_recent_events()

    print("\nEVENT PROCESSING COMPLETED")


if __name__ == "__main__":
    demo()