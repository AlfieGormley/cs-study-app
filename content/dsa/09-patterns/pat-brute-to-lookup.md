---
id: pat-brute-to-lookup
title: From brute force to a lookup
level: basic
minutes: 5
sourceLesson: pat-approach
summary: A brute-force solution supplies a correctness baseline and exposes repeated work.
---

The input has n elements. This unit shows the routine's middle steps on one example: a scan of all pairs becomes a lookup of earlier values. The Hash Tables & Hashing module's "Two-sum and complement lookup" unit covers the hash-map side in more depth; the focus here is how you get from the slow version to the fast one.

## Step 3: brute force

State the obvious solution and its complexity out loud, even if it is slow. It proves you understand the problem, gives you a fallback, and is often the starting point for the optimisation.

Classic example, **two sum**: given an unsorted array and a target, return the indices of two numbers that add up to the target.

```python
def two_sum_brute(a, target):
    n = len(a)
    for i in range(n):
        # Only later indices can form a
        # pair.
        for j in range(i + 1, n):
            if a[i] + a[j] == target:
                return i, j
    return None
```

The two loops look at every pair of positions once, so in the worst case the `if` line runs about half of n squared times: 4 elements give 6 pairs, and 100,000 elements give about 5 billion. (The Complexity Analysis module's "Comparing every pair" unit counts these pairs exactly.)

That is O(n²) time and O(1) extra space: the work grows with the square of n, while the memory used beyond the input stays fixed. You don't always need to code the brute force; saying it and its cost is usually enough.

## Step 4: optimise

Look for wasted work. Three useful questions are:

1. **What is the bottleneck?** In two sum, the inner loop: for each `a[i]`, we search the rest of the array for `target - a[i]`, the one value that would complete the pair. With target 6 and current value 2, only a 4 can work, so the question becomes "have I seen 4?" rather than "which pair works?". That single partner is what makes a lookup structure useful.
2. **Is there a data structure that answers that inner question faster?** "Have I seen value v?" is a hash-set lookup: O(1) on average.
3. **Am I recomputing something?** Running totals, window contents and "best so far" values can usually be carried forward instead of recomputed.

```python
def two_sum(a, target):
    seen = {}            # value -> index
    for i, x in enumerate(a):
        # Find a partner from an earlier
        # position.
        if target - x in seen:
            return seen[target - x], i
        # Store this value for later
        # elements.
        seen[x] = i
    return None
```

Now it is expected O(n) time under constant-cost, well-distributed hashing and O(n) space. We traded memory for time, which is the most common trade in this whole module.

> [!note] Why check before inserting?
> If `x` is exactly half the target (say target 6 and a current value of 3), inserting first would let `x` pair with itself. Checking first means a value can only pair with an *earlier* element.

## Reuse the lookup idea for duplicates

To detect any duplicate, keep a hash set of values already scanned. Check membership before adding each value. A repeated value answers yes; exhausting the input answers no. Under expected constant-cost hashing, one pass takes expected O(n) time and up to O(n) set entries, where n is the input length.

Sorting then comparing neighbouring values is another option with an O(n log n) comparison bound. It changes the data order, and Python’s in-place list sort can still need O(n) temporary references. Neither bound alone predicts the faster implementation for a particular input.

If the optimal approach is unclear, stating a correct brute-force baseline exposes the bottleneck and gives a concrete direction to discuss. The routine does not require discovering the optimum before explaining any solution.

## Key takeaways
- A brute-force solution supplies a correctness baseline and exposes repeated work.
- Check the complement before inserting the current value so two sum uses distinct positions.
- Hash-based acceleration trades memory for expected speed under stated hashing and numeric-cost assumptions.

## Further reading
- [Coding interview techniques — Tech Interview Handbook](https://www.techinterviewhandbook.org/coding-interview-techniques/)
- [Coding interview cheatsheet — Tech Interview Handbook](https://www.techinterviewhandbook.org/coding-interview-cheatsheet/)
- [How to Solve It (Pólya) — Wikipedia](https://en.wikipedia.org/wiki/How_to_Solve_It)
- [Time complexity — Wikipedia](https://en.wikipedia.org/wiki/Time_complexity)
