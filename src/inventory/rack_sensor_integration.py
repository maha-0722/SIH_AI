import serial
import time

SERIAL_PORT = "COM3"
BAUD_RATE = 115200

previous_weight = None

def parse_weight(line):
    line = line.strip()

    if line.startswith("RACK_WEIGHT:"):
        try:
            return float(line.split(":", 1)[1])
        except ValueError:
            return None

    return None

def detect_change(current_weight, previous_weight):
    if previous_weight is None:
        return "INITIAL_READING"

    change = current_weight - previous_weight

    if change < -500:
        return "SIGNIFICANT_REMOVAL"

    if change < -100:
        return "STOCK_REMOVAL"

    if change > 100:
        return "REFILL_DETECTED"

    return "STABLE"

def main():
    global previous_weight

    print("\nSIH26179 - RACK SENSOR INTEGRATION")
    print("=" * 60)

    try:
        ser = serial.Serial(
            SERIAL_PORT,
            BAUD_RATE,
            timeout=1
        )
    except serial.SerialException as e:
        print("Could not open serial port.")
        print(e)
        return

    time.sleep(2)

    print("ESP32 connected.")
    print("Waiting for rack sensor data...\n")

    while True:
        try:
            line = ser.readline().decode(
                "utf-8",
                errors="ignore"
            ).strip()

            weight = parse_weight(line)

            if weight is None:
                continue

            status = detect_change(
                weight,
                previous_weight
            )

            if previous_weight is None:
                change = 0
            else:
                change = weight - previous_weight

            print(
                f"Weight: {weight:10.2f} g | "
                f"Change: {change:10.2f} g | "
                f"Status: {status}"
            )

            previous_weight = weight

        except KeyboardInterrupt:
            print("\nIntegration stopped.")
            break

        except Exception as e:
            print("Error:", e)

    ser.close()

if __name__ == "__main__":
    main()