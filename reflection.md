# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

For my initial UML design, I used:
Task: to represent the pet-care task containing the title, duration_minutes, and the priority which is based on numeric score. I also included time_window and recurrence. Methods I used are validation and a score() helper function to help sorting.

Pet: to contian the name, species, and simple preferences which include preffered times, and activity tolerances.

Owner: contains name, available_time_slots, and high-level preferences which include max total care time per day.

Schedular: is the core class that take Owner, Pet, and a list of Task objests and produces a Schedule. Responsibilities for schedular include applying contraints (e.g. availability, total time), sort and filters tasks based on priority and duration, fit tasks into time slots, and produce explanations for the choices made.

Schedule: is the resulting object from schedular. It contains an ordered list of tasks with start time and reasonings on why it was chosen/how it was organized.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

Yes, some of my design changed during implementation. For example, I moved some preference fields in owner into a preferences dictionary in Pet. I did this because I realized that most settings applied pet-pet instead of per-owner. This simplified data flow between the UI and schedular.

I also changed priority from a string to a numeric weight early in my implementation to make sorting deterministic. By doing this, I made scheduling rules easier to work with and test.

I added an explain() method to Schedule to return explanations fro each placement after testing the first schedular. I did this because the UI needs solid and clear explanations for users.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

My scheduler considers three main constraints. First is the owner's availability: it only places tasks inside the `available_time_slots` the owner provides, and it defaults to an 08:00-20:00 window if none are given. Second is task duration, since a task is only placed if it actually fits in the remaining minutes of a slot. Third is priority, which is a numeric weight I use to decide ordering. On top of these, I added conflict detection that flags when two tasks' time windows overlap, so the user gets a warning instead of a silently broken schedule.

I decided priority mattered most because pet care has non-negotiable tasks (like giving medication) that should be placed before optional ones (like brushing fur). So `sort_tasks()` sorts by priority descending first, then by shorter duration as a tiebreaker so quick, high-value tasks get slotted in early. Availability is the hard constraint that everything else has to respect, and duration is what actually determines whether a task can be placed once its turn comes up.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

The main tradeoff is that I use a greedy, first-fit placement strategy instead of searching for a globally optimal schedule. The scheduler walks through the sorted tasks once and drops each one into the first slot where it fits; it never backtracks. This means it can leave a slot partially empty (a 45-minute task won't fit a 30-minute gap even if two 15-minute tasks would have), and lower-priority tasks can end up unscheduled with a "no time available" note rather than being squeezed in through rearranging.

That tradeoff is reasonable for this scenario because a daily pet-care routine is small (a handful of tasks per pet) and the priority ordering already puts the important tasks first, so the greedy approach almost always places what matters most. A full optimizer would be much more complex, harder to test, and harder to explain to the user, whereas the greedy pass is predictable, fast, and pairs naturally with the `explain()` output and the conflict warnings so the user can see and fix any gaps themselves.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

I used AI throughout the build, but for specific jobs rather than to write everything for me. Early on I used it to brainstorm my class structure and sanity-check the UML. During implementation I leaned on it most for the algorithmic pieces: how to sort `"HH:MM"` strings with a `sorted()` lambda key, how to use `timedelta` to advance a due date for daily and weekly recurrence, and a lightweight way to detect overlapping time windows without crashing. I also used it to wire those backend methods into the Streamlit UI and to keep my README and docstrings in sync with the code.

The most helpful prompts were narrow and concrete ones tied to a single method, like "how do I sort tasks by an HH:MM time attribute" or "give me a conflict check that returns a warning instead of raising." Vague prompts gave me generic answers; specific prompts that named the method, the data type, and the desired behavior gave me code I could actually drop in and test.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

One moment was the recurring-task feature. The first suggestion put the "create the next occurrence" logic inside `Task.mark_complete()`, but a `Task` has no reference back to its `Pet`, so it couldn't actually add the new instance to any list. I rejected that and instead split the responsibility: `Task.next_occurrence()` does the date math and returns a new task, while `Pet.mark_task_complete()` owns the collection and appends it. That kept each class responsible for only what it can see.

I verified suggestions by testing rather than trusting them. For recurrence I wrote tests asserting the new `due_date` was exactly `today + timedelta(days=1)` for daily and `+ 7 days` for weekly, and that a one-off task returned `None`. For conflict detection I tested overlapping, non-overlapping, and missing-time cases. I also ran `main.py` and the Streamlit app to watch the behavior end-to-end, so I was confirming real output, not just that the code ran.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

I wrote 8 tests in `tests/test_pawpal.py` covering the behaviors most likely to break silently. These include task completion (`mark_complete()` flips the flag), adding tasks to a pet, recurring-task creation (daily spawns a next-day instance, weekly spawns a next-week instance, one-off spawns nothing), and conflict detection (overlapping tasks are flagged, non-overlapping tasks are ignored, and tasks without a time are skipped).

These tests mattered because they target the logic that is easy to get subtly wrong: date arithmetic for recurrence and interval math for conflicts. A bug there wouldn't throw an error, it would just produce a quietly wrong schedule, which is exactly the kind of thing a user might not notice until they miss a task. Pinning the exact expected dates and the exact conflict count locks that behavior in.

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

I am fairly confident, around 4 out of 5. All 8 tests pass, and I have run both the CLI (`main.py`) and the Streamlit UI to confirm the sorting, filtering, conflict warnings, and recurrence all behave as expected in practice.

The main gap is that I do not yet have automated tests for `generate_schedule()` end-to-end, which is the most complex method. If I had more time I would test slot filling and the overflow case where low-priority tasks get the "no time available" note, a time slot that wraps past midnight, conflict detection when recurring tasks land on different due dates, and invalid inputs like a malformed time string or a zero-duration task.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

I am most satisfied with the recurring-task feature and how cleanly the responsibilities ended up split between `Task.next_occurrence()` and `Pet.mark_task_complete()`. It was the trickiest piece to reason about, I backed it with tests, and it surfaces nicely in the UI where completing a daily task instantly schedules tomorrow's instance. Seeing that work end-to-end, from the date math up through the Streamlit button, felt like the system actually being "smart."

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

I would improve `generate_schedule()`. Right now it uses a greedy first-fit pass that never backtracks, so it can leave gaps and push tasks to "no time available" even when a rearrangement would fit them. I would also make conflict detection date-aware so it compares `due_date` as well as time, and add persistence so tasks survive a Streamlit restart instead of living only in session state.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

My biggest takeaway is that clear class responsibilities make everything else easier. The recurrence bug came from putting logic in a class that couldn't see the data it needed, and fixing that by respecting each class's boundaries made the code simpler to write, test, and explain. Working with AI reinforced this: it is great for generating a specific method quickly, but I still had to own the design decisions and verify the output with tests, because the AI could produce code that runs while quietly violating the structure of the system.
