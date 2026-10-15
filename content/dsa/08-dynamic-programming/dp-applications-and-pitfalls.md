---
id: dp-applications-and-pitfalls
title: Spot repeated states in real problems
level: basic
minutes: 3
summary: DP also solves counting and decision problems.
sourceLesson: dp-intro
---

## DP vs its neighbours

| Technique | Subproblems | Choice |
|---|---|---|
| Typical divide and conquer | Separate smaller inputs | Combine recursive results |
| Greedy | One per step | Commit locally |
| Typical DP | Reusable states | Combine feasible alternatives |

**Greedy** makes one locally best choice and never revisits it. It can avoid examining alternatives, but needs a proof that the local choice is safe. DP tries every option for each decision and keeps the best, which is why it handles problems where greedy fails (you'll see coin change with coins `{1, 3, 4}` in “Minimise the coins for an amount”).

## Where DP shows up in the real world

DP is not just an interview topic. A few systems that are DP at their core:

- **`diff` and `git diff`** are built on longest common subsequence and related edit-script algorithms.
- **Spell checkers and fuzzy search** use edit (Levenshtein) distance.
- **Bioinformatics** aligns DNA and protein sequences with Needleman–Wunsch and Smith–Waterman, both grid DPs.
- **Hidden Markov models** use Viterbi decoding to find the most likely hidden-state sequence; speech recognition is a classical application.
- **Network routing**: Bellman–Ford, used in distance-vector protocols like RIP, is DP over path lengths.
- **Query optimisers** in databases have long used DP to choose join orders (the System R approach).

## Why those recurrences can repeat work

For a right/down grid, going right then down reaches the same cell as going down then right. A naive recursion from either route therefore asks for the same remaining grid paths. Stair counts with one-step and two-step choices repeat in the same way as Fibonacci. In longest common subsequence, mismatching characters permit skipping from either string; different skip histories can reach the same pair of remaining prefixes. A cache identifies that repeated pair rather than remembering the whole skip history. Binary search follows only one smaller range, while ordinary merge sort visits distinct input intervals.

## Common pitfalls

1. **Caching without overlap.** Memoising standard merge sort by input interval adds overhead and does not reuse an interval; a content-based cache has different key costs and may reuse equal-valued segments. Check that subproblems actually repeat.
2. **A state that's missing information.** If the answer depends on something you didn't put in the cache key, the cache returns wrong answers. More in the next lesson.
3. **Forgetting base cases**, which leads to infinite recursion or off-by-one tables.
4. **Exponential numbers.** `F(1000)` has 209 digits. Python integers grow as needed. Fixed-width Java integer arithmetic wraps; signed integer overflow in C++ is undefined behavior, while arbitrary-precision libraries are available. Reduce modulo a value only when that is the requested output.

## Key takeaways
- DP also solves counting and decision problems.
- Greedy needs a proof that each committed choice is safe.
- Check overlap, sufficient state, base cases and numeric limits.

## Further reading
- [Selinger and colleagues: System R access-path selection](https://web.stanford.edu/class/cs346/2014/selinger.pdf)
- [RIP distance-vector foundations](https://www.rfc-editor.org/rfc/rfc2453)
- [Erickson: dynamic programming](https://jeffe.cs.illinois.edu/teaching/algorithms/book/03-dynprog.pdf)
- [MIT algorithms course](https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-spring-2020/)
