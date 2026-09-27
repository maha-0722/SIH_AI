STAFF = [
    {
        "id": "STAFF001",
        "name": "Staff 1",
        "role": "sales",
        "section": "Shelf 1",
        "status": "Available"
    },
    {
        "id": "STAFF002",
        "name": "Staff 2",
        "role": "inventory",
        "section": "Shelf 2",
        "status": "Available"
    },
    {
        "id": "STAFF003",
        "name": "Staff 3",
        "role": "inventory",
        "section": "Shelf 3",
        "status": "Busy"
    }
]


def find_available_staff(required_role, section):
    candidates = []

    for staff in STAFF:
        if (
            staff["status"] == "Available"
            and staff["role"] == required_role
        ):
            distance = 0 if staff["section"] == section else 1

            candidates.append(
                (distance, staff)
            )

    if not candidates:
        return None

    candidates.sort(key=lambda x: x[0])

    return candidates[0][1]


def create_task(
    task_id,
    task_type,
    section,
    required_role
):
    staff = find_available_staff(
        required_role,
        section
    )

    if staff is None:
        return {
            "task_id": task_id,
            "status": "PENDING",
            "assigned_staff": None,
            "message": "No suitable available staff"
        }

    staff["status"] = "Busy"

    return {
        "task_id": task_id,
        "task_type": task_type,
        "section": section,
        "status": "ACCEPTED",
        "assigned_staff": staff["id"],
        "staff_name": staff["name"]
    }


def update_task(task, new_status):
    valid_states = [
        "Pending",
        "Accepted",
        "In Progress",
        "Completed"
    ]

    if new_status not in valid_states:
        return False

    task["status"] = new_status

    if new_status == "Completed":
        staff_id = task.get("assigned_staff")

        for staff in STAFF:
            if staff["id"] == staff_id:
                staff["status"] = "Available"

    return True


def display_staff():
    print("\nSTAFF STATUS")
    print("-" * 50)

    for staff in STAFF:
        print(
            f"{staff['id']} | "
            f"{staff['name']} | "
            f"{staff['role']} | "
            f"{staff['section']} | "
            f"{staff['status']}"
        )


def generate_refill_task(
    shelf_name,
    product_name
):
    task = create_task(
        task_id=f"REFILL_{shelf_name.replace(' ', '_')}",
        task_type=f"REFILL_{product_name}",
        section=shelf_name,
        required_role="inventory"
    )

    return task


display_staff()

task = generate_refill_task(
    "Shelf 2",
    "jinthaa_juice"
)

print("\nGENERATED TASK")
print("-" * 50)

for key, value in task.items():
    print(f"{key}: {value}")

if task["status"] == "ACCEPTED":

    print("\nTask accepted")

    update_task(
        task,
        "In Progress"
    )

    print("Task status:", task["status"])

    update_task(
        task,
        "Completed"
    )

    print("Task status:", task["status"])

display_staff()