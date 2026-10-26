---
id: disc-derangements-surjections
title: "Derangements and onto assignments"
level: intermediate
minutes: 2
summary: "Derangements exclude every fixed point by inclusion–exclusion."
sourceLesson: disc-inclusion-recurrences
---

### Derangements

A **derangement** is a permutation where nothing stays in its original place: every guest leaves with someone else's coat, or every reviewer gets someone else's pull request.

The forbidden event for each person is receiving their own item. Those events can happen together.

Start with all assignments. For each person, exclude assignments with that self-review. Those forbidden groups overlap: an assignment with two self-reviews was removed twice, so restore their intersection. Continue alternating for larger overlaps.

For a uniformly random permutation, the fraction with no fixed points approaches about 36.8% as the number of items grows. This is a limiting probability, not an exact rule for small groups.

For one item avoiding its original position is impossible; for two, swapping them is the only derangement. Small cases need not match the limiting proportion.

### Counting onto functions

Suppose five distinct jobs must be assigned to three distinct servers, leaving none idle.

Jobs are distinct and servers are distinct. Start with unrestricted assignments, exclude those leaving each server idle, and restore overlaps where several servers were idle. An assignment using only one server belongs to two of the idle-server groups.

Unlike stars and bars, this tracks which particular job goes to each server. Two assignments with the same job counts per server may still be different.

Inclusion–exclusion is the go-to method whenever the condition is "every X is covered" or "no X is bad": count the complement events, which are often easier, and alternate.

## Key takeaways

- Derangements exclude every fixed point by inclusion–exclusion.
- Onto assignments exclude missed targets and restore overlaps with alternating signs.

## Further reading

- [Derangement — Wikipedia](https://en.wikipedia.org/wiki/Derangement)
- [Mathematics for Computer Science — MIT](https://courses.csail.mit.edu/6.042/spring18/mcs.pdf)
