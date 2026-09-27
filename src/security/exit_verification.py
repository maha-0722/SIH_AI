import json
import time
import os

POS_FILE = "pos_paid_items.json"
EXIT_FILE = "exit_events.json"
ALERT_FILE = "exit_alerts.json"


def load_data(filename):
    if not os.path.exists(filename):
        return []

    try:
        with open(
            filename,
            "r",
            encoding="utf-8"
        ) as file:
            return json.load(file)

    except json.JSONDecodeError:
        return []


def save_data(filename, data):
    with open(
        filename,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            data,
            file,
            indent=4
        )


def register_paid_item(
    tag_id,
    product,
    quantity=1
):
    paid_items = load_data(POS_FILE)

    paid_items.append({
        "tag_id": tag_id,
        "product": product,
        "quantity": quantity,
        "payment_status": "PAID",
        "timestamp": time.time()
    })

    save_data(
        POS_FILE,
        paid_items
    )


def get_payment_status(tag_id):
    paid_items = load_data(POS_FILE)

    for item in paid_items:
        if item["tag_id"] == tag_id:
            return item["payment_status"]

    return "UNRESOLVED"


def record_exit_event(
    tag_id,
    product,
    outward_crossing=True
):
    exit_events = load_data(EXIT_FILE)

    event = {
        "event_id": f"EXIT_{int(time.time() * 1000)}",
        "tag_id": tag_id,
        "product": product,
        "outward_crossing": outward_crossing,
        "timestamp": time.time()
    }

    exit_events.append(event)

    save_data(
        EXIT_FILE,
        exit_events
    )

    return event


def verify_exit(event):
    if not event["outward_crossing"]:
        return {
            "status": "NO_EXIT",
            "message": "Outward crossing not detected"
        }

    payment_status = get_payment_status(
        event["tag_id"]
    )

    if payment_status == "PAID":
        return {
            "status": "PAID",
            "message": "Item payment verified"
        }

    return {
        "status": "REVIEW_REQUIRED",
        "message": "Possible unpaid item - staff verification required"
    }


def create_security_alert(
    event,
    verification
):
    if verification["status"] != "REVIEW_REQUIRED":
        return None

    alerts = load_data(ALERT_FILE)

    alert = {
        "alert_id": f"SECURITY_{int(time.time() * 1000)}",
        "type": "POSSIBLE_UNPAID_ITEM",
        "severity": "HIGH",
        "tag_id": event["tag_id"],
        "product": event["product"],
        "message": verification["message"],
        "event_time": event["timestamp"],
        "security_review_required": True
    }

    alerts.append(alert)

    save_data(
        ALERT_FILE,
        alerts
    )

    return alert


def process_exit(
    tag_id,
    product,
    outward_crossing=True
):
    event = record_exit_event(
        tag_id,
        product,
        outward_crossing
    )

    verification = verify_exit(event)

    alert = create_security_alert(
        event,
        verification
    )

    print("\nEXIT VERIFICATION")
    print("-" * 50)
    print("Tag ID:", tag_id)
    print("Product:", product)
    print("Outward Crossing:", outward_crossing)
    print("Payment Status:", verification["status"])
    print("Message:", verification["message"])

    if alert:
        print("\nSECURITY ALERT")
        print("-" * 50)
        print("Type:", alert["type"])
        print("Severity:", alert["severity"])
        print("Message:", alert["message"])


def run_demo():

    print("SIH26179 - RFID/EAS-POS-Camera Exit Verification")

    register_paid_item(
        "RFID001",
        "water_bottle"
    )

    register_paid_item(
        "RFID002",
        "jinthaa_juice"
    )

    print("\nPaid item test:")
    process_exit(
        "RFID001",
        "water_bottle",
        True
    )

    print("\nUnresolved item test:")
    process_exit(
        "RFID999",
        "lifebuoy",
        True
    )

    print("\nNo outward crossing test:")
    process_exit(
        "RFID002",
        "jinthaa_juice",
        False
    )


if __name__ == "__main__":
    run_demo()