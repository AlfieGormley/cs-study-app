---
id: cx-resizing-policies
sourceLesson: cx-amortised-analysis
title: Growth policies and safe shrinking
level: advanced
minutes: 2
summary: Choose growth and shrink thresholds that avoid repeated full-array copying.
---

Amortised append performance depends on the growth rule. Assume a resize copies all current items, each copy costs one unit, and the array starts empty with fixed initial capacity.

## Fixed increments keep resizes too frequent

Adding a hundred slots at a time eventually means copying a huge array after only another hundred appends. Copy sizes grow in an arithmetic progression. Across n appends the total copying is quadratic in n, so amortised cost per append grows linearly.

Multiplying capacity by a fixed factor greater than one instead creates room for proportionally more appends each time. Copy sizes form a geometric progression and total copying is linear. Doubling, growing by one half, and growing by a fixed one eighth all give constant amortised append cost with suitable integer rounding.

A smaller fixed factor saves spare capacity but causes more copying. Exact growth factors are implementation details; CPython 3.14 uses proportional over-allocation with rounding and small-size adjustments. A bulk insertion can follow additional rules, so do not infer its allocation from a single-item append example.

## Separate growth and shrink thresholds

Suppose the array doubles when full and halves as soon as it becomes half full. Append to a full array, then pop: the append grows it, the pop shrinks it, and the next append must grow it again. Every operation can copy nearly the whole array.

Use **hysteresis**: for example, grow when full but shrink only at a quarter full, halving capacity. After shrinking, the array is half full; after growth it is roughly half full. A substantial number of updates must occur before another resize. With a fixed minimum capacity, this supports constant amortised push and pop cost.

> [!analogy] Real-world analogy: A thermostat's dead band
> Heating does not switch on and off at exactly the same temperature boundary.
>
> **How it maps:** Separated thresholds prevent tiny reversals from repeatedly triggering an expensive state change.
>
> **Where it stops:** Array guarantees follow counted updates and copying costs, not physical heating dynamics.

## Key takeaways
- Fixed-factor growth spaces expensive copies apart.
- Fixed-increment growth leads to quadratic total copying.
- Separate growth and shrink thresholds prevent repeated resizing at one boundary.

## Further reading
- [CPython 3.14 list implementation](https://raw.githubusercontent.com/python/cpython/3.14/Objects/listobject.c)
- [Erickson: Amortized Analysis](https://jeffe.cs.illinois.edu/teaching/algorithms/notes/09-amortize.pdf)
