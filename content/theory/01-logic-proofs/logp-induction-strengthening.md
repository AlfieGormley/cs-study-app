---
id: logp-induction-strengthening
title: Making the induction hypothesis stronger
level: intermediate
minutes: 3
sourceLesson: logp-induction
summary: A stronger bound can track the slack needed for the next step.
---

## Strengthening the hypothesis

Sometimes induction fails because the IH is too *weak* to carry the step. The surprising fix is to prove something **stronger**.

Claim: the sum of the reciprocals of the squares stays below 2:

```formula
S(n) = 1/1^2 + 1/2^2 + ... + 1/n^2
S(n) < 2   for n ≥ 1
where
S(n): the sum of 1 divided by each square from 1² up to n²
n: a whole number, n ≥ 1
...: and so on, one term for every whole number up to n
≥: at least
<: less than
In words: however many terms you add, the total stays below 2. For n = 3: 1 + 1/4 + 1/9 ≈ 1.36.
```

Try it directly: assume S(n) is less than 2. Then S(n plus 1) equals S(n) plus 1/(n plus 1) squared, which is less than 2 plus something positive. Stuck: knowing S(n) is less than 2 leaves no room for the next fraction.

Prove instead the stronger claim S(n) is at most 2 minus 1/n. **Base**, n equals 1: S(1) equals 1 and 2 minus 1 equals 1, so 1 is at most 1. ✓ **Step**: assume S(n) is at most 2 minus 1/n. The aim is to reach S(n plus 1) is at most 2 minus 1/(n plus 1). Adding the next fraction gives the first line below, so it is enough that the next fraction fits into the gap between 2 minus 1/n and 2 minus 1/(n plus 1), which is the second line:

```formula
S(n + 1) ≤ 2 − 1/n + 1/(n + 1)^2
1/n − 1/(n + 1) ≥ 1/(n + 1)^2
1/(n(n + 1)) ≥ 1/(n + 1)^2
where
S(n): the sum 1/1² + ... + 1/n², assumed at most 2 − 1/n (the strengthened hypothesis)
n: a whole number, n ≥ 1
≤, ≥: is at most, is at least
In words: the last line holds because n is less than n + 1, so n × (n + 1) is less than (n + 1)², and dividing 1 by a smaller number gives a bigger result. The third line is the second with the gap simplified, so the second line is true, which is exactly what the step needs. ∎
```

Since 2 minus 1/n is less than 2, the original claim follows. The stronger statement tracks *how far* below 2 we are, which is exactly what the step needs. The same trick appears when choosing loop invariants in the next lesson.


A recurrence proof uses the same method: state the cost at the smallest input, substitute the proposed expression for each smaller recursive cost, then simplify to the expression for the current input. When sizes repeatedly halve, induction on the number of halvings keeps every size in the power-of-two domain.

## Key takeaways
- A stronger bound can track the slack needed for the next step.
- Check the strengthened base and show the extra term fits the gap to the next bound.

## Further reading
- [MIT Mathematics for Computer Science](https://ocw.mit.edu/courses/6-042j-mathematics-for-computer-science-spring-2015/mit6_042js15_textbook.pdf)
- [Mathematics for Computer Science — MIT OpenCourseWare](https://ocw.mit.edu/courses/6-042j-mathematics-for-computer-science-spring-2015/)
