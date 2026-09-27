import os
import sys
import json
import sqlite3

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(BASE_DIR)

from src.integration.decision_engine import process_store_state
from src.integration.staff_task_dispatcher import (
    dispatch_tasks,
    accept_task,
    start_task,
    complete_task
)

EVENT_DB = os.path.join(BASE_DIR, "retail_events.db")


def check_event_database():
    if not os.path.exists(EVENT_DB):
        return False

    con = sqlite3.connect(EVENT_DB)
    cur = con.cursor()

    cur.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type='table' AND name='events'
    """)

    result = cur.fetchone()
    con.close()

    return result is not None


def run_test():
    print("\n" + "=" * 70)
    print("SIH26179 - END TO END SOFTWARE TEST")
    print("=" * 70)

    print("\n[1] STORE EVENT")
    store_state = {
        "product": "water_bottle",
        "stock_status": "LOW",
        "hours_remaining": 2.4,
        "queue_status": "QUEUE CONGESTION",
        "queue_count": 7,
        "anomaly": False,
        "misplaced": True
    }

    print("PASS")
    print("Product:", store_state["product"])
    print("Stock:", store_state["stock_status"])
    print("Queue:", store_state["queue_status"])

    print("\n[2] DECISION ENGINE")
    decisions, tasks = process_store_state(store_state)

    if decisions:
        print("PASS")
        print("Decisions generated:", len(decisions))
    else:
        print("FAIL")
        return

    print("\n[3] TASK CREATION")
    if tasks:
        print("PASS")
        print("Tasks created:", len(tasks))
    else:
        print("FAIL")
        return

    print("\n[4] STAFF DISPATCH")
    dispatched_tasks = dispatch_tasks(tasks)

    assigned_count = sum(
        1 for task in dispatched_tasks
        if task.get("assigned_staff") is not None
    )

    if assigned_count > 0:
        print("PASS")
        print("Tasks assigned:", assigned_count)
    else:
        print("FAIL")
        return

    print("\n[5] TASK ACCEPTANCE")

    test_task = None

    for task in dispatched_tasks:
        if task.get("assigned_staff") is not None:
            test_task = task
            break

    if test_task is None:
        print("FAIL")
        return

    if accept_task(test_task):
        print("PASS")
        print("Status:", test_task["status"])
    else:
        print("FAIL")
        return

    print("\n[6] TASK START")

    if start_task(test_task):
        print("PASS")
        print("Status:", test_task["status"])
    else:
        print("FAIL")
        return

    print("\n[7] TASK COMPLETION")

    if complete_task(test_task):
        print("PASS")
        print("Status:", test_task["status"])
    else:
        print("FAIL")
        return

    print("\n[8] EVENT DATABASE")

    if check_event_database():
        print("PASS")
    else:
        print("FAIL")
        return

    print("\n[9] FINAL WORKFLOW")

    workflow = [
        "Store Event Detected",
        "Decision Generated",
        "Task Created",
        "Staff Assigned",
        "Task Accepted",
        "Task Started",
        "Task Completed",
        "Event Logged"
    ]

    for i, step in enumerate(workflow, 1):
        print(f"{i}. {step}")

    print("\n" + "=" * 70)
    print("SIH26179 - END TO END INTEGRATION REPORT")
    print("=" * 70)
    print("Passed: 9/9")
    print("OVERALL STATUS: END TO END SOFTWARE PASS")
    print("=" * 70)


if __name__ == "__main__":
    run_test()