---
id: prob-randomised-guarantees
title: Distinguish randomised algorithm guarantees
level: advanced
minutes: 3
sourceLesson: prob-algorithms
summary: Las Vegas correctness is certain while runtime can vary.
---

Randomness is one of the most useful tools in algorithm design. Independent uniform pivots give quicksort good expected performance on fixed distinct-key inputs. Secret keyed hashing makes precomputed collision attacks harder. Random sampling can reduce the data needed for an estimate, with accuracy and runtime depending on the task.

Using randomness well needs the probability from the earlier lessons: indicators and linearity, the complement trick and the union bound. This lesson applies them to the problems you will meet in interviews and in production.

## Two kinds of randomised algorithm

| Kind | Always correct? | Running time |
|---|---|---|
| Las Vegas | Yes | Random |
| Monte Carlo | Not always | Bounded |

- **Las Vegas** algorithms always give the right answer; only their running time is random. Quicksort with uniform random pivots is the standard example: it always sorts, but how long it takes depends on the pivots.
- **Monte Carlo** algorithms run in bounded time but may be wrong with small probability. The Miller–Rabin primality test may call a composite number "probably prime", with probability at most 1/4 per round for an odd composite input when the base is sampled uniformly from the required range.

Monte Carlo errors can be driven down by independent repetition. With independent rounds, a composite number must fool every round to be accepted:

```formula
P(F) ≤ (1/4)^k
(1/4)^20 = 1 / 2^40 ≈ 9.1 × 10^{−13}
where
P: probability of measurable events, dimensionless and between zero and one
F: the event "a fixed odd composite input passes all k rounds"
k: the number of independent Miller–Rabin rounds, 20 in the second line
1/4: the most a single round can be fooled, when its base is chosen uniformly at random
P(F): the probability of F
≤: less than or equal to
≈: approximately equal to
10^{−13}: ten to the minus 13, 0.0000000000001
In words: each independent round at least quarters the chance of being fooled, so 20 rounds leave less than one chance in a trillion (10^{−12}).
```

This bounds acceptance of a fixed composite under the sampling model; it is not directly the posterior probability that a returned candidate is composite.

> [!note] Evidence gap
> The previous comparison with hardware-fault probability is omitted because no hardware error model or measured execution exposure supported it.

## Key takeaways
- Las Vegas correctness is certain while runtime can vary.
- Independent repetitions reduce the stated fixed-input Monte Carlo error bound.

## Further reading
- [Mathematics for Computer Science — MIT](https://ocw.mit.edu/courses/6-042j-mathematics-for-computer-science-fall-2010/)
