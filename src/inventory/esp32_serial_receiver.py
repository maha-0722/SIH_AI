import serial
import time

SERIAL_PORT = "COM3"
BAUD_RATE = 115200

def parse_weight(line):
    line = line.strip()

    if line.startswith("RACK_WEIGHT:"):
        value = line.split(":", 1)[1]

        try:
            return float(value)
        except ValueError:
            return None

    return None

def get_rack_status(weight_change):
    if weight_change < -500:
        return "SIGNIFICANT_REMOVAL"

    if weight_change < -100:
        return "STOCK_REMOVAL"

    if weight_change > 100:
        return "REFILL_DETECTED"

    return "STABLE"

def main():
    print("\nSIH26179 - ESP32 RACK SENSOR RECEIVER")
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

    previous_weight = None

    print("Waiting for ESP32 rack sensor data...\n")

    while True:
        try:
            line = ser.readline().decode(
                "utf-8",
                errors="ignore"
            ).strip()

            if not line:
                continue

            if line == "SENSOR_ERROR":
                print("HX711 sensor error")
                continue

            weight = parse_weight(line)

            if weight is None:
                continue

            if previous_weight is None:
                change = 0
                status = "INITIAL_READING"
            else:
                change = weight - previous_weight
                status = get_rack_status(change)

            print(
                f"Rack Weight: {weight:10.2f} g | "
                f"Change: {change:10.2f} g | "
                f"Status: {status}"
            )

            previous_weight = weight

        except KeyboardInterrupt:
            print("\nSensor monitoring stopped.")
            break

        except Exception as e:
            print("Reading error:", e)

    ser.close()

if __name__ == "__main__":
    main()