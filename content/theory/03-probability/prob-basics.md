---
id: prob-basics
title: Probability basics and conditional probability
level: basic
minutes: 12
summary: Sample spaces, events, the axioms, complements, independence and conditional probability, with the counting tricks and reliability sums engineers use every day.
---

Probability is the maths of uncertainty. In computer science it turns up everywhere: hash collisions, randomised algorithms, network packet loss, cache hit ratios, the chance that three replicas fail at once, and every A/B test your product team runs.

This lesson builds the vocabulary from first principles. Everything later in the module (Bayes, expectation, distributions) rests on the ideas here, especially **conditional probability**.

## Sample spaces and events

An **experiment** is anything with an uncertain outcome: rolling a die, sending a packet, picking a random pivot.

- The **sample space** Ω is the set of all possible outcomes. For one die, Ω = {1, 2, 3, 4, 5, 6}.
- An **event** is a subset of Ω. "Roll an even number" is the event {2, 4, 6}.
- A **probability** P assigns each event a number between 0 and 1.

In a finite nonempty sample space, when every outcome is equally likely (a fair die, a uniformly random key), probability is just counting:

```
P(A) = |A| / |Ω|
     = favourable outcomes / all outcomes
```

Rolling two independent fair six-sided dice gives 6 × 6 = 36 equally likely ordered pairs. Six of them sum to 7: (1,6), (2,5), (3,4), (4,3), (5,2), (6,1). So P(sum = 7) = 6/36 = 1/6.

> [!warning] Order matters when counting
> (1,6) and (6,1) are different outcomes. A classic mistake is to treat the 21 unordered pairs as equally likely: that gives the mixed pair {1,6} probability 1/21 instead of 2/36, or gives sum 7 probability 3/21 instead of 6/36. They are not: a double like (3,3) can happen one way, a mixed pair two ways.

## The axioms and the rules that follow

In general probability spaces, events belong to a specified collection of measurable subsets. For finite examples here, every subset can be an event. Kolmogorov's axioms are:

1. P(A) ≥ 0 for every event A.
2. P(Ω) = 1. Something happens.
3. For any countable collection of pairwise **disjoint** events, the probability of their union equals the sum of their probabilities. For two events, this gives P(A ∪ B) = P(A) + P(B).

From these come the everyday rules:

| Rule | Formula |
|---|---|
| Complement | P(not A) = 1 − P(A) |
| Union | P(A ∪ B) = P(A) + P(B) − P(A ∩ B) |
| Bounds | 0 ≤ P(A) ≤ 1 |
| Union bound | P(A ∪ B) ≤ P(A) + P(B) |

The **union rule** (inclusion–exclusion) subtracts the overlap, which would otherwise be counted twice. Of the numbers 1 to 100, 50 are divisible by 2, 33 by 3, and 16 by both (the multiples of 6). So 50 + 33 − 16 = 67 are divisible by 2 or 3.

The **union bound** drops the subtraction. It is crude but always safe, and it is the workhorse of algorithm analysis: "each of n bad events has probability at most p, so the chance any of them happens is at most np".

### The complement trick

"At least one" questions are almost always easier through the complement. What is the chance of at least one six in four independent rolls of a fair six-sided die?

Counting directly means handling one six, two sixes and so on. Instead:

```
P(no six in 4 rolls) = (5/6)^4 ≈ 0.482
P(at least one six)  = 1 − 0.482 ≈ 0.518
```

This is the same calculation as "what is the chance at least one of my 4 requests hits a slow server?"

## Conditional probability

Often you learn something that shrinks the sample space. When P(B) > 0, the **conditional probability** of A given B is:

```
P(A | B) = P(A ∩ B) / P(B)
```

Read it as: "restrict attention to the outcomes where B happened, and ask what fraction of those are also in A."

> [!example] Two dice, sum is 8
> Given that two independent fair six-sided dice sum to 8, what is the chance the first die shows 3?
>
> The outcomes summing to 8 are (2,6), (3,5), (4,4), (5,3), (6,2). That is 5 outcomes, and one has a first die of 3. So P(first = 3 | sum = 8) = 1/5, higher than the unconditional 1/6.

Rearranging gives the **multiplication rule**, which is how you compute probabilities of sequences (the displayed conditional requires P(A) > 0):

```
P(A ∩ B) = P(A) × P(B | A)
```

Draw two cards from a uniformly shuffled standard 52-card deck without replacement. The chance both are aces is:

```
P(1st ace)          = 4/52
P(2nd ace | 1st ace) = 3/51
P(both)  = 4/52 × 3/51 = 12/2652 = 1/221
```

The second factor is conditional because the first draw changed the deck.

### The law of total probability

If B₁, B₂, ... form a countable partition of Ω into disjoint pieces, then (omitting any zero-probability pieces):

```
P(A) = Σ P(A | Bᵢ) × P(Bᵢ)
```

Suppose 70% of your traffic hits region X with a 1% error rate and 30% hits region Y with a 4% error rate. The overall error rate is 0.7 × 0.01 + 0.3 × 0.04 = 0.007 + 0.012 = 0.019, or 1.9%. This rule is the denominator of Bayes' theorem in the next lesson.

## Independence

A and B are **independent** if knowing one tells you nothing about the other:

```
P(A ∩ B) = P(A) × P(B)
equivalently, if P(B) > 0: P(A | B) = P(A)
```

Independence is a property of the numbers, not of physical separation, and it can be surprising. With two independent fair six-sided dice, "first die is even" and "sum is 7" are independent: P(both) = 3/36 = 1/12, and 1/2 × 1/6 = 1/12. But "first die is even" and "sum is 8" are not: P(both) = 3/36, while 1/2 × 5/36 = 5/72.

> [!warning] Disjoint is not independent
> If A and B are disjoint and both have positive probability, they are *dependent*: knowing A happened tells you B certainly did not. P(A ∩ B) = 0, but P(A) × P(B) > 0.

## Reliability: the engineer's favourite use

Independence makes system reliability easy to estimate.

**In series** (every component must work), multiply the availabilities. A request that passes through three services, each independently up 99.9% of the time, in a model with no other causes of failure:

```
0.999 × 0.999 × 0.999 ≈ 0.997
```

So the chain is down about 0.3% of the time, roughly three times worse than any single service. Long dependency chains erode availability.

**In parallel** (any one working replica is sufficient, with ideal routing and failover), multiply the failure probabilities. Three replicas, each down 1% of the time independently:

```
P(all down) = 0.01³ = 0.000001
P(up)       = 0.999999 ("six nines")
```

> [!warning] Real failures are correlated
> The six-nines figure assumes the replicas fail independently. Put them in the same rack, region, power feed or software version and a single event takes them all down. Separating replicas across failure domains can reduce shared infrastructure risks, while a bad deployment across all replicas can still defeat redundancy. When an estimate looks too good, the independence assumption is usually the culprit.

## Checking your answers by simulation

When you are unsure of a calculation, simulate it. For independent trials from the specified model, the sample frequency converges to the model probability as the number of trials grows. This checks arithmetic against a simulation; it does not establish that the model describes the real system.

```python
import random

def at_least_one_six(rolls=4):
    return any(random.randint(1, 6) == 6
               for _ in range(rolls))

trials = 1_000_000
hits = sum(at_least_one_six()
           for _ in range(trials))
print(hits / trials)   # about 0.518
```

For small sample spaces you can be exact instead, by enumerating every outcome:

```python
from itertools import product
from fractions import Fraction

dice = list(product(range(1, 7), repeat=2))
sum8 = [d for d in dice if sum(d) == 8]
first3 = [d for d in sum8 if d[0] == 3]
print(Fraction(len(first3), len(sum8)))
# 1/5
```

For n independent Bernoulli trials, the estimate has standard error √(p(1 − p)/n), at most 0.0005 for a million trials. This is not a guarantee of three correct decimal places. Rare events can require far more trials for small relative error; exact enumeration is preferable when feasible.

## Common pitfalls

- **Assuming equal likelihood.** Counting outcomes only works if each is equally likely. "Either it rains or it doesn't" is not 50/50.
- **Confusing P(A | B) with P(B | A).** The chance a test is positive given disease is not the chance of disease given a positive test. The next lesson is entirely about this.
- **Assuming independence by default.** Retries to the same overloaded server, disks from the same batch, and users in the same household can be correlated.
- **The gambler's fallacy.** Independent events have no memory. After five heads, a fair coin is still 50/50.

## Key takeaways
- In a finite nonempty sample space with equally likely outcomes, P(A) = favourable / total; count ordered outcomes carefully.
- Use the complement for "at least one": 1 − P(none).
- P(A | B) = P(A ∩ B) / P(B) requires P(B) > 0 and restricts the sample space to B; the multiplication rule chains conditionals.
- Independence means P(A ∩ B) = P(A)P(B). Disjoint events with positive probability are dependent.
- Series availability multiplies uptimes; parallel availability multiplies failure probabilities, but only if failures are truly independent.
- Simulate or enumerate to check any answer you are unsure of.

## Further reading
- [Probability axioms — Wikipedia](https://en.wikipedia.org/wiki/Probability_axioms)
- [Conditional probability — Wikipedia](https://en.wikipedia.org/wiki/Conditional_probability)
- [Independence (probability theory) — Wikipedia](https://en.wikipedia.org/wiki/Independence_(probability_theory))
- [Mathematics for Computer Science (MIT OCW 6.042J)](https://ocw.mit.edu/courses/6-042j-mathematics-for-computer-science-fall-2010/)
- [Introduction to Probability — Grinstead and Snell (free PDF)](https://math.dartmouth.edu/~prob/prob/prob.pdf)

> [!note] Evidence gap
> The previous precise attribution of the four-roll example to a particular 1654 exchange is omitted because that historical detail was not independently established in this review. The calculation is unchanged.
