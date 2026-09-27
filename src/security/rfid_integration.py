import json
import os
from datetime import datetime


BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../..")
)

POS_FILE = os.path.join(
    BASE_DIR,
    "pos_paid_items.json"
)

RFID_FILE = os.path.join(
    BASE_DIR,
    "rfid_events.json"
)

ALERT_FILE = os.path.join(
    BASE_DIR,
    "rfid_security_alerts.json"
)


def load_json(filename, default):
    if not os.path.exists(filename):
        return default

    try:
        with open(filename, "r") as file:
            return json.load(file)
    except:
        return default


def save_json(filename, data):
    with open(filename, "w") as file:
        json.dump(
            data,
            file,
            indent=4
        )


def timestamp():
    return datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )


def register_paid_item(
    tag_id,
    product,
    quantity=1,
    transaction_id=None
):
    paid_items = load_json(
        POS_FILE,
        []
    )

    if transaction_id is None:
        transaction_id = (
            "TXN-" +
            datetime.now().strftime(
                "%Y%m%d%H%M%S"
            )
        )

    item = {
        "tag_id": tag_id,
        "product": product,
        "quantity": quantity,
        "transaction_id": transaction_id,
        "paid": True,
        "timestamp": timestamp()
    }

    paid_items.append(item)

    save_json(
        POS_FILE,
        paid_items
    )

    return item


def get_payment_status(tag_id):
    paid_items = load_json(
        POS_FILE,
        []
    )

    for item in paid_items:
        if item["tag_id"] == tag_id:
            if item.get("paid") is True:
                return "PAID"

    return "UNRESOLVED"


def record_rfid_event(
    tag_id,
    product,
    reader_location,
    outward_crossing
):
    events = load_json(
        RFID_FILE,
        []
    )

    event = {
        "event_id": len(events) + 1,
        "timestamp": timestamp(),
        "tag_id": tag_id,
        "product": product,
        "reader_location": reader_location,
        "outward_crossing": outward_crossing
    }

    events.append(event)

    save_json(
        RFID_FILE,
        events
    )

    return event


def create_security_alert(
    tag_id,
    product,
    payment_status,
    reader_location
):
    alerts = load_json(
        ALERT_FILE,
        []
    )

    alert = {
        "alert_id": len(alerts) + 1,
        "timestamp": timestamp(),
        "type": "POSSIBLE_UNPAID_ITEM",
        "tag_id": tag_id,
        "product": product,
        "payment_status": payment_status,
        "reader_location": reader_location,
        "action": "STAFF_VERIFICATION_REQUIRED"
    }

    alerts.append(alert)

    save_json(
        ALERT_FILE,
        alerts
    )

    return alert


def verify_exit(
    tag_id,
    product,
    reader_location,
    outward_crossing
):
    payment_status = get_payment_status(
        tag_id
    )

    event = record_rfid_event(
        tag_id=tag_id,
        product=product,
        reader_location=reader_location,
        outward_crossing=outward_crossing
    )

    result = {
        "tag_id": tag_id,
        "product": product,
        "payment_status": payment_status,
        "outward_crossing": outward_crossing,
        "security_alert": False,
        "event": event
    }

    if (
        outward_crossing
        and payment_status == "UNRESOLVED"
    ):
        alert = create_security_alert(
            tag_id=tag_id,
            product=product,
            payment_status=payment_status,
            reader_location=reader_location
        )

        result["security_alert"] = True
        result["alert"] = alert

    return result


def display_result(result):
    print("\nEXIT VERIFICATION")
    print("=" * 70)

    print(
        f"Tag ID          : {result['tag_id']}"
    )

    print(
        f"Product          : {result['product']}"
    )

    print(
        f"Payment Status   : {result['payment_status']}"
    )

    print(
        f"Outward Crossing : {result['outward_crossing']}"
    )

    if result["security_alert"]:
        print(
            "\nALERT: POSSIBLE UNPAID ITEM"
        )

        print(
            "Action: STAFF VERIFICATION REQUIRED"
        )
    else:
        print(
            "\nNo security alert generated."
        )


def demo():
    print(
        "\nSIH26179 - RFID / POS EXIT VERIFICATION"
    )

    print("=" * 70)

    paid_item = register_paid_item(
        tag_id="RFID001",
        product="water_bottle",
        quantity=1,
        transaction_id="TXN1001"
    )

    print(
        "\nPaid item registered:"
    )

    print(paid_item)

    result1 = verify_exit(
        tag_id="RFID001",
        product="water_bottle",
        reader_location="STORE_EXIT",
        outward_crossing=True
    )

    display_result(result1)

    result2 = verify_exit(
        tag_id="RFID999",
        product="jinthaa_juice",
        reader_location="STORE_EXIT",
        outward_crossing=True
    )

    display_result(result2)

    result3 = verify_exit(
        tag_id="RFID888",
        product="lifebuoy",
        reader_location="STORE_EXIT",
        outward_crossing=False
    )

    display_result(result3)

    print(
        "\nRFID verification completed."
    )


if __name__ == "__main__":
    demo()