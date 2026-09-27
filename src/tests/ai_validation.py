import os
import time
import cv2
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

CLASS_NAMES = {
    0: "person",
    1: "water_bottle",
    2: "jinthaa_juice",
    3: "lifebuoy",
    4: "dhal"
}


def test_model_loading():
    print("\n1. MODEL LOADING")
    print("-" * 60)

    if os.path.exists(MODEL_PATH):
        print("YOLOv8n model: PASS")
        print("Model:", MODEL_PATH)
        return True

    print("YOLOv8n model: FAIL")
    return False


def test_image_detection(image_path):
    print("\n2. OBJECT DETECTION")
    print("-" * 60)

    if not os.path.exists(image_path):
        print("Test image not found.")
        return False

    image = cv2.imread(image_path)

    if image is None:
        print("Image could not be opened.")
        return False

    results = model(
        image,
        conf=CONFIDENCE,
        verbose=False
    )

    detection_count = 0

    for result in results:
        if result.boxes is None:
            continue

        for box in result.boxes:
            class_id = int(box.cls[0])
            confidence = float(box.conf[0])

            class_name = CLASS_NAMES.get(
                class_id,
                "unknown"
            )

            detection_count += 1

            print(
                f"Detected: {class_name} | "
                f"Confidence: {confidence:.2f}"
            )

    if detection_count > 0:
        print(
            f"\nDetection test: PASS "
            f"({detection_count} objects)"
        )
        return True

    print("\nDetection test: NO OBJECTS DETECTED")
    return False


def test_camera():

    print("\n3. CAMERA TEST")
    print("-" * 60)

    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Camera: FAIL")
        return False

    ret, frame = cap.read()

    if not ret:
        print("Camera frame: FAIL")
        cap.release()
        return False

    results = model(
        frame,
        conf=CONFIDENCE,
        verbose=False
    )

    detection_count = 0

    for result in results:

        if result.boxes is None:
            continue

        detection_count += len(result.boxes)

        for box in result.boxes:

            x1, y1, x2, y2 = map(
                int,
                box.xyxy[0]
            )

            class_id = int(box.cls[0])
            confidence = float(box.conf[0])

            class_name = CLASS_NAMES.get(
                class_id,
                "unknown"
            )

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
                (x1, max(y1 - 10, 20)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 255, 255),
                2
            )

    cv2.putText(
        frame,
        f"Detections: {detection_count}",
        (10, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2
    )

    cv2.imshow(
        "SIH26179 - AI Validation",
        frame
    )

    print(
        f"Camera detection count: {detection_count}"
    )

    print(
        "Press any key in the camera window..."
    )

    cv2.waitKey(0)

    cap.release()
    cv2.destroyAllWindows()

    return True


def test_inference_speed():

    print("\n4. INFERENCE PERFORMANCE")
    print("-" * 60)

    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Camera unavailable.")
        return False

    frame_times = []

    for _ in range(10):

        ret, frame = cap.read()

        if not ret:
            continue

        start = time.time()

        model(
            frame,
            conf=CONFIDENCE,
            verbose=False
        )

        end = time.time()

        frame_times.append(
            end - start
        )

    cap.release()

    if not frame_times:
        print("Performance test failed.")
        return False

    average_time = (
        sum(frame_times) /
        len(frame_times)
    )

    fps = 1 / average_time

    print(
        f"Average inference time: "
        f"{average_time:.3f} seconds"
    )

    print(
        f"Approximate inference FPS: "
        f"{fps:.2f}"
    )

    print("Performance test: PASS")

    return True


def test_bytetrack():

    print("\n5. BYTETRACK TEST")
    print("-" * 60)

    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Camera unavailable.")
        return False

    tracking_detected = False

    for _ in range(30):

        ret, frame = cap.read()

        if not ret:
            break

        results = model.track(
            frame,
            persist=True,
            tracker="bytetrack.yaml",
            conf=CONFIDENCE,
            verbose=False
        )

        for result in results:

            if result.boxes is None:
                continue

            if result.boxes.id is not None:

                tracking_detected = True

                ids = [
                    int(track_id)
                    for track_id in result.boxes.id
                ]

                print(
                    "Tracking IDs:",
                    ids
                )

                break

        if tracking_detected:
            break

    cap.release()

    if tracking_detected:
        print("ByteTrack: PASS")
        return True

    print(
        "ByteTrack: NO TRACKING ID DETECTED"
    )

    return False


def generate_report(results):

    print("\n")
    print("=" * 70)
    print("SIH26179 AI VALIDATION REPORT")
    print("=" * 70)

    passed = sum(
        1 for result in results
        if result
    )

    total = len(results)

    print(
        f"Tests Passed: {passed}/{total}"
    )

    if passed == total:
        print(
            "\nOVERALL STATUS: PASS"
        )
    else:
        print(
            "\nOVERALL STATUS: NEEDS REVIEW"
        )

    print("=" * 70)


def main():

    print(
        "\nSIH26179 - AI VALIDATION"
    )

    results = []

    results.append(
        test_model_loading()
    )

    results.append(
        test_camera()
    )

    results.append(
        test_inference_speed()
    )

    results.append(
        test_bytetrack()
    )

    generate_report(results)


if __name__ == "__main__":
    main()