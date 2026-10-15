---
id: pat-nearest-variants
title: Adapt nearest-element answers to distance and wraparound
level: advanced
minutes: 3
sourceLesson: pat-monotonic
summary: Daily temperatures records an index gap rather than the warmer value.
---

Use the preceding next-greater stack as the prerequisite. Here n is the input length; comparisons and indexing are treated as constant-cost.

## Nearest-element variants

| Want | Scan | Pop while top is |
|---|---|---|
| Next greater (right) | L→R | `< x` |
| Next smaller (right) | L→R | `> x` |
| Previous greater | L→R | `<= x`, then top |
| Previous smaller | L→R | `>= x`, then top |

For "previous" variants, the answer for `x` is whatever is left on top of the stack *after* popping (or none if empty).

**Circular arrays** (the element after the last is the first): loop `i` over `range(2 * n)` and use `a[i % n]`, only pushing during the first pass. Here `%` is Python's remainder operator, so `i % n` wraps index n back to 0, n + 1 to 1, and so on.

**Daily temperatures** ("how many days until a warmer day?") is the same algorithm storing `i - j` instead of the value, where `j` is the index being popped (the colder day) and `i` the index of the warmer day that pops it. **Stock span** uses the previous greater element.

## Translate the answer, retain the waiting invariant

For temperatures `[73, 74, 75, 71, 69, 72, 76, 73]`, days at indices 3 and 4 remain waiting when 72 arrives at index 5. It answers both: the waits are two days and one day respectively. The later 76 answers the earlier 75 at index 2 with a four-day wait. Initialise unanswered waits to zero rather than the next-value example’s minus-one marker.

For circular next greater on `[5, 4, 3, 2, 1]`, the first pass leaves every index waiting. On the second pass, 5 answers the four smaller values. The original 5 stays unanswered because equality is not strictly greater. Push only first-pass positions so the second pass supplies answers without duplicating work.

For **stock span**, count today and all immediately preceding no-higher prices. After discarding no-greater stack candidates, subtract the previous strictly greater price’s index from today’s index; use minus one for that earlier index if no such price exists. This includes today in the returned span.

## Key takeaways
- Daily temperatures records an index gap rather than the warmer value.
- A second circular pass supplies wraparound answers without pushing indices twice.
- Previous-element variants answer from the remaining stack top after discarding unsuitable values.

## Further reading
- [All nearest smaller values — Wikipedia](https://en.wikipedia.org/wiki/All_nearest_smaller_values)
- [Minimum stack / minimum queue — cp-algorithms](https://cp-algorithms.com/data_structures/stack_queue_modification.html)
- [Sliding window — USACO Guide](https://usaco.guide/gold/sliding-window)
- [Amortized analysis — Wikipedia](https://en.wikipedia.org/wiki/Amortized_analysis)
