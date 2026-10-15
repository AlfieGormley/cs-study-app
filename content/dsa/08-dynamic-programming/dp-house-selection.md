---
id: dp-house-selection
title: Choose non-adjacent houses
level: intermediate
minutes: 3
summary: For each house, compare skipping it with taking it after the best non-neighbouring prefix.
sourceLesson: dp-1d
---

## House robber

> Houses in a row hold amounts `h[0..n-1]`. You can't rob two adjacent houses. Maximise the total.

**State**: `best[i]` records the most you can take from the first i houses.

**Recurrence**: for house i − 1 (the last of the first i houses) there are two choices.

- Skip it: `best[i-1]`.
- Rob it: then house i − 2 is off limits, so `best[i-2] + h[i-1]`.

```formula
best[i] = max(best[i − 1],
  best[i − 2] + h[i − 1])
best[0] = 0
best[1] = max(0, h[0])
where
best[i]: the largest total you can take from houses 0 to i − 1 (the first i houses) without robbing two neighbours
i: how many houses, counted from the left, are being considered; the first line applies for i of 2 or more
h[i − 1]: the amount in house i − 1 (houses are numbered from 0)
max: the larger of the values listed
In words: either leave the last house alone and keep the best plan for the houses before it, or rob it and add its amount to the best plan that stops two houses earlier.
```

Taking no houses is allowed, which is why best[1] can be 0 if amounts may be negative.

Each state needs only the previous two, so two variables suffice:

```python
def rob(h):
    prev, cur = 0, 0  # best[i-2], best[i-1]
    for x in h:
        # Compare skipping with a
        # non-adjacent take.
        prev, cur = cur, max(cur, prev + x)
    return cur
```

Trace `h = [2, 7, 9, 3, 1]`:

```
house  x   prev  cur
start      0     0
0      2   0     2
1      7   2     7
2      9   7     11   (2 + 9)
3      3   11    11   (7 + 3 = 10 < 11)
4      1   11    12   (11 + 1)
```

Answer 12: houses 0, 2 and 4 (2 + 9 + 1).

> [!note] Why greedy fails here
> "Take the biggest house, remove its neighbours, repeat" fails on `[2, 3, 2]`: it takes the 3 and must stop, but robbing both 2s gives 4. Local choices interact, and DP's "try both, keep the best" handles that.

**Variant**: houses in a **circle** (first and last adjacent). With at least two houses, run the linear version on `h[1:]` and `h[:-1]` and take the max. Every valid plan excludes at least one end. Return zero for no houses. For one house, return the larger of zero and that house’s amount. Here n is the number of houses. Slicing allocates O(n) extra space; index-bounded passes avoid those copies.

## Real-world use

- **House robber** is the 1-D case of **maximum-weight independent set**, which is NP-hard on general graphs but easy on paths and trees (see the later tree-DP units).

## Key takeaways
- For each house, compare skipping it with taking it after the best non-neighbouring prefix.
- On a circle, a valid plan excludes at least one of the two end houses.

## Further reading
- [Erickson: dynamic programming](https://jeffe.cs.illinois.edu/teaching/algorithms/book/03-dynprog.pdf)
- [MIT algorithms course](https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-spring-2020/)
