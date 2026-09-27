from ultralytics import YOLO
import cv2
import time

model = YOLO(r"C:\Users\Maha\Documents\SIH_AI\runs\detect\train-2\weights\best.pt")

cap = cv2.VideoCapture(0)

track_start = {}

while True:
    ret, frame = cap.read()
    if not ret:
        break

    results = model.track(
        frame,
        persist=True,
        tracker="bytetrack.yaml",
        imgsz=416,
        conf=0.25,
        verbose=False
    )

    result = results[0]
    current_ids = set()

    if result.boxes is not None and result.boxes.id is not None:
        boxes = result.boxes.xyxy.cpu().numpy()
        ids = result.boxes.id.cpu().numpy().astype(int)
        classes = result.boxes.cls.cpu().numpy().astype(int)
        confidences = result.boxes.conf.cpu().numpy()

        for box, track_id, cls, conf in zip(boxes, ids, classes, confidences):
            x1, y1, x2, y2 = map(int, box)
            current_ids.add(track_id)

            if track_id not in track_start:
                track_start[track_id] = time.time()

            dwell = time.time() - track_start[track_id]
            name = model.names[cls]

            label = f"{name} ID:{track_id} Dwell:{dwell:.1f}s"

            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(
                frame,
                label,
                (x1, max(y1 - 10, 20)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 0),
                2
            )

    cv2.putText(
        frame,
        f"Tracked Objects: {len(current_ids)}",
        (20, 35),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 255, 255),
        2
    )

    cv2.imshow("SIH Retail AI - YOLOv8 + ByteTrack", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()