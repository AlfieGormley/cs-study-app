---
id: sepr-kanban-flow
title: Control work in progress and reason about flow
level: intermediate
minutes: 5
summary: Use pull policies and Little’s law with consistent boundaries and long-run averages.
sourceLesson: sepr-agile-estimation
---

Scrum creates a regular inspection rhythm. Kanban focuses on the flow of work and can be used alongside it, especially when arrivals are unpredictable.

## Kanban
Kanban comes from Toyota's production system, where cards ("kanban" means signboard) signalled when to produce more. David J. Anderson adapted it for software in the mid-2000s.

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

The numbers are WIP limits. Dev is full at 3, and Review is full at 2: A and B occupy its two slots. Help finish Review work first. Review may then pull C when its policy allows; finishing C alone does not create Dev capacity until it leaves that stage. Pull from To do only after a Dev slot opens. Keep the card and any delivery blockage visible. This is a **pull system**, not push: work moves when there is capacity downstream. Stop starting, start finishing.

### Little's law

Why limit WIP? **Little's law**, proved by John Little in 1961 for queueing systems, links three averages. It answers the question "if we keep this much work open, how long will each item take on average?" It holds for a stable system over the long run, meaning work leaves at about the rate it arrives, so the queue is not growing without limit:

```formula
L = λ × W
W = L / λ
where
L: the average WIP: how many items are in progress (started but not finished) at any moment, in items
λ: flow-rate lambda, the average throughput: how many items the workflow finishes per unit of time, in items per week
W: the average cycle time: how long one item spends between starting and finishing, in weeks
In words: the average amount of open work equals the finishing rate times the average time each item spends in the system, so with the finishing rate fixed, less open work means each item gets through faster.
```

The second line is the same law rearranged. All three must use the same workflow boundary (say, "from Dev to Done") and the same time unit. The law says nothing about any single item, and a short filling or draining interval cannot be treated as a steady-state forecast without accounting for boundary effects. Temporary variation does not disprove the long-run identity.

> [!example] Halving WIP
> In a stable workflow, average throughput is 4 items a week and average WIP is 12. Then average WIP falls to 6 while throughput stays at 4. A WIP cap is not the measured average, and this does not promise that every item finishes twice as fast.

```formula
W = L / λ
W = 12 items / (4 items per wk)
W = 3 wk
W = 6 items / (4 items per wk)
W = 1.5 wk
where
W: the average cycle time, in weeks (wk)
L: the average WIP, in items: 12 before, 6 after
λ: flow-rate lambda, the average throughput, in items per week; 4 in both cases
items: count of work items inside the workflow boundary
wk: weeks, the unit of time used here
In words: with the finishing rate unchanged, halving the average amount of open work halves the average time an item takes, from 3 weeks to 1.5 weeks.
```

Lower WIP may reduce context switching, but excessive restriction can starve stages and reduce throughput. Measure both flow and capacity.

### Scrum versus Kanban

| | Scrum | Kanban |
|---|---|---|
| Cadence | Fixed Sprints | Continuous flow |
| Roles | PO, SM, Developers | None required |
| Planning focus | Sprint Goal and evolving plan | Flow and WIP policies |
| Useful measures | Goal outcomes and product value | WIP, throughput, work-item age, cycle time |

Kanban suits work that arrives unpredictably (operations, support, platform teams). Scrum suits product development where a regular rhythm of planning and review helps. Kanban can also complement Scrum. Sprint scope may be clarified and renegotiated with the Product Owner as learning occurs without endangering the Sprint Goal.

## Key takeaways
- Pull work only when the receiving stage has capacity under its explicit policies.
- Little’s law links compatible long-run averages; a WIP cap is not the measured average.
- Reducing WIP reduces average cycle time only if throughput remains fixed under the model.

## Further reading
- [The Kanban Guide (May 2025)](https://kanbanguides.org/the-kanban-guide/2025.5/)
- [The official Kanban Guide — Kanban University](https://kanban.university/kanban-guide/)
