---
id: disc-counting-rules-complements
title: "Counting rules and complements"
level: intermediate
minutes: 2
summary: "Multiply choices along a sequence; add counts only for disjoint alternatives."
sourceLesson: disc-counting
---

Counting estimates the size of a search space or test set. Before choosing a method, decide what counts as the same outcome and whether cases overlap.

## The two basic rules

**Product rule.** If a task is a sequence of steps, and the number of choices at each step is fixed for that stage, regardless of the earlier choices, multiply the counts.

**Sum rule.** If a task can be done in one of several *disjoint* ways (no outcome belongs to two of them), add the counts.

A four-digit code allows any digit first. If repeats are forbidden, each later position has one fewer available digit. Codes of different lengths are disjoint cases, so their counts can be added.

> [!example] How big is a brute-force search?
> Each extra independent uniformly chosen character multiplies the number of possible passwords by the alphabet size. An assumed guesses-per-second rate can translate this into a search-time estimate, but it is not a hardware benchmark. Human-chosen passwords need a different probability model.

## Counting at least one

Count the complement: all possibilities minus those with none. Choosing a position for a digit and filling the rest freely overcounts strings containing several digits.

All six-character strings over letters and digits split into two disjoint groups: those containing a digit and those containing none. Subtracting the all-letter group counts each valid string exactly once.

If cases overlap, the sum rule needs inclusion–exclusion or a disjoint reformulation.

## Key takeaways

- Multiply choices along a sequence; add counts only for disjoint alternatives.
- For an “at least one” constraint, subtract the outcomes with none from all outcomes.

## Further reading

- [Mathematics for Computer Science — MIT](https://courses.csail.mit.edu/6.042/spring18/mcs.pdf)
