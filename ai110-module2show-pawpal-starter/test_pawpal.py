"""
PawPal+ Test Suite

Verifies all backend classes and the scheduling algorithm.
Run with: pytest test_pawpal.py -v
"""

import pytest
from pawpal_system import (
    Task, RecurringTask, Pet, Owner, Schedule, Scheduler,
    VALID_TIME_PREFERENCES, VALID_SORT_STRATEGIES,
)


# ── Task Tests ───────────────────────────────────────────────────────

class TestTask:
    def test_creation(self):
        t = Task("Walk", 30, priority=1, time_preference="morning", pet_name="Mochi")
        assert t.title == "Walk"
        assert t.duration_minutes == 30
        assert t.priority == 1
        assert t.time_preference == "morning"
        assert t.pet_name == "Mochi"
        assert t.completed is False

    def test_default_values(self):
        t = Task("Feed", 10)
        assert t.priority == 3
        assert t.time_preference == "any"
        assert t.pet_name == ""

    def test_invalid_priority_low(self):
        with pytest.raises(ValueError, match="Priority must be 1-5"):
            Task("Walk", 30, priority=0)

    def test_invalid_priority_high(self):
        with pytest.raises(ValueError, match="Priority must be 1-5"):
            Task("Walk", 30, priority=6)

    def test_invalid_duration(self):
        with pytest.raises(ValueError, match="Duration must be positive"):
            Task("Walk", -5)

    def test_zero_duration(self):
        with pytest.raises(ValueError, match="Duration must be positive"):
            Task("Walk", 0)

    def test_invalid_time_preference(self):
        with pytest.raises(ValueError, match="Invalid time_preference"):
            Task("Walk", 30, time_preference="midnight")

    def test_empty_title(self):
        with pytest.raises(ValueError, match="title cannot be empty"):
            Task("", 30)

    def test_mark_complete(self):
        t = Task("Walk", 30)
        t.mark_complete()
        assert t.completed is True

    def test_to_dict(self):
        t = Task("Walk", 30, priority=1, time_preference="morning", pet_name="Mochi")
        d = t.to_dict()
        assert d["title"] == "Walk"
        assert d["duration_minutes"] == 30
        assert d["priority"] == 1
        assert d["priority_label"] == "Critical"
        assert d["time_preference"] == "morning"
        assert d["pet_name"] == "Mochi"
        assert d["completed"] is False

    def test_repr(self):
        t = Task("Walk", 30, priority=1, time_preference="morning")
        assert "Walk" in repr(t)
        assert "30min" in repr(t)


# ── RecurringTask Tests ──────────────────────────────────────────────

class TestRecurringTask:
    def test_creation(self):
        rt = RecurringTask("Feed", 10, priority=1, frequency="daily", times_per_day=3)
        assert rt.frequency == "daily"
        assert rt.times_per_day == 3

    def test_is_task(self):
        rt = RecurringTask("Feed", 10)
        assert isinstance(rt, Task)

    def test_expand_single(self):
        rt = RecurringTask("Feed", 10, times_per_day=1)
        expanded = rt.expand()
        assert len(expanded) == 1
        assert expanded[0].title == "Feed"

    def test_expand_multiple(self):
        rt = RecurringTask("Feed", 10, priority=1, times_per_day=3, pet_name="Mochi")
        expanded = rt.expand()
        assert len(expanded) == 3
        assert expanded[0].title == "Feed (1 of 3)"
        assert expanded[1].title == "Feed (2 of 3)"
        assert expanded[2].title == "Feed (3 of 3)"

    def test_expand_distributes_time_slots(self):
        rt = RecurringTask("Feed", 10, times_per_day=3)
        expanded = rt.expand()
        assert expanded[0].time_preference == "morning"
        assert expanded[1].time_preference == "afternoon"
        assert expanded[2].time_preference == "evening"

    def test_expand_preserves_pet_name(self):
        rt = RecurringTask("Feed", 10, pet_name="Mochi", times_per_day=2)
        expanded = rt.expand()
        assert all(t.pet_name == "Mochi" for t in expanded)

    def test_invalid_frequency(self):
        with pytest.raises(ValueError, match="Invalid frequency"):
            RecurringTask("Feed", 10, frequency="monthly")

    def test_invalid_times_per_day(self):
        with pytest.raises(ValueError, match="times_per_day must be >= 1"):
            RecurringTask("Feed", 10, times_per_day=0)


# ── Pet Tests ────────────────────────────────────────────────────────

class TestPet:
    def test_creation(self):
        p = Pet("Mochi", "dog", age=3, special_needs=["medication"])
        assert p.name == "Mochi"
        assert p.species == "dog"
        assert p.age == 3
        assert p.special_needs == ["medication"]
        assert p.tasks == []

    def test_add_task(self):
        p = Pet("Mochi", "dog")
        t = Task("Walk", 30)
        p.add_task(t)
        assert len(p.tasks) == 1
        assert p.tasks[0].title == "Walk"

    def test_add_task_sets_pet_name(self):
        p = Pet("Mochi", "dog")
        t = Task("Walk", 30)
        p.add_task(t)
        assert t.pet_name == "Mochi"

    def test_remove_task(self):
        p = Pet("Mochi", "dog")
        p.add_task(Task("Walk", 30))
        assert p.remove_task("Walk") is True
        assert len(p.tasks) == 0

    def test_remove_nonexistent_task(self):
        p = Pet("Mochi", "dog")
        assert p.remove_task("Fly") is False

    def test_get_tasks_by_priority(self):
        p = Pet("Mochi", "dog")
        p.add_task(Task("Play", 20, priority=4))
        p.add_task(Task("Feed", 10, priority=1))
        p.add_task(Task("Brush", 10, priority=3))
        sorted_tasks = p.get_tasks_by_priority()
        assert [t.priority for t in sorted_tasks] == [1, 3, 4]

    def test_invalid_species(self):
        with pytest.raises(ValueError, match="Invalid species"):
            Pet("Mochi", "dragon")

    def test_empty_name(self):
        with pytest.raises(ValueError, match="Pet name cannot be empty"):
            Pet("", "dog")


# ── Owner Tests ──────────────────────────────────────────────────────

class TestOwner:
    def test_creation(self):
        o = Owner("Jordan", 120)
        assert o.name == "Jordan"
        assert o.available_minutes == 120
        assert o.pets == []

    def test_add_pet(self):
        o = Owner("Jordan")
        p = Pet("Mochi", "dog")
        o.add_pet(p)
        assert len(o.pets) == 1

    def test_remove_pet(self):
        o = Owner("Jordan")
        o.add_pet(Pet("Mochi", "dog"))
        assert o.remove_pet("Mochi") is True
        assert len(o.pets) == 0

    def test_get_all_tasks(self):
        o = Owner("Jordan")
        p1 = Pet("Mochi", "dog")
        p2 = Pet("Whiskers", "cat")
        p1.add_task(Task("Walk", 30))
        p1.add_task(Task("Feed", 10))
        p2.add_task(Task("Play", 15))
        o.add_pet(p1)
        o.add_pet(p2)
        assert len(o.get_all_tasks()) == 3

    def test_total_task_duration(self):
        o = Owner("Jordan")
        p = Pet("Mochi", "dog")
        p.add_task(Task("Walk", 30))
        p.add_task(Task("Feed", 10))
        o.add_pet(p)
        assert o.total_task_duration() == 40

    def test_empty_name(self):
        with pytest.raises(ValueError, match="Owner name cannot be empty"):
            Owner("")

    def test_invalid_minutes(self):
        with pytest.raises(ValueError, match="Available minutes must be positive"):
            Owner("Jordan", 0)


# ── Schedule Tests ───────────────────────────────────────────────────

class TestSchedule:
    def test_add_within_budget(self):
        s = Schedule(60)
        assert s.add_task(Task("Walk", 30)) is True
        assert s.total_minutes_used == 30
        assert len(s.scheduled_tasks) == 1

    def test_add_exceeds_budget(self):
        s = Schedule(60)
        s.add_task(Task("Walk", 50))
        assert s.add_task(Task("Play", 20)) is False
        assert len(s.skipped_tasks) == 1
        assert s.total_minutes_used == 50

    def test_add_exactly_fills_budget(self):
        s = Schedule(30)
        assert s.add_task(Task("Walk", 30)) is True
        assert s.total_minutes_used == 30

    def test_has_conflict_when_skipped(self):
        s = Schedule(10)
        s.add_task(Task("Walk", 30))  # skipped
        assert s.has_conflict() is True

    def test_no_conflict_when_all_fit(self):
        s = Schedule(100)
        s.add_task(Task("Walk", 30))
        assert s.has_conflict() is False

    def test_get_explanation_nonempty(self):
        s = Schedule(60)
        s.add_task(Task("Walk", 30, pet_name="Mochi"))
        explanation = s.get_explanation()
        assert "Walk" in explanation
        assert "SCHEDULED" in explanation

    def test_to_timeline(self):
        s = Schedule(120)
        s.add_task(Task("Walk", 30, pet_name="Mochi"))
        s.add_task(Task("Feed", 10, pet_name="Mochi"))
        timeline = s.to_timeline(start_hour=8)
        assert len(timeline) == 2
        assert timeline[0]["start_time"] == "08:00"
        assert timeline[0]["end_time"] == "08:30"
        assert timeline[1]["start_time"] == "08:30"
        assert timeline[1]["end_time"] == "08:40"

    def test_to_timeline_keys(self):
        s = Schedule(60)
        s.add_task(Task("Walk", 30, pet_name="Mochi"))
        entry = s.to_timeline()[0]
        assert "task" in entry
        assert "pet" in entry
        assert "start_time" in entry
        assert "end_time" in entry


# ── Scheduler Tests ──────────────────────────────────────────────────

class TestScheduler:
    def _make_owner_with_tasks(self) -> Owner:
        """Helper: create an owner with a dog that has several tasks."""
        owner = Owner("Jordan", available_minutes=60)
        pet = Pet("Mochi", "dog")
        pet.add_task(Task("Walk", 30, priority=1, time_preference="morning"))
        pet.add_task(Task("Feed", 10, priority=1, time_preference="morning"))
        pet.add_task(Task("Play", 20, priority=3, time_preference="afternoon"))
        pet.add_task(Task("Brush", 10, priority=4, time_preference="evening"))
        owner.add_pet(pet)
        return owner

    def test_build_basic(self):
        owner = Owner("Jordan", available_minutes=200)
        pet = Pet("Mochi", "dog")
        pet.add_task(Task("Walk", 30, priority=1))
        pet.add_task(Task("Feed", 10, priority=2))
        owner.add_pet(pet)
        scheduler = Scheduler(owner)
        schedule = scheduler.build_schedule()
        assert len(schedule.scheduled_tasks) == 2
        assert len(schedule.skipped_tasks) == 0

    def test_build_overflow(self):
        owner = self._make_owner_with_tasks()  # 70min of tasks, 60min budget
        scheduler = Scheduler(owner, sort_strategy="priority")
        schedule = scheduler.build_schedule()
        assert len(schedule.skipped_tasks) > 0
        # High priority tasks should be scheduled first
        for task in schedule.scheduled_tasks:
            for skipped in schedule.skipped_tasks:
                assert task.priority <= skipped.priority

    def test_sort_by_priority(self):
        owner = self._make_owner_with_tasks()
        scheduler = Scheduler(owner, sort_strategy="priority")
        tasks = scheduler._sort_tasks(owner.get_all_tasks())
        priorities = [t.priority for t in tasks]
        assert priorities == sorted(priorities)

    def test_sort_by_duration(self):
        owner = self._make_owner_with_tasks()
        scheduler = Scheduler(owner, sort_strategy="duration")
        tasks = scheduler._sort_tasks(owner.get_all_tasks())
        durations = [t.duration_minutes for t in tasks]
        assert durations == sorted(durations)

    def test_sort_by_time_preference(self):
        owner = self._make_owner_with_tasks()
        scheduler = Scheduler(owner, sort_strategy="time_preference")
        tasks = scheduler._sort_tasks(owner.get_all_tasks())
        prefs = [t.time_preference for t in tasks]
        assert prefs.index("morning") < prefs.index("afternoon")

    def test_recurring_expansion(self):
        owner = Owner("Jordan", available_minutes=200)
        pet = Pet("Mochi", "dog")
        pet.add_task(RecurringTask("Feed", 10, times_per_day=3))
        owner.add_pet(pet)
        scheduler = Scheduler(owner)
        schedule = scheduler.build_schedule()
        # 1 RecurringTask should expand into 3 scheduled tasks
        assert len(schedule.scheduled_tasks) == 3

    def test_conflict_detection(self):
        owner = self._make_owner_with_tasks()
        scheduler = Scheduler(owner)
        tasks = owner.get_all_tasks()
        conflicts = scheduler._detect_conflicts(tasks)
        assert len(conflicts) > 0  # 70min > 60min budget
        assert "exceeds" in conflicts[0].lower()

    def test_explain_schedule(self):
        owner = self._make_owner_with_tasks()
        scheduler = Scheduler(owner)
        schedule = scheduler.build_schedule()
        explanation = scheduler.explain_schedule(schedule)
        assert "Jordan" in explanation
        assert "priority" in explanation.lower()

    def test_invalid_sort_strategy(self):
        owner = Owner("Jordan")
        with pytest.raises(ValueError, match="Invalid sort_strategy"):
            Scheduler(owner, sort_strategy="random")

    def test_scheduled_never_exceeds_budget(self):
        owner = self._make_owner_with_tasks()
        scheduler = Scheduler(owner)
        schedule = scheduler.build_schedule()
        assert schedule.total_minutes_used <= owner.available_minutes


# ── Integration Test ─────────────────────────────────────────────────

class TestIntegration:
    def test_full_workflow(self):
        """End-to-end: owner, pets, tasks (including recurring), schedule."""
        owner = Owner("Jordan", available_minutes=90)
        dog = Pet("Mochi", "dog", age=3)
        cat = Pet("Whiskers", "cat", age=5)

        dog.add_task(RecurringTask("Walk", 20, priority=1, times_per_day=2))
        dog.add_task(Task("Feed", 10, priority=1))
        cat.add_task(Task("Feed", 5, priority=1))
        cat.add_task(Task("Play", 15, priority=3))

        owner.add_pet(dog)
        owner.add_pet(cat)

        scheduler = Scheduler(owner, sort_strategy="priority")
        schedule = scheduler.build_schedule()

        # All tasks accounted for
        total_tasks = len(schedule.scheduled_tasks) + len(schedule.skipped_tasks)
        assert total_tasks == 5  # 2 walks (expanded) + Feed + Feed + Play

        # Budget respected
        assert schedule.total_minutes_used <= owner.available_minutes

        # Timeline is sequential
        timeline = schedule.to_timeline()
        for i in range(1, len(timeline)):
            assert timeline[i]["start_time"] >= timeline[i - 1]["end_time"]
