---
id: pat-amortised-dominance
title: Prove linear total stack and deque work
level: advanced
minutes: 4
sourceLesson: pat-monotonic
summary: Count total pushes and pops across the scan rather than multiplying loop bounds.
---

Here n is the input length. The preceding examples remove each stored candidate at most once; all stated linear bounds use constant-cost comparisons and amortised container operations.

## Why it's O(n): the amortised argument

Count operations per element rather than per loop iteration:

- each index is pushed exactly once: n pushes;
- each index is popped no more than once: at most n pops.

So the combined pushes and pops number at most twice the input length; loop tests, comparisons and output writes add O(n) more work. A single step may pop many elements, but then those elements are gone and can't be popped again.

## Recognising the pattern

| Cue | Structure |
|---|---|
| "next/previous greater/smaller" | Monotonic stack |
| "days until warmer", "span" | Monotonic stack |
| Area bounded by shortest bar | Increasing stack |
| Max/min of each window | Monotonic deque |
| DP over a sliding max/min | Monotonic deque |
| Remove k digits for smallest | Increasing stack (greedy) |

## Pitfalls

- **Storing values instead of indices.** You usually need the index for widths, distances or window expiry. Store indices; look values up.
- **Strict vs non-strict comparisons.** Decide what duplicates should do and pick `<` or `<=` deliberately.
- **Forgetting leftovers.** Elements still on the stack at the end have no next greater; use a suitable flushing value or a final pass.
- **Expiry check in the deque.** Compare the front index with `i - k`, not the value with anything.

## Recap of the pattern family
- A monotonic stack keeps elements sorted; each pop reveals a "next greater/smaller" relationship.
- Every element is pushed and popped no more than once, so the scan is O(n) amortised.
- Largest rectangle uses smaller-height boundaries; the code assigns equal heights asymmetrically (previous strictly smaller, next smaller-or-equal) to cover their full span.
- A monotonic deque gives the max or min of every sliding window in O(n), while a heap with unbounded lazy deletion can take O(n log n).
- Store indices, choose strict or non-strict comparisons deliberately, and flush leftovers.

## Greedy digit removal uses a deletion budget

To make a nonnegative decimal number as small as possible after removing a fixed number of digits, scan its digits left to right. While deletions remain and the kept last digit is larger than the incoming digit, delete that last digit. At the first differing position, keeping the smaller incoming digit wins lexicographically for equal-length digit strings. If deletions remain after the scan, remove that many trailing digits. Strip leading zeros for the returned numeric representation and return zero if nothing remains.

The deletion budget matters: after it is exhausted, the retained digits need not stay monotonic. Each digit is still appended once and removed at most once, so the scan is linear in the number of input digits. This greedy use shares the stack’s total-operation proof, not every invariant of next-greater search.

## Key takeaways
- Count total pushes and pops across the scan rather than multiplying loop bounds.
- Permanent dominance supports nearest-element, sliding-extremum and greedy digit patterns.
- Indices retain position information needed for output, widths and expiry.

## Further reading
- [All nearest smaller values — Wikipedia](https://en.wikipedia.org/wiki/All_nearest_smaller_values)
- [Minimum stack / minimum queue — cp-algorithms](https://cp-algorithms.com/data_structures/stack_queue_modification.html)
- [Sliding window — USACO Guide](https://usaco.guide/gold/sliding-window)
- [Amortized analysis — Wikipedia](https://en.wikipedia.org/wiki/Amortized_analysis)
