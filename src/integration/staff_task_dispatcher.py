import os
import sys
import json
import sqlite3
from datetime import datetime

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(BASE_DIR)

EVENT_DB = os.path.join(BASE_DIR, "retail_events.db")
TASK_FILE = os.path.join(BASE_DIR, "staff_tasks.json")

STAFF = [
    {
        "id": "S001",
        "name": "Staff 1",
        "role": "sales",
        "section": "Shelf 1",
        "status": "Available"
    },
    {
        "id": "S002",
        "name": "Staff 2",
        "role": "sales",
        "section": "Shelf 2",
        "status": "Available"
    },
    {
        "id": "S003",
        "name": "Staff 3",
        "role": "sales",
        "section": "Checkout",
        "status": "Available"
    }
]


def load_tasks():
    if not os.path.exists(TASK_FILE):
        return []

    try:
        with open(TASK_FILE, "r") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except:
        return []


def save_tasks(tasks):
    with open(TASK_FILE, "w") as f:
        json.dump(tasks, f, indent=4)


def log_event(event_type, data):
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
        "staff_task_dispatcher",
        json.dumps(data)
    ))

    con.commit()
    con.close()


def find_available_staff(task):
    task_type = task.get("task_type", "")
    product = task.get("product", "")

    available = [
        staff for staff in STAFF
        if staff["status"] == "Available"
    ]

    if not available:
        return None

    if task_type == "QUEUE_SUPPORT":
        for staff in available:
            if staff["section"] == "Checkout":
                return staff

    if task_type in ["REFILL", "SHELF_CHECK"]:
        for staff in available:
            if product and staff["section"] in ["Shelf 1", "Shelf 2"]:
                return staff

    return available[0]


def create_dispatch_task(task):
    staff = find_available_staff(task)

    task["dispatch_status"] = "Assigned" if staff else "Waiting"
    task["assigned_staff"] = staff["id"] if staff else None
    task["assigned_staff_name"] = staff["name"] if staff else None
    task["assigned_at"] = datetime.now().isoformat() if staff else None

    if staff:
        staff["status"] = "Busy"

    log_event(
        "TASK_ASSIGNED" if staff else "TASK_WAITING",
        task
    )

    return task


def accept_task(task):
    if task.get("dispatch_status") != "Assigned":
        return False

    task["status"] = "Accepted"
    task["accepted_at"] = datetime.now().isoformat()

    log_event(
        "TASK_ACCEPTED",
        task
    )

    return True


def start_task(task):
    if task.get("status") != "Accepted":
        return False

    task["status"] = "In Progress"
    task["started_at"] = datetime.now().isoformat()

    log_event(
        "TASK_STARTED",
        task
    )

    return True


def complete_task(task):
    if task.get("status") != "In Progress":
        return False

    task["status"] = "Completed"
    task["completed_at"] = datetime.now().isoformat()

    staff_id = task.get("assigned_staff")

    for staff in STAFF:
        if staff["id"] == staff_id:
            staff["status"] = "Available"

    log_event(
        "TASK_COMPLETED",
        task
    )

    return True


def decline_task(task):
    if task.get("status") not in ["Pending", "Accepted"]:
        return False

    staff_id = task.get("assigned_staff")

    for staff in STAFF:
        if staff["id"] == staff_id:
            staff["status"] = "Available"

    task["status"] = "Pending"
    task["dispatch_status"] = "Waiting"
    task["assigned_staff"] = None
    task["assigned_staff_name"] = None
    task["declined_at"] = datetime.now().isoformat()

    log_event(
        "TASK_DECLINED",
        task
    )

    return True


def dispatch_tasks(tasks):
    dispatched = []

    for task in tasks:
        dispatched_task = create_dispatch_task(task)
        dispatched.append(dispatched_task)

    save_tasks(dispatched)

    return dispatched


def display_staff():
    print("\nSTAFF STATUS")
    print("-" * 65)

    for staff in STAFF:
        print(
            f"{staff['id']} | "
            f"{staff['name']} | "
            f"{staff['role']} | "
            f"{staff['section']} | "
            f"{staff['status']}"
        )


def display_tasks(tasks):
    print("\nTASK DISPATCH")
    print("-" * 65)

    for task in tasks:
        print(
            f"{task['task_type']} | "
            f"Priority: {task['priority']} | "
            f"Staff: {task.get('assigned_staff_name', 'None')} | "
            f"Status: {task['status']} | "
            f"Dispatch: {task.get('dispatch_status', 'Waiting')}"
        )


def demo():
    tasks = [
        {
            "task_type": "REFILL",
            "product": "water_bottle",
            "priority": "HIGH",
            "status": "Pending"
        },
        {
            "task_type": "QUEUE_SUPPORT",
            "priority": "HIGH",
            "queue_count": 7,
            "status": "Pending"
        },
        {
            "task_type": "SHELF_CHECK",
            "product": "jinthaa_juice",
            "priority": "MEDIUM",
            "status": "Pending"
        }
    ]

    print("\n" + "=" * 70)
    print("SIH26179 - STAFF TASK DISPATCHER")
    print("=" * 70)

    display_staff()

    dispatched = dispatch_tasks(tasks)

    display_tasks(dispatched)

    print("\nTASK LIFECYCLE TEST")
    print("-" * 65)

    task = dispatched[0]

    print("1. Task assigned to:", task.get("assigned_staff_name"))

    if accept_task(task):
        print("2. Task accepted")

    if start_task(task):
        print("3. Task started")

    if complete_task(task):
        print("4. Task completed")

    print("\nFINAL TASK STATUS")
    print("-" * 65)

    print(
        f"Task: {task['task_type']} | "
        f"Staff: {task.get('assigned_staff_name')} | "
        f"Status: {task['status']}"
    )

    display_staff()

    save_tasks(dispatched)

    print("\n" + "=" * 70)
    print("STAFF TASK DISPATCH COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    demo()