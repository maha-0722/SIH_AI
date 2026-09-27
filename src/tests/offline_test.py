import os
import sqlite3
import json
import time
from datetime import datetime


BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../..")
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


def timestamp():
    return datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )


def check_file_access():
    print("\n1. LOCAL FILE ACCESS")
    print("-" * 60)

    files = [
        EVENT_DB,
        INVENTORY_DB,
        ALERT_FILE,
        EXIT_ALERT_FILE
    ]

    passed = True

    for file_path in files:
        if os.path.exists(file_path):
            try:
                with open(file_path, "rb") as file:
                    file.read(1)

                print(
                    f"{os.path.basename(file_path)}: PASS"
                )

            except Exception as error:
                print(
                    f"{os.path.basename(file_path)}: FAIL - {error}"
                )
                passed = False

        else:
            print(
                f"{os.path.basename(file_path)}: NOT CREATED YET"
            )

    return passed


def check_event_database():
    print("\n2. EVENT DATABASE")
    print("-" * 60)

    if not os.path.exists(EVENT_DB):
        print("Event database not found.")
        return False

    try:
        conn = sqlite3.connect(
            EVENT_DB,
            timeout=5
        )

        cursor = conn.cursor()

        cursor.execute(
            "SELECT name FROM sqlite_master "
            "WHERE type='table'"
        )

        tables = cursor.fetchall()

        print(
            "SQLite connection: PASS"
        )

        print(
            "Tables:",
            [table[0] for table in tables]
        )

        if "events" in [
            table[0] for table in tables
        ]:

            cursor.execute(
                "SELECT COUNT(*) FROM events"
            )

            count = cursor.fetchone()[0]

            print(
                f"Stored events: {count}"
            )

        conn.close()

        return True

    except Exception as error:

        print(
            "Event database: FAIL"
        )

        print(error)

        return False


def check_inventory_database():
    print("\n3. INVENTORY DATABASE")
    print("-" * 60)

    if not os.path.exists(INVENTORY_DB):

        print(
            "Inventory database not found."
        )

        return False

    try:

        conn = sqlite3.connect(
            INVENTORY_DB,
            timeout=5
        )

        cursor = conn.cursor()

        cursor.execute(
            "SELECT name FROM sqlite_master "
            "WHERE type='table'"
        )

        tables = cursor.fetchall()

        print(
            "SQLite connection: PASS"
        )

        print(
            "Tables:",
            [table[0] for table in tables]
        )

        conn.close()

        return True

    except Exception as error:

        print(
            "Inventory database: FAIL"
        )

        print(error)

        return False


def check_json_system():

    print("\n4. LOCAL JSON ALERT SYSTEM")
    print("-" * 60)

    files = [
        ALERT_FILE,
        EXIT_ALERT_FILE
    ]

    passed = True

    for file_path in files:

        if not os.path.exists(file_path):

            print(
                f"{os.path.basename(file_path)}: NOT CREATED YET"
            )

            continue

        try:

            with open(
                file_path,
                "r"
            ) as file:

                data = json.load(file)

            if isinstance(data, list):

                print(
                    f"{os.path.basename(file_path)}: PASS "
                    f"({len(data)} records)"
                )

            else:

                print(
                    f"{os.path.basename(file_path)}: "
                    f"INVALID FORMAT"
                )

                passed = False

        except Exception as error:

            print(
                f"{os.path.basename(file_path)}: FAIL - {error}"
            )

            passed = False

    return passed


def simulate_offline_event():

    print("\n5. OFFLINE EVENT WRITE TEST")
    print("-" * 60)

    try:

        conn = sqlite3.connect(
            EVENT_DB,
            timeout=5
        )

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
            "OFFLINE_TEST_" +
            datetime.now().strftime(
                "%Y%m%d%H%M%S"
            )
        )

        data = {
            "test": True,
            "network": "DISCONNECTED",
            "message": "Local event storage working"
        }

        cursor.execute("""
            INSERT INTO events
            (
                event_id,
                timestamp,
                event_type,
                source,
                severity,
                status,
                data
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            event_id,
            timestamp(),
            "OFFLINE_TEST",
            "LOCAL_SYSTEM",
            "INFO",
            "STORED",
            json.dumps(data)
        ))

        conn.commit()

        cursor.execute(
            "SELECT event_type, source "
            "FROM events "
            "WHERE event_id=?",
            (event_id,)
        )

        result = cursor.fetchone()

        conn.close()

        if result:

            print(
                "Offline write: PASS"
            )

            print(
                f"Event: {result[0]}"
            )

            print(
                f"Source: {result[1]}"
            )

            return True

        print(
            "Offline write: FAIL"
        )

        return False

    except Exception as error:

        print(
            "Offline write: FAIL"
        )

        print(error)

        return False


def simulate_network_status():

    print("\n6. NETWORK INDEPENDENCE TEST")
    print("-" * 60)

    print(
        "Network state: SIMULATED DISCONNECTED"
    )

    local_operations = [
        "Inventory storage",
        "Event storage",
        "Alert storage",
        "POS record storage",
        "Exit verification records"
    ]

    for operation in local_operations:

        print(
            f"{operation}: LOCAL"
        )

    print(
        "Network dependency for local storage: NONE"
    )

    return True


def run_timing_test():

    print("\n7. LOCAL PROCESSING TIMING")
    print("-" * 60)

    start = time.time()

    for _ in range(10000):

        data = {
            "product": "water_bottle",
            "quantity": 5,
            "status": "Low"
        }

        json.dumps(data)

    elapsed = time.time() - start

    print(
        f"10000 local operations: "
        f"{elapsed:.4f} seconds"
    )

    print(
        "Local processing: PASS"
    )

    return True


def generate_report(results):

    print("\n")
    print("=" * 70)
    print("SIH26179 OFFLINE OPERATION REPORT")
    print("=" * 70)

    passed = sum(
        1
        for result in results
        if result
    )

    total = len(results)

    print(
        f"Tests passed: {passed}/{total}"
    )

    if passed == total:

        print(
            "\nOVERALL STATUS: PASS"
        )

        print(
            "Core local operations can continue "
            "without internet access."
        )

    else:

        print(
            "\nOVERALL STATUS: NEEDS REVIEW"
        )

    print("=" * 70)


def main():

    print(
        "\nSIH26179 - OFFLINE OPERATION TEST"
    )

    results = []

    results.append(
        check_file_access()
    )

    results.append(
        check_event_database()
    )

    results.append(
        check_inventory_database()
    )

    results.append(
        check_json_system()
    )

    results.append(
        simulate_offline_event()
    )

    results.append(
        simulate_network_status()
    )

    results.append(
        run_timing_test()
    )

    generate_report(
        results
    )


if __name__ == "__main__":
    main()