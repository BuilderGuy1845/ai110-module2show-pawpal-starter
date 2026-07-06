from datetime import time

from pawpal_system import Owner, Pet, Task, Scheduler


def main():
    owner = Owner(name="Jordan", available_time_slots=[(time(8, 0), time(12, 0)), (time(13, 0), time(17, 0))])

    dog = Pet(name="Mochi", species="dog")
    cat = Pet(name="Luna", species="cat")

    # Add tasks intentionally out of chronological order to prove sorting works.
    dog.add_task(Task(title="Evening walk", duration_minutes=30, priority=3, time="18:00"))
    dog.add_task(Task(title="Give medication", duration_minutes=10, priority=5, time="08:30", recurrence="daily"))
    cat.add_task(Task(title="Play with toy", duration_minutes=20, priority=2, time="14:15"))
    cat.add_task(Task(title="Brush fur", duration_minutes=15, priority=1, time="09:45"))

    # Overlapping tasks (different pets, same time) to trigger a conflict warning.
    cat.add_task(Task(title="Vet call", duration_minutes=30, priority=4, time="08:30"))

    # Mark one task complete so filtering by status has something to show.
    cat.tasks[0].mark_complete()

    owner.add_pet(dog)
    owner.add_pet(cat)

    scheduler = Scheduler(owner=owner)

    print("All tasks sorted by time")
    print("========================")
    for task in scheduler.sort_by_time(owner.get_all_tasks(include_completed=True)):
        status = "done" if task.completed else "todo"
        print(f"{task.time} - {task.title} ({task.pet_name}) [{status}]")

    print("\nMochi's tasks only (filter by pet name)")
    print("=======================================")
    for task in scheduler.filter_tasks(pet_name="Mochi"):
        print(f"{task.time} - {task.title}")

    print("\nCompleted tasks only (filter by status)")
    print("=======================================")
    for task in scheduler.filter_tasks(completed=True):
        print(f"{task.time} - {task.title} ({task.pet_name})")

    print("\nIncomplete tasks, sorted by time")
    print("================================")
    incomplete = scheduler.filter_tasks(completed=False)
    for task in scheduler.sort_by_time(incomplete):
        print(f"{task.time} - {task.title} ({task.pet_name})")

    print("\nSchedule conflicts")
    print("==================")
    conflicts = scheduler.detect_conflicts()
    if conflicts:
        for warning in conflicts:
            print(f"WARNING: {warning}")
    else:
        print("No conflicts found.")

    print("\nRecurring task: complete it and watch the next one appear")
    print("========================================================")
    med = dog.tasks[1]  # "Give medication" is a daily task
    print(f"before: {len(dog.tasks)} tasks for {dog.name}")
    next_med = dog.mark_task_complete(med)
    print(f"completed: {med.title} (due {med.due_date or 'today'})")
    print(f"auto-created: {next_med.title} due {next_med.due_date}")
    print(f"after: {len(dog.tasks)} tasks for {dog.name}")


if __name__ == "__main__":
    main()
