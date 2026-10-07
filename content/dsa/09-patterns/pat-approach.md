---
id: pat-approach
title: How to approach a coding problem
level: basic
minutes: 10
summary: A repeatable five-step method (clarify, examples, brute force, optimise, test), how input sizes tell you the target complexity, and how to talk through it in an interview.
---

A routine can help you clarify the requested behavior, develop a correct approach, explain your reasoning and test boundary cases. Treat the following as practical advice, not a guarantee of interview success; interview formats and scoring vary.

> [!note] Content gap
> Population-wide claims about why most candidates fail are omitted because no reliable survey or causal evidence is provided.

This module is a catalogue of patterns. This first lesson is the routine you run *before* picking one.

## The five steps

```flow
Clarify: what exactly is asked?
Examples: small cases and edge cases
Brute force: correct first, slow is OK
Optimise: find the wasted work
Test: trace by hand, then edge cases
```

One possible allocation for a 45-minute practice session is: 5 minutes clarifying and on examples, 5–10 on the approach, 15–20 coding, 5–10 testing. Adjust this to the task and interviewer; a short or familiar problem may need less planning.

## Step 1: clarify

Restate the problem in your own words, then ask about anything that would change the algorithm.

- **Input size.** "How large can `n` be?" Use the answer to compare growth against the resource budget (see the table below).
- **Value ranges.** Negative numbers? Zeros? Can values overflow 32 bits?
- **Sortedness and duplicates.** Is the array sorted? Can values repeat?
- **Output shape.** Indices or values? One answer or all? What if there is no answer: return `-1`, `None`, raise?
- **Mutability.** May I modify the input in place?
- **Ties.** If several answers are valid, does it matter which?

> [!tip] Questions are signals
> "Is the array sorted?" is not small talk. A yes points straight at binary search or two pointers. "Can values be negative?" matters for monotone sum-window rules (lesson 3), though fixed-size windows and other window predicates can still handle negatives.

## Step 2: examples

Write one ordinary example and work it by hand. Then list the edge cases you'll test at the end:

- empty input, a single element
- all values equal, all distinct
- already sorted, reverse sorted
- negatives, zeros, the largest allowed values
- the answer at the very start or very end

Working an example by hand often reveals the algorithm. Watch what *you* do: if you keep scanning back over the same elements, that repeated scan is the thing to optimise.

## Step 3: brute force

State the obvious solution and its complexity out loud, even if it is slow. It proves you understand the problem, gives you a fallback, and is often the starting point for the optimisation.

Classic example, **two sum**: given an unsorted array and a target, return the indices of two numbers that add up to the target.

```python
def two_sum_brute(a, target):
    n = len(a)
    for i in range(n):
        for j in range(i + 1, n):
            if a[i] + a[j] == target:
                return i, j
    return None
```

That is O(n²) time and O(1) extra space. You don't always need to code the brute force; saying it and its cost is usually enough.

## Step 4: optimise

Look for wasted work. Three useful questions are:

1. **What is the bottleneck?** In two sum, the inner loop: for each `a[i]`, we search the rest of the array for `target - a[i]`.
2. **Is there a data structure that answers that inner question faster?** "Have I seen value v?" is a hash-set lookup: O(1) on average.
3. **Am I recomputing something?** Running totals, window contents and "best so far" values can usually be carried forward instead of recomputed.

```python
def two_sum(a, target):
    seen = {}            # value -> index
    for i, x in enumerate(a):
        if target - x in seen:
            return seen[target - x], i
        seen[x] = i
    return None
```

Now it is expected O(n) time under constant-cost, well-distributed hashing and O(n) space. Numeric examples assume exact arithmetic; large Python integers add bit-length costs. We traded memory for time, which is the most common trade in this whole module.

> [!note] Why check before inserting?
> If `x` is exactly half the target (say target 6, `x = 3`), inserting first would let `x` pair with itself. Checking first means a value can only pair with an *earlier* element.

## Let the constraints choose the complexity

Interview and contest problems state limits like `1 <= n <= 10^5`. That is a heavy hint. Input size helps compare growth, but feasibility also depends on the algorithm’s constants, operation types, numeric sizes, memory, hardware and deadline.

> [!note] Content gap
> Generic C++/Python operations-per-second figures and universal pass/fail thresholds are omitted because no pinned benchmark or judge configuration establishes them.

The table lists growth expressions to investigate for illustrative input sizes, not guaranteed feasible limits.

| Example n | Growth to investigate | Candidate technique |
|---|---|---|
| ≤ 10 | O(n!) | Permutations |
| ≤ 20 | O(2ⁿ) | Subsets, bitmasks |
| ≤ 500 | O(n³) | Triple loop, DP |
| ≤ 5,000 | O(n²) | Pairs, 2-D DP |
| ≤ 10⁶ | O(n log n) | Sort, heap |
| > 10⁶ | O(n), O(log n) | One pass, math |

For n = 10⁵, n² = 10¹⁰ while n log₂n ≈ 1.66 × 10⁶. These are work expressions, not exact operation counts inferred from big-O. Compare them with the actual resource budget before choosing.

## Spotting the pattern

Once you understand the problem, match its shape against the patterns in this module.

| Cue in the problem | Try |
|---|---|
| Sorted array, pair/triple | Two pointers |
| Contiguous subarray/substring | Sliding window |
| Many range-sum queries | Prefix sums |
| Sum equals k, negatives allowed | Prefix sum + hash map |
| Next greater/smaller | Monotonic stack |
| Max of every window | Monotonic deque |
| Overlapping ranges, schedules | Sort intervals |
| k largest / k-th / stream | Heap |
| Merge k sorted inputs | Heap (k-way) |
| "Appears once", n ≤ 20 | Bits, masks |
| "Have I seen this?" | Hash map/set |

Other modules cover the rest of the toolkit: binary search, BFS/DFS, backtracking and dynamic programming.

> [!warning] Patterns are hypotheses
> A cue suggests a pattern; it doesn't prove it fits. "Longest subarray with sum ≤ k" looks like a sliding window, but if values can be negative the window logic breaks. Check the pattern's preconditions before you commit.

## Step 5: test

Don't announce "done" and wait. Test like an engineer:

1. **Trace your normal example** through the code line by line, tracking variables. This can reveal off-by-one errors; examples supplement an invariant or correctness argument rather than proving correctness for all inputs.
2. **Run the edge cases** from step 2: empty input, one element, duplicates.
3. **Check the complexity** you claimed against the code you wrote. A hidden `in list` check or slice inside a loop can turn O(n) into O(n²).

For `two_sum([3, 2, 4], 6)`:

```
i=0 x=3  need 3, seen={}       add 3:0
i=1 x=2  need 4, seen={3}      add 2:1
i=2 x=4  need 2, found at 1  -> (1, 2)
```

Note that 3 + 3 = 6 was correctly *not* returned, because there is only one 3.

## Talking through it

Make your reasoning available for discussion. Useful ways to narrate include:

- **Before coding:** "Brute force is O(n²) by checking every pair. The inner loop is a lookup, so a hash map should get us to O(n) with O(n) space. Shall I go with that?" Getting a nod before coding avoids building the wrong thing.
- **While coding:** say what each block is for, not every keystroke. Use clear names (`seen`, `lo`, `hi`), not `a1`, `tmp2`.
- **When stuck:** say what you're trying. "Sorting would help, but we need original indices... we could sort pairs of (value, index)." Explaining the sticking point gives the interviewer something concrete to respond to.
- **When you spot a bug:** say so and fix it. Finding your own bug is a positive signal.

Hints are not failure. Take them, acknowledge them and build on them.

## Common pitfalls

- **Solving the wrong problem.** Returning values when indices were asked for; assuming sorted input when it wasn't.
- **Premature optimisation.** Spending 20 minutes hunting an O(n) trick and running out of time with nothing written. A correct O(n log n) beats an unfinished O(n).
- **Skipping the complexity.** Always state time *and* space, and justify them.
- **Ignoring Python costs.** `x in some_list` is O(n); `s[1:]` copies; `list.pop(0)` is O(n). Use sets, indices and `collections.deque`.

## Key takeaways
- Run the same routine every time: clarify, examples, brute force, optimise, test.
- Ask about input size, value ranges, sortedness and duplicates; each changes the algorithm.
- Use constraints to compare growth and resource needs; n ≈ 10⁵ makes a quadratic scan a significant concern, not a universal impossibility.
- Optimise by finding the bottleneck, then asking which data structure answers it faster.
- Narrate your reasoning, get agreement before coding, and test by tracing, not by hoping.

## Further reading
- [Coding interview techniques — Tech Interview Handbook](https://www.techinterviewhandbook.org/coding-interview-techniques/)
- [Coding interview cheatsheet — Tech Interview Handbook](https://www.techinterviewhandbook.org/coding-interview-cheatsheet/)
- [How to Solve It (Pólya) — Wikipedia](https://en.wikipedia.org/wiki/How_to_Solve_It)
- [Time complexity — Wikipedia](https://en.wikipedia.org/wiki/Time_complexity)
