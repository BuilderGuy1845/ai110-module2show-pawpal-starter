from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, date, time, timedelta


@dataclass
class Task:
    title: str
    duration_minutes: int
    priority: int = 1
    time_window: Optional[str] = None
    # Scheduled start time as a "HH:MM" string, e.g. "08:30"
    time: Optional[str] = None
    # How often the task repeats: "daily", "weekly", or None for one-off.
    recurrence: Optional[str] = None
    # Calendar date the task is due (used to compute the next occurrence).
    due_date: Optional[date] = None
    completed: bool = False
    # Name of the pet this task belongs to (used for filtering)
    pet_name: Optional[str] = None

    def validate(self) -> bool:
        """Return whether the task has valid required data."""
        return bool(self.title) and self.duration_minutes > 0

    def mark_complete(self) -> None:
        """Mark the task as completed."""
        self.completed = True

    def next_occurrence(self) -> Optional["Task"]:
        """Return a fresh, incomplete copy of this task for its next due date.

        Recurring tasks advance their due date with ``timedelta``: "daily"
        tasks move forward one day, "weekly" tasks move forward seven days.
        Returns ``None`` for one-off tasks (no recurrence).
        """
        deltas = {"daily": timedelta(days=1), "weekly": timedelta(weeks=1)}
        delta = deltas.get((self.recurrence or "").lower())
        if delta is None:
            return None
        # Base the next date on this task's due date, falling back to today.
        base_date = self.due_date or date.today()
        return Task(
            title=self.title,
            duration_minutes=self.duration_minutes,
            priority=self.priority,
            time_window=self.time_window,
            time=self.time,
            recurrence=self.recurrence,
            due_date=base_date + delta,
            completed=False,
            pet_name=self.pet_name,
        )

    def score(self) -> float:
        """Compute a simple task score used for sorting."""
        return float(self.priority) / max(1, self.duration_minutes)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the task to a dictionary."""
        return {
            "title": self.title,
            "duration_minutes": self.duration_minutes,
            "priority": self.priority,
            "time_window": self.time_window,
            "time": self.time,
            "recurrence": self.recurrence,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "completed": self.completed,
            "pet_name": self.pet_name,
        }


@dataclass
class Pet:
    name: str
    species: str = "other"
    preferences: Dict[str, Any] = field(default_factory=dict)
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a validated task to this pet."""
        if not task.validate():
            raise ValueError("Invalid task")
        # Stamp the owning pet's name so tasks can be filtered by pet later.
        task.pet_name = self.name
        self.tasks.append(task)

    def remove_task(self, task: Task) -> None:
        """Remove a task from this pet."""
        self.tasks.remove(task)

    def mark_task_complete(self, task: Task) -> Optional[Task]:
        """Mark a task complete and auto-schedule its next occurrence.

        For "daily"/"weekly" tasks this appends a new incomplete instance for
        the next due date and returns it; for one-off tasks it returns ``None``.
        """
        task.mark_complete()
        next_task = task.next_occurrence()
        if next_task is not None:
            self.add_task(next_task)
        return next_task

    def get_tasks(self, include_completed: bool = False) -> List[Task]:
        """Return the pet's tasks, optionally including completed ones."""
        if include_completed:
            return list(self.tasks)
        return [t for t in self.tasks if not t.completed]


@dataclass
class Owner:
    name: str
    # Each slot is a tuple (start_time, end_time) using datetime.time
    available_time_slots: List[Tuple[time, time]] = field(default_factory=list)
    preferences: Dict[str, Any] = field(default_factory=dict)
    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's collection."""
        self.pets.append(pet)

    def remove_pet(self, pet: Pet) -> None:
        """Remove a pet from this owner's collection."""
        self.pets.remove(pet)

    def get_all_tasks(self, include_completed: bool = False) -> List[Task]:
        """Get all tasks from every pet owned by this owner."""
        tasks: List[Task] = []
        for p in self.pets:
            tasks.extend(p.get_tasks(include_completed=include_completed))
        return tasks


@dataclass
class ScheduledItem:
    task: Task
    start_time: Optional[datetime] = None
    rationale: Optional[str] = None


@dataclass
class Schedule:
    items: List[ScheduledItem] = field(default_factory=list)

    def explain(self) -> List[str]:
        """Return a human-readable explanation for each scheduled item."""
        return [f"{it.start_time.strftime('%H:%M') if it.start_time else '??:??'} - {it.task.title}: {it.rationale or ''}" for it in self.items]


class Scheduler:
    """Simple scheduler that fills owner slots with tasks from pets.

    Scheduling strategy (simple greedy):
    - Collect tasks from `owner` (or from a specific pet)
    - Sort by `priority` desc, then by shorter duration
    - Iterate available slots and place tasks sequentially until no time remains
    """

    def __init__(self, owner: Owner, pet: Optional[Pet] = None):
        """Initialize the scheduler with an owner and optional pet filter."""
        self.owner = owner
        self.pet = pet

    def _slot_length_minutes(self, start: time, end: time) -> int:
        """Return the slot duration in minutes between two times."""
        today = date.today()
        s = datetime.combine(today, start)
        e = datetime.combine(today, end)
        if e <= s:
            e = e + timedelta(days=1)
        return int((e - s).total_seconds() // 60)

    def _slot_start_datetime(self, start: time) -> datetime:
        """Create a datetime object for a slot start time on today."""
        return datetime.combine(date.today(), start)

    def _collect_tasks(self) -> List[Task]:
        """Return tasks from the selected pet or from the owner across all pets."""
        if self.pet:
            return self.pet.get_tasks()
        return self.owner.get_all_tasks()

    def sort_tasks(self, tasks: Optional[List[Task]] = None) -> List[Task]:
        """Sort tasks by priority descending and duration ascending."""
        tasks = tasks or self._collect_tasks()
        return sorted(tasks, key=lambda t: (-t.priority, t.duration_minutes))

    def sort_by_time(self, tasks: Optional[List[Task]] = None) -> List[Task]:
        """Sort tasks chronologically by their ``time`` attribute ("HH:MM").

        Because "HH:MM" strings are zero-padded, plain string comparison sorts
        them in true chronological order. Tasks without a time are pushed to the
        end so they don't jump ahead of scheduled ones.
        """
        tasks = tasks or self._collect_tasks()
        # The lambda "key" tells sorted() what to compare: the time string, with
        # a sentinel ("99:99") for tasks that have no time set.
        return sorted(tasks, key=lambda t: t.time or "99:99")

    @staticmethod
    def _minutes_since_midnight(hhmm: str) -> Optional[int]:
        """Convert an "HH:MM" string to minutes since midnight, or None if unparseable."""
        try:
            hours, minutes = hhmm.split(":")
            return int(hours) * 60 + int(minutes)
        except (ValueError, AttributeError):
            return None

    def detect_conflicts(self, tasks: Optional[List[Task]] = None) -> List[str]:
        """Return warning messages for tasks whose scheduled times overlap.

        Lightweight, non-crashing strategy: each task's window is
        [start, start + duration). Any two windows that overlap produce a
        warning string. Tasks without a valid ``time`` are skipped rather than
        raising. An empty list means no conflicts were found.
        """
        if tasks is None:
            tasks = self.owner.get_all_tasks(include_completed=True)

        # Keep only tasks with a parseable start time, paired with their window.
        timed = []
        for t in tasks:
            start = self._minutes_since_midnight(t.time) if t.time else None
            if start is not None:
                timed.append((t, start, start + max(0, t.duration_minutes)))

        warnings: List[str] = []
        for i in range(len(timed)):
            for j in range(i + 1, len(timed)):
                task_a, start_a, end_a = timed[i]
                task_b, start_b, end_b = timed[j]
                # Two half-open intervals overlap when each starts before the other ends.
                if start_a < end_b and start_b < end_a:
                    warnings.append(
                        f"Conflict: '{task_a.title}' ({task_a.pet_name or 'unknown'}) at {task_a.time} "
                        f"overlaps '{task_b.title}' ({task_b.pet_name or 'unknown'}) at {task_b.time}"
                    )
        return warnings

    def filter_tasks(
        self,
        tasks: Optional[List[Task]] = None,
        completed: Optional[bool] = None,
        pet_name: Optional[str] = None,
    ) -> List[Task]:
        """Return tasks matching the given completion status and/or pet name.

        Any argument left as ``None`` is ignored, so callers can filter by just
        completion, just pet, or both at once.
        """
        if tasks is None:
            # Include completed tasks so filtering by completion status works.
            tasks = self.owner.get_all_tasks(include_completed=True)
        result = tasks
        if completed is not None:
            result = [t for t in result if t.completed == completed]
        if pet_name is not None:
            result = [t for t in result if t.pet_name == pet_name]
        return result

    def generate_schedule(self) -> Schedule:
        """Build a daily schedule using owner availability and task priority."""
        tasks = self.sort_tasks()
        schedule = Schedule()

        slots = list(self.owner.available_time_slots)
        if not slots:
            # default slot: 08:00-20:00
            slots = [(time(8, 0), time(20, 0))]

        task_idx = 0
        for slot_start, slot_end in slots:
            slot_minutes = self._slot_length_minutes(slot_start, slot_end)
            cursor = self._slot_start_datetime(slot_start)

            while task_idx < len(tasks) and slot_minutes > 0:
                task = tasks[task_idx]
                if task.duration_minutes <= slot_minutes:
                    item = ScheduledItem(
                        task=task,
                        start_time=cursor,
                        rationale=f"priority={task.priority}; fits in slot",
                    )
                    schedule.items.append(item)
                    # advance
                    cursor = cursor + timedelta(minutes=task.duration_minutes)
                    slot_minutes -= task.duration_minutes
                    task_idx += 1
                else:
                    # task doesn't fit in this slot, try next slot
                    break

        # Any tasks left unscheduled get a rationale explaining lack of time
        while task_idx < len(tasks):
            t = tasks[task_idx]
            schedule.items.append(ScheduledItem(task=t, start_time=None, rationale="no time available"))
            task_idx += 1

        return schedule

