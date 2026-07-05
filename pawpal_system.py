from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime, time


@dataclass
class Task:
    title: str
    duration_minutes: int
    priority: int = 1
    time_window: Optional[str] = None
    recurrence: Optional[str] = None

    def validate(self) -> bool:
        if not self.title:
            return False
        if self.duration_minutes <= 0:
            return False
        return True

    def score(self) -> float:
        return float(self.priority) / max(1, self.duration_minutes)


@dataclass
class Pet:
    name: str
    species: str = "other"
    preferences: Dict[str, Any] = field(default_factory=dict)
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        self.tasks.append(task)

    def remove_task(self, task: Task) -> None:
        self.tasks.remove(task)


@dataclass
class Owner:
    name: str
    available_time_slots: List[Dict[str, time]] = field(default_factory=list)
    preferences: Dict[str, Any] = field(default_factory=dict)
    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        self.pets.append(pet)


@dataclass
class ScheduledItem:
    task: Task
    start_time: Optional[datetime] = None
    rationale: Optional[str] = None


@dataclass
class Schedule:
    items: List[ScheduledItem] = field(default_factory=list)

    def explain(self) -> List[str]:
        return [f"{it.task.title}: {it.rationale or ''}" for it in self.items]


class Scheduler:
    """Core scheduler that produces a Schedule from Owner, Pet, and Tasks.

    This file contains skeletons only; implement scheduling logic in small steps.
    """

    def __init__(self, owner: Owner, pet: Pet, tasks: Optional[List[Task]] = None):
        self.owner = owner
        self.pet = pet
        self.tasks: List[Task] = tasks or list(pet.tasks)

    def generate_schedule(self) -> Schedule:
        raise NotImplementedError()

    def sort_tasks(self) -> List[Task]:
        return sorted(self.tasks, key=lambda t: (-t.priority, t.duration_minutes))

    def fit_tasks_into_slots(self) -> Schedule:
        raise NotImplementedError()
