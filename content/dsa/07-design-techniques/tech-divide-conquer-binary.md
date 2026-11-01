---
id: tech-divide-conquer-binary
title: Binary search and one shrinking subproblem
level: intermediate
minutes: 2
sourceLesson: tech-divide-conquer
summary: Use the master theorem to count midpoint probes when only one half survives.
---

Here n is the number of sorted items. The previous unit compared local work with leaf growth; binary search is its equal-exponent case with just one surviving half at each step.

### Binary search

Compare the target with the middle element and discard the half that can't contain it. That leaves **one** subproblem of half the size, and each call does only a constant amount of work: one probe and comparison.

In master-theorem terms there is a single call (so the number of calls never grows) and constant local work, which is the "every level equal" case. Constant work on each of about log₂ n levels gives a **logarithmic** running time.

What that means in practice:

- A billion sorted items need at most **30** midpoint probes: each probe halves the remaining range, and 2 to the power 30 is just over a billion.
- **Doubling** the data adds just **one** more probe: the first comparison cuts the doubled range back to the old size.
- Ten halvings shrink the range about a thousandfold, so every factor of a thousand in data costs about ten more probes.

```formula reference
p_max = floor(log_2(n)) + 1
where
p_max: the maximum number of midpoint probes ordinary binary search makes on a non-empty sorted range
n: the number of items in the range
floor: round down to the nearest whole number
log_2: the base-two logarithm: the number of times you can halve a number before reaching 1
In words: the worst case is one probe per halving, plus the final probe on a single remaining item; a billion items need at most thirty.
```

A three-way comparator can classify a probe in one comparison; separate equality and ordering tests may perform more.

Binary search is the degenerate case where "combine" is free and one half is thrown away entirely. Some people call this *decrease and conquer*.

> [!analogy] Real-world analogy: finding a name in a printed phone book
> You open the book near the middle, see whether the name you want comes before or after that page, and ignore the other half of the book. Then you repeat with the half you kept.
>
> **How it maps:** opening a page is a midpoint probe; alphabetical order is the sorted-input requirement that makes discarding half safe; each look roughly halves what is left, so even a huge book needs only a couple of dozen looks.
>
> **Where it stops:** people jump closer to the right letter (for "W" they open near the back), which is closer to interpolation search. Binary search always probes the exact middle, and it only works when the data really is sorted by the same key you compare.

## Key takeaways
- A midpoint comparison discards one half and leaves no costly combination.
- Count midpoint probes separately from language-level equality and ordering tests.

## Further reading
- [Recursive cost analysis — Erickson](https://jeffe.cs.illinois.edu/teaching/algorithms/book/01-recursion.pdf)
