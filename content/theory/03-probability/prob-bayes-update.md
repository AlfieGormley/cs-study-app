---
id: prob-bayes-update
title: Derive the Bayesian update
level: basic
minutes: 3
sourceLesson: prob-bayes
summary: The posterior combines likelihood and prior, then normalises by the evidence.
---

In a hypothetical example, your fraud model detects 98% of fraud and only flags 1% of honest payments. A payment is flagged. How likely is it to be fraud?

The 98% detection rate is not the answer. Under this model, if 1 in 1,000 payments is fraudulent, the answer is about **9%**. More than nine out of ten alerts are false alarms.

Ignoring the base rate when interpreting that detection rate is the base-rate fallacy, and Bayes' theorem is the tool that fixes it. It matters for monitoring, intrusion detection, spam filtering, medical tests, ML classifiers and debugging alike.

## The theorem

Bayes' theorem answers one question: you know how likely the evidence is if a cause is true, and you want how likely the cause is now that you have seen the evidence. It comes straight from the multiplication rule of the previous lesson, which writes the chance of "A and B" in two ways. Both events need positive probability for the conditionals to make sense.

```formula
P(A ∩ B) = P(A | B) × P(B)
P(A ∩ B) = P(B | A) × P(A)
P(A | B) = (P(B | A)P(A)) / P(B)
where
P: probability of measurable events, dimensionless and between zero and one
A, B: two events, each with probability greater than 0
P(A): the probability of A, a number from 0 to 1
P(A ∩ B): the probability that A and B both happen (∩ means "and")
P(A | B): the probability of A given B; the bar | is read "given", meaning "once we know B happened"
P(B | A): the probability of B given A, the conditional the other way round
Conditioning: every event to the right of a given bar in this card has positive probability
In words: write "A and B" both ways round, set the two equal and divide by P(B); that turns "B given A" into "A given B".
```

Renamed for real use, with H a hypothesis (a possible cause) and E the evidence you observed, each part has a name:

```formula
P(H | E) = (P(E | H)P(H)) / P(E)
where
H: a positive-probability hypothesis, for example "this patient is ill" or "this payment is fraud"
E: the observed event, for example "the test came back positive"; its probability must be positive
P(H): the **prior probability** (the prior), your belief in H before seeing the evidence (often the base rate)
P(E | H): the **likelihood term** (the likelihood), how expected the evidence is if H is true (| is read "given")
P(E): the **evidence term**, how common the evidence is overall, from every cause
P(H | E): the **posterior**, your belief in H after seeing the evidence
P: probability, from 0 to 1; probabilities are dimensionless and apply to measurable events
Conditioning: every event to the right of a given bar in this card has positive probability
In words: belief after = how well H explains the evidence × belief before ÷ how common the evidence is anyway.
```

The denominator comes from the law of total probability: the evidence can arise when H is true or when it is false.

```formula
P(E) = P(E | H) × P(H)
     + P(E | ¬H) × P(¬H)
where
P: probability of measurable events, dimensionless and between zero and one
H: the hypothesis; both H and its complement have positive probability for these conditional terms
¬H: "not H", the hypothesis is false (¬ is the symbol for "not")
E: the evidence event, assumed to have positive probability when used for the Bayesian update
P(E | H): how often the evidence appears when H is true (| is read "given")
P(E | ¬H): how often the evidence appears when H is false, the false positive rate
P(H), P(¬H): the prior chances of H and of not H; they add up to 1
Conditioning: every event to the right of a given bar in this card has positive probability
In words: evidence comes from true cases and from false alarms, so its overall chance is the sum of both routes.
```

That second term, the false positives from the huge "not H" population, is what intuition forgets.

## Key takeaways
- The posterior combines likelihood and prior, then normalises by the evidence.
- Positive conditioning probabilities are required.

## Further reading
- [Introduction to Probability — Grinstead and Snell](https://math.dartmouth.edu/~prob/prob/prob.pdf)
