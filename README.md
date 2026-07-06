# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like:

```
# e.g.:
# Daily plan for Biscuit (Golden Retriever):
#   08:00 — Morning walk (30 min) [priority: high]
#   09:00 — Feeding (10 min) [priority: high]
#   ...
```
My Output:
Today's Schedule
=================
08:00 - Give medication (10 min) [5] - priority=5; fits in slot
08:10 - Morning walk (30 min) [3] - priority=3; fits in slot
08:40 - Play with toy (20 min) [2] - priority=2; fits in slot
09:00 - Brush fur (15 min) [1] - priority=1; fits in slot

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
# Paste your pytest output here
```

## 📐 Smarter Scheduling

PawPal+ goes beyond a flat task list with several scheduling features. Each is
implemented as a method on the `Scheduler`, `Task`, or `Pet` class in
`pawpal_system.py`.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Priority sorting | `Scheduler.sort_tasks()` | Orders tasks by priority (descending), then by shorter duration as a tiebreaker. Used by `generate_schedule()`. |
| Time sorting | `Scheduler.sort_by_time()` | Sorts tasks chronologically by their `"HH:MM"` `time` attribute using a `sorted()` key. Tasks with no time sort to the end. |
| Filtering | `Scheduler.filter_tasks()` | Filters by completion status and/or pet name; any argument left `None` is ignored. Pet-level filtering also available via `Pet.get_tasks(include_completed=...)`. |
| Conflict detection | `Scheduler.detect_conflicts()` | Compares tasks pairwise; two tasks conflict when their `[start, start + duration)` windows overlap. Returns a list of warning strings instead of raising. Helper: `Scheduler._minutes_since_midnight()`. |
| Recurring tasks | `Pet.mark_task_complete()` + `Task.next_occurrence()` | Completing a `"daily"`/`"weekly"` task auto-creates the next instance. `next_occurrence()` advances the `due_date` with `timedelta` (+1 day / +7 days); one-off tasks return `None`. |

### How each feature works

- **Sorting behavior — `Scheduler.sort_by_time()`**: Because `"HH:MM"` strings
  are zero-padded, plain string comparison already yields chronological order, so
  the method uses `sorted(tasks, key=lambda t: t.time or "99:99")`. The `"99:99"`
  sentinel keeps untimed tasks at the end. `Scheduler.sort_tasks()` provides the
  alternate priority-first ordering the scheduler uses when placing tasks.

- **Filtering behavior — `Scheduler.filter_tasks(completed=..., pet_name=...)`**:
  Returns tasks matching the given completion status and/or pet name. Passing
  only `pet_name` filters by pet, only `completed` filters by status, and both
  narrows on both. It collects tasks including completed ones so filtering by
  status is meaningful.

- **Conflict detection — `Scheduler.detect_conflicts()`**: A lightweight,
  non-crashing check. Each task's time window is the half-open interval
  `[start, start + duration_minutes)`; two windows overlap when
  `start_a < end_b and start_b < end_a`. It works across all pets, so both
  same-pet and cross-pet clashes are caught, and tasks with missing/invalid
  times are skipped rather than causing an error. Returns warning strings
  (empty list = no conflicts).

- **Recurring task logic — `Pet.mark_task_complete()` and
  `Task.next_occurrence()`**: Marking a recurring task complete triggers
  creation of a fresh, incomplete copy for its next due date. `next_occurrence()`
  looks up the recurrence (`"daily"` → `timedelta(days=1)`,
  `"weekly"` → `timedelta(weeks=1)`), advances the `due_date` (falling back to
  today if unset), and returns the new `Task`; `mark_task_complete()` appends it
  to the pet's task list. One-off tasks recur nothing and return `None`.

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
