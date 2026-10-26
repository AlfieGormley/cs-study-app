---
id: cx-doubling-loops
sourceLesson: cx-analysing-code
title: Doubling and growing inner loops
level: intermediate
minutes: 2
summary: Recognise logarithmic loops and sum a geometric series of inner-loop lengths.
---

Repeated multiplication reaches a large bound much sooner than repeated addition. Throughout, n is a positive integer input bound and `work()` is one constant-cost step.

## Count doublings, not the final value

```python
i = 1
while i < n:
    i *= 2
```

The values before each update are one, two, four, eight and so on. A bound of sixteen needs four updates; seventeen needs one more. Doubling the bound adds only about one pass, giving logarithmic work. A fixed multiplier greater than one gives the same growth class. Integer division by a fixed factor has a similar effect when its stopping condition guarantees termination.

A loop that increments by one while `i * i <= n` instead makes about the square root of the bound in updates. Inspect the update and stopping rule together.

## Restarting changes the total

Restart a full doubling loop for each of n outer iterations and the total is Θ(n log n). But this different pattern is linear:

```python
i = 1
while i < n:
    for j in range(i):
        work()
    i *= 2
```

The inner lengths double. All earlier lengths together are smaller than twice the last length, and the last length is a substantial fraction of the bound. This **geometric series** therefore gives Θ(n) total work. Charging the largest inner loop on every pass overestimates it.

Another trap starts the inner doubling variable at the outer value:

```python
for i in range(1, n + 1):
    j = i
    while j < n:
        j *= 2
```

Most starting values need very few doublings. Almost all permit a first update, about half a second, about a quarter a third. These shrinking groups sum to linear work; the outer scan is also linear. It is Θ(n), not linear times log.

## Key takeaways
- Multiplicative updates often give logarithmic iteration counts.
- Sum the inner loops actually performed, including their starting values.
- Geometrically changing lengths can give a linear total.

## Further reading
- [Erickson: Solving Recurrences](https://jeffe.cs.illinois.edu/teaching/algorithms/notes/99-recurrences.pdf)
