import time
import cv2
from ultralytics import YOLO

MODEL_PATH = "runs/detect/train-2/weights/best.pt"
CONFIDENCE_THRESHOLD = 0.5
TEST_FRAMES = 50

def main():
    print("\nSIH26179 - AI PERFORMANCE MONITOR")
    print("=" * 60)

    model = YOLO(MODEL_PATH)

    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Could not open camera.")
        return

    frame_count = 0
    total_time = 0
    total_objects = 0

    print(f"Testing {TEST_FRAMES} frames...")
    print("Press Q to stop early.\n")

    while frame_count < TEST_FRAMES:
        ret, frame = cap.read()

        if not ret:
            print("Camera frame error.")
            break

        start_time = time.perf_counter()

        results = model.track(
            frame,
            persist=True,
            tracker="bytetrack.yaml",
            conf=CONFIDENCE_THRESHOLD,
            verbose=False
        )

        elapsed = time.perf_counter() - start_time

        total_time += elapsed
        frame_count += 1

        result = results[0]

        if result.boxes is not None:
            total_objects += len(result.boxes)

        fps = 1 / elapsed if elapsed > 0 else 0

        cv2.putText(
            frame,
            f"FPS: {fps:.2f}",
            (20, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2
        )

        cv2.putText(
            frame,
            f"Frame: {frame_count}/{TEST_FRAMES}",
            (20, 60),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2
        )

        cv2.imshow(
            "SIH26179 Performance Monitor",
            frame
        )

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()

    if frame_count == 0:
        print("No frames processed.")
        return

    average_time = total_time / frame_count
    average_fps = 1 / average_time if average_time > 0 else 0
    average_objects = total_objects / frame_count

    print("\n" + "=" * 60)
    print("PERFORMANCE SUMMARY")
    print("=" * 60)

    print(f"Frames processed       : {frame_count}")
    print(f"Total inference time   : {total_time:.2f} seconds")
    print(f"Average inference time : {average_time:.3f} seconds")
    print(f"Average FPS            : {average_fps:.2f}")
    print(f"Average objects/frame  : {average_objects:.2f}")

    if average_fps >= 15:
        performance = "GOOD"
    elif average_fps >= 8:
        performance = "ACCEPTABLE"
    else:
        performance = "LOW"

    print(f"Performance status     : {performance}")
    print("\nPerformance test completed.")

if __name__ == "__main__":
    main()