from datetime import time

import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="Jordan")

owner = st.session_state.owner

st.subheader("Owner and Pets")
owner_name = st.text_input("Owner name", value=owner.name)
if owner_name != owner.name:
    owner.name = owner_name

st.markdown("### Add a pet")
pet_name = st.text_input("Pet name", value="")
species = st.selectbox("Species", ["dog", "cat", "other"])
if st.button("Add pet"):
    if pet_name:
        owner.add_pet(Pet(name=pet_name, species=species))
        st.success(f"Added {pet_name} to {owner.name}'s pets")
    else:
        st.error("Please enter a pet name.")

if owner.pets:
    st.write("Current pets:")
    for pet in owner.pets:
        st.write(f"- {pet.name} ({pet.species})")
else:
    st.info("No pets yet. Add one above.")

st.divider()

st.subheader("Tasks")
st.caption("Add a task to a selected pet and then generate the schedule.")

if owner.pets:
    pet_names = [pet.name for pet in owner.pets]
    selected_pet_name = st.selectbox("Select pet", pet_names)
    selected_pet = next(p for p in owner.pets if p.name == selected_pet_name)

    col1, col2, col3 = st.columns(3)
    with col1:
        task_title = st.text_input("Task title", value="Morning walk", key="task_title")
    with col2:
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20, key="duration")
    with col3:
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=2, key="priority")

    col4, col5 = st.columns(2)
    with col4:
        scheduled_time = st.time_input("Scheduled time", value=time(8, 0), key="scheduled_time")
    with col5:
        recurrence = st.selectbox("Repeats", ["none", "daily", "weekly"], key="recurrence")

    if st.button("Add task to pet"):
        if task_title:
            priority_value = {"low": 1, "medium": 2, "high": 3}[priority]
            selected_pet.add_task(
                Task(
                    title=task_title,
                    duration_minutes=int(duration),
                    priority=priority_value,
                    time=scheduled_time.strftime("%H:%M"),
                    recurrence=None if recurrence == "none" else recurrence,
                )
            )
            st.success(f"Added task to {selected_pet.name}")
        else:
            st.error("Please enter a task title.")

    if selected_pet.tasks:
        st.write(f"Tasks for {selected_pet.name}:")
        # Sort this pet's tasks chronologically using the Scheduler method.
        scheduler = Scheduler(owner=owner, pet=selected_pet)
        for t in scheduler.sort_by_time(list(selected_pet.tasks)):
            info_col, action_col = st.columns([4, 1])
            with info_col:
                status = "✅" if t.completed else "⏳"
                repeat = f" · 🔁 {t.recurrence}" if t.recurrence else ""
                st.write(
                    f"{status} **{t.time or '--:--'}** — {t.title} "
                    f"({t.duration_minutes} min, priority {t.priority}){repeat}"
                )
            with action_col:
                if not t.completed and st.button("Complete", key=f"complete_{selected_pet.name}_{id(t)}"):
                    next_task = selected_pet.mark_task_complete(t)
                    if next_task is not None:
                        st.success(f"Completed! Next {t.recurrence} occurrence due {next_task.due_date}.")
                    else:
                        st.success("Task completed.")
                    st.rerun()
    else:
        st.info(f"{selected_pet.name} has no tasks yet.")
else:
    st.info("Add a pet first to assign tasks.")

st.divider()

st.subheader("All Tasks")
st.caption("Sorted by time, with filters for pet and completion status.")

if owner.pets:
    scheduler = Scheduler(owner=owner)

    fcol1, fcol2 = st.columns(2)
    with fcol1:
        pet_filter = st.selectbox("Filter by pet", ["All pets"] + [p.name for p in owner.pets])
    with fcol2:
        status_filter = st.selectbox("Filter by status", ["All", "Incomplete", "Completed"])

    completed_arg = {"All": None, "Incomplete": False, "Completed": True}[status_filter]
    pet_arg = None if pet_filter == "All pets" else pet_filter

    filtered = scheduler.filter_tasks(completed=completed_arg, pet_name=pet_arg)
    sorted_tasks = scheduler.sort_by_time(filtered)

    if sorted_tasks:
        st.table([
            {
                "time": t.time or "--:--",
                "pet": t.pet_name,
                "title": t.title,
                "duration (min)": t.duration_minutes,
                "priority": t.priority,
                "repeats": t.recurrence or "—",
                "status": "completed" if t.completed else "incomplete",
            }
            for t in sorted_tasks
        ])
    else:
        st.info("No tasks match the selected filters.")
else:
    st.info("Add a pet and some tasks to see them here.")

st.divider()

st.subheader("Build Schedule")
st.caption("Generate the schedule for all owned pets based on current tasks.")

if st.button("Generate schedule"):
    scheduler = Scheduler(owner=owner)

    # Surface any overlapping-time conflicts before showing the plan.
    conflicts = scheduler.detect_conflicts()
    if conflicts:
        for warning in conflicts:
            st.warning(f"⚠️ {warning}")
    else:
        st.success("No scheduling conflicts detected.")

    schedule = scheduler.generate_schedule()
    st.write("### Today's Schedule")
    if schedule.items:
        st.table([
            {
                "start": item.start_time.strftime("%H:%M") if item.start_time else "(unscheduled)",
                "task": item.task.title,
                "duration (min)": item.task.duration_minutes,
                "priority": item.task.priority,
                "why": item.rationale or "",
            }
            for item in schedule.items
        ])
    else:
        st.info("No tasks to schedule yet.")
