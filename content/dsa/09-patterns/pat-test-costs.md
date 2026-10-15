---
id: pat-test-costs
title: Test the code and audit hidden costs
level: basic
minutes: 3
sourceLesson: pat-approach
summary: Trace representative and boundary inputs, then state an invariant or correctness argument.
---

Testing complements a correctness argument. Here n is the number of input elements; the earlier two-sum implementation checks a hash map before inserting the current element.

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
- **When you spot a bug:** say so and fix it. Finding and explaining a bug makes the correction available for discussion.

Hints are not failure. Take them, acknowledge them and build on them.

## Common pitfalls

- **Solving the wrong problem.** Returning values when indices were asked for; assuming sorted input when it wasn't.
- **Premature optimisation.** Spending 20 minutes hunting an O(n) trick and running out of time with nothing written. A correct O(n log n) beats an unfinished O(n).
- **Skipping the complexity.** Always state time *and* space, and justify them.
- **Ignoring Python costs.** `x in some_list` is O(n); `s[1:]` copies; `list.pop(0)` is O(n). Use sets, indices and `collections.deque`.

## Recap of the pattern family
- Run the same routine every time: clarify, examples, brute force, optimise, test.
- Ask about input size, value ranges, sortedness and duplicates; each changes the algorithm.
- Use constraints to compare growth and resource needs; an input of about 100,000 elements makes a quadratic scan a significant concern, not a universal impossibility.
- Optimise by finding the bottleneck, then asking which data structure answers it faster.
- Narrate your reasoning, get agreement before coding, and test by tracing, not by hoping.

## Key takeaways
- Trace representative and boundary inputs, then state an invariant or correctness argument.
- Python list membership, front removal and slices can add hidden linear work.
- Explain time and space costs alongside your reasoning.

## Further reading
- [Coding interview techniques — Tech Interview Handbook](https://www.techinterviewhandbook.org/coding-interview-techniques/)
- [Coding interview cheatsheet — Tech Interview Handbook](https://www.techinterviewhandbook.org/coding-interview-cheatsheet/)
- [How to Solve It (Pólya) — Wikipedia](https://en.wikipedia.org/wiki/How_to_Solve_It)
- [Time complexity — Wikipedia](https://en.wikipedia.org/wiki/Time_complexity)
