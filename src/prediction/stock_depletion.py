from ultralytics import YOLO
import cv2
import time
from collections import deque

MODEL_PATH = r"C:\Users\Maha\Documents\SIH_AI\runs\detect\train-2\weights\best.pt"

model = YOLO(MODEL_PATH)

cap = cv2.VideoCapture(0)

SHELVES = {
    "Shelf 1": "water_bottle",
    "Shelf 2": "jinthaa_juice",
    "Shelf 3": "lifebuoy",
    "Shelf 4": "dhal"
}

LOW_STOCK = 3
SAMPLE_INTERVAL = 5
HISTORY_SIZE = 20

history = {
    shelf: deque(maxlen=HISTORY_SIZE)
    for shelf in SHELVES
}

last_sample_time = 0


def get_shelf(y_center, frame_height):
    ratio = y_center / frame_height

    if 0.00 <= ratio < 0.25:
        return "Shelf 1"

    if 0.25 <= ratio < 0.50:
        return "Shelf 2"

    if 0.50 <= ratio < 0.75:
        return "Shelf 3"

    if 0.75 <= ratio <= 1.00:
        return "Shelf 4"

    return None


def calculate_prediction(shelf):
    records = history[shelf]

    if len(records) < 2:
        return None, "INSUFFICIENT_HISTORY"

    first_time, first_quantity = records[0]
    last_time, last_quantity = records[-1]

    elapsed_hours = (last_time - first_time) / 3600

    if elapsed_hours <= 0:
        return None, "INSUFFICIENT_HISTORY"

    quantity_removed = first_quantity - last_quantity

    if quantity_removed <= 0:
        return None, "NO_DEPLETION"

    removal_rate = quantity_removed / elapsed_hours

    if removal_rate <= 0:
        return None, "NO_DEPLETION"

    hours_remaining = last_quantity / removal_rate

    return hours_remaining, removal_rate


while True:
    ret, frame = cap.read()

    if not ret:
        break

    height, width = frame.shape[:2]

    results = model.predict(
        frame,
        imgsz=416,
        conf=0.35,
        verbose=False
    )

    result = results[0]

    shelf_counts = {
        shelf: 0
        for shelf in SHELVES
    }

    if result.boxes is not None:
        boxes = result.boxes.xyxy.cpu().numpy()
        classes = result.boxes.cls.cpu().numpy().astype(int)
        confidences = result.boxes.conf.cpu().numpy()

        for box, cls, confidence in zip(
            boxes,
            classes,
            confidences
        ):
            x1, y1, x2, y2 = map(int, box)

            class_name = model.names[cls]

            center_x = (x1 + x2) / 2
            center_y = (y1 + y2) / 2

            shelf = get_shelf(center_y, height)

            if shelf is not None:
                expected_product = SHELVES[shelf]

                if class_name == expected_product:
                    shelf_counts[shelf] += 1

                    cv2.rectangle(
                        frame,
                        (x1, y1),
                        (x2, y2),
                        (0, 255, 0),
                        2
                    )

                    cv2.putText(
                        frame,
                        class_name,
                        (x1, max(y1 - 8, 15)),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        (0, 255, 0),
                        2
                    )

    current_time = time.time()

    if current_time - last_sample_time >= SAMPLE_INTERVAL:
        for shelf in SHELVES:
            quantity = shelf_counts[shelf]

            history[shelf].append(
                (current_time, quantity)
            )

        last_sample_time = current_time

    shelf_index = 0

    for shelf in SHELVES:
        quantity = shelf_counts[shelf]

        if quantity == 0:
            status = "EMPTY"
        elif quantity <= LOW_STOCK:
            status = "LOW STOCK"
        else:
            status = "NORMAL"

        prediction, rate = calculate_prediction(shelf)

        y = 35 + shelf_index * 95

        cv2.putText(
            frame,
            f"{shelf}: {quantity} | {status}",
            (10, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            (255, 255, 255),
            2
        )

        if isinstance(rate, float):
            cv2.putText(
                frame,
                f"Removal Rate: {rate:.2f} units/hour",
                (10, y + 25),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 255, 255),
                2
            )

            cv2.putText(
                frame,
                f"Estimated Empty: {prediction:.2f} hours",
                (10, y + 48),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 255, 255),
                2
            )

        else:
            cv2.putText(
                frame,
                f"Prediction: {rate}",
                (10, y + 25),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 255),
                2
            )

        shelf_index += 1

    cv2.putText(
        frame,
        "SIH26179 - Automatic Stock Depletion Prediction",
        (10, height - 20),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.65,
        (255, 255, 255),
        2
    )

    cv2.imshow(
        "SIH Retail AI - Stock Prediction",
        frame
    )

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()