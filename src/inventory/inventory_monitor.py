from ultralytics import YOLO
import cv2
import time

MODEL_PATH = r"C:\Users\Maha\Documents\SIH_AI\runs\detect\train-2\weights\best.pt"

model = YOLO(MODEL_PATH)

cap = cv2.VideoCapture(0)

SHELVES = {
    "Shelf 1": {
        "product": "water_bottle",
        "y1": 0.00,
        "y2": 0.25,
        "expected_quantity": 10
    },
    "Shelf 2": {
        "product": "jinthaa_juice",
        "y1": 0.25,
        "y2": 0.50,
        "expected_quantity": 10
    },
    "Shelf 3": {
        "product": "lifebuoy",
        "y1": 0.50,
        "y2": 0.75,
        "expected_quantity": 10
    },
    "Shelf 4": {
        "product": "dhal",
        "y1": 0.75,
        "y2": 1.00,
        "expected_quantity": 10
    }
}

LOW_STOCK_RATIO = 0.30
OUT_OF_STOCK_FRAMES = 15

previous_status = {}
empty_frame_count = {}

for shelf in SHELVES:
    previous_status[shelf] = "UNKNOWN"
    empty_frame_count[shelf] = 0


def get_shelf(y_center, frame_height):
    relative_y = y_center / frame_height

    for shelf_name, shelf_data in SHELVES.items():
        if shelf_data["y1"] <= relative_y < shelf_data["y2"]:
            return shelf_name

    return None


def get_stock_status(quantity, expected_quantity):
    if quantity <= 0:
        return "EMPTY"

    ratio = quantity / expected_quantity

    if ratio <= LOW_STOCK_RATIO:
        return "LOW"

    if ratio <= 0.60:
        return "MEDIUM"

    return "FULL"


def fuse_inventory(camera_count, sensor_quantity):
    if sensor_quantity is None:
        return {
            "quantity": camera_count,
            "source": "CAMERA",
            "confidence": "VISIBLE_ONLY"
        }

    difference = abs(camera_count - sensor_quantity)

    if difference <= 1:
        return {
            "quantity": sensor_quantity,
            "source": "CAMERA_SENSOR",
            "confidence": "HIGH"
        }

    return {
        "quantity": sensor_quantity,
        "source": "SENSOR",
        "confidence": "CHECK_REQUIRED"
    }


def draw_shelf(frame, shelf_name, shelf_data, quantity, status):
    height = frame.shape[0]
    width = frame.shape[1]

    y1 = int(shelf_data["y1"] * height)
    y2 = int(shelf_data["y2"] * height)

    cv2.rectangle(
        frame,
        (0, y1),
        (width, y2),
        (255, 255, 0),
        2
    )

    text = f"{shelf_name} | Expected: {shelf_data['product']} | Qty: {quantity} | {status}"

    cv2.putText(
        frame,
        text,
        (10, max(y1 + 25, 25)),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (255, 255, 255),
        2
    )


while True:
    ret, frame = cap.read()

    if not ret:
        break

    frame_height, frame_width = frame.shape[:2]

    results = model.predict(
        frame,
        imgsz=416,
        conf=0.35,
        verbose=False
    )

    result = results[0]

    shelf_objects = {
        shelf: []
        for shelf in SHELVES
    }

    if result.boxes is not None:
        boxes = result.boxes.xyxy.cpu().numpy()
        classes = result.boxes.cls.cpu().numpy().astype(int)
        confidences = result.boxes.conf.cpu().numpy()

        for box, cls, confidence in zip(boxes, classes, confidences):
            x1, y1, x2, y2 = map(int, box)

            class_name = model.names[cls]

            center_x = (x1 + x2) / 2
            center_y = (y1 + y2) / 2

            shelf_name = get_shelf(center_y, frame_height)

            if shelf_name is None:
                continue

            shelf_objects[shelf_name].append({
                "class": class_name,
                "confidence": float(confidence),
                "box": (x1, y1, x2, y2)
            })

            cv2.rectangle(
                frame,
                (x1, y1),
                (x2, y2),
                (0, 255, 0),
                2
            )

            cv2.putText(
                frame,
                f"{class_name} {confidence:.2f}",
                (x1, max(y1 - 8, 15)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 0),
                2
            )

    for shelf_name, shelf_data in SHELVES.items():

        expected_product = shelf_data["product"]

        objects = shelf_objects[shelf_name]

        camera_count = 0
        misplaced_count = 0

        for obj in objects:
            if obj["class"] == expected_product:
                camera_count += 1
            else:
                misplaced_count += 1

        sensor_quantity = None

        inventory = fuse_inventory(
            camera_count,
            sensor_quantity
        )

        quantity = inventory["quantity"]

        status = get_stock_status(
            quantity,
            shelf_data["expected_quantity"]
        )

        if camera_count == 0:
            empty_frame_count[shelf_name] += 1
        else:
            empty_frame_count[shelf_name] = 0

        out_of_stock = (
            empty_frame_count[shelf_name] >= OUT_OF_STOCK_FRAMES
        )

        if out_of_stock:
            status = "OUT_OF_STOCK"

        if misplaced_count > 0:
            status_text = "MISPLACED_PRODUCT"
        else:
            status_text = status

        draw_shelf(
            frame,
            shelf_name,
            shelf_data,
            quantity,
            status_text
        )

        if misplaced_count > 0:
            cv2.putText(
                frame,
                f"{shelf_name}: {misplaced_count} misplaced product(s)",
                (10, min(
                    int(shelf_data["y2"] * frame_height) - 10,
                    frame_height - 10
                )),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                (0, 0, 255),
                2
            )

        if out_of_stock:
            cv2.putText(
                frame,
                f"ALERT: {shelf_name} OUT OF STOCK",
                (frame_width - 330, 30 + list(SHELVES.keys()).index(shelf_name) * 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                (0, 0, 255),
                2
            )

        previous_status[shelf_name] = status

    cv2.putText(
        frame,
        "SIH26179 - Inventory & Planogram Monitor",
        (10, frame_height - 20),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.65,
        (255, 255, 255),
        2
    )

    cv2.imshow(
        "SIH Retail AI - Inventory Monitoring",
        frame
    )

    key = cv2.waitKey(1) & 0xFF

    if key == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()