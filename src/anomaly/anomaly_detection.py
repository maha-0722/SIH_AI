from collections import deque
from sklearn.ensemble import IsolationForest
import numpy as np
import time

HISTORY_SIZE = 50

history = deque(maxlen=HISTORY_SIZE)


def add_event(
    people_count,
    queue_count,
    stock_change,
    dwell_time
):
    history.append([
        people_count,
        queue_count,
        stock_change,
        dwell_time
    ])


def detect_anomaly():
    if len(history) < 10:
        return {
            "status": "INSUFFICIENT_HISTORY",
            "score": None
        }

    data = np.array(history)

    model = IsolationForest(
        contamination=0.10,
        random_state=42
    )

    model.fit(data)

    latest = data[-1].reshape(1, -1)

    prediction = model.predict(latest)
    score = model.decision_function(latest)[0]

    if prediction[0] == -1:
        status = "ANOMALY"
    else:
        status = "NORMAL"

    return {
        "status": status,
        "score": float(score)
    }


print("SIH26179 - Operational Anomaly Detection")

print("\nCollecting operational data...")

sample_data = [
    (4, 2, 1, 20),
    (5, 2, 1, 22),
    (4, 3, 0, 18),
    (6, 3, 1, 25),
    (5, 2, 1, 21),
    (4, 2, 0, 19),
    (6, 3, 1, 24),
    (5, 2, 1, 23),
    (4, 2, 0, 20),
    (5, 3, 1, 22),
    (6, 3, 1, 25),
    (5, 2, 0, 21)
]

for event in sample_data:
    add_event(
        people_count=event[0],
        queue_count=event[1],
        stock_change=event[2],
        dwell_time=event[3]
    )

    time.sleep(0.05)


result = detect_anomaly()

print("\nStatus:", result["status"])

if result["score"] is not None:
    print("Anomaly Score:", round(result["score"], 4))

print("\nMonitoring features:")
print("- People count")
print("- Queue count")
print("- Stock change")
print("- Dwell time")