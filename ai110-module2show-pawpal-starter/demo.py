"""
PawPal+ CLI Demo

Verifies the backend scheduling logic without any UI dependencies.
Run with: python demo.py
"""

from pawpal_system import Task, RecurringTask, Pet, Owner, Scheduler


def main() -> None:
    print("=" * 50)
    print("  PawPal+ CLI Demo")
    print("=" * 50)

    # ── Create owner ──────────────────────────────────
    owner = Owner("Jordan", available_minutes=120)
    print(f"\nOwner: {owner}")

    # ── Create pets ───────────────────────────────────
    mochi = Pet("Mochi", "dog", age=3, special_needs=["joint supplement"])
    whiskers = Pet("Whiskers", "cat", age=5)

    owner.add_pet(mochi)
    owner.add_pet(whiskers)
    print(f"Pets: {mochi}, {whiskers}")

    # ── Add tasks to Mochi (dog) ──────────────────────
    mochi.add_task(RecurringTask(
        "Walk", 30, priority=1, time_preference="morning",
        frequency="daily", times_per_day=2,
    ))
    mochi.add_task(RecurringTask(
        "Feed", 10, priority=1, time_preference="any",
        frequency="daily", times_per_day=2,
    ))
    mochi.add_task(Task("Brush teeth", 10, priority=3, time_preference="evening"))
    mochi.add_task(Task("Play fetch", 20, priority=4, time_preference="afternoon"))
    mochi.add_task(Task("Vet appointment", 60, priority=2, time_preference="morning"))

    # ── Add tasks to Whiskers (cat) ───────────────────
    whiskers.add_task(RecurringTask(
        "Feed", 5, priority=1, time_preference="any",
        frequency="daily", times_per_day=2,
    ))
    whiskers.add_task(Task("Clean litter box", 10, priority=2, time_preference="morning"))
    whiskers.add_task(Task("Playtime", 15, priority=3, time_preference="afternoon"))

    # ── Show all tasks ────────────────────────────────
    all_tasks = owner.get_all_tasks()
    total = owner.total_task_duration()
    print(f"\nTotal tasks: {len(all_tasks)}")
    print(f"Total duration (before recurring expansion): {total} minutes")
    print(f"Available time: {owner.available_minutes} minutes")

    # ── Build schedule (sort by priority) ─────────────
    print("\n" + "=" * 50)
    print("  Schedule #1: Sort by PRIORITY")
    print("=" * 50)

    scheduler = Scheduler(owner, sort_strategy="priority")
    schedule = scheduler.build_schedule()
    print(scheduler.explain_schedule(schedule))

    # ── Show timeline ─────────────────────────────────
    print("\nTimeline:")
    for entry in schedule.to_timeline():
        print(
            f"  {entry['start_time']} - {entry['end_time']}  "
            f"{entry['task']} [{entry['pet']}] "
            f"({entry['priority_label']})"
        )

    # ── Build schedule (sort by duration) ─────────────
    print("\n" + "=" * 50)
    print("  Schedule #2: Sort by DURATION (shortest first)")
    print("=" * 50)

    scheduler2 = Scheduler(owner, sort_strategy="duration")
    schedule2 = scheduler2.build_schedule()
    print(scheduler2.explain_schedule(schedule2))

    # ── Build schedule (sort by time preference) ──────
    print("\n" + "=" * 50)
    print("  Schedule #3: Sort by TIME PREFERENCE")
    print("=" * 50)

    scheduler3 = Scheduler(owner, sort_strategy="time_preference")
    schedule3 = scheduler3.build_schedule()
    print(scheduler3.explain_schedule(schedule3))

    print("\n" + "=" * 50)
    print("  Demo complete!")
    print("=" * 50)


if __name__ == "__main__":
    main()
