---
id: tech-greedy-exchange
title: Proving earliest-finish greedy
level: intermediate
minutes: 2
sourceLesson: tech-greedy
summary: Swap the earliest-finishing meeting into an optimal solution without losing later meetings.
---

The previous unit schedules positive-duration half-open intervals by earliest finish time. This unit proves that this rule maximises the number accepted; it does not yet assert any guarantee about meetings with different values.

### Why it's correct: the exchange argument

The standard proof technique for greedy is the **exchange argument**: take any optimal solution, and show you can swap in the greedy choice without making it worse.

1. Let g be the meeting with the earliest finish time overall.
2. Take any optimal schedule O, and let o be its first meeting.
3. Since g finishes earliest of all, it ends no later than o.
4. Replace o with g. Every other meeting in O starts at or after the end of o, which is at or after the end of g, so none of them overlap g:

```formula
e_g ≤ e_o ≤ s_x
where
e_g: the end time of g, the meeting that finishes first overall
e_o: the end time of o, the first meeting in the optimal schedule O
s_x: the start time of any other meeting x in O
≤: is at or before (less than or equal to)
In words: g ends no later than o, and every later meeting in O starts no earlier than o ends, so swapping o for g creates no clash.
```

5. The new schedule is still valid and has the same size: it's also optimal, and it starts with g.

So the greedy first choice is safe (greedy choice property). After choosing g, the remaining problem is "schedule the meetings starting at or after the end of g", the same problem on a smaller input (optimal substructure). Induction finishes the proof.

A related proof style is **greedy stays ahead**: show that after k steps, greedy's k-th meeting ends no later than the k-th meeting of any other valid schedule. Then greedy can never fall behind, so it fits at least as many.

## Key takeaways
- Swap the earliest-finishing meeting into an optimal solution without losing later meetings.
- The remaining compatible meetings form the same problem, so induction completes the proof.

## Further reading
- [Greedy correctness — Erickson](https://jeffe.cs.illinois.edu/teaching/algorithms/book/04-greedy.pdf)
