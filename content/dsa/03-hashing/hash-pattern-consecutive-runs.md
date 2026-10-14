---
id: hash-pattern-consecutive-runs
title: Sets for consecutive runs and recognising patterns
level: intermediate
minutes: 3
sourceLesson: hash-patterns
summary: Nested loops do not necessarily imply quadratic work.
---

Nested loops do not necessarily imply quadratic work. The consecutive-run algorithm starts a traversal only at a value with no predecessor, so it does not repeatedly walk the same run.

## Sets for O(1) membership

Sometimes all you need is fast membership. **Longest consecutive sequence** (`[100, 4, 200, 1, 3, 2]` → 4, for 1, 2, 3, 4) looks like it needs sorting, O(n log n) for n numbers. With a set it is O(n):

```python
def longest_consecutive(nums):
    s = set(nums)
    best = 0
    for x in s:
        if x - 1 not in s:  # x starts a run
            y = x
            while y + 1 in s:
                y += 1
            best = max(best, y - x + 1)
    return best
```

The `x - 1 not in s` test means each run is walked only from its start, so every element is visited a constant number of times.



## Recognising the pattern

| Clue in the problem | Pattern |
|---|---|
| "two elements that sum to" | complement lookup |
| "how many times", "most frequent" | frequency map |
| "group", "anagrams", "same pattern" | canonical key |
| "subarray sum", negatives allowed | prefix sum + map |
| "longest/shortest substring with" | sliding window + map |

> [!note] The cost
> Every pattern here trades O(n) extra memory for speed, and every O(1) is the *average* case. In an interview, say so; on a real system with adversarial input, remember Hash flooding and runtime randomisation.

## Walk each run once

For the set built from 100, 4, 200, 1, 3 and 2, only 1 starts the four-value run. Values 2, 3 and 4 each have a predecessor in the set, so their outer-loop visits do not start another traversal. Values 100 and 200 start singleton runs. The best recorded length is four.

Converting the input to a set also removes duplicate values. If the original list contains several copies of 1, they do not trigger repeated scans of the same run. Iteration order does not affect the result because each run’s start is detected from membership, not from which value appears first.

Across all successful inner-loop increments, each distinct value is reached from exactly one run start. Failed predecessor and end-of-run checks add only constant work per distinct value. For n input items and expected constant-time set operations, construction and scanning are therefore expected O(n) time, with O(n) space. Empty input returns zero; negative consecutive integers work identically.

The recognition table is a starting point, not a proof. State the remembered information, when it is updated, and why the lookups identify exactly the requested answer. Then check whether the memory trade and average-case hashing assumptions are acceptable.

## Key takeaways
- Start a run only when its predecessor is absent.
- Set deduplication prevents repeated traversal from duplicate starts.
- Count total successful traversals rather than multiplying the apparent loop nesting.

## Further reading
- [Time complexity of Python operations — Python wiki](https://wiki.python.org/moin/TimeComplexity)
- [Hash table — Wikipedia](https://en.wikipedia.org/wiki/Hash_table)
