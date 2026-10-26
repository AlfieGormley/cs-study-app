---
id: cx-aggregate-appends
sourceLesson: cx-amortised-analysis
title: Dynamic arrays and total append cost
level: advanced
minutes: 3
summary: Bound the total writes and copies over a sequence of dynamic-array appends.
---

A dynamic array stores items in a contiguous region with spare capacity. Most appends fill a spare slot. When it is full, a resize may allocate a larger region and copy existing items.

## Analyse a sequence, not just its slowest operation

Consider an idealised array that starts empty with capacity one and doubles when full. Count one unit per copied or newly written element; ignore allocator details. Here n is the number of appends.

A resize-triggering append can copy every current item, so one operation can be linear in the current length. But it is too pessimistic to charge that cost to every append. After doubling, many spare slots can be filled before the next copy.

The copied capacities are one, two, four, eight and so on. This geometric series is bounded by a constant multiple of its largest term. Adding the one write per append therefore gives linear total work. For this model, total work is below three units per append when spread across the sequence.

**Aggregate analysis** establishes a bound for the whole sequence, then divides by its length. Constant amortised append cost means any sequence of n appends from the stated starting state costs O(n) total work. It does not mean every append is fast.

> [!analogy] Real-world analogy: Moving to a bigger bookshelf
> Moving books to a shelf with twice the space is expensive, but many later books fit without another move.
>
> **How it maps:** Spare shelf space corresponds to spare capacity; increasingly separated moves explain the linear total copying.
>
> **Where it stops:** The proof counts item moves under a fixed growth policy. Real allocation and item-copy costs may differ.

## No probability is involved

Amortised analysis averages cost across an operation sequence, not across random inputs. The sequence bound is deterministic under its model. Starting with a large full array would require accounting for that initial state; the from-empty proof cannot silently charge its first resize to earlier appends that never occurred.

CPython lists grow with spare capacity rather than precisely doubling. The same geometric-growth idea explains their amortised append behaviour; exact capacity sequences are implementation details.

## Key takeaways
- Rare expensive appends can coexist with linear total sequence cost.
- Amortised guarantees need a starting state and operation policy.
- Amortisation is different from average-case probability.

## Further reading
- [Erickson: Amortized Analysis](https://jeffe.cs.illinois.edu/teaching/algorithms/notes/09-amortize.pdf)
- [CPython 3.14 list implementation](https://raw.githubusercontent.com/python/cpython/3.14/Objects/listobject.c)
