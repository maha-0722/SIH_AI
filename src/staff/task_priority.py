from datetime import datetime


PRIORITY_LEVELS = {
    "CRITICAL": 4,
    "HIGH": 3,
    "MEDIUM": 2,
    "LOW": 1
}


def calculate_priority(
    task_type,
    stock_status="Normal",
    hours_remaining=None,
    queue_status="NORMAL",
    anomaly=False
):
    score = 0
    reasons = []

    if stock_status == "Empty":
        score += 4
        reasons.append("Stock is empty")
    elif stock_status == "Low":
        score += 3
        reasons.append("Stock is low")
    elif stock_status == "Medium":
        score += 1
        reasons.append("Stock is medium")

    if hours_remaining is not None:
        if hours_remaining <= 0.5:
            score += 4
            reasons.append("Stock may become empty soon")
        elif hours_remaining <= 1:
            score += 3
            reasons.append("Low remaining stock time")
        elif hours_remaining <= 2:
            score += 2
            reasons.append("Stock depletion approaching")

    if queue_status == "QUEUE CONGESTION":
        score += 3
        reasons.append("Queue congestion detected")
    elif queue_status == "MODERATE":
        score += 1
        reasons.append("Moderate queue")

    if anomaly:
        score += 2
        reasons.append("Anomaly detected")

    if task_type == "REFILL" and stock_status == "Empty":
        score += 2
        reasons.append("Immediate refill required")

    if score >= 8:
        priority = "CRITICAL"
    elif score >= 5:
        priority = "HIGH"
    elif score >= 3:
        priority = "MEDIUM"
    else:
        priority = "LOW"

    return {
        "priority": priority,
        "score": score,
        "reasons": reasons
    }


def create_task(
    task_id,
    task_type,
    product,
    shelf,
    stock_status="Normal",
    hours_remaining=None,
    queue_status="NORMAL",
    anomaly=False
):
    result = calculate_priority(
        task_type=task_type,
        stock_status=stock_status,
        hours_remaining=hours_remaining,
        queue_status=queue_status,
        anomaly=anomaly
    )

    return {
        "task_id": task_id,
        "task_type": task_type,
        "product": product,
        "shelf": shelf,
        "priority": result["priority"],
        "priority_score": result["score"],
        "reasons": result["reasons"],
        "status": "Pending",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }


def sort_tasks(tasks):
    return sorted(
        tasks,
        key=lambda task: (
            PRIORITY_LEVELS.get(task["priority"], 1),
            task["priority_score"]
        ),
        reverse=True
    )


def display_tasks(tasks):
    print("\nTASK PRIORITY")
    print("=" * 100)

    for task in tasks:
        print(
            f"Task: {task['task_id']} | "
            f"Type: {task['task_type']} | "
            f"Product: {task['product']} | "
            f"Shelf: {task['shelf']} | "
            f"Priority: {task['priority']} | "
            f"Score: {task['priority_score']} | "
            f"Status: {task['status']}"
        )

        if task["reasons"]:
            print("Reason:", ", ".join(task["reasons"]))


def demo():
    tasks = []

    tasks.append(
        create_task(
            task_id="T001",
            task_type="REFILL",
            product="water_bottle",
            shelf=1,
            stock_status="Empty",
            hours_remaining=0,
            queue_status="NORMAL"
        )
    )

    tasks.append(
        create_task(
            task_id="T002",
            task_type="REFILL",
            product="jinthaa_juice",
            shelf=2,
            stock_status="Low",
            hours_remaining=1.2,
            queue_status="QUEUE CONGESTION"
        )
    )

    tasks.append(
        create_task(
            task_id="T003",
            task_type="CHECK",
            product="lifebuoy",
            shelf=3,
            stock_status="Medium",
            hours_remaining=3,
            queue_status="NORMAL"
        )
    )

    tasks.append(
        create_task(
            task_id="T004",
            task_type="INVESTIGATE",
            product="dhal",
            shelf=4,
            stock_status="Low",
            hours_remaining=2,
            queue_status="NORMAL",
            anomaly=True
        )
    )

    tasks = sort_tasks(tasks)

    display_tasks(tasks)


if __name__ == "__main__":
    demo()