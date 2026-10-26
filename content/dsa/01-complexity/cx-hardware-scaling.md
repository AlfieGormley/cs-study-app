---
id: cx-hardware-scaling
sourceLesson: cx-growth-rates
title: What faster hardware buys
level: basic
minutes: 2
summary: Translate a hardware speedup into the input size each growth rate can handle.
---

A faster machine can help immediately. How much larger an input it can handle in the same time depends on the algorithm's growth.

## More work budget, different input gains

Assume the new machine performs every counted operation at the same fixed speedup, with memory and other resources sufficient. This deliberately excludes changes in parallel overhead, cache behaviour or algorithm choice.

- For a linear scan, twice the work budget buys twice as many items.
- For pairwise work, twice as many items need roughly four times the budget. Input capacity grows more slowly than hardware speed.
- For a search that checks every subset at constant cost, each additional item doubles the candidate count. A doubling of machine speed therefore buys only one more item.

That last rule is additive: repeated hardware doublings add items rather than multiplying the previous item limit. A thousandfold speedup buys about ten extra binary choices under this model. It does not make an arbitrary exponential search practical.

> [!analogy] Real-world analogy: A growing dinner party
> Serving one plate per guest and arranging a conversation between every pair scale differently.
>
> **How it maps:** Plates resemble linear work; pair meetings resemble quadratic work. Faster service buys less extra capacity when the number of relationships also grows.
>
> **Where it stops:** Real meetings can overlap. The algorithm comparison assumes a fixed counted-work model and a uniform speedup.

A lower growth rate can give a larger long-term improvement than a constant hardware speedup, but that is not a reason to dismiss hardware upgrades. Measure the current bottleneck and expected input range. A better algorithm may have extra setup or memory costs; a practical decision includes those too.

## Key takeaways
- Hardware changes the work budget under the stated model.
- Quadratic work turns a large speed gain into a smaller input gain.
- Binary-choice exhaustive search gains one item per doubling of speed.

## Further reading
- [Erickson: Introduction](https://jeffe.cs.illinois.edu/teaching/algorithms/book/00-intro.pdf)
