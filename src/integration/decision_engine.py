import os
import sys
import json
import sqlite3
from datetime import datetime

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(BASE_DIR)

ALERT_FILE = os.path.join(BASE_DIR, "alerts.json")
EVENT_DB = os.path.join(BASE_DIR, "retail_events.db")


def load_alerts():
    if not os.path.exists(ALERT_FILE):
        return []

    try:
        with open(ALERT_FILE, "r") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except:
        return []


def save_alerts(alerts):
    with open(ALERT_FILE, "w") as f:
        json.dump(alerts, f, indent=4)


def create_alert(alert_type, message, priority, source):
    alerts = load_alerts()

    alert = {
        "id": len(alerts) + 1,
        "timestamp": datetime.now().isoformat(),
        "type": alert_type,
        "message": message,
        "priority": priority,
        "source": source,
        "status": "NEW"
    }

    alerts.append(alert)
    save_alerts(alerts)

    return alert


def create_event(event_type, source, data):
    os.makedirs(os.path.dirname(EVENT_DB), exist_ok=True)

    con = sqlite3.connect(EVENT_DB)
    cur = con.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            event_type TEXT,
            source TEXT,
            data TEXT
        )
    """)

    cur.execute("""
        INSERT INTO events(timestamp, event_type, source, data)
        VALUES (?, ?, ?, ?)
    """, (
        datetime.now().isoformat(),
        event_type,
        source,
        json.dumps(data)
    ))

    con.commit()
    con.close()


def calculate_task_priority(stock_status=None, hours_remaining=None,
                            queue_status=None, anomaly=False):

    priority = 0

    if stock_status == "EMPTY":
        priority += 50
    elif stock_status == "LOW":
        priority += 35
    elif stock_status == "MEDIUM":
        priority += 15

    if hours_remaining is not None:
        if hours_remaining <= 1:
            priority += 30
        elif hours_remaining <= 3:
            priority += 20
        elif hours_remaining <= 6:
            priority += 10

    if queue_status == "QUEUE CONGESTION":
        priority += 20
    elif queue_status == "MODERATE":
        priority += 10

    if anomaly:
        priority += 15

    if priority >= 60:
        return "HIGH"
    elif priority >= 30:
        return "MEDIUM"
    return "LOW"


def generate_decision(data):
    decisions = []

    product = data.get("product", "unknown")
    stock_status = data.get("stock_status")
    hours_remaining = data.get("hours_remaining")
    queue_status = data.get("queue_status")
    queue_count = data.get("queue_count", 0)
    anomaly = data.get("anomaly", False)
    misplaced = data.get("misplaced", False)

    if stock_status == "EMPTY":
        decisions.append({
            "action": "CREATE_REFILL_TASK",
            "product": product,
            "priority": "HIGH",
            "reason": "Shelf is empty"
        })

        create_alert(
            "OUT_OF_STOCK",
            f"{product} shelf is empty. Refill required.",
            "HIGH",
            "decision_engine"
        )

    elif stock_status == "LOW":
        priority = calculate_task_priority(
            stock_status,
            hours_remaining,
            queue_status,
            anomaly
        )

        decisions.append({
            "action": "CREATE_REFILL_TASK",
            "product": product,
            "priority": priority,
            "reason": "Low shelf stock"
        })

        create_alert(
            "LOW_STOCK",
            f"{product} stock is low.",
            priority,
            "decision_engine"
        )

    if hours_remaining is not None and hours_remaining <= 3:
        decisions.append({
            "action": "DEPLETION_WARNING",
            "product": product,
            "hours_remaining": hours_remaining
        })

        create_alert(
            "DEPLETION_WARNING",
            f"{product} may be depleted in approximately {hours_remaining:.2f} hours.",
            "MEDIUM",
            "decision_engine"
        )

    if queue_status == "QUEUE CONGESTION":
        decisions.append({
            "action": "QUEUE_INTERVENTION",
            "queue_count": queue_count,
            "priority": "HIGH"
        })

        create_alert(
            "QUEUE_CONGESTION",
            f"Queue congestion detected. People in queue: {queue_count}",
            "HIGH",
            "decision_engine"
        )

    elif queue_status == "MODERATE":
        decisions.append({
            "action": "MONITOR_QUEUE",
            "queue_count": queue_count,
            "priority": "MEDIUM"
        })

        create_alert(
            "QUEUE_CONGESTION",
            f"Moderate queue detected. People in queue: {queue_count}",
            "MEDIUM",
            "decision_engine"
        )

    if misplaced:
        decisions.append({
            "action": "CHECK_SHELF",
            "product": product,
            "priority": "MEDIUM"
        })

        create_alert(
            "MISPLACED_PRODUCT",
            f"Possible misplaced product detected near {product} shelf.",
            "MEDIUM",
            "decision_engine"
        )

    if anomaly:
        decisions.append({
            "action": "REVIEW_ANOMALY",
            "priority": "MEDIUM"
        })

        create_alert(
            "ANOMALY",
            "Unusual store event requires staff review.",
            "MEDIUM",
            "decision_engine"
        )

    return decisions


def create_staff_tasks(decisions):
    tasks = []

    for decision in decisions:
        action = decision["action"]

        if action == "CREATE_REFILL_TASK":
            task = {
                "task_type": "REFILL",
                "product": decision["product"],
                "priority": decision["priority"],
                "status": "Pending",
                "created_at": datetime.now().isoformat()
            }

            tasks.append(task)

            create_event(
                "STAFF_TASK_CREATED",
                "decision_engine",
                task
            )

        elif action == "QUEUE_INTERVENTION":
            task = {
                "task_type": "QUEUE_SUPPORT",
                "priority": decision["priority"],
                "queue_count": decision["queue_count"],
                "status": "Pending",
                "created_at": datetime.now().isoformat()
            }

            tasks.append(task)

            create_event(
                "STAFF_TASK_CREATED",
                "decision_engine",
                task
            )

        elif action == "CHECK_SHELF":
            task = {
                "task_type": "SHELF_CHECK",
                "product": decision["product"],
                "priority": decision["priority"],
                "status": "Pending",
                "created_at": datetime.now().isoformat()
            }

            tasks.append(task)

            create_event(
                "STAFF_TASK_CREATED",
                "decision_engine",
                task
            )

        elif action == "REVIEW_ANOMALY":
            task = {
                "task_type": "ANOMALY_REVIEW",
                "priority": decision["priority"],
                "status": "Pending",
                "created_at": datetime.now().isoformat()
            }

            tasks.append(task)

            create_event(
                "STAFF_TASK_CREATED",
                "decision_engine",
                task
            )

    return tasks


def process_store_state(data):
    decisions = generate_decision(data)
    tasks = create_staff_tasks(decisions)

    create_event(
        "DECISION_PROCESSED",
        "decision_engine",
        {
            "input": data,
            "decisions": decisions,
            "tasks_created": len(tasks)
        }
    )

    return decisions, tasks


def display_results(decisions, tasks):
    print("\n" + "=" * 65)
    print("SIH26179 - AI DECISION ENGINE")
    print("=" * 65)

    print("\nDECISIONS")
    print("-" * 65)

    if not decisions:
        print("No action required.")
    else:
        for decision in decisions:
            print(
                f"{decision['action']} | "
                f"Priority: {decision.get('priority', '-')}"
            )

    print("\nSTAFF TASKS")
    print("-" * 65)

    if not tasks:
        print("No staff tasks created.")
    else:
        for task in tasks:
            print(
                f"{task['task_type']} | "
                f"Priority: {task['priority']} | "
                f"Status: {task['status']}"
            )

    print("\n" + "=" * 65)


def demo():
    store_state = {
        "product": "water_bottle",
        "stock_status": "LOW",
        "hours_remaining": 2.4,
        "queue_status": "QUEUE CONGESTION",
        "queue_count": 7,
        "anomaly": False,
        "misplaced": True
    }

    decisions, tasks = process_store_state(store_state)

    display_results(decisions, tasks)


if __name__ == "__main__":
    demo()