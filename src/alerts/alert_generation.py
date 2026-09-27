import json
import time


def create_alert(
    alert_type,
    message,
    severity,
    source,
    data=None
):
    return {
        "alert_id": f"ALERT_{int(time.time() * 1000)}",
        "type": alert_type,
        "message": message,
        "severity": severity,
        "source": source,
        "data": data or {},
        "timestamp": time.time()
    }


def low_stock_alert(product, quantity):
    return create_alert(
        "LOW_STOCK",
        f"{product} stock is low",
        "MEDIUM",
        "INVENTORY",
        {
            "product": product,
            "quantity": quantity
        }
    )


def out_of_stock_alert(product):
    return create_alert(
        "OUT_OF_STOCK",
        f"{product} is out of stock",
        "HIGH",
        "INVENTORY",
        {
            "product": product
        }
    )


def misplaced_product_alert(
    product,
    expected_shelf,
    detected_shelf
):
    return create_alert(
        "MISPLACED_PRODUCT",
        f"{product} detected in wrong shelf",
        "MEDIUM",
        "PLANOGRAM",
        {
            "product": product,
            "expected_shelf": expected_shelf,
            "detected_shelf": detected_shelf
        }
    )


def queue_congestion_alert(
    queue_count,
    waiting_time
):
    return create_alert(
        "QUEUE_CONGESTION",
        "Queue congestion detected",
        "HIGH",
        "QUEUE",
        {
            "queue_count": queue_count,
            "waiting_time_minutes": waiting_time
        }
    )


def depletion_warning_alert(
    product,
    hours_remaining
):
    return create_alert(
        "DEPLETION_WARNING",
        f"{product} may become empty soon",
        "MEDIUM",
        "STOCK_PREDICTION",
        {
            "product": product,
            "hours_remaining": hours_remaining
        }
    )


def anomaly_alert(
    score,
    features
):
    return create_alert(
        "ANOMALY",
        "Unusual operational pattern detected",
        "MEDIUM",
        "ANOMALY_DETECTION",
        {
            "score": score,
            "features": features
        }
    )


def refill_task_alert(
    task_id,
    product,
    shelf
):
    return create_alert(
        "REFILL_TASK",
        f"Refill required for {product}",
        "HIGH",
        "STAFF_ASSIGNMENT",
        {
            "task_id": task_id,
            "product": product,
            "shelf": shelf
        }
    )


def save_alert(alert):
    filename = "alerts.json"

    try:
        with open(
            filename,
            "r",
            encoding="utf-8"
        ) as file:
            alerts = json.load(file)
    except (
        FileNotFoundError,
        json.JSONDecodeError
    ):
        alerts = []

    alerts.append(alert)

    with open(
        filename,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            alerts,
            file,
            indent=4
        )


def process_alert(alert):
    print("\nALERT GENERATED")
    print("-" * 45)
    print("Type:", alert["type"])
    print("Severity:", alert["severity"])
    print("Message:", alert["message"])
    print("Source:", alert["source"])
    print("Data:", alert["data"])

    save_alert(alert)


def generate_test_alerts():

    alerts = []

    alerts.append(
        low_stock_alert(
            "water_bottle",
            2
        )
    )

    alerts.append(
        out_of_stock_alert(
            "jinthaa_juice"
        )
    )

    alerts.append(
        misplaced_product_alert(
            "dhal",
            "Shelf 4",
            "Shelf 2"
        )
    )

    alerts.append(
        queue_congestion_alert(
            8,
            12.5
        )
    )

    alerts.append(
        depletion_warning_alert(
            "lifebuoy",
            1.8
        )
    )

    alerts.append(
        anomaly_alert(
            -0.21,
            {
                "people_count": 18,
                "queue_count": 9,
                "stock_change": 6,
                "dwell_time": 42
            }
        )
    )

    alerts.append(
        refill_task_alert(
            "REFILL_SHELF_1",
            "water_bottle",
            "Shelf 1"
        )
    )

    for alert in alerts:
        process_alert(alert)


if __name__ == "__main__":
    print("SIH26179 - Alert Generation System")
    generate_test_alerts()