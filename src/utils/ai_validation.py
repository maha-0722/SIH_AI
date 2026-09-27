import os
import time
import cv2
from ultralytics import YOLO

MODEL_PATH = "runs/detect/train-2/weights/best.pt"
TEST_FOLDER = "data/test"
OUTPUT_FOLDER = "results/detection"

CONFIDENCE_THRESHOLD = 0.5

def validate_images():
    print("\nSIH26179 - AI MODEL VALIDATION")
    print("=" * 60)

    if not os.path.exists(MODEL_PATH):
        print("Model not found:")
        print(MODEL_PATH)
        return

    if not os.path.exists(TEST_FOLDER):
        print("Test folder not found:")
        print(TEST_FOLDER)
        return

    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    model = YOLO(MODEL_PATH)

    images = [
        f for f in os.listdir(TEST_FOLDER)
        if f.lower().endswith(
            (".jpg", ".jpeg", ".png")
        )
    ]

    if not images:
        print("No test images found.")
        return

    total_images = 0
    total_objects = 0
    total_time = 0

    class_counts = {}

    for image_name in images:
        image_path = os.path.join(
            TEST_FOLDER,
            image_name
        )

        frame = cv2.imread(image_path)

        if frame is None:
            continue

        start_time = time.time()

        results = model.predict(
            source=frame,
            conf=CONFIDENCE_THRESHOLD,
            verbose=False
        )

        elapsed = time.time() - start_time

        result = results[0]

        detections = 0

        if result.boxes is not None:
            detections = len(result.boxes)

            for box in result.boxes:
                class_id = int(box.cls[0])
                class_name = model.names[class_id]

                class_counts[class_name] = (
                    class_counts.get(class_name, 0) + 1
                )

        total_images += 1
        total_objects += detections
        total_time += elapsed

        output_path = os.path.join(
            OUTPUT_FOLDER,
            image_name
        )

        annotated = result.plot()

        cv2.imwrite(
            output_path,
            annotated
        )

        print(
            f"{image_name:30} | "
            f"Objects: {detections:2} | "
            f"Time: {elapsed:.3f}s"
        )

    average_time = total_time / total_images
    fps = 1 / average_time if average_time > 0 else 0

    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)

    print(f"Images tested       : {total_images}")
    print(f"Objects detected    : {total_objects}")
    print(f"Average time/image  : {average_time:.3f}s")
    print(f"Approx FPS          : {fps:.2f}")

    print("\nCLASS DETECTIONS")
    print("-" * 40)

    for class_name, count in class_counts.items():
        print(f"{class_name:20} : {count}")

    print("\nAnnotated results saved in:")
    print(OUTPUT_FOLDER)

if __name__ == "__main__":
    validate_images()