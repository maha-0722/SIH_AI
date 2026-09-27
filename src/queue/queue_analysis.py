from ultralytics import YOLO
import cv2
import time
from collections import deque

MODEL_PATH = r"C:\Users\Maha\Documents\SIH_AI\runs\detect\train-2\weights\best.pt"

model = YOLO(MODEL_PATH)

cap = cv2.VideoCapture(0)

QUEUE_X1 = 0.25
QUEUE_Y1 = 0.35
QUEUE_X2 = 0.75
QUEUE_Y2 = 0.95

SERVICE_RATE_WINDOW = 60
WAITING_HISTORY_SIZE = 20

queue_history = deque(maxlen=WAITING_HISTORY_SIZE)
service_times = deque(maxlen=SERVICE_RATE_WINDOW)

track_start = {}
track_previous_queue = {}

last_time = time.time()


def inside_queue(x, y, width, height):
    x1 = int(QUEUE_X1 * width)
    y1 = int(QUEUE_Y1 * height)
    x2 = int(QUEUE_X2 * width)
    y2 = int(QUEUE_Y2 * height)

    return x1 <= x <= x2 and y1 <= y <= y2


def calculate_service_rate():
    if len(service_times) < 2:
        return 0

    total_time = sum(service_times)

    if total_time <= 0:
        return 0

    return len(service_times) / (total_time / 60)


def estimate_waiting_time(queue_count, service_rate):
    if queue_count == 0:
        return 0

    if service_rate <= 0:
        return None

    return queue_count / service_rate


def queue_status(queue_count, waiting_time):
    if queue_count == 0:
        return "NO QUEUE"

    if waiting_time is None:
        return "SERVICE DATA INSUFFICIENT"

    if waiting_time <= 5:
        return "NORMAL"

    if waiting_time <= 10:
        return "MODERATE"

    return "QUEUE CONGESTION"


while True:
    ret, frame = cap.read()

    if not ret:
        break

    height, width = frame.shape[:2]

    results = model.track(
        frame,
        persist=True,
        tracker="bytetrack.yaml",
        imgsz=416,
        conf=0.35,
        verbose=False
    )

    result = results[0]

    queue_count = 0
    current_queue_ids = set()
    current_time = time.time()

    if (
        result.boxes is not None
        and result.boxes.id is not None
    ):
        boxes = result.boxes.xyxy.cpu().numpy()
        ids = result.boxes.id.cpu().numpy().astype(int)
        classes = result.boxes.cls.cpu().numpy().astype(int)
        confidences = result.boxes.conf.cpu().numpy()

        for box, track_id, cls, confidence in zip(
            boxes,
            ids,
            classes,
            confidences
        ):
            class_name = model.names[cls]

            if class_name != "person":
                continue

            x1, y1, x2, y2 = map(int, box)

            center_x = int((x1 + x2) / 2)
            center_y = int((y1 + y2) / 2)

            if track_id not in track_start:
                track_start[track_id] = current_time

            in_queue = inside_queue(
                center_x,
                center_y,
                width,
                height
            )

            if in_queue:
                queue_count += 1
                current_queue_ids.add(track_id)

                if track_id not in track_previous_queue:
                    track_previous_queue[track_id] = current_time

                queue_time = (
                    current_time -
                    track_previous_queue[track_id]
                )

                cv2.rectangle(
                    frame,
                    (x1, y1),
                    (x2, y2),
                    (0, 255, 255),
                    2
                )

                cv2.putText(
                    frame,
                    f"Queue ID:{track_id} {queue_time:.1f}s",
                    (x1, max(y1 - 10, 20)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 255, 255),
                    2
                )

            else:
                cv2.rectangle(
                    frame,
                    (x1, y1),
                    (x2, y2),
                    (0, 255, 0),
                    2
                )

    previous_queue_ids = set(track_previous_queue.keys())

    completed_ids = (
        previous_queue_ids -
        current_queue_ids
    )

    for track_id in completed_ids:
        if track_id in track_previous_queue:
            service_time = (
                current_time -
                track_previous_queue[track_id]
            )

            if service_time > 1:
                service_times.append(service_time)

            del track_previous_queue[track_id]

    service_rate = calculate_service_rate()

    waiting_time = estimate_waiting_time(
        queue_count,
        service_rate
    )

    status = queue_status(
        queue_count,
        waiting_time
    )

    queue_history.append(
        {
            "time": current_time,
            "count": queue_count
        }
    )

    queue_x1 = int(QUEUE_X1 * width)
    queue_y1 = int(QUEUE_Y1 * height)
    queue_x2 = int(QUEUE_X2 * width)
    queue_y2 = int(QUEUE_Y2 * height)

    cv2.rectangle(
        frame,
        (queue_x1, queue_y1),
        (queue_x2, queue_y2),
        (255, 0, 255),
        2
    )

    cv2.putText(
        frame,
        "QUEUE AREA",
        (queue_x1, max(queue_y1 - 10, 20)),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (255, 0, 255),
        2
    )

    cv2.putText(
        frame,
        f"Queue Count: {queue_count}",
        (10, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2
    )

    if service_rate > 0:
        cv2.putText(
            frame,
            f"Service Rate: {service_rate:.2f} persons/min",
            (10, 60),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2
        )
    else:
        cv2.putText(
            frame,
            "Service Rate: Collecting data",
            (10, 60),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2
        )

    if waiting_time is not None:
        cv2.putText(
            frame,
            f"Estimated Waiting Time: {waiting_time:.2f} min",
            (10, 90),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2
        )
    else:
        cv2.putText(
            frame,
            "Estimated Waiting Time: Insufficient data",
            (10, 90),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 255, 255),
            2
        )

    cv2.putText(
        frame,
        f"Status: {status}",
        (10, 120),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.65,
        (0, 0, 255) if status == "QUEUE CONGESTION" else (255, 255, 255),
        2
    )

    cv2.putText(
        frame,
        "SIH26179 - Queue Congestion Analysis",
        (10, height - 20),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.65,
        (255, 255, 255),
        2
    )

    cv2.imshow(
        "SIH Retail AI - Queue Analysis",
        frame
    )

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()