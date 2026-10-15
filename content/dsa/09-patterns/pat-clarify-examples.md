---
id: pat-clarify-examples
title: Clarify the problem and work an example
level: basic
minutes: 3
sourceLesson: pat-approach
summary: Clarify input domains, permitted mutations and the required return value before choosing an algorithm.
---

A routine can help you clarify the requested behavior, develop a correct approach, explain your reasoning and test boundary cases. Treat the following as practical advice, not a guarantee of interview success; interview formats and scoring vary.

> [!note] Content gap
> Population-wide claims about why most candidates fail are omitted because no reliable survey or causal evidence is provided.

This module is a catalogue of patterns. These first units cover the routine you run *before* picking one.

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

- **Input size.** "How large can `n` be?" Here, and throughout this module, n means the number of elements in the input (the length of the array or string) unless a problem says otherwise. Use the answer to compare growth against the resource budget (see the following input-growth unit).
- **Value ranges.** Negative numbers? Zeros? Can values cause integer overflow in 32 bits?
- **Sortedness and duplicates.** Is the array sorted? Can values repeat?
- **Output shape.** Indices or values? One answer or all? What if there is no answer: return `-1`, `None`, raise?
- **Mutability.** May I modify the input in place?
- **Ties.** If several answers are valid, does it matter which?

> [!tip] Questions are signals
> "Is the array sorted?" is not small talk. A yes points straight at binary search or two pointers. "Can values be negative?" matters for monotone sum-window rules (the sliding-window units), though fixed-size windows and other window predicates can still handle negatives.

## Step 2: examples

Write one ordinary example and work it by hand. Then list the edge cases you'll test at the end:

- empty input, a single element
- all values equal, all distinct
- already sorted, reverse sorted
- negatives, zeros, the largest allowed values
- the answer at the very start or very end

Working an example by hand often reveals the algorithm. Watch what *you* do: if you keep scanning back over the same elements, that repeated scan is the thing to optimise.

## Key takeaways
- Clarify input domains, permitted mutations and the required return value before choosing an algorithm.
- Work a normal case by hand and record boundary cases for later tests.
- The five-step routine is practical advice; interview timing and scoring vary.

## Further reading
- [Coding interview techniques — Tech Interview Handbook](https://www.techinterviewhandbook.org/coding-interview-techniques/)
- [Coding interview cheatsheet — Tech Interview Handbook](https://www.techinterviewhandbook.org/coding-interview-cheatsheet/)
- [How to Solve It (Pólya) — Wikipedia](https://en.wikipedia.org/wiki/How_to_Solve_It)
- [Time complexity — Wikipedia](https://en.wikipedia.org/wiki/Time_complexity)
