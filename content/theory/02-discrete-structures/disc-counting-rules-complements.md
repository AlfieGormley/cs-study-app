---
id: disc-counting-rules-complements
title: "Counting rules and complements"
level: intermediate
minutes: 3
summary: "Multiply choices along a sequence; add counts only for disjoint alternatives."
sourceLesson: disc-counting
---

Counting sounds like primary school, but it is how you estimate brute-force search spaces, password strength, the number of test cases, the probability of a collision and the size of the output of an algorithm. Most errors come from one of two mistakes: counting the same thing twice, or not being clear whether **order matters**.

The good news is that nearly every problem reduces to a handful of rules, applied carefully.

## The two basic rules

**Product rule.** If a task is a sequence of steps, and the number of choices at each step is fixed for that stage, regardless of the earlier choices, multiply the counts.

**Sum rule.** If a task can be done in one of several *disjoint* ways (no outcome belongs to two of them), add the counts.

```formula
N_seq = a × b
N_alt = a + b
where
N_seq: the number of ways to do step one and then step two (product rule)
N_alt: the number of ways to do the task one way or the other, when no outcome is counted by both ways (sum rule)
a: the number of choices in the first step, or the number of outcomes of the first way
b: the number of choices in the second step (the same whatever the first choice was), or the number of outcomes of the second way
In words: "and then" multiplies, "or" (with no overlap) adds. Both extend to any number of steps or ways.
```

Three everyday examples: a 4-digit PIN, a PIN with no repeated digit, and a lower-case password of length 1 to 3.

```formula
N_PIN = 10 × 10 × 10 × 10 = 10^4
N_PIN = 10,000
N_dist = 10 × 9 × 8 × 7 = 5,040
N_pw = 26 + 26^2 + 26^3
N_pw = 26 + 676 + 17,576 = 18,278
where
N_PIN: the number of 4-digit PINs when any digit 0–9 may appear in any position, repeats allowed
N_dist: the number of 4-digit PINs with no repeated digit: 10 choices, then 9 left, then 8, then 7
N_pw: the number of passwords of length 1, 2 or 3 made from the 26 letters a–z
10^4: 4 copies of 10 multiplied together (one factor of 10 per position)
26^2, 26^3: 26 × 26 and 26 × 26 × 26: the counts of 2-letter and 3-letter passwords
In words: the PIN counts are the product rule (the second with shrinking choices); the password count is the sum rule over the three disjoint lengths, then the product rule inside each length.
```

> [!example] How big is a brute-force search?
> An 8-character password over 62 symbols (a–z, A–Z, 0–9) has about 218 trillion possibilities. At an assumed ten billion guesses per second, exhausting the space takes about 6 hours; this is arithmetic, not a measured hardware benchmark. Add 4 characters and there are about 3.2 sextillion possibilities, taking around 10,000 years at that assumed rate. For independently and uniformly chosen symbols, adding length multiplies the search space exponentially. Human-chosen passwords need a different model.

## Counting at least one

Count the complement: all possibilities minus those with none. Choosing a position for a digit and filling the rest freely overcounts strings containing several digits.

```formula
N_1 = 36^6 − 26^6
N_1 = 2,176,782,336 − 308,915,776
N_1 = 1,867,866,560
where
N_1: the number of 6-character passwords over a–z and 0–9 (36 symbols) with at least one digit
36^6: all 6-character strings over the 36 symbols
26^6: the strings with no digit at all, letters only
In words: everything minus the all-letter passwords leaves exactly those with at least one digit.
```

If cases overlap, the sum rule needs inclusion–exclusion or a disjoint reformulation.

## Key takeaways

- Multiply choices along a sequence; add counts only for disjoint alternatives.
- For an “at least one” constraint, subtract the outcomes with none from all outcomes.

## Further reading

- [Mathematics for Computer Science — MIT](https://courses.csail.mit.edu/6.042/spring18/mcs.pdf)
