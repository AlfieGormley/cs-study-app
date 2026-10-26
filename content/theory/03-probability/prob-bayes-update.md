---
id: prob-bayes-update
title: Update beliefs with Bayes’ theorem
level: basic
minutes: 3
sourceLesson: prob-bayes
summary: The posterior combines likelihood and prior, then normalises by the evidence.
---

A detector catching most fraud does not mean most of its alerts are fraud. One statement starts with fraudulent payments; the other starts with flagged payments. **Bayes’ theorem** connects those different reference groups.

## Reweight competing explanations

Start with a **prior probability**: how plausible each explanation is before this evidence. For each explanation, ask how likely it would make the evidence: its **likelihood**. Combine prior and likelihood, then normalise across the possible explanations. The result is a **posterior**.

```formula essential
P(H | E) = (P(E | H)P(H)) / P(E)
where
H: a positive-probability hypothesis, for example "this patient is ill" or "this payment is fraud"
E: the observed event, for example "the test came back positive"; its probability must be positive
P(H): the **prior probability** (the prior), your belief in H before seeing the evidence (often the base rate)
P(E | H): the **likelihood term** (the likelihood), how expected the evidence is if H is true (| is read "given")
P(E): the **evidence term**, how common the evidence is overall, from every cause
P(H | E): the **posterior**, your belief in H after seeing the evidence
P: probability, from 0 to 1; probabilities are dimensionless and apply to measurable events
In words: Reweight the prior by how likely the hypothesis makes the evidence, then normalise by the evidence probability across all explanations.
```

The denominator counts every way the evidence can arise, including false alerts. The elementary update needs positive evidence probability; the displayed likelihood also needs a positive prior for its conditioning hypothesis.

## A strong detector can still have many false alerts

Imagine fraudulent payments are rare. Even a small false-positive rate applied to the much larger legitimate population can generate more alerts than correctly detected fraud. A flag can raise the probability of fraud substantially while leaving fraud less likely than a false alarm.

Ignoring the prior is the **base-rate fallacy**. Ignoring how often legitimate cases trigger the evidence is another way to lose the comparison. Neither the detection rate alone nor the prior alone determines the posterior.

Within a fixed model, positive-probability evidence cannot revive a hypothesis assigned prior probability zero. Evidence the model declares impossible makes this elementary update undefined; revisit the model rather than dividing by zero.

## Key takeaways
- Prior, likelihood and posterior describe different stages of reasoning.
- Include all explanations for the observed evidence.
- A detection rate is not the probability that an alert is genuine.

## Further reading
- [Introduction to Probability — Grinstead and Snell](https://math.dartmouth.edu/~prob/prob/prob.pdf)
