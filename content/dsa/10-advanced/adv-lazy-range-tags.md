---
id: adv-lazy-range-tags
title: Lazy range updates and deferred tags
level: advanced
minutes: 2
summary: A fully covered node updates its summary immediately.
sourceLesson: adv-segment-trees
---

Here n is the non-empty input array’s length. Big-O bounds count constant-time combines of constant-size summaries on word-sized values.

## Lazy propagation: updating whole ranges

Now add a third request: “add the same amount to every element in this range”. Running a separate point update for each element repeats many root-to-leaf traversals and can take O(n log n) for a whole-array update.

**Lazy propagation** stops at fully covered nodes. It updates the node's summary immediately, then leaves a **pending tag** recording work still owed to its children. For a sum, add the increment once per covered element; for the tag, accumulate the increment once.

For example, adding five to four zeros makes the covering node's sum twenty and its pending addition five. Its children remain untouched. A later operation must push that addition before descending into them, so stale child summaries never answer a query directly.

> [!analogy] Real-world analogy: A team-wide instruction
> A manager records a change for an entire team, passing it to subteams only when their individual records are needed.
>
> **How it maps:** The parent already records the team's new total; the pending instruction represents updates still owed to children. Descending requires passing the instruction on first.
>
> **Where it stops:** This works only when the summary can be updated without inspecting each member and instructions can be combined correctly. Arbitrary data changes do not have those properties.

## Key takeaways

- A fully covered node updates its summary immediately.
- A pending tag records work still owed to the children.

## Further reading
- [Segment trees — cp-algorithms](https://cp-algorithms.com/data_structures/segment_tree.html)
