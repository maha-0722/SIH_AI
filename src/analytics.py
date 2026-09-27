from ultralytics import YOLO
import cv2
import numpy as np
import time

model = YOLO(r"C:\Users\Maha\Documents\SIH_AI\runs\detect\train-2\weights\best.pt")

cap = cv2.VideoCapture(0)

heatmap = None
queue_roi = None

while True:
    ret, frame = cap.read()
    if not ret:
        break

    h, w = frame.shape[:2]

    if heatmap is None:
        heatmap = np.zeros((h, w), dtype=np.float32)

    results = model.track(
        frame,
        persist=True,
        tracker="bytetrack.yaml",
        imgsz=416,
        conf=0.25,
        verbose=False
    )

    result = results[0]
    person_count = 0
    queue_count = 0

    if result.boxes is not None:
        boxes = result.boxes.xyxy.cpu().numpy()
        classes = result.boxes.cls.cpu().numpy().astype(int)

        for box, cls in zip(boxes, classes):
            if model.names[cls] != "person":
                continue

            person_count += 1

            x1, y1, x2, y2 = map(int, box)

            cx = (x1 + x2) // 2
            cy = (y1 + y2) // 2

            heatmap[cy, cx] += 1

            if queue_roi is not None:
                qx1, qy1, qx2, qy2 = queue_roi

                if qx1 < cx < qx2 and qy1 < cy < qy2:
                    queue_count += 1
                    cv2.rectangle(
                        frame,
                        (x1, y1),
                        (x2, y2),
                        (0, 0, 255),
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
            else:
                cv2.rectangle(
                    frame,
                    (x1, y1),
                    (x2, y2),
                    (0, 255, 0),
                    2
                )

    heat = cv2.normalize(heatmap, None, 0, 255, cv2.NORM_MINMAX)
    heat = heat.astype(np.uint8)
    heat = cv2.applyColorMap(heat, cv2.COLORMAP_JET)

    output = cv2.addWeighted(frame, 0.7, heat, 0.3, 0)

    if queue_roi is not None:
        qx1, qy1, qx2, qy2 = queue_roi
        cv2.rectangle(
            output,
            (qx1, qy1),
            (qx2, qy2),
            (255, 255, 0),
            2
        )
        cv2.putText(
            output,
            "QUEUE AREA",
            (qx1, qy1 - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 0),
            2
        )

    cv2.putText(
        output,
        f"People Count: {person_count}",
        (20, 35),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (255, 255, 255),
        2
    )

    cv2.putText(
        output,
        f"Queue Count: {queue_count}",
        (20, 70),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (255, 255, 255),
        2
    )

    cv2.imshow("SIH Retail - Heatmap + Queue Analytics", output)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()