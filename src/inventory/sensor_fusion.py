def sensor_fusion(camera_quantity, sensor_quantity):
    if sensor_quantity is None:
        return {
            "quantity": camera_quantity,
            "source": "CAMERA",
            "status": "VISIBLE_ONLY"
        }

    difference = abs(camera_quantity - sensor_quantity)

    if difference <= 1:
        return {
            "quantity": sensor_quantity,
            "source": "CAMERA_SENSOR",
            "status": "CONFIRMED"
        }

    return {
        "quantity": sensor_quantity,
        "source": "SENSOR",
        "status": "UNCERTAIN_CHECK_REQUIRED"
    }


def get_stock_status(quantity, capacity):
    if quantity <= 0:
        return "EMPTY"

    ratio = quantity / capacity

    if ratio <= 0.30:
        return "LOW"

    if ratio <= 0.60:
        return "MEDIUM"

    return "FULL"


def process_shelf(
    shelf_name,
    camera_quantity,
    sensor_quantity,
    capacity
):
    result = sensor_fusion(
        camera_quantity,
        sensor_quantity
    )

    stock_status = get_stock_status(
        result["quantity"],
        capacity
    )

    return {
        "shelf": shelf_name,
        "quantity": result["quantity"],
        "source": result["source"],
        "confidence": result["status"],
        "stock_status": stock_status
    }


if __name__ == "__main__":

    shelves = [
        process_shelf(
            "Shelf 1",
            camera_quantity=8,
            sensor_quantity=8,
            capacity=10
        ),
        process_shelf(
            "Shelf 2",
            camera_quantity=5,
            sensor_quantity=5,
            capacity=10
        ),
        process_shelf(
            "Shelf 3",
            camera_quantity=2,
            sensor_quantity=None,
            capacity=10
        ),
        process_shelf(
            "Shelf 4",
            camera_quantity=4,
            sensor_quantity=7,
            capacity=10
        )
    ]

    for shelf in shelves:
        print(shelf)