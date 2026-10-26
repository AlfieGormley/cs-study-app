---
id: prob-randomised-guarantees
title: Distinguish randomised algorithm guarantees
level: advanced
minutes: 3
sourceLesson: prob-algorithms
summary: Las Vegas correctness is certain while runtime can vary.
---

When an algorithm uses randomness, ask which part of its promise is uncertain: the answer, the amount of work, or both. An average running time is different from a limit on every execution.

## Two kinds of guarantee

A **Las Vegas algorithm** produces a correct answer when it returns; its running time depends on random choices. Quicksort with fresh uniform pivots always sorts its distinct-key input correctly, but an unlucky sequence can still cause quadratic work.

A **Monte Carlo algorithm** has a controlled running-time budget but may return an incorrect answer. The randomised Miller–Rabin primality test can label a composite input “probably prime”. For a fixed odd composite and a uniformly chosen base in the required range, at most one-quarter of bases fool a round.

## What repetition buys

For the same fixed composite to fool several independent rounds, every round must accept it. Independence lets their error bounds multiply. More rounds reduce the fixed-input error bound; reusing the same random base does not supply fresh independent evidence.

```formula reference
P(F) ≤ (1/4)^k
where
P: probability of measurable events, dimensionless and between zero and one
F: the event "a fixed odd composite input passes all k rounds"
k: the positive integer number of independent Miller–Rabin rounds
1/4: the most a single round can be fooled, when its base is chosen uniformly at random
P(F): the probability of F
≤: less than or equal to
In words: Each independent uniformly sampled round reduces the stated fixed-composite acceptance bound by a factor of four.
```

The bound concerns acceptance conditional on a fixed composite input. It is not the posterior probability that a candidate is composite after acceptance; that also depends on how candidates were selected. The distinction is the same confusion about the direction of conditioning encountered with alert detectors.

Choose the number of rounds from the acceptable error bound and threat model, using a trusted implementation. Do not substitute predictable random choices for the stated uniform independent sampling assumption.

## Key takeaways
- Las Vegas correctness and random runtime are separate properties.
- Independent repetition can reduce a Monte Carlo error bound.
- A fixed-input error bound is not automatically a posterior probability.

## Further reading
- [Miller–Rabin error bounds — Handbook of Applied Cryptography, chapter 4](https://cacr.uwaterloo.ca/hac/about/chap4.pdf)
- [Mathematics for Computer Science — MIT](https://ocw.mit.edu/courses/6-042j-mathematics-for-computer-science-fall-2010/)
