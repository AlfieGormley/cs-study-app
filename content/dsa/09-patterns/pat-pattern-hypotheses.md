---
id: pat-pattern-hypotheses
title: Use problem cues to form a hypothesis
level: basic
minutes: 2
sourceLesson: pat-approach
summary: A problem cue suggests a technique; its preconditions decide whether the technique is valid.
---

Before selecting a template, identify the input shape, the requested output and what information must be maintained. This short catalogue previews the concrete patterns that follow.

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
| "Appears once", at most 20 items | Bits, masks |
| "Have I seen this?" | Hash map/set |

Other modules cover the rest of the toolkit: binary search, BFS/DFS, backtracking and dynamic programming.

> [!warning] Patterns are hypotheses
> A cue suggests a pattern; it doesn't prove it fits. "Longest subarray with sum at most k", where k is a limit the problem gives you, looks like a sliding window, but if values can be negative the window logic breaks. Check the pattern's preconditions before you commit.

## Key takeaways
- A problem cue suggests a technique; its preconditions decide whether the technique is valid.
- Signed sum problems often call for prefix values and an appropriate lookup structure.
- Other modules cover graph search, backtracking, binary search and dynamic programming.

## Further reading
- [Coding interview techniques — Tech Interview Handbook](https://www.techinterviewhandbook.org/coding-interview-techniques/)
- [Coding interview cheatsheet — Tech Interview Handbook](https://www.techinterviewhandbook.org/coding-interview-cheatsheet/)
- [How to Solve It (Pólya) — Wikipedia](https://en.wikipedia.org/wiki/How_to_Solve_It)
- [Time complexity — Wikipedia](https://en.wikipedia.org/wiki/Time_complexity)
