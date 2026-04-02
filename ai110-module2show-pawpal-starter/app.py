"""
PawPal+ Streamlit Application

A pet care planning assistant that helps owners schedule daily care tasks
for their pets using priority-based scheduling algorithms.
"""

import streamlit as st
from pawpal_system import (
    Task, RecurringTask, Pet, Owner, Scheduler,
    VALID_SPECIES, VALID_SORT_STRATEGIES, PRIORITY_LABELS,
)

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="wide")

# ── Session State Initialization ─────────────────────────────────────

if "owner" not in st.session_state:
    st.session_state.owner = None
if "pets" not in st.session_state:
    st.session_state.pets = []
if "schedule" not in st.session_state:
    st.session_state.schedule = None

# ── Sidebar: Owner & Pet Setup ───────────────────────────────────────

with st.sidebar:
    st.header("Setup")

    # Owner info
    st.subheader("Owner")
    owner_name = st.text_input("Your name", value="Jordan")
    available_minutes = st.number_input(
        "Available minutes today", min_value=10, max_value=480, value=120, step=10
    )

    st.divider()

    # Pet management
    st.subheader("Pets")
    with st.expander("Add a Pet", expanded=len(st.session_state.pets) == 0):
        pet_name = st.text_input("Pet name", value="Mochi")
        species = st.selectbox("Species", list(VALID_SPECIES))
        pet_age = st.number_input("Age (years)", min_value=0, max_value=30, value=3)
        special_needs = st.text_input("Special needs (comma-separated)", value="")

        if st.button("Add Pet"):
            needs = [s.strip() for s in special_needs.split(",") if s.strip()]
            try:
                pet = Pet(pet_name, species, pet_age, needs)
                st.session_state.pets.append(pet)
                st.session_state.schedule = None
                st.success(f"Added {pet_name} the {species}!")
            except ValueError as e:
                st.error(str(e))

    # Show current pets
    if st.session_state.pets:
        for i, pet in enumerate(st.session_state.pets):
            needs_str = ", ".join(pet.special_needs) if pet.special_needs else "None"
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"**{pet.name}** ({pet.species}, age {pet.age}) — Needs: {needs_str}")
            with col2:
                if st.button("Remove", key=f"remove_pet_{i}"):
                    st.session_state.pets.pop(i)
                    st.session_state.schedule = None
                    st.rerun()
    else:
        st.info("No pets yet. Add one above.")

    st.divider()

    # Task management
    st.subheader("Tasks")
    if st.session_state.pets:
        with st.expander("Add a Task", expanded=True):
            pet_names = [p.name for p in st.session_state.pets]
            task_pet = st.selectbox("For which pet?", pet_names)
            task_title = st.text_input("Task title", value="Morning walk")
            task_duration = st.number_input(
                "Duration (minutes)", min_value=1, max_value=240, value=20
            )
            task_priority = st.slider("Priority (1=Critical, 5=Optional)", 1, 5, 2)
            st.caption(f"Priority level: **{PRIORITY_LABELS[task_priority]}**")
            task_time_pref = st.selectbox(
                "Time preference", ["morning", "afternoon", "evening", "any"]
            )

            is_recurring = st.checkbox("Recurring task?")
            times_per_day = 1
            if is_recurring:
                times_per_day = st.number_input(
                    "Times per day", min_value=1, max_value=5, value=2
                )

            if st.button("Add Task"):
                try:
                    target_pet = next(p for p in st.session_state.pets if p.name == task_pet)
                    if is_recurring:
                        task = RecurringTask(
                            task_title, int(task_duration), task_priority,
                            task_time_pref, frequency="daily",
                            times_per_day=int(times_per_day),
                        )
                    else:
                        task = Task(
                            task_title, int(task_duration), task_priority, task_time_pref
                        )
                    target_pet.add_task(task)
                    st.session_state.schedule = None
                    st.success(f"Added '{task_title}' for {task_pet}!")
                except ValueError as e:
                    st.error(str(e))
    else:
        st.info("Add a pet first, then you can add tasks.")

    st.divider()

    # Scheduling options
    st.subheader("Scheduling")
    sort_strategy = st.selectbox(
        "Sort strategy",
        list(VALID_SORT_STRATEGIES),
        format_func=lambda s: {
            "priority": "Priority (critical first)",
            "duration": "Duration (shortest first)",
            "time_preference": "Time of Day (morning first)",
        }[s],
    )

# ── Main Area ────────────────────────────────────────────────────────

st.title("PawPal+")
st.caption("Smart daily care planning for your pets")

# Show current task summary
if st.session_state.pets:
    st.subheader("Current Tasks by Pet")

    for pet in st.session_state.pets:
        if pet.tasks:
            with st.expander(f"{pet.name} ({pet.species}) — {len(pet.tasks)} tasks", expanded=True):
                task_data = []
                for task in pet.tasks:
                    label = "Recurring" if isinstance(task, RecurringTask) else "One-time"
                    if isinstance(task, RecurringTask):
                        label += f" (x{task.times_per_day}/day)"
                    task_data.append({
                        "Task": task.title,
                        "Duration": f"{task.duration_minutes} min",
                        "Priority": PRIORITY_LABELS[task.priority],
                        "When": task.time_preference.capitalize(),
                        "Type": label,
                    })
                st.table(task_data)
        else:
            st.write(f"**{pet.name}**: No tasks yet.")

    st.divider()

    # Generate Schedule button
    if st.button("Generate Schedule", type="primary", use_container_width=True):
        try:
            owner = Owner(owner_name, available_minutes)
            for pet in st.session_state.pets:
                owner.add_pet(pet)

            scheduler = Scheduler(owner, sort_strategy=sort_strategy)
            schedule = scheduler.build_schedule()
            st.session_state.schedule = (scheduler, schedule)
        except ValueError as e:
            st.error(str(e))

    # Display schedule results
    if st.session_state.schedule:
        scheduler, schedule = st.session_state.schedule

        st.subheader("Daily Care Plan")

        # Metrics row
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Time Used", f"{schedule.total_minutes_used} min")
        with col2:
            st.metric("Available", f"{schedule.available_minutes} min")
        with col3:
            st.metric("Scheduled", len(schedule.scheduled_tasks))
        with col4:
            st.metric("Skipped", len(schedule.skipped_tasks))

        # Timeline table
        timeline = schedule.to_timeline()
        if timeline:
            st.subheader("Timeline")
            timeline_display = []
            for entry in timeline:
                timeline_display.append({
                    "Time": f"{entry['start_time']} - {entry['end_time']}",
                    "Task": entry["task"],
                    "Pet": entry["pet"],
                    "Duration": f"{entry['duration_minutes']} min",
                    "Priority": entry["priority_label"],
                    "Preferred": entry["time_preference"].capitalize(),
                })
            st.table(timeline_display)

        # Skipped tasks warning
        if schedule.skipped_tasks:
            st.subheader("Skipped Tasks")
            st.warning("These tasks did not fit within your available time:")
            for task in schedule.skipped_tasks:
                st.write(
                    f"- **{task.title}** ({task.duration_minutes} min, "
                    f"{PRIORITY_LABELS[task.priority]}) [{task.pet_name}]"
                )

        # Conflicts
        if schedule.conflicts:
            st.subheader("Conflicts Detected")
            for conflict in schedule.conflicts:
                st.error(conflict)

        # Full explanation
        with st.expander("Full Schedule Explanation"):
            st.text(scheduler.explain_schedule(schedule))

else:
    st.info(
        "Add pets and tasks in the sidebar, then click **Generate Schedule** "
        "to build your daily care plan."
    )

# Footer
st.divider()
st.caption("PawPal+ — Built with Python OOP and Streamlit")
