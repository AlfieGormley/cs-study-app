---
id: pat-brute-to-lookup
title: From brute force to a lookup
level: basic
minutes: 5
sourceLesson: pat-approach
summary: A brute-force solution supplies a correctness baseline and exposes repeated work.
---

The input has n elements. This unit turns a scan of all pairs into a lookup of earlier values, preserving original indices.

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

The two loops look at every pair of positions once. The number of pairs tells you the cost:

```formula
N_pairs = (n(n − 1)) / 2
N_pairs = 4 × 3 / 2 = 6
where
N_pairs: the number of different (i, j) pairs with i before j, which is how many times the `if` line runs in the worst case
n: the number of elements in the array; here 4
i: the index (position, counting from 0) of the first number in a pair
j: the index of the second number in a pair, always greater than i
In words: each of the n elements is paired with each of the n − 1 others, and halving removes the double count of (i, j) and (j, i); 4 elements give 6 pairs, and 100,000 elements give about 5 billion.
```

That is O(n²) time and O(1) extra space: the work grows with the square of n, while the memory used beyond the input stays fixed. You don't always need to code the brute force; saying it and its cost is usually enough.

## Step 4: optimise

Look for wasted work. Three useful questions are:

1. **What is the bottleneck?** In two sum, the inner loop: for each `a[i]`, we search the rest of the array for `target - a[i]`, the one value that would complete the pair:

```formula
y = T − x
y = 6 − 2 = 4
where
y: the complement, the value that must already be in the array to pair with x
T: the target sum (`target` in the code); here 6
x: the current element (`a[i]` or `x` in the code); here 2
In words: once you know the target and the current number, only one partner can work, so the question becomes "have I seen 4?" rather than "which pair works?".
```

That single partner is what makes a lookup structure useful in the next question.
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

Now it is expected O(n) time under constant-cost, well-distributed hashing and O(n) space. Numeric examples assume exact arithmetic; large Python integers add bit-length costs. We traded memory for time, which is the most common trade in this whole module.

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
