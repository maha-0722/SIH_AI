import cv2
import time
import os
import sys
from collections import defaultdict, deque
from datetime import datetime

from ultralytics import YOLO


BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../..")
)

MODEL_PATH = os.path.join(
    BASE_DIR,
    "runs",
    "detect",
    "train-2",
    "weights",
    "best.pt"
)

model = YOLO(MODEL_PATH)

PRODUCTS = {
    "water_bottle": 1,
    "jinthaa_juice": 2,
    "lifebuoy": 3,
    "dhal": 4
}

SHELF_PRODUCTS = {
    1: "water_bottle",
    2: "jinthaa_juice",
    3: "lifebuoy",
    4: "dhal"
}

TRACKER = "bytetrack.yaml"

CONFIDENCE = 0.40

OUT_OF_STOCK_FRAMES = 15

HISTORY_SIZE = 20

SAMPLE_INTERVAL = 5


track_start_time = {}

track_last_seen = {}

track_positions = defaultdict(list)

stock_history = {
    1: deque(maxlen=HISTORY_SIZE),
    2: deque(maxlen=HISTORY_SIZE),
    3: deque(maxlen=HISTORY_SIZE),
    4: deque(maxlen=HISTORY_SIZE)
}

zero_stock_frames = {
    1: 0,
    2: 0,
    3: 0,
    4: 0
}

last_stock_sample = 0


def timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def get_shelf(y_center, frame_height):
    ratio = y_center / frame_height

    if ratio < 0.25:
        return 1
    elif ratio < 0.50:
        return 2
    elif ratio < 0.75:
        return 3
    else:
        return 4


def calculate_dwell(track_id):
    current_time = time.time()

    if track_id not in track_start_time:
        track_start_time[track_id] = current_time

    track_last_seen[track_id] = current_time

    return current_time - track_start_time[track_id]


def clean_old_tracks():
    current_time = time.time()

    expired = []

    for track_id, last_seen in track_last_seen.items():
        if current_time - last_seen > 10:
            expired.append(track_id)

    for track_id in expired:
        track_last_seen.pop(track_id, None)
        track_start_time.pop(track_id, None)
        track_positions.pop(track_id, None)


def calculate_heatmap_point(center_x, center_y, width, height):
    x = int((center_x / width) * 100)
    y = int((center_y / height) * 100)

    return x, y


def count_products(results, frame):
    shelf_counts = {
        1: defaultdict(int),
        2: defaultdict(int),
        3: defaultdict(int),
        4: defaultdict(int)
    }

    detections = []

    for result in results:
        if result.boxes is None:
            continue

        for box in result.boxes:
            confidence = float(box.conf[0])

            if confidence < CONFIDENCE:
                continue

            class_id = int(box.cls[0])
            class_name = model.names[class_id]

            if class_name == "person":
                continue

            x1, y1, x2, y2 = map(int, box.xyxy[0])

            center_x = (x1 + x2) // 2
            center_y = (y1 + y2) // 2

            shelf = get_shelf(
                center_y,
                frame.shape[0]
            )

            shelf_counts[shelf][class_name] += 1

            detections.append({
                "product": class_name,
                "shelf": shelf,
                "confidence": confidence,
                "bbox": [x1, y1, x2, y2]
            })

    return shelf_counts, detections


def analyze_inventory(shelf_counts):
    inventory_events = []

    for shelf, products in shelf_counts.items():
        expected_product = SHELF_PRODUCTS[shelf]

        quantity = products.get(
            expected_product,
            0
        )

        if quantity == 0:
            zero_stock_frames[shelf] += 1
        else:
            zero_stock_frames[shelf] = 0

        if quantity == 0:
            if zero_stock_frames[shelf] >= OUT_OF_STOCK_FRAMES:
                status = "Empty"
            else:
                status = "Checking"
        elif quantity <= 2:
            status = "Low"
        elif quantity <= 5:
            status = "Medium"
        else:
            status = "Full"

        inventory_events.append({
            "shelf": shelf,
            "product": expected_product,
            "quantity": quantity,
            "status": status
        })

        for product, count in products.items():
            if product != expected_product:
                inventory_events.append({
                    "shelf": shelf,
                    "product": product,
                    "quantity": count,
                    "status": "MISPLACED"
                })

    return inventory_events


def update_stock_history(inventory_events):
    global last_stock_sample

    current_time = time.time()

    if current_time - last_stock_sample < SAMPLE_INTERVAL:
        return

    last_stock_sample = current_time

    for event in inventory_events:
        shelf = event["shelf"]

        if event["status"] != "MISPLACED":
            stock_history[shelf].append(
                (
                    current_time,
                    event["quantity"]
                )
            )


def calculate_depletion():
    predictions = []

    for shelf in range(1, 5):

        history = list(stock_history[shelf])

        if len(history) < 2:
            predictions.append({
                "shelf": shelf,
                "status": "INSUFFICIENT_HISTORY",
                "hours_remaining": None
            })
            continue

        first_time, first_quantity = history[0]
        last_time, last_quantity = history[-1]

        elapsed_hours = (
            last_time - first_time
        ) / 3600

        quantity_removed = (
            first_quantity - last_quantity
        )

        if elapsed_hours <= 0:
            predictions.append({
                "shelf": shelf,
                "status": "INSUFFICIENT_HISTORY",
                "hours_remaining": None
            })
            continue

        if quantity_removed <= 0:
            predictions.append({
                "shelf": shelf,
                "status": "NO_DEPLETION",
                "hours_remaining": None
            })
            continue

        removal_rate = (
            quantity_removed /
            elapsed_hours
        )

        current_quantity = last_quantity

        if removal_rate <= 0:
            hours_remaining = None
        else:
            hours_remaining = (
                current_quantity /
                removal_rate
            )

        if hours_remaining is not None:

            if hours_remaining <= 0.5:
                status = "CRITICAL"

            elif hours_remaining <= 1:
                status = "LOW_STOCK"

            elif hours_remaining <= 2:
                status = "DEPLETION_WARNING"

            else:
                status = "NORMAL"

        else:
            status = "NORMAL"

        predictions.append({
            "shelf": shelf,
            "status": status,
            "hours_remaining": hours_remaining
        })

    return predictions


def analyze_queue(person_count):
    if person_count >= 8:
        status = "QUEUE CONGESTION"
    elif person_count >= 5:
        status = "MODERATE"
    else:
        status = "NORMAL"

    estimated_wait = 0

    if person_count > 0:
        estimated_wait = round(
            person_count * 1.5,
            2
        )

    return {
        "queue_count": person_count,
        "estimated_wait": estimated_wait,
        "status": status
    }


def analyze_people(results, frame):
    people = []

    for result in results:

        if result.boxes is None:
            continue

        if result.boxes.id is None:
            continue

        for box, track_id in zip(
            result.boxes,
            result.boxes.id
        ):

            confidence = float(box.conf[0])

            if confidence < CONFIDENCE:
                continue

            class_id = int(box.cls[0])
            class_name = model.names[class_id]

            if class_name != "person":
                continue

            track_id = int(track_id)

            x1, y1, x2, y2 = map(
                int,
                box.xyxy[0]
            )

            center_x = (x1 + x2) // 2
            center_y = (y1 + y2) // 2

            dwell = calculate_dwell(
                track_id
            )

            position = calculate_heatmap_point(
                center_x,
                center_y,
                frame.shape[1],
                frame.shape[0]
            )

            track_positions[track_id].append(
                position
            )

            people.append({
                "track_id": track_id,
                "dwell_time": round(dwell, 2),
                "position": position,
                "bbox": [x1, y1, x2, y2]
            })

    return people


def create_events(
    people,
    inventory_events,
    queue_data,
    depletion_data
):
    events = []

    for person in people:
        events.append({
            "timestamp": timestamp(),
            "type": "CUSTOMER_TRACKING",
            "source": "YOLO_BYTE_TRACK",
            "data": {
                "track_id": person["track_id"],
                "dwell_time": person["dwell_time"],
                "position": person["position"]
            }
        })

    for inventory in inventory_events:
        events.append({
            "timestamp": timestamp(),
            "type": "INVENTORY_UPDATE",
            "source": "YOLO_INVENTORY",
            "data": inventory
        })

    events.append({
        "timestamp": timestamp(),
        "type": "QUEUE_UPDATE",
        "source": "QUEUE_AI",
        "data": queue_data
    })

    for prediction in depletion_data:
        events.append({
            "timestamp": timestamp(),
            "type": "STOCK_PREDICTION",
            "source": "STOCK_PREDICTION_AI",
            "data": prediction
        })

    return events


def draw_inventory(frame, inventory_events):
    height, width = frame.shape[:2]

    for shelf in range(1, 5):

        y = int(
            height * shelf / 4
        )

        cv2.line(
            frame,
            (0, y),
            (width, y),
            (255, 255, 255),
            1
        )

    for event in inventory_events:

        shelf = event["shelf"]

        expected = SHELF_PRODUCTS[shelf]

        quantity = event["quantity"]

        status = event["status"]

        y = int(
            height * ((shelf - 1) / 4)
        ) + 30

        text = (
            f"Shelf {shelf}: "
            f"{expected} "
            f"Qty={quantity} "
            f"{status}"
        )

        cv2.putText(
            frame,
            text,
            (10, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (255, 255, 255),
            2
        )


def draw_people(frame, people):

    for person in people:

        x1, y1, x2, y2 = (
            person["bbox"]
        )

        track_id = person["track_id"]

        dwell = person["dwell_time"]

        cv2.rectangle(
            frame,
            (x1, y1),
            (x2, y2),
            (255, 255, 255),
            2
        )

        label = (
            f"ID {track_id} "
            f"Dwell {dwell:.1f}s"
        )

        cv2.putText(
            frame,
            label,
            (x1, y1 - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (255, 255, 255),
            2
        )


def draw_queue(frame, queue_data):

    text = (
        f"Queue: "
        f"{queue_data['queue_count']} | "
        f"Wait: "
        f"{queue_data['estimated_wait']} min | "
        f"{queue_data['status']}"
    )

    cv2.putText(
        frame,
        text,
        (10, frame.shape[0] - 20),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (255, 255, 255),
        2
    )


def display_events(events):

    print("\nAI PIPELINE EVENTS")
    print("=" * 100)

    for event in events:

        print(
            f"{event['timestamp']} | "
            f"{event['source']} | "
            f"{event['type']} | "
            f"{event['data']}"
        )


def run():

    print("\nSIH26179 - INTEGRATED AI PIPELINE")
    print("=" * 70)

    if not os.path.exists(MODEL_PATH):

        print(
            "\nModel not found:"
        )

        print(MODEL_PATH)

        return

    cap = cv2.VideoCapture(0)

    if not cap.isOpened():

        print(
            "\nCamera could not be opened."
        )

        return

    print(
        "\nIntegrated AI pipeline started."
    )

    print(
        "YOLOv8n + ByteTrack + "
        "Inventory + Queue + "
        "Dwell Time + Stock Prediction"
    )

    print(
        "Press Q to stop."
    )

    frame_counter = 0

    while True:

        ret, frame = cap.read()

        if not ret:
            break

        frame_counter += 1

        results = model.track(
            frame,
            persist=True,
            tracker=TRACKER,
            verbose=False
        )

        people = analyze_people(
            results,
            frame
        )

        shelf_counts, detections = count_products(
            results,
            frame
        )

        inventory_events = analyze_inventory(
            shelf_counts
        )

        update_stock_history(
            inventory_events
        )

        depletion_data = calculate_depletion()

        queue_data = analyze_queue(
            len(people)
        )

        events = create_events(
            people,
            inventory_events,
            queue_data,
            depletion_data
        )

        draw_inventory(
            frame,
            inventory_events
        )

        draw_people(
            frame,
            people
        )

        draw_queue(
            frame,
            queue_data
        )

        cv2.imshow(
            "SIH26179 - Integrated AI Pipeline",
            frame
        )

        if frame_counter % 30 == 0:

            print(
                f"\nFrame: {frame_counter}"
            )

            print(
                f"People: {len(people)}"
            )

            print(
                f"Queue: {queue_data['queue_count']}"
            )

            for inventory in inventory_events:

                if inventory["status"] != "MISPLACED":

                    print(
                        f"Shelf {inventory['shelf']} | "
                        f"{inventory['product']} | "
                        f"Qty={inventory['quantity']} | "
                        f"{inventory['status']}"
                    )

            for prediction in depletion_data:

                print(
                    f"Stock Prediction | "
                    f"Shelf {prediction['shelf']} | "
                    f"{prediction['status']}"
                )

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

        clean_old_tracks()

    cap.release()

    cv2.destroyAllWindows()

    print(
        "\nIntegrated AI pipeline stopped."
    )


if __name__ == "__main__":
    run()