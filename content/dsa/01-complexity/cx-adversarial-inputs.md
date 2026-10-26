---
id: cx-adversarial-inputs
sourceLesson: cx-in-practice
title: Hostile inputs and worst-case bounds
level: advanced
minutes: 2
summary: Recognise when an attacker can force expensive algorithm paths.
---

Typical performance is not enough when someone can choose inputs that expose expensive paths. Ask what the algorithm guarantees under the actual input and randomness model.

## Three ways input can amplify work

- **Hash collisions:** a basic hash table can degrade to a linear scan when many keys collide. Repeated insertion can then take quadratic work in the key count. Keyed hash randomisation makes predictable collision attacks harder; it is not a universal constant-time guarantee for arbitrary keys.
- **Regex backtracking:** some patterns force a backtracking engine to explore many alternatives, giving superlinear or exponential behaviour. Cloudflare's July 2019 outage involved excessive backtracking that exhausted CPU capacity. Check the engine and the exact search API: guarantees for one fixed-pattern search do not automatically cover repeated-match iteration or an unbounded pattern size.
- **Predictable quicksort pivots:** repeatedly selecting an end element on sorted distinct input leaves one nearly unchanged partition and can cause quadratic work. Randomisation gives an expected guarantee under its assumptions; an introspective fallback to heapsort supplies a worst-case time bound.

## Match the defence to the source of risk

Use a suitable worst-case bound when latency must be bounded by the algorithm. Where randomisation is appropriate, state what remains unpredictable to the input chooser. Apply input and resource limits as well: even a linear scan takes too long or too much memory on an unbounded request.

A fixed tiny configuration list and an ordinary fixed-width numeric sum do not have the same shape-dependent amplification as those examples. That does not make all costs irrelevant: huge input, expensive user-defined comparisons or growing integers require their own model.

## Key takeaways
- Check who chooses the input and which slow paths remain reachable.
- Randomised expected guarantees and worst-case guarantees are different.
- Bound input size and operation cost as well as the growth rate.

## Further reading
- [Python hash randomisation](https://docs.python.org/3.14/reference/datamodel.html#object.__hash__)
- [Cloudflare's July 2019 outage analysis](https://blog.cloudflare.com/details-of-the-cloudflare-outage-on-july-2-2019/)
- [RE2 design guarantees](https://github.com/google/re2)
