# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

The initial UML design included six classes: `Task`, `RecurringTask`, `Pet`, `Owner`, `Schedule`, and `Scheduler`. Responsibilities were clearly separated: `Task` and `RecurringTask` represent what needs to be done, `Pet` and `Owner` represent who is involved, `Schedule` holds the output, and `Scheduler` contains the algorithm. The class hierarchy uses inheritance (RecurringTask extends Task) and composition (Owner has Pets, Pets have Tasks).

**b. Design changes**

The main design change was in the scheduling output. Initially, I planned a simple list of scheduled tasks. During implementation, I realized the `Schedule` class needed a separate `skipped_tasks` list alongside `scheduled_tasks` to give users transparency into what was dropped and why. I also added the `to_timeline()` method to Schedule, which wasn't in the original UML, because the Streamlit UI needed time-stamped data to display a readable daily plan.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler considers three constraints:
1. **Time budget** — the owner's available minutes per day is a hard limit
2. **Task priority** — priority 1 (Critical) tasks are scheduled before priority 5 (Optional) tasks
3. **Time preference** — tasks can be tagged as morning/afternoon/evening/any to influence ordering

Priority was the most important constraint because missing a critical task (medication, feeding) has real consequences, while missing an optional task (extra playtime) does not.

**b. Tradeoffs**

The scheduler uses a greedy algorithm: it sorts tasks and fills the schedule in order, skipping any task that would exceed the time budget. This means a large high-priority task might block several smaller lower-priority tasks that could have collectively fit. For example, a 60-minute vet appointment might prevent three 15-minute tasks from being scheduled, even though fitting those three would use more total time. This tradeoff is reasonable because the greedy approach is simple, predictable, and transparent. In a real-world pet care scenario, the owner would rather have critical tasks guaranteed than maximize time usage.

---

## 3. AI Collaboration

**a. How you used AI**

AI tools were used in three phases:
- **Design brainstorming** — generating the class hierarchy and discussing which attributes each class needs
- **Code scaffolding** — producing the initial class structure with type hints, validation, and docstrings
- **Test generation** — creating a comprehensive pytest suite covering validation, edge cases, and integration

The most helpful prompts were specific and constrained, like "design a greedy scheduling algorithm for daily pet care tasks with a time budget" rather than vague requests like "build me a scheduler."

**b. Judgment and verification**

One case where I did not accept the AI suggestion as-is was the scheduling threshold logic. The AI initially suggested a simple threshold (score >= 2 = "schedule") that was too rigid. After running `demo.py` with different sort strategies, I observed that the time-preference sort scheduled morning-heavy tasks at the expense of evening tasks, which wasn't ideal. This led to adding secondary sort keys (priority as tiebreaker within time slots) so that within the same time block, critical tasks still come first. I verified the change by comparing demo output before and after.

---

## 4. Testing and Verification

**a. What you tested**

53 tests cover:
- **Input validation** — invalid priorities (0, 6), negative durations, empty names, bad species
- **RecurringTask expansion** — correct number of expanded tasks, proper title numbering, time slot distribution
- **Pet/Owner aggregation** — tasks correctly associated with pets, cross-pet task collection
- **Schedule budget enforcement** — tasks exceeding time budget are skipped, budget never exceeded
- **Scheduler sorting** — all three strategies produce correctly ordered output
- **Conflict detection** — over-budget and duplicate task warnings
- **Integration** — end-to-end workflow from owner creation through schedule generation

These tests were important because the scheduling algorithm has several interacting parts (expansion, sorting, conflict detection, greedy fill) that could silently produce wrong results without verification.

**b. Confidence**

I am confident the scheduler works correctly for the tested scenarios. The greedy algorithm is deterministic and the test suite covers the main code paths. Edge cases I would test next with more time:
- Very large numbers of tasks (100+) to check performance
- All tasks having the same priority (tiebreaker behavior)
- Multiple recurring tasks for the same pet with overlapping time preferences
- Boundary case where total task time exactly equals available time

---

## 5. Reflection

**a. What went well**

The "CLI-first" workflow was very effective. Building `demo.py` before touching the Streamlit UI caught several issues early — like RecurringTask expansion creating too many time slots and the greedy algorithm not properly tracking remaining time. By the time the UI was connected, the backend was already solid.

**b. What you would improve**

If I had another iteration, I would:
- Add a **drag-and-drop reorder** feature in the Streamlit UI so owners can manually adjust the schedule
- Implement a **knapsack algorithm** as an alternative to greedy — it would maximize total time usage at the cost of simplicity
- Add **persistent storage** (SQLite or JSON) so the owner's pets and tasks survive page refreshes

**c. Key takeaway**

The most important lesson was that **separation of concerns** makes everything easier. By keeping the scheduling logic in `pawpal_system.py` with zero UI dependencies, the same backend powered the CLI demo, the test suite, and the Streamlit app. When the UI needed changes, the backend didn't change at all. This modularity is what makes real systems maintainable.

---
