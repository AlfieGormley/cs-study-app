---
id: prob-axioms-unions
title: Combine events without double-counting
level: basic
minutes: 4
sourceLesson: prob-basics
summary: Subtract the overlap when combining events.
---

## The axioms and the rules that follow

In general probability spaces, events belong to a specified collection of measurable subsets. For finite examples here, every subset can be an event. Kolmogorov's axioms are three rules every probability must obey: no probability is negative, something always happens, and for events that cannot happen together (**disjoint** events) probabilities add. The third rule holds for any countable collection of pairwise disjoint events; for two events it reads as the last line below.

```formula
P(A) ≥ 0   for every A
P(Ω) = 1
P(A ∪ B) = P(A) + P(B)   if A ∩ B = ∅
where
P: probability of measurable events, dimensionless and between zero and one
P(A): the probability of event A
A, B: any two events (sets of outcomes)
Ω: omega, the sample space, the set of all outcomes; it always happens
≥: greater than or equal to
A ∪ B: the union of A and B, the event "A or B (or both) happens"
A ∩ B: the intersection of A and B, the event "A and B both happen"
∅: the empty set, an event containing no outcomes, so it can never happen
In words: probabilities are never negative, the certain event has probability 1, and when two events can never happen together, the chance of one or the other is the sum of their chances.
```

From these three come the everyday rules. The **complement** of A is the event "A does not happen"; the **addition rule** (union rule) handles "A or B" when the two can overlap; the **union bound** is a cruder but always-safe version of it.

```formula
P(¬A) = 1 − P(A)
P(A ∪ B) = P(A) + P(B) − P(A ∩ B)
0 ≤ P(A) ≤ 1
P(A ∪ B) ≤ P(A) + P(B)
where
P: probability of measurable events, dimensionless and between zero and one
P(A): the probability of event A
A, B: any two events
¬A: the complement of A, the event "A does not happen" (¬ is the symbol for "not")
A ∪ B: the event "A or B (or both) happens"
A ∩ B: the event "both A and B happen"
≤: less than or equal to
In words: the chance of "not A" is whatever is left over from 1; for "A or B" add the two chances and subtract the overlap you counted twice; every probability lies between 0 and 1; and adding the two chances never underestimates the chance of "A or B".
```

The **addition rule** (inclusion–exclusion) subtracts the overlap, which would otherwise be counted twice. Of the numbers 1 to 100, 50 are divisible by 2, 33 by 3, and 16 by both (the multiples of 6).

```formula
|D_2 ∪ D_3| = |D_2| + |D_3| − |D_2 ∩ D_3|
|D_2 ∪ D_3| = 50 + 33 − 16 = 67
where
D_2: the set of numbers from 1 to 100 divisible by 2
D_3: the set of numbers from 1 to 100 divisible by 3
|D_2|: the number of elements in D_2 (vertical bars mean "how many")
∪: union, "in either set (or both)"
∩: intersection, "in both sets"; D_2 ∩ D_3 is the multiples of 6
In words: 50 even numbers plus 33 multiples of 3 counts the 16 multiples of 6 twice, so subtract them once: 67 numbers are divisible by 2 or 3.
```

The **union bound** drops the subtraction. It is crude but always safe, and it is the workhorse of algorithm analysis: if each of several bad events is individually unlikely, the chance that any of them happens is at most the total.

```formula
P(B_1 ∪ B_2 ∪ … ∪ B_n) ≤ n × p
where
B_1, B_2, …, B_n: n "bad" events, for example "request i hits a slow server"
n: how many bad events there are
p: an upper limit on each bad event's probability, so P(B_i) ≤ p for every i
P: probability; probabilities are dimensionless and apply to measurable events
∪: union, "at least one of these happens"
…: and so on, for every event in between
≤: less than or equal to
In words: the chance that at least one of n bad things happens is never more than n times the largest individual chance, whether or not the events are independent.
```

For example, 100 hash lookups that each fail with probability at most 0.0001 fail one or more times with probability at most 100 × 0.0001 = 0.01. The bound becomes useless once the summed upper bound exceeds one, because every probability is at most 1 anyway.

## Key takeaways
- Subtract the overlap when combining events.
- The union bound needs no independence and can exceed one.

## Further reading
- [Introduction to Probability — Grinstead and Snell](https://math.dartmouth.edu/~prob/prob/prob.pdf)
