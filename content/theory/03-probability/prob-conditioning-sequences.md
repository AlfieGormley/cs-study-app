---
id: prob-conditioning-sequences
title: Condition on evidence and draw sequences
level: basic
minutes: 3
sourceLesson: prob-basics
summary: Condition only on events with positive probability.
---

## Conditional probability

Often you learn something that shrinks the sample space. When the known event has positive probability, the **conditional probability** is:

```formula
P(A | B) = P(A ∩ B) / P(B)
where
P: probability of measurable events, dimensionless and between zero and one
P(A | B): the probability of A given B; the vertical bar | is read "given" and means "once we know B happened"
A: the event we are asking about
B: the event we already know happened; P(B) must be greater than 0
P(A ∩ B): the probability that A and B both happen (∩ means "and", both together)
P(B): the probability of B
Conditioning: every event to the right of a given bar in this card has positive probability
In words: restrict attention to the outcomes where B happened, and ask what fraction of those are also in A.
```

This elementary ratio is undefined when the conditioning event has probability zero. Infinite models can have possible events of probability zero, and other definitions of conditioning are needed there.

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
P: probability; probabilities are dimensionless and apply to measurable events
|: "given"; the probability on the left assumes we already know S = 8
1/36: the probability of the single outcome (3,5), where F = 3 and S = 8 together
5/36: the probability that the sum is 8 (5 of the 36 ordered pairs)
Conditioning: every event to the right of a given bar in this card has positive probability
In words: among the 5 equally likely ways to make 8, exactly one starts with a 3, so the chance is 1/5, higher than the unconditional 1/6.
```

Rearranging gives the **multiplication rule**, which is how you compute probabilities of sequences (the first event must have positive probability for the conditional on the right):

```formula
P(A ∩ B) = P(A) × P(B | A)
where
P: probability of measurable events, dimensionless and between zero and one
P(A ∩ B): the probability that A and B both happen
P(A): the probability that A happens (here, the first step)
P(B | A): the probability of B given that A has already happened (| is read "given")
Conditioning: every event to the right of a given bar in this card has positive probability
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
P: probability; probabilities are dimensionless and apply to measurable events
|: "given"; P(A_2 | A_1) is the chance of a second ace once the first card was an ace
∩: "and"; A_1 ∩ A_2 is "both cards are aces"
4/52: 4 aces among 52 cards
3/51: after one ace is gone, 3 aces remain among 51 cards
Conditioning: every event to the right of a given bar in this card has positive probability
In words: a first ace happens 4 times in 52; after that, a second ace happens 3 times in 51; multiplying gives about a 0.45% chance (1 in 221).
```

The second fraction is conditional because the first draw changed the deck.

## Key takeaways
- Condition only on events with positive probability.
- Without replacement, the next draw depends on the first.

## Further reading
- [Introduction to Probability — Grinstead and Snell](https://math.dartmouth.edu/~prob/prob/prob.pdf)
