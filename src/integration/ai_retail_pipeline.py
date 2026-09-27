import cv2
from ultralytics import YOLO
from collections import defaultdict
import time

MODEL_PATH = "runs/detect/train-2/weights/best.pt"

model = YOLO(MODEL_PATH)

SHELF_CONFIG = {
    "water_bottle": (0.00, 0.25),
    "jinthaa_juice": (0.25, 0.50),
    "lifebuoy": (0.50, 0.75),
    "dhal": (0.75, 1.00)
}

ZERO_FRAME_LIMIT = 15

zero_frames = defaultdict(int)
track_start_time = {}
track_last_seen = {}

def get_shelf(y_center, frame_height):
    ratio = y_center / frame_height

    for product, (start, end) in SHELF_CONFIG.items():
        if start <= ratio < end:
            return product

    return None

def process_detections(result, frame):
    detections = []
    product_counts = defaultdict(int)
    people_count = 0

    if result.boxes is None:
        return detections, product_counts, people_count

    for box in result.boxes:
        cls_id = int(box.cls[0])
        confidence = float(box.conf[0])

        if confidence < 0.5:
            continue

        class_name = model.names[cls_id]

        x1, y1, x2, y2 = map(
            int,
            box.xyxy[0].tolist()
        )

        center_x = (x1 + x2) // 2
        center_y = (y1 + y2) // 2

        track_id = None

        if box.id is not None:
            track_id = int(box.id[0])

        if class_name == "person":
            people_count += 1

            if track_id is not None:
                if track_id not in track_start_time:
                    track_start_time[track_id] = time.time()

                track_last_seen[track_id] = time.time()

            detections.append({
                "type": "person",
                "track_id": track_id,
                "confidence": confidence
            })

        elif class_name in SHELF_CONFIG:
            product = get_shelf(
                center_y,
                frame.shape[0]
            )

            if product == class_name:
                product_counts[class_name] += 1
                placement = "CORRECT"
            else:
                placement = "MISPLACED"

            detections.append({
                "type": "product",
                "product": class_name,
                "shelf": product,
                "placement": placement,
                "confidence": confidence
            })

        cv2.rectangle(
            frame,
            (x1, y1),
            (x2, y2),
            (255, 255, 255),
            2
        )

        label = f"{class_name} {confidence:.2f}"

        if track_id is not None:
            label += f" ID:{track_id}"

        cv2.putText(
            frame,
            label,
            (x1, max(y1 - 10, 20)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (255, 255, 255),
            2
        )

    return detections, product_counts, people_count

def update_stock_status(product_counts):
    status = {}

    for product in SHELF_CONFIG:
        quantity = product_counts.get(product, 0)

        if quantity == 0:
            zero_frames[product] += 1
        else:
            zero_frames[product] = 0

        if zero_frames[product] >= ZERO_FRAME_LIMIT:
            status[product] = "OUT_OF_STOCK"
        elif quantity <= 2:
            status[product] = "LOW_STOCK"
        else:
            status[product] = "NORMAL"

    return status

def calculate_dwell_times():
    current_time = time.time()
    dwell_times = {}

    for track_id, start_time in track_start_time.items():
        if track_id in track_last_seen:
            dwell_times[track_id] = round(
                current_time - start_time,
                2
            )

    return dwell_times

def main():
    print("\nSIH26179 - AI RETAIL PIPELINE")
    print("=" * 60)

    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Could not open camera.")
        return

    print("Camera started.")
    print("Press Q to stop.\n")

    while True:
        ret, frame = cap.read()

        if not ret:
            print("Camera frame error.")
            break

        results = model.track(
            frame,
            persist=True,
            tracker="bytetrack.yaml",
            verbose=False
        )

        result = results[0]

        detections, product_counts, people_count = process_detections(
            result,
            frame
        )

        stock_status = update_stock_status(
            product_counts
        )

        dwell_times = calculate_dwell_times()

        cv2.putText(
            frame,
            f"People: {people_count}",
            (20, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2
        )

        y = 60

        for product in SHELF_CONFIG:
            quantity = product_counts.get(
                product,
                0
            )

            status = stock_status[product]

            text = f"{product}: {quantity} | {status}"

            cv2.putText(
                frame,
                text,
                (20, y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                (255, 255, 255),
                2
            )

            y += 25

        y += 10

        for track_id, dwell in dwell_times.items():
            text = f"ID {track_id} Dwell: {dwell:.1f}s"

            cv2.putText(
                frame,
                text,
                (20, y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 255, 255),
                2
            )

            y += 22

        cv2.imshow(
            "SIH26179 AI Retail Pipeline",
            frame
        )

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()

    print("\nAI pipeline stopped.")

if __name__ == "__main__":
    main()