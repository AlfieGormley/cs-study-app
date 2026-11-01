---
id: sepr-kanban-flow
title: Control work in progress and reason about flow
level: intermediate
minutes: 5
summary: Use pull policies and WIP limits, and know what Little's law does and does not promise about cycle time.
sourceLesson: sepr-agile-estimation
---

Scrum creates a regular inspection rhythm. Kanban focuses on the flow of work and can be used alongside it, especially when arrivals are unpredictable.

## Kanban
Kanban comes from Toyota's production system, where cards ("kanban" means signboard) signalled when to produce more. David J. Anderson adapted it for software in the mid-2000s.

There is no single official definition: Kanban University's Kanban Method and *The Kanban Guide* (kanbanguides.org) describe different sets of practices and even use different names for similar flow measures.

Kanban does not prescribe roles or iterations. Useful practices include:

1. **Visualise the workflow** on a board, with a column per stage.
2. **Control work in progress (WIP)** with explicit policies; limits may cover individual stages or a larger part of the workflow.
3. **Manage flow**: measure how work moves and remove blockages.
4. **Make policies explicit**, such as what "ready for review" means.
5. **Improve continuously** using data and feedback loops.

```
| To do | Dev (3) | Review (2) | Done |
|-------|---------|------------|------|
| F     | C       | A          | X    |
| G     | D       | B          | Y    |
| H     | E       |            |      |
```

The numbers are WIP limits, and both Dev (3) and Review (2) are full. Rather than starting F, help finish A or B. When one leaves Review, C can move in, which frees a Dev slot for F. This is a **pull system**: work moves only when the next stage has capacity. Stop starting, start finishing.

### Little's law

Why limit WIP? **Little's law**, proved by John Little in 1961 for queueing systems, links three long-run averages. It answers the question "if we keep this much work open, how long will each item take on average?"

```formula essential
L = λ W
where
L: the average WIP: how many items are in progress (started but not finished) at any moment, in items
λ: flow-rate lambda, the average throughput: how many items the workflow finishes per unit of time, in items per week
W: the average cycle time: how long one item spends between starting and finishing, in weeks
In words: the average amount of open work equals the finishing rate multiplied by the average time each item spends in progress, so if the finishing rate stays the same, less open work means each item gets through faster on average.
```

For example, a team that finishes about 4 items a week while keeping about 12 in progress has an average cycle time of about 3 weeks. If it cuts average WIP to 6 and still finishes 4 a week, the average falls to about 1.5 weeks.

What the law does and does not tell you:

- **It is about long-run averages.** It says nothing about any single item, and holds only when work leaves at about the rate it arrives. A few weeks of filling or draining the board are not a steady state.
- **All three numbers must match.** Use the same workflow boundary (say, "from Dev to Done") and the same time unit for each.
- **A WIP cap is not the average WIP.** Setting a limit of 6 does not mean 6 items are open on average.
- **Throughput is not guaranteed to stay fixed.** Lower WIP often reduces context switching, but a limit set too low can starve a stage and cut throughput, so cycle time falls by less than expected. Measure both.

> [!analogy] Real-world analogy: a busy café
> A café serves about 30 customers an hour, and each one spends about 20 minutes inside. On average, then, about 10 customers are in the café at once. If service stays at 30 an hour but each visit stretched to 40 minutes, the room would hold about 20.
>
> **How it maps:** Customers inside are WIP, customers served per hour are throughput, and the time each one spends inside is cycle time. Letting fewer people in at once while serving at the same rate means each spends less time waiting.
>
> **Where it stops:** A café's capacity is mostly the counter; a software team's throughput depends on the work itself, and too few items in progress can leave people idle and lower throughput. The relationship also holds only on average, over a long enough period.

### Scrum versus Kanban

| | Scrum | Kanban |
|---|---|---|
| Cadence | Fixed Sprints | Continuous flow |
| Roles | PO, SM, Developers | None required |
| Planning focus | Sprint Goal and evolving plan | Flow and WIP policies |
| Useful measures | Goal outcomes and product value | WIP, throughput, work-item age, cycle time |

Kanban suits work that arrives unpredictably (operations, support, platform teams); Scrum suits product work that benefits from a regular rhythm of planning and review. The two can be combined, and even within Scrum, Sprint scope can be renegotiated with the Product Owner as long as the Sprint Goal holds.

## Key takeaways
- Pull work only when the receiving stage has capacity under its explicit policies.
- Little’s law links compatible long-run averages; a WIP cap is not the measured average.
- Reducing WIP reduces average cycle time only if throughput holds up; a limit set too low can cut throughput.

## Further reading
- [The Kanban Guide (May 2025)](https://kanbanguides.org/the-kanban-guide/2025.5/)
- [The official Kanban Guide — Kanban University](https://kanban.university/kanban-guide/)
