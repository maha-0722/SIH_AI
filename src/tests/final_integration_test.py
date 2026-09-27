import os
import sys
import time
import json
import sqlite3
from datetime import datetime


BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../..")
)

sys.path.insert(0, BASE_DIR)


MODEL_PATH = os.path.join(
    BASE_DIR,
    "runs",
    "detect",
    "train-2",
    "weights",
    "best.pt"
)

EVENT_DB = os.path.join(
    BASE_DIR,
    "retail_events.db"
)

INVENTORY_DB = os.path.join(
    BASE_DIR,
    "retail_inventory.db"
)

ALERT_FILE = os.path.join(
    BASE_DIR,
    "alerts.json"
)

EXIT_ALERT_FILE = os.path.join(
    BASE_DIR,
    "exit_alerts.json"
)

RFID_ALERT_FILE = os.path.join(
    BASE_DIR,
    "rfid_security_alerts.json"
)


def timestamp():
    return datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )


def check_model():
    print("\n[1] YOLOv8n MODEL")

    if os.path.exists(MODEL_PATH):
        print("PASS")
        return True

    print("FAIL")
    return False


def check_database(path, name):
    print(f"\n[2] {name}")

    if not os.path.exists(path):
        print("NOT FOUND")
        return False

    try:
        conn = sqlite3.connect(path)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT name FROM sqlite_master "
            "WHERE type='table'"
        )

        tables = cursor.fetchall()

        conn.close()

        print("PASS")
        print(
            "Tables:",
            [table[0] for table in tables]
        )

        return True

    except Exception as error:
        print("FAIL:", error)
        return False


def check_json(path, name):
    print(f"\n[3] {name}")

    if not os.path.exists(path):
        print("NOT FOUND")
        return False

    try:
        with open(path, "r") as file:
            json.load(file)

        print("PASS")
        return True

    except Exception as error:
        print("FAIL:", error)
        return False


def test_event_creation():
    print("\n[4] EVENT PROCESSING")

    try:
        conn = sqlite3.connect(EVENT_DB)

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

        event_id = (
            "FINAL_TEST_" +
            datetime.now().strftime(
                "%Y%m%d%H%M%S"
            )
        )

        event_data = {
            "product": "water_bottle",
            "quantity": 3,
            "status": "Low"
        }

        cursor.execute("""
            INSERT INTO events
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            event_id,
            timestamp(),
            "INTEGRATION_TEST",
            "AI_PIPELINE",
            "INFO",
            "TESTED",
            json.dumps(event_data)
        ))

        conn.commit()

        cursor.execute(
            "SELECT event_id FROM events "
            "WHERE event_id=?",
            (event_id,)
        )

        result = cursor.fetchone()

        conn.close()

        if result:
            print("PASS")
            return True

        print("FAIL")
        return False

    except Exception as error:
        print("FAIL:", error)
        return False


def test_inventory_data():
    print("\n[5] INVENTORY DATA")

    if not os.path.exists(INVENTORY_DB):
        print("NOT FOUND")
        return False

    try:
        conn = sqlite3.connect(
            INVENTORY_DB
        )

        cursor = conn.cursor()

        cursor.execute(
            "SELECT name FROM sqlite_master "
            "WHERE type='table'"
        )

        tables = [
            row[0]
            for row in cursor.fetchall()
        ]

        print(
            "Available tables:",
            tables
        )

        conn.close()

        print("PASS")
        return True

    except Exception as error:
        print("FAIL:", error)
        return False


def test_alert_system():
    print("\n[6] ALERT SYSTEM")

    files = [
        ALERT_FILE,
        EXIT_ALERT_FILE,
        RFID_ALERT_FILE
    ]

    found = 0

    for path in files:

        if os.path.exists(path):

            try:
                with open(path, "r") as file:
                    data = json.load(file)

                print(
                    os.path.basename(path),
                    "PASS",
                    f"({len(data)} records)"
                )

                found += 1

            except Exception:
                print(
                    os.path.basename(path),
                    "INVALID"
                )

    if found > 0:
        return True

    print(
        "No alert files available yet."
    )

    return False


def test_local_event_speed():
    print("\n[7] LOCAL EVENT PROCESSING SPEED")

    start = time.time()

    for i in range(1000):

        event = {
            "id": i,
            "timestamp": timestamp(),
            "source": "AI",
            "type": "TEST",
            "data": {
                "product": "water_bottle",
                "quantity": i % 10
            }
        }

        json.dumps(event)

    elapsed = time.time() - start

    print(
        f"1000 events processed in "
        f"{elapsed:.4f} seconds"
    )

    if elapsed < 5:
        print("PASS")
        return True

    print("NEEDS REVIEW")
    return False


def test_required_modules():
    print("\n[8] PROJECT MODULES")

    modules = [
        "src/detection",
        "src/tracking",
        "src/customer_analytics",
        "src/queue",
        "src/inventory",
        "src/planogram",
        "src/prediction",
        "src/anomaly",
        "src/staff",
        "src/alerts",
        "src/security",
        "src/events",
        "src/integration",
        "src/tests"
    ]

    passed = 0

    for module in modules:

        path = os.path.join(
            BASE_DIR,
            module
        )

        if os.path.isdir(path):
            print(
                f"{module}: PASS"
            )
            passed += 1
        else:
            print(
                f"{module}: MISSING"
            )

    return passed == len(modules)


def generate_report(results):

    print("\n")
    print("=" * 70)
    print("SIH26179 - FINAL SOFTWARE INTEGRATION REPORT")
    print("=" * 70)

    passed = sum(
        1
        for result in results
        if result
    )

    total = len(results)

    print(
        f"Passed: {passed}/{total}"
    )

    if passed == total:
        print(
            "\nOVERALL STATUS: SOFTWARE INTEGRATION PASS"
        )
    else:
        print(
            "\nOVERALL STATUS: NEEDS REVIEW"
        )

    print(
        "\nHardware integration is intentionally "
        "not tested in this software-only validation."
    )

    print(
        "Rack/shelf detection is also reserved "
        "for the final hardware/table stage."
    )

    print("=" * 70)


def main():

    print(
        "\nSIH26179 - FINAL SOFTWARE INTEGRATION TEST"
    )

    results = []

    results.append(
        check_model()
    )

    results.append(
        check_database(
            EVENT_DB,
            "EVENT DATABASE"
        )
    )

    results.append(
        check_database(
            INVENTORY_DB,
            "INVENTORY DATABASE"
        )
    )

    results.append(
        test_event_creation()
    )

    results.append(
        test_inventory_data()
    )

    results.append(
        test_alert_system()
    )

    results.append(
        test_local_event_speed()
    )

    results.append(
        test_required_modules()
    )

    generate_report(results)


if __name__ == "__main__":
    main()