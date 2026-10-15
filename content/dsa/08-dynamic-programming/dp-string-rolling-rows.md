---
id: dp-string-rolling-rows
title: Save rows without losing dependencies
level: intermediate
minutes: 2
summary: Only the previous row is needed to compute the next one.
sourceLesson: dp-2d
---

## Space optimisation: rolling rows

Create each mutable table row separately. In Python, `[[0] * n] * m` repeats references to one row: changing one row also changes all the others. The list comprehension used in the full-table examples creates independent rows; the rolling version likewise allocates a fresh current row.

All three recurrences only look at the current row and the previous row. So keep two rows and swap them:

```python
def lcs_length(a, b):
    prev = [0] * (len(b) + 1)
    for x in a:
        # Allocate a separate row, not
        # shared refs.
        cur = [0] * (len(b) + 1)
        for j, y in enumerate(b, 1):
            if x == y:
                cur[j] = prev[j - 1] + 1
            else:
                cur[j] = max(prev[j],
                             cur[j - 1])
        # The completed row becomes the
        # previous.
        prev = cur
    return prev[-1]
```

With m the length of `a` and n the length of `b`, memory falls from O(m·n) to O(n). Make the **shorter** string the columns to get O(min(m, n)), where min picks the smaller length.

You can go down to a **single row**, but recurrences that read the diagonal `[i-1][j-1]` need a saved copy, because by the time you reach column j you've overwritten column j − 1 with the current row:

```python
row = list(range(len(b) + 1))
for i, x in enumerate(a, 1):
    # Save the diagonal before overwriting
    # it.
    diag, row[0] = row[0], i
    for j, y in enumerate(b, 1):
        up = row[j]          # old row[j]
        if x == y:
            row[j] = diag
        else:
            row[j] = 1 + min(up, row[j-1],
                             diag)
        # Preserve the old row value for
        # next time.
        diag = up  # next cell's diag
```

The catch: with rolling rows you **lose the stored history for a direct traceback**, because the earlier rows are gone. If you need both linear memory and the alignment itself, use **Hirschberg's algorithm**, which finds the midpoint of the optimal path with a forward and a backward pass and recurses. For nonempty strings it retains O(mn) time and O(m + n) space including output; the exact constant depends on the implementation. Repeated full recomputation is another space/time tradeoff.

## Key takeaways
- Only the previous row is needed to compute the next one.
- One-row updates must save the old diagonal before overwriting it.
- Recovering an alignment needs stored history or additional computation.

## Further reading
- [Erickson: dynamic programming](https://jeffe.cs.illinois.edu/teaching/algorithms/book/03-dynprog.pdf)
- [Levenshtein distance](https://en.wikipedia.org/wiki/Levenshtein_distance)
- [Hirschberg’s algorithm](https://en.wikipedia.org/wiki/Hirschberg%27s_algorithm)
