from datetime import date, timedelta

import pytest

from pawpal_system import Task, Pet, Owner, Scheduler


def test_task_mark_complete():
    task = Task(title="Test task", duration_minutes=10, priority=2)
    assert not task.completed

    task.mark_complete()

    assert task.completed


def test_pet_add_task_increases_count():
    pet = Pet(name="Mochi", species="dog")
    assert len(pet.tasks) == 0

    pet.add_task(Task(title="Walk", duration_minutes=20, priority=3))

    assert len(pet.tasks) == 1
    assert pet.tasks[0].title == "Walk"


def test_daily_task_spawns_next_day_occurrence():
    pet = Pet(name="Mochi", species="dog")
    today = date.today()
    pet.add_task(Task(title="Medication", duration_minutes=10, recurrence="daily", due_date=today))

    next_task = pet.mark_task_complete(pet.tasks[0])

    assert pet.tasks[0].completed
    assert next_task is not None
    assert not next_task.completed
    assert next_task.due_date == today + timedelta(days=1)
    assert next_task in pet.tasks


def test_weekly_task_spawns_next_week_occurrence():
    pet = Pet(name="Luna", species="cat")
    today = date.today()
    pet.add_task(Task(title="Nail trim", duration_minutes=15, recurrence="weekly", due_date=today))

    next_task = pet.mark_task_complete(pet.tasks[0])

    assert next_task.due_date == today + timedelta(weeks=1)


def test_one_off_task_does_not_spawn_occurrence():
    pet = Pet(name="Mochi", species="dog")
    pet.add_task(Task(title="Vet visit", duration_minutes=60))

    next_task = pet.mark_task_complete(pet.tasks[0])

    assert next_task is None
    assert len(pet.tasks) == 1


def _scheduler_with_tasks(*tasks):
    pet = Pet(name="Mochi", species="dog")
    for t in tasks:
        pet.add_task(t)
    owner = Owner(name="Jordan")
    owner.add_pet(pet)
    return Scheduler(owner=owner)


def test_detect_conflicts_flags_overlapping_tasks():
    scheduler = _scheduler_with_tasks(
        Task(title="Walk", duration_minutes=30, time="08:30"),
        Task(title="Feed", duration_minutes=15, time="08:45"),
    )

    conflicts = scheduler.detect_conflicts()

    assert len(conflicts) == 1
    assert "Walk" in conflicts[0] and "Feed" in conflicts[0]


def test_detect_conflicts_ignores_non_overlapping_tasks():
    scheduler = _scheduler_with_tasks(
        Task(title="Walk", duration_minutes=30, time="08:00"),
        Task(title="Feed", duration_minutes=15, time="09:00"),
    )

    assert scheduler.detect_conflicts() == []


def test_detect_conflicts_skips_tasks_without_time():
    scheduler = _scheduler_with_tasks(
        Task(title="Walk", duration_minutes=30, time="08:00"),
        Task(title="Someday", duration_minutes=15),
    )

    assert scheduler.detect_conflicts() == []
