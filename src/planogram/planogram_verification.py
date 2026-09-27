import cv2
from ultralytics import YOLO


MODEL_PATH = "runs/detect/train-2/weights/best.pt"

EXPECTED_SHELVES = {
    1: "water_bottle",
    2: "jinthaa_juice",
    3: "lifebuoy",
    4: "dhal"
}


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


def verify_planogram(results, frame):
    shelf_products = {
        1: [],
        2: [],
        3: [],
        4: []
    }

    for result in results:
        boxes = result.boxes

        if boxes is None:
            continue

        for box in boxes:
            cls_id = int(box.cls[0])
            confidence = float(box.conf[0])

            if confidence < 0.40:
                continue

            label = result.names[cls_id]

            if label == "person":
                continue

            x1, y1, x2, y2 = box.xyxy[0].tolist()

            center_y = (y1 + y2) / 2

            shelf = get_shelf(
                center_y,
                frame.shape[0]
            )

            shelf_products[shelf].append(label)

    return shelf_products


def analyze_planogram(shelf_products):
    results = []

    for shelf, expected_product in EXPECTED_SHELVES.items():

        products = shelf_products[shelf]

        if len(products) == 0:
            results.append({
                "shelf": shelf,
                "expected": expected_product,
                "detected": "EMPTY",
                "status": "EMPTY"
            })
            continue

        correct_count = products.count(expected_product)
        misplaced = [
            product
            for product in products
            if product != expected_product
        ]

        if misplaced:
            status = "MISPLACED"
        else:
            status = "CORRECT"

        results.append({
            "shelf": shelf,
            "expected": expected_product,
            "detected": products,
            "correct_count": correct_count,
            "misplaced": misplaced,
            "status": status
        })

    return results


def draw_shelves(frame):
    height, width = frame.shape[:2]

    y1 = int(height * 0.25)
    y2 = int(height * 0.50)
    y3 = int(height * 0.75)

    cv2.line(frame, (0, y1), (width, y1), (255, 255, 255), 2)
    cv2.line(frame, (0, y2), (width, y2), (255, 255, 255), 2)
    cv2.line(frame, (0, y3), (width, y3), (255, 255, 255), 2)

    cv2.putText(
        frame,
        "Shelf 1 - Water Bottle",
        (10, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (255, 255, 255),
        2
    )

    cv2.putText(
        frame,
        "Shelf 2 - Jinthaa Juice",
        (10, int(height * 0.25) + 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (255, 255, 255),
        2
    )

    cv2.putText(
        frame,
        "Shelf 3 - Lifebuoy",
        (10, int(height * 0.50) + 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (255, 255, 255),
        2
    )

    cv2.putText(
        frame,
        "Shelf 4 - Dhal",
        (10, int(height * 0.75) + 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (255, 255, 255),
        2
    )


def draw_status(frame, analysis):
    height, width = frame.shape[:2]

    y = height - 120

    for item in analysis:
        text = (
            f"Shelf {item['shelf']} | "
            f"Expected: {item['expected']} | "
            f"Status: {item['status']}"
        )

        cv2.putText(
            frame,
            text,
            (10, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (255, 255, 255),
            1
        )

        y += 22

        if y > height - 10:
            break


def main():
    model = YOLO(MODEL_PATH)

    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Camera could not be opened.")
        return

    print("\nSIH26179 - PLANOGRAM VERIFICATION")
    print("=" * 70)
    print("Press Q to quit.")

    while True:
        ret, frame = cap.read()

        if not ret:
            break

        results = model(
            frame,
            conf=0.40,
            verbose=False
        )

        annotated = results[0].plot()

        shelf_products = verify_planogram(
            results,
            frame
        )

        analysis = analyze_planogram(
            shelf_products
        )

        draw_shelves(annotated)
        draw_status(
            annotated,
            analysis
        )

        cv2.imshow(
            "SIH26179 - Planogram Verification",
            annotated
        )

        key = cv2.waitKey(1) & 0xFF

        if key == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()