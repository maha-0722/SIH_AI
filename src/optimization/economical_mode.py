import cv2
import time
import os
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

CONFIDENCE = 0.40

NORMAL_INTERVAL = 0.0
ECONOMICAL_INTERVAL = 0.20

NORMAL_IMGSZ = 416
ECONOMICAL_IMGSZ = 320


def run_mode(
    cap,
    mode,
    duration=20
):
    if mode == "NORMAL":
        interval = NORMAL_INTERVAL
        imgsz = NORMAL_IMGSZ
    else:
        interval = ECONOMICAL_INTERVAL
        imgsz = ECONOMICAL_IMGSZ

    start_time = time.time()
    last_inference = 0

    frame_count = 0
    inference_count = 0

    inference_times = []

    while time.time() - start_time < duration:

        ret, frame = cap.read()

        if not ret:
            break

        frame_count += 1

        current_time = time.time()

        if current_time - last_inference < interval:
            cv2.putText(
                frame,
                f"{mode} - waiting",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2
            )

            cv2.imshow(
                "SIH26179 - Economical Processing",
                frame
            )

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

            continue

        inference_start = time.time()

        results = model(
            frame,
            imgsz=imgsz,
            conf=CONFIDENCE,
            verbose=False
        )

        inference_end = time.time()

        inference_time = (
            inference_end -
            inference_start
        )

        inference_times.append(
            inference_time
        )

        inference_count += 1

        last_inference = current_time

        detection_count = 0

        for result in results:

            if result.boxes is None:
                continue

            detection_count += len(
                result.boxes
            )

            for box in result.boxes:

                x1, y1, x2, y2 = map(
                    int,
                    box.xyxy[0]
                )

                class_id = int(
                    box.cls[0]
                )

                confidence = float(
                    box.conf[0]
                )

                class_name = model.names[
                    class_id
                ]

                cv2.rectangle(
                    frame,
                    (x1, y1),
                    (x2, y2),
                    (255, 255, 255),
                    2
                )

                cv2.putText(
                    frame,
                    f"{class_name} {confidence:.2f}",
                    (x1, max(y1 - 8, 20)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (255, 255, 255),
                    2
                )

        cv2.putText(
            frame,
            f"Mode: {mode}",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2
        )

        cv2.putText(
            frame,
            f"Detections: {detection_count}",
            (10, 60),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2
        )

        cv2.imshow(
            "SIH26179 - Economical Processing",
            frame
        )

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    if inference_count == 0:
        return {
            "mode": mode,
            "frames": frame_count,
            "inferences": 0,
            "average_inference": 0,
            "inference_rate": 0
        }

    average_inference = (
        sum(inference_times) /
        len(inference_times)
    )

    inference_rate = (
        inference_count /
        duration
    )

    return {
        "mode": mode,
        "frames": frame_count,
        "inferences": inference_count,
        "average_inference": average_inference,
        "inference_rate": inference_rate
    }


def display_comparison(normal, economical):

    print("\n")
    print("=" * 70)
    print("ECONOMICAL PROCESSING COMPARISON")
    print("=" * 70)

    print(
        f"\nNORMAL MODE"
    )

    print(
        f"Frames: {normal['frames']}"
    )

    print(
        f"Inferences: {normal['inferences']}"
    )

    print(
        f"Average inference time: "
        f"{normal['average_inference']:.3f} sec"
    )

    print(
        f"Inference rate: "
        f"{normal['inference_rate']:.2f}/sec"
    )

    print(
        f"\nECONOMICAL MODE"
    )

    print(
        f"Frames: {economical['frames']}"
    )

    print(
        f"Inferences: {economical['inferences']}"
    )

    print(
        f"Average inference time: "
        f"{economical['average_inference']:.3f} sec"
    )

    print(
        f"Inference rate: "
        f"{economical['inference_rate']:.2f}/sec"
    )

    if normal["inferences"] > 0:

        reduction = (
            1 -
            (
                economical["inferences"] /
                normal["inferences"]
            )
        ) * 100

        print(
            f"\nInference reduction: "
            f"{reduction:.2f}%"
        )

    print(
        "\nNote: inference reduction is not the same "
        "as measured power reduction."
    )

    print("=" * 70)


def main():

    print(
        "\nSIH26179 - ECONOMICAL AI PROCESSING"
    )

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
        "\nNORMAL MODE running..."
    )

    normal_result = run_mode(
        cap,
        "NORMAL",
        duration=15
    )

    print(
        "\nECONOMICAL MODE running..."
    )

    economical_result = run_mode(
        cap,
        "ECONOMICAL",
        duration=15
    )

    cap.release()

    cv2.destroyAllWindows()

    display_comparison(
        normal_result,
        economical_result
    )


if __name__ == "__main__":
    main()