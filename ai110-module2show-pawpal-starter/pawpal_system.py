"""
PawPal+ Backend System

Core classes for the PawPal+ pet care scheduling application.
Handles task management, pet/owner modeling, and daily schedule generation
using a greedy priority-based algorithm.

Classes:
    Task            -- A single pet care activity with duration and priority.
    RecurringTask   -- A Task that repeats multiple times per day.
    Pet             -- A pet with a list of care tasks.
    Owner           -- A pet owner with available time and one or more pets.
    Schedule        -- The output of the scheduler: ordered tasks + explanation.
    Scheduler       -- Builds an optimized daily schedule from an Owner's tasks.
"""

from __future__ import annotations
from typing import List, Optional


# ── Constants ────────────────────────────────────────────────────────

VALID_TIME_PREFERENCES = ("morning", "afternoon", "evening", "any")
VALID_FREQUENCIES = ("daily", "weekly")
VALID_SPECIES = ("dog", "cat", "bird", "fish", "rabbit", "other")
VALID_SORT_STRATEGIES = ("priority", "duration", "time_preference")

TIME_ORDER = {"morning": 0, "afternoon": 1, "evening": 2, "any": 3}
PRIORITY_LABELS = {1: "Critical", 2: "High", 3: "Medium", 4: "Low", 5: "Optional"}


# ── Task ─────────────────────────────────────────────────────────────

class Task:
    """A single pet care task with a title, duration, priority, and time preference."""

    def __init__(
        self,
        title: str,
        duration_minutes: int,
        priority: int = 3,
        time_preference: str = "any",
        pet_name: str = "",
    ) -> None:
        if not title.strip():
            raise ValueError("Task title cannot be empty.")
        if duration_minutes <= 0:
            raise ValueError(f"Duration must be positive, got {duration_minutes}.")
        if priority < 1 or priority > 5:
            raise ValueError(f"Priority must be 1-5, got {priority}.")
        if time_preference not in VALID_TIME_PREFERENCES:
            raise ValueError(
                f"Invalid time_preference '{time_preference}'. "
                f"Choose from {VALID_TIME_PREFERENCES}."
            )

        self.title = title.strip()
        self.duration_minutes = duration_minutes
        self.priority = priority
        self.time_preference = time_preference
        self.pet_name = pet_name
        self.completed = False

    def mark_complete(self) -> None:
        self.completed = True

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "duration_minutes": self.duration_minutes,
            "priority": self.priority,
            "priority_label": PRIORITY_LABELS.get(self.priority, "Unknown"),
            "time_preference": self.time_preference,
            "pet_name": self.pet_name,
            "completed": self.completed,
        }

    def __repr__(self) -> str:
        return (
            f"Task('{self.title}', {self.duration_minutes}min, "
            f"priority={self.priority}, {self.time_preference})"
        )


# ── RecurringTask ────────────────────────────────────────────────────

class RecurringTask(Task):
    """A task that repeats multiple times per day (e.g., feeding, walks)."""

    def __init__(
        self,
        title: str,
        duration_minutes: int,
        priority: int = 3,
        time_preference: str = "any",
        pet_name: str = "",
        frequency: str = "daily",
        times_per_day: int = 1,
    ) -> None:
        super().__init__(title, duration_minutes, priority, time_preference, pet_name)

        if frequency not in VALID_FREQUENCIES:
            raise ValueError(
                f"Invalid frequency '{frequency}'. Choose from {VALID_FREQUENCIES}."
            )
        if times_per_day < 1:
            raise ValueError(f"times_per_day must be >= 1, got {times_per_day}.")

        self.frequency = frequency
        self.times_per_day = times_per_day

    def expand(self) -> List[Task]:
        """Expand this recurring task into concrete Task instances.

        Distributes time preferences across morning/afternoon/evening
        to spread tasks throughout the day.
        """
        if self.times_per_day == 1:
            return [Task(
                self.title, self.duration_minutes, self.priority,
                self.time_preference, self.pet_name,
            )]

        time_slots = ["morning", "afternoon", "evening"]
        tasks = []
        for i in range(self.times_per_day):
            slot = time_slots[i % len(time_slots)]
            tasks.append(Task(
                f"{self.title} ({i + 1} of {self.times_per_day})",
                self.duration_minutes,
                self.priority,
                slot,
                self.pet_name,
            ))
        return tasks

    def __repr__(self) -> str:
        return (
            f"RecurringTask('{self.title}', {self.duration_minutes}min, "
            f"priority={self.priority}, {self.frequency}, "
            f"x{self.times_per_day}/day)"
        )


# ── Pet ──────────────────────────────────────────────────────────────

class Pet:
    """A pet with a name, species, and a list of care tasks."""

    def __init__(
        self,
        name: str,
        species: str,
        age: int = 1,
        special_needs: Optional[List[str]] = None,
    ) -> None:
        if not name.strip():
            raise ValueError("Pet name cannot be empty.")
        if species.lower() not in VALID_SPECIES:
            raise ValueError(
                f"Invalid species '{species}'. Choose from {VALID_SPECIES}."
            )
        if age < 0:
            raise ValueError(f"Age must be non-negative, got {age}.")

        self.name = name.strip()
        self.species = species.lower()
        self.age = age
        self.special_needs = special_needs or []
        self.tasks: List[Task] = []

    def add_task(self, task: Task) -> None:
        task.pet_name = self.name
        self.tasks.append(task)

    def remove_task(self, title: str) -> bool:
        for i, task in enumerate(self.tasks):
            if task.title == title:
                self.tasks.pop(i)
                return True
        return False

    def get_tasks_by_priority(self) -> List[Task]:
        return sorted(self.tasks, key=lambda t: t.priority)

    def __repr__(self) -> str:
        return f"Pet('{self.name}', {self.species}, age={self.age}, tasks={len(self.tasks)})"


# ── Owner ────────────────────────────────────────────────────────────

class Owner:
    """A pet owner with a daily time budget and one or more pets."""

    def __init__(self, name: str, available_minutes: int = 120) -> None:
        if not name.strip():
            raise ValueError("Owner name cannot be empty.")
        if available_minutes <= 0:
            raise ValueError(f"Available minutes must be positive, got {available_minutes}.")

        self.name = name.strip()
        self.available_minutes = available_minutes
        self.pets: List[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        self.pets.append(pet)

    def remove_pet(self, name: str) -> bool:
        for i, pet in enumerate(self.pets):
            if pet.name == name:
                self.pets.pop(i)
                return True
        return False

    def get_all_tasks(self) -> List[Task]:
        all_tasks = []
        for pet in self.pets:
            all_tasks.extend(pet.tasks)
        return all_tasks

    def total_task_duration(self) -> int:
        return sum(t.duration_minutes for t in self.get_all_tasks())

    def __repr__(self) -> str:
        return (
            f"Owner('{self.name}', {self.available_minutes}min, "
            f"pets={len(self.pets)})"
        )


# ── Schedule ─────────────────────────────────────────────────────────

class Schedule:
    """The result of running the scheduler: an ordered list of tasks
    that fit within the time budget, plus skipped tasks and explanations."""

    def __init__(self, available_minutes: int) -> None:
        self.available_minutes = available_minutes
        self.scheduled_tasks: List[Task] = []
        self.skipped_tasks: List[Task] = []
        self.total_minutes_used = 0
        self.conflicts: List[str] = []

    def add_task(self, task: Task) -> bool:
        """Try to add a task to the schedule. Returns True if it fits."""
        if self.total_minutes_used + task.duration_minutes <= self.available_minutes:
            self.scheduled_tasks.append(task)
            self.total_minutes_used += task.duration_minutes
            return True
        else:
            self.skipped_tasks.append(task)
            return False

    def has_conflict(self) -> bool:
        return len(self.skipped_tasks) > 0 or len(self.conflicts) > 0

    def get_explanation(self) -> str:
        """Return a human-readable explanation of the schedule."""
        lines = []
        lines.append(f"Schedule: {self.total_minutes_used}/{self.available_minutes} minutes used")
        lines.append(f"Tasks scheduled: {len(self.scheduled_tasks)}, "
                      f"Tasks skipped: {len(self.skipped_tasks)}")
        lines.append("")

        if self.scheduled_tasks:
            lines.append("SCHEDULED:")
            for i, task in enumerate(self.scheduled_tasks, 1):
                label = PRIORITY_LABELS.get(task.priority, "?")
                lines.append(
                    f"  {i}. {task.title} ({task.duration_minutes}min, "
                    f"{label} priority, {task.time_preference}) "
                    f"[{task.pet_name}]"
                )

        if self.skipped_tasks:
            lines.append("")
            lines.append("SKIPPED (not enough time):")
            for task in self.skipped_tasks:
                label = PRIORITY_LABELS.get(task.priority, "?")
                lines.append(
                    f"  - {task.title} ({task.duration_minutes}min, "
                    f"{label} priority) [{task.pet_name}]"
                )

        if self.conflicts:
            lines.append("")
            lines.append("CONFLICTS:")
            for conflict in self.conflicts:
                lines.append(f"  ! {conflict}")

        return "\n".join(lines)

    def to_timeline(self, start_hour: int = 8) -> List[dict]:
        """Convert scheduled tasks into a timeline with start/end times."""
        timeline = []
        current_minutes = start_hour * 60  # minutes since midnight

        for task in self.scheduled_tasks:
            start_h, start_m = divmod(current_minutes, 60)
            end_minutes = current_minutes + task.duration_minutes
            end_h, end_m = divmod(end_minutes, 60)

            timeline.append({
                "task": task.title,
                "pet": task.pet_name,
                "start_time": f"{start_h:02d}:{start_m:02d}",
                "end_time": f"{end_h:02d}:{end_m:02d}",
                "duration_minutes": task.duration_minutes,
                "priority": task.priority,
                "priority_label": PRIORITY_LABELS.get(task.priority, "?"),
                "time_preference": task.time_preference,
            })
            current_minutes = end_minutes

        return timeline

    def __repr__(self) -> str:
        return (
            f"Schedule({len(self.scheduled_tasks)} tasks, "
            f"{self.total_minutes_used}/{self.available_minutes}min)"
        )


# ── Scheduler ────────────────────────────────────────────────────────

class Scheduler:
    """Builds an optimized daily schedule for a pet owner.

    Uses a greedy algorithm: tasks are sorted by the chosen strategy,
    then packed into the available time budget in order. Tasks that
    don't fit are recorded as skipped.
    """

    def __init__(self, owner: Owner, sort_strategy: str = "priority") -> None:
        if sort_strategy not in VALID_SORT_STRATEGIES:
            raise ValueError(
                f"Invalid sort_strategy '{sort_strategy}'. "
                f"Choose from {VALID_SORT_STRATEGIES}."
            )
        self.owner = owner
        self.sort_strategy = sort_strategy

    def _expand_recurring(self, tasks: List[Task]) -> List[Task]:
        """Replace RecurringTask instances with their expanded concrete tasks."""
        expanded = []
        for task in tasks:
            if isinstance(task, RecurringTask):
                expanded.extend(task.expand())
            else:
                expanded.append(task)
        return expanded

    def _sort_tasks(self, tasks: List[Task]) -> List[Task]:
        """Sort tasks by the selected strategy.

        - priority: ascending by priority number (1 = Critical first)
        - duration: ascending by duration (shortest first)
        - time_preference: morning → afternoon → evening → any, then by priority
        """
        if self.sort_strategy == "priority":
            return sorted(tasks, key=lambda t: (t.priority, t.duration_minutes))
        elif self.sort_strategy == "duration":
            return sorted(tasks, key=lambda t: (t.duration_minutes, t.priority))
        elif self.sort_strategy == "time_preference":
            return sorted(tasks, key=lambda t: (TIME_ORDER[t.time_preference], t.priority))
        return tasks

    def _detect_conflicts(self, tasks: List[Task]) -> List[str]:
        """Check for scheduling conflicts before building the schedule."""
        conflicts = []

        # Check total duration vs available time
        total = sum(t.duration_minutes for t in tasks)
        if total > self.owner.available_minutes:
            conflicts.append(
                f"Total task duration ({total}min) exceeds available time "
                f"({self.owner.available_minutes}min). "
                f"Some tasks will be skipped."
            )

        # Check for duplicate task titles per pet
        seen = set()
        for task in tasks:
            key = (task.pet_name, task.title)
            if key in seen:
                conflicts.append(
                    f"Duplicate task '{task.title}' for pet '{task.pet_name}'."
                )
            seen.add(key)

        return conflicts

    def build_schedule(self) -> Schedule:
        """Build an optimized daily schedule using a greedy algorithm.

        Steps:
        1. Gather all tasks from the owner's pets
        2. Expand recurring tasks into concrete instances
        3. Sort by the selected strategy
        4. Detect conflicts
        5. Greedily pack tasks into the time budget
        """
        all_tasks = self.owner.get_all_tasks()
        expanded = self._expand_recurring(all_tasks)
        sorted_tasks = self._sort_tasks(expanded)
        conflicts = self._detect_conflicts(sorted_tasks)

        schedule = Schedule(self.owner.available_minutes)
        schedule.conflicts = conflicts

        for task in sorted_tasks:
            schedule.add_task(task)

        return schedule

    def explain_schedule(self, schedule: Schedule) -> str:
        """Return a full explanation of the schedule with a header."""
        header = (
            f"Daily Care Plan for {self.owner.name}\n"
            f"Strategy: sort by {self.sort_strategy}\n"
            f"{'=' * 45}\n"
        )
        return header + schedule.get_explanation()
