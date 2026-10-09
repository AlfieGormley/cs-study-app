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

- **Input size.** "How large can `n` be?" Here, and throughout this module, n means the number of elements in the input (the length of the array or string) unless a problem says otherwise. Use the answer to compare growth against the resource budget (see the table below).
- **Value ranges.** Negative numbers? Zeros? Can values cause integer overflow in 32 bits?
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

The two loops look at every pair of positions once. The number of pairs tells you the cost:

```formula
N_pairs = n × (n − 1) / 2
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
        if target - x in seen:
            return seen[target - x], i
        seen[x] = i
    return None
```

Now it is expected O(n) time under constant-cost, well-distributed hashing and O(n) space. Numeric examples assume exact arithmetic; large Python integers add bit-length costs. We traded memory for time, which is the most common trade in this whole module.

> [!note] Why check before inserting?
> If `x` is exactly half the target (say target 6, `x = 3`), inserting first would let `x` pair with itself. Checking first means a value can only pair with an *earlier* element.

## Let the constraints choose the complexity

Interview and contest problems state limits like `1 <= n <= 10^5`, written in code style. In maths notation that constraint reads:

```formula
1 ≤ n ≤ 10^5
where
n: the number of elements in the input; its upper limit 10^5 is ten to the power 5, a 1 followed by five zeros: 100,000
≤: "is less than or equal to"
In words: the input holds at least one element and at most 100,000 of them.
```

That is a heavy hint. Input size helps compare growth, but whether an approach is fast enough also depends on the algorithm’s constants, operation types, numeric sizes, memory, hardware and deadline.

> [!note] Content gap
> Generic C++/Python operations-per-second figures and universal pass/fail thresholds are omitted because no pinned benchmark or judge configuration establishes them.

The table uses a few growth expressions you may not have met. Each one describes how the work grows with n:

```formula
n! = n × (n − 1) × … × 2 × 1
2^n = 2 × 2 × … × 2
4! = 4 × 3 × 2 × 1 = 24
2^4 = 2 × 2 × 2 × 2 = 16
where
n: the number of elements in the input
n!: "n factorial", the number of different orders (permutations) of n distinct items
2^n: 2 multiplied by itself n times, the number of subsets of n items (each item is either in or out)
…: "and so on", continuing the same pattern
In words: factorial counts orderings and grows fastest of all; 2^n counts in-or-out choices and doubles with every extra item.
```

The table also uses Big-O notation: O(f) means "the work grows no faster than f, ignoring constant factors", and log n is the base-2 logarithm of n, the number of times you can halve n before reaching 1 (about 17 for 100,000).

The table lists growth expressions to investigate for illustrative input sizes, not guaranteed feasible limits.

| Example n | Growth to investigate | Candidate technique |
|---|---|---|
| ≤ 10 | O(n!) | Permutations |
| ≤ 20 | O(2ⁿ) | Subsets, bitmasks |
| ≤ 500 | O(n³) | Triple loop, DP |
| ≤ 5,000 | O(n²) | Pairs, 2-D DP |
| ≤ 10⁶ | O(n log n) | Sort, heap |
| > 10⁶ | O(n), O(log n) | One pass, math |

Plugging the largest allowed n into two of these expressions shows the gap:

```formula
n^2 = (10^5)^2 = 10^10
n × log_2(n) = 10^5 × log_2(10^5)
n × log_2(n) ≈ 10^5 × 16.6
n × log_2(n) ≈ 1.66 × 10^6
where
n: the number of elements in the input; here 10^5 = 100,000
n^2: n squared, n × n
log_2: the base-2 logarithm: log_2(n) is the power you raise 2 to in order to get n, so log_2(1024) = 10
≈: approximately equal to (the result is rounded)
In words: a quadratic algorithm faces about 10 billion units of work at 100,000 elements, while an n log n algorithm faces about 1.7 million, roughly 6,000 times less.
```

These are work expressions, not exact operation counts inferred from big-O. Compare them with the actual resource budget before choosing.

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
> A cue suggests a pattern; it doesn't prove it fits. "Longest subarray with sum at most k", where k is a limit the problem gives you, looks like a sliding window, but if values can be negative the window logic breaks. Check the pattern's preconditions before you commit.

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
- Use constraints to compare growth and resource needs; an input of about 100,000 elements makes a quadratic scan a significant concern, not a universal impossibility.
- Optimise by finding the bottleneck, then asking which data structure answers it faster.
- Narrate your reasoning, get agreement before coding, and test by tracing, not by hoping.

## Further reading
- [Coding interview techniques — Tech Interview Handbook](https://www.techinterviewhandbook.org/coding-interview-techniques/)
- [Coding interview cheatsheet — Tech Interview Handbook](https://www.techinterviewhandbook.org/coding-interview-cheatsheet/)
- [How to Solve It (Pólya) — Wikipedia](https://en.wikipedia.org/wiki/How_to_Solve_It)
- [Time complexity — Wikipedia](https://en.wikipedia.org/wiki/Time_complexity)
