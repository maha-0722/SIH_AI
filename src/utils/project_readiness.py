import os

BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../..")
)

REQUIRED_FILES = [
    "runs/detect/train-2/weights/best.pt",

    "src/tracking/realtime_tracking.py",

    "src/inventory/inventory_monitor.py",
    "src/inventory/sensor_fusion.py",
    "src/inventory/sensor_simulator.py",
    "src/inventory/pos_sync.py",
    "src/inventory/esp32_serial_receiver.py",
    "src/inventory/rack_sensor_integration.py",

    "src/prediction/stock_depletion.py",
    "src/prediction/stock_prediction.py",

    "src/queue/queue_analysis.py",

    "src/planogram/planogram_verification.py",

    "src/anomaly/anomaly_detection.py",

    "src/staff/staff_assignment.py",
    "src/staff/task_priority.py",

    "src/alerts/alert_generation.py",

    "src/security/exit_verification.py",

    "src/events/event_processor.py",

    "src/integration/ai_pipeline.py",
    "src/integration/ai_retail_pipeline.py",
    "src/integration/decision_engine.py",
    "src/integration/staff_task_dispatcher.py",

    "src/utils/ai_validation.py",
    "src/utils/performance_monitor.py",

    "hardware/esp32/rack_sensor.ino"
]

def check_file(relative_path):
    full_path = os.path.join(
        BASE_DIR,
        relative_path
    )

    return os.path.isfile(full_path)

def main():
    print("\nSIH26179 - PROJECT READINESS CHECK")
    print("=" * 70)

    completed = 0
    missing = []

    for file in REQUIRED_FILES:
        if check_file(file):
            print(f"[OK]      {file}")
            completed += 1
        else:
            print(f"[MISSING] {file}")
            missing.append(file)

    total = len(REQUIRED_FILES)

    percentage = (
        completed / total * 100
        if total > 0
        else 0
    )

    print("\n" + "=" * 70)
    print("READINESS SUMMARY")
    print("=" * 70)

    print(f"Required files : {total}")
    print(f"Completed      : {completed}")
    print(f"Missing        : {len(missing)}")
    print(f"Readiness      : {percentage:.1f}%")

    if missing:
        print("\nMISSING FILES")
        print("-" * 70)

        for file in missing:
            print(file)

    else:
        print("\nAll required project files are present.")

    print("\nNote:")
    print("File presence does not mean hardware or real-world validation")
    print("is complete.")

if __name__ == "__main__":
    main()