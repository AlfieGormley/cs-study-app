---
id: prob-basics
title: Probability basics and conditional probability
level: basic
minutes: 14
summary: Sample spaces, events, the axioms, complements, independence and conditional probability, with the counting tricks and reliability sums engineers use every day.
---

Probability is the maths of uncertainty. In computer science it turns up everywhere: hash collisions, randomised algorithms, network packet loss, cache hit ratios, the chance that three replicas fail at once, and every A/B test your product team runs.

This lesson builds the vocabulary from first principles. Everything later in the module (Bayes, expectation, distributions) rests on the ideas here, especially **conditional probability**.

## Sample spaces and events

A **random experiment** is anything with an uncertain outcome: rolling a die, sending a packet, picking a random pivot.

- The **sample space** is the set of all possible outcomes; formulas write it as the Greek capital letter omega. For one die, the sample space is {1, 2, 3, 4, 5, 6}.
- A **random event** (usually just called an event) is a subset of the sample space. "Roll an even number" is the event {2, 4, 6}.
- A **probability** P assigns each event a number between 0 and 1.

In a finite nonempty sample space, when every outcome is equally likely (a fair die, a uniformly random key), probability is just counting: the number of outcomes you are interested in, divided by the number of outcomes there are.

```formula
P(A) = |A| / |Ω|
where
P(A): the probability of event A, a number from 0 (it never happens) to 1 (it always happens)
A: the event we care about, written as the set of outcomes that count as "A happened"
Ω: omega, the sample space: the set of every possible outcome
|A|: the number of outcomes in A (vertical bars around a set mean "how many elements it has")
|Ω|: the total number of possible outcomes
In words: when every outcome is equally likely, the probability of an event is the fraction of all outcomes that belong to it.
```

Rolling two independent fair six-sided dice gives 6 × 6 = 36 equally likely ordered pairs. Six of them sum to 7: (1,6), (2,5), (3,4), (4,3), (5,2), (6,1).

```formula
P(S = 7) = 6 / 36 = 1/6
where
S: the sum of the two dice, a whole number from 2 to 12
P(S = 7): the probability that the two dice add up to 7
6: the number of ordered pairs that sum to 7
36: the number of ordered pairs (first die, second die), 6 × 6
In words: 6 of the 36 equally likely ordered pairs give a total of 7, so a 7 turns up one roll in six on average.
```

This only works when the outcomes really are equally likely. If they are not (a loaded die, a skewed traffic mix), you must weight each outcome by its own probability instead of counting.

> [!warning] Order matters when counting
> (1,6) and (6,1) are different outcomes. A classic mistake is to treat the 21 unordered pairs as equally likely: that gives the mixed pair {1,6} probability 1/21 instead of 2/36, or gives sum 7 probability 3/21 instead of 6/36. They are not: a double like (3,3) can happen one way, a mixed pair two ways.

## The axioms and the rules that follow

In general probability spaces, events belong to a specified collection of measurable subsets. For finite examples here, every subset can be an event. Kolmogorov's axioms are three rules every probability must obey: no probability is negative, something always happens, and for events that cannot happen together (**disjoint** events) probabilities add. The third rule holds for any countable collection of pairwise disjoint events; for two events it reads as the last line below.

```formula
P(A) ≥ 0   for every A
P(Ω) = 1
P(A ∪ B) = P(A) + P(B)   if A ∩ B = ∅
where
P(A): the probability of event A
A, B: any two events (sets of outcomes)
Ω: omega, the sample space, the set of all outcomes; it always happens
≥: greater than or equal to
A ∪ B: the union of A and B, the event "A or B (or both) happens"
A ∩ B: the intersection of A and B, the event "A and B both happen"
∅: the empty set, an event containing no outcomes, so it can never happen
In words: probabilities are never negative, the certain event has probability 1, and when two events can never happen together, the chance of one or the other is the sum of their chances.
```

From these three come the everyday rules. The **complement** of A is the event "A does not happen"; the **addition rule** (union rule) handles "A or B" when the two can overlap; the **union bound** is a cruder but always-safe version of it.

```formula
P(¬A) = 1 − P(A)
P(A ∪ B) = P(A) + P(B) − P(A ∩ B)
0 ≤ P(A) ≤ 1
P(A ∪ B) ≤ P(A) + P(B)
where
P(A): the probability of event A
A, B: any two events
¬A: the complement of A, the event "A does not happen" (¬ is the symbol for "not")
A ∪ B: the event "A or B (or both) happens"
A ∩ B: the event "both A and B happen"
≤: less than or equal to
In words: the chance of "not A" is whatever is left over from 1; for "A or B" add the two chances and subtract the overlap you counted twice; every probability lies between 0 and 1; and adding the two chances never underestimates the chance of "A or B".
```

The **addition rule** (inclusion–exclusion) subtracts the overlap, which would otherwise be counted twice. Of the numbers 1 to 100, 50 are divisible by 2, 33 by 3, and 16 by both (the multiples of 6).

```formula
|D_2 ∪ D_3| = |D_2| + |D_3| − |D_2 ∩ D_3|
|D_2 ∪ D_3| = 50 + 33 − 16 = 67
where
D_2: the set of numbers from 1 to 100 divisible by 2
D_3: the set of numbers from 1 to 100 divisible by 3
|D_2|: the number of elements in D_2 (vertical bars mean "how many")
∪: union, "in either set (or both)"
∩: intersection, "in both sets"; D_2 ∩ D_3 is the multiples of 6
In words: 50 even numbers plus 33 multiples of 3 counts the 16 multiples of 6 twice, so subtract them once: 67 numbers are divisible by 2 or 3.
```

The **union bound** drops the subtraction. It is crude but always safe, and it is the workhorse of algorithm analysis: if each of several bad events is individually unlikely, the chance that any of them happens is at most the total.

```formula
P(B_1 ∪ B_2 ∪ … ∪ B_n) ≤ n × p
where
B_1, B_2, …, B_n: n "bad" events, for example "request i hits a slow server"
n: how many bad events there are
p: an upper limit on each bad event's probability, so P(B_i) ≤ p for every i
P: probability
∪: union, "at least one of these happens"
…: and so on, for every event in between
≤: less than or equal to
In words: the chance that at least one of n bad things happens is never more than n times the largest individual chance, whether or not the events are independent.
```

For example, 100 hash lookups that each fail with probability at most 0.0001 fail one or more times with probability at most 100 × 0.0001 = 0.01. The bound becomes useless once n × p exceeds 1, because every probability is at most 1 anyway.

### The complement trick

"At least one" questions are almost always easier through the complement. What is the chance of at least one six in four independent rolls of a fair six-sided die?

Counting directly means handling one six, two sixes and so on. Instead, work out the chance of no six at all (each roll avoids a six with probability 5/6, and independent rolls multiply), then subtract from 1.

```formula
P(N = 0) = (5/6)^4 ≈ 0.482
P(N ≥ 1) = 1 − (5/6)^4 ≈ 0.518
where
N: the number of sixes in the four rolls
P(N = 0): the probability of no six in any of the four rolls
5/6: the chance that one roll is not a six
(5/6)^4: 5/6 multiplied by itself four times, once per independent roll
≈: approximately equal to (rounded)
≥: greater than or equal to
In words: four non-sixes in a row happen about 48% of the time, so at least one six happens about 52% of the time.
```

This is the same calculation as "what is the chance at least one of my 4 requests hits a slow server?" It relies on the rolls (or requests) being independent; correlated failures break the multiplication.

## Conditional probability

Often you learn something that shrinks the sample space. When P(B) > 0, the **conditional probability** of A given B is:

```formula
P(A | B) = P(A ∩ B) / P(B)
where
P(A | B): the probability of A given B; the vertical bar | is read "given" and means "once we know B happened"
A: the event we are asking about
B: the event we already know happened; P(B) must be greater than 0
P(A ∩ B): the probability that A and B both happen (∩ means "and", both together)
P(B): the probability of B
In words: restrict attention to the outcomes where B happened, and ask what fraction of those are also in A.
```

The formula fails when P(B) = 0: you cannot condition on something that never happens, and the division would be by zero.

> [!example] Two dice, sum is 8
> Given that two independent fair six-sided dice sum to 8, what is the chance the first die shows 3?
>
> The outcomes summing to 8 are (2,6), (3,5), (4,4), (5,3), (6,2). That is 5 outcomes, and one has a first die of 3.

```formula
P(F = 3 | S = 8) = (1/36) / (5/36)
P(F = 3 | S = 8) = 1/5
where
F: the value shown by the first die
S: the sum of the two dice
P: probability
|: "given"; the probability on the left assumes we already know S = 8
1/36: the probability of the single outcome (3,5), where F = 3 and S = 8 together
5/36: the probability that the sum is 8 (5 of the 36 ordered pairs)
In words: among the 5 equally likely ways to make 8, exactly one starts with a 3, so the chance is 1/5, higher than the unconditional 1/6.
```

Rearranging gives the **multiplication rule**, which is how you compute probabilities of sequences (the conditional on the right requires P(A) > 0):

```formula
P(A ∩ B) = P(A) × P(B | A)
where
P(A ∩ B): the probability that A and B both happen
P(A): the probability that A happens (here, the first step)
P(B | A): the probability of B given that A has already happened (| is read "given")
In words: the chance of A then B is the chance of A, times the chance of B once A has happened.
```

Draw two cards from a uniformly shuffled standard 52-card deck without replacement. The chance both are aces is:

```formula
P(A_1) = 4/52
P(A_2 | A_1) = 3/51
P(A_1 ∩ A_2) = 4/52 × 3/51
P(A_1 ∩ A_2) = 12/2652 = 1/221
where
A_1: the event "the first card is an ace"
A_2: the event "the second card is an ace"
P: probability
|: "given"; P(A_2 | A_1) is the chance of a second ace once the first card was an ace
∩: "and"; A_1 ∩ A_2 is "both cards are aces"
4/52: 4 aces among 52 cards
3/51: after one ace is gone, 3 aces remain among 51 cards
In words: a first ace happens 4 times in 52; after that, a second ace happens 3 times in 51; multiplying gives about a 0.45% chance (1 in 221).
```

The second fraction is conditional because the first draw changed the deck.

### The law of total probability

If B₁, B₂, ... form a countable partition of the sample space into disjoint pieces (every outcome lies in exactly one piece), you can find P(A) by working out A's chance inside each piece and weighting by how likely each piece is. Pieces with zero probability are left out.

```formula
P(A) = Σ_i P(A | B_i) × P(B_i)
where
P(A): the overall probability of event A
B_i: the i-th piece of the partition, for example "the request went to region i"
i: an index counting the pieces 1, 2, 3, …
Σ_i: sigma, "add up the following term for every piece i"
P(A | B_i): the probability of A given that we are in piece B_i (| is read "given")
P(B_i): the probability of landing in piece B_i
In words: the overall chance of A is a weighted average of its chance in each case, weighted by how often each case happens.
```

Suppose 70% of your traffic hits region X with a 1% error rate and 30% hits region Y with a 4% error rate.

```formula
P(R) = P(R | X) × P(X) + P(R | Y) × P(Y)
P(R) = 0.01 × 0.7 + 0.04 × 0.3
P(R) = 0.007 + 0.012 = 0.019
where
R: the event "a request returns an error"
X: the event "the request went to region X"; P(X) = 0.7 (70%)
Y: the event "the request went to region Y"; P(Y) = 0.3 (30%)
P(R | X): the error rate given region X, 0.01 (1%); | is read "given"
P(R | Y): the error rate given region Y, 0.04 (4%)
In words: the overall error rate is 1.9%, a traffic-weighted average of the two regional rates.
```

This rule is the denominator of Bayes' theorem in the next lesson.

## Independence

A and B are **independent events** if knowing one tells you nothing about the other:

```formula
P(A ∩ B) = P(A) × P(B)
P(A | B) = P(A)   if P(B) > 0
where
A, B: two events
P(A ∩ B): the probability that both A and B happen
P(A), P(B): the separate probabilities of A and of B
P(A | B): the probability of A given that B happened (| is read "given")
In words: two events are independent when the chance of both is the product of their chances; equivalently, learning that B happened leaves A's chance unchanged.
```

Independence is a property of the numbers, not of physical separation, and it can be surprising. With two independent fair six-sided dice, "first die is even" and "sum is 7" are independent, but "first die is even" and "sum is 8" are not:

```formula
P(V ∩ S_7) = 3/36 = 1/12
P(V) × P(S_7) = 1/2 × 1/6 = 1/12
P(V ∩ S_8) = 3/36 = 6/72
P(V) × P(S_8) = 1/2 × 5/36 = 5/72
where
V: the event "the first die is even"; P(V) = 1/2
S_7: the event "the sum is 7"; P(S_7) = 6/36 = 1/6
S_8: the event "the sum is 8"; P(S_8) = 5/36
P: probability
∩: "and", both events together
In words: for "sum is 7" the chance of both equals the product (1/12 each way), so it is independent of the first die being even; for "sum is 8" the two numbers differ (6/72 versus 5/72), so it is not.
```

The intuition: whatever the first die shows, exactly one second-die value makes 7, but a first die of 1 can never make 8.

> [!warning] Disjoint is not independent
> If A and B are disjoint and both have positive probability, they are *dependent*: knowing A happened tells you B certainly did not.

```formula
P(A ∩ B) = 0
P(A) × P(B) > 0
where
A, B: two disjoint events, each with probability above 0
P(A ∩ B): the probability that both happen, which is 0 because they never happen together
P(A), P(B): their separate probabilities
In words: for disjoint events the chance of both is zero, but the product of their chances is not, so the independence equation fails.
```

## Reliability: the engineer's favourite use

Independence makes system reliability easy to estimate. **System availability** is the fraction of time a component is up and serving.

In a **series system** (components in series: every component must work), multiply the availabilities. A request that passes through three services, each independently up 99.9% of the time, in a model with no other causes of failure:

```formula
A_s = a_1 × a_2 × a_3
A_s = 0.999 × 0.999 × 0.999 ≈ 0.997
where
A_s: the availability of the whole chain, the fraction of time every service is up at once
a_1, a_2, a_3: the availability of each service, here 0.999 (99.9%)
≈: approximately equal to (0.997003, rounded)
In words: the chain works only when all three work, so with independent failures the chance is the product, about 99.7%.
```

So the chain is down about 0.3% of the time, roughly three times worse than any single service. Long chains of dependencies erode availability.

With **parallel redundancy** (components in parallel: any one working replica is sufficient, with ideal routing and failover), multiply the failure probabilities. Three replicas, each down 1% of the time independently:

```formula
P(D) = q^3 = 0.01^3 = 0.000001
1 − P(D) = 0.999999
where
q: the probability that one replica is down, here 0.01 (1%)
q^3: q multiplied by itself three times, one factor per independent replica
D: the event "all three replicas are down at once"
P(D): the probability of D
In words: the cluster fails only when all three replicas are down together, about one moment in a million, giving "six nines" (99.9999%) availability.
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

How close should the simulated fraction be? Each simulated run is a **Bernoulli trial** (a yes/no experiment), and the typical size of the error in the estimated fraction is its **standard error**:

```formula
SE = √(p × (1 − p) / n)
SE ≤ √(0.25 / 1,000,000) = 0.0005
where
SE: the standard error, the typical distance between the simulated fraction and the true probability
p: the true probability being estimated (about 0.518 here)
n: the number of independent simulated trials, here 1,000,000
√: the square root
≤: less than or equal to
0.25: the largest possible value of p × (1 − p), reached when p = 0.5
In words: the error shrinks like one over the square root of the number of trials, so a million trials gives a typical error of at most 0.0005.
```

This is not a guarantee of three correct decimal places: the estimate can stray a few standard errors. Rare events (tiny p) can require far more trials for small relative error; exact enumeration is preferable when feasible.

## Common pitfalls

- **Assuming equal likelihood.** Counting outcomes only works if each is equally likely. "Either it rains or it doesn't" is not 50/50.
- **Confusing "A given B" with "B given A".** The chance a test is positive given disease is not the chance of disease given a positive test. The next lesson is entirely about this.
- **Assuming independence by default.** Retries to the same overloaded server, disks from the same batch, and users in the same household can be correlated.
- **The gambler's fallacy.** Independent events have no memory. After five heads, a fair coin is still 50/50.

## Key takeaways
- In a finite nonempty sample space with equally likely outcomes, the probability of an event is favourable outcomes divided by total outcomes; count ordered outcomes carefully.
- Use the complement for "at least one": one minus the chance of none.
- The conditional probability of A given B is the chance of both divided by the chance of B. It requires B to have positive probability and restricts the sample space to B; the multiplication rule chains conditionals.
- Independence means the chance of both equals the product of the chances. Disjoint events with positive probability are dependent.
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
