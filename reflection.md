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

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
