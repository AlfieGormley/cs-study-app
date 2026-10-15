---
id: prob-odds-repeated-evidence
title: Update odds and repeated evidence
level: basic
minutes: 3
sourceLesson: prob-bayes
summary: Likelihood ratios multiply prior odds.
---

## The odds form: Bayes in your head

**Odds** compare the chance something happens with the chance it does not. A probability of 1% is odds of 1 : 99 ("1 to 99").

```formula
O = p / (1 − p)
p = O / (1 + O)
where
O: the odds in favour, as a single number; odds of 1 : 99 are O = 1/99
p: the probability, strictly between 0 and 1 (at exactly 0 or 1 the odds are 0 or infinite)
In words: odds are the chance of yes divided by the chance of no; the second line converts back.
```

In odds form Bayes becomes a single multiplication by the **likelihood ratio (L_ratio)**, how many times more likely the evidence is when H is true than when it is false. This needs the false positive rate to be above 0.

```formula
O_post = O_prior × L_ratio
L_ratio = P(E | H) / P(E | ¬H)
where
O_prior: the odds of H before the evidence
O_post: the odds of H after the evidence
L_ratio: the likelihood ratio
H: the hypothesis; ¬H means "H is false" (¬ is "not")
E: the evidence
P(E | H): how likely the evidence is if H is true (| is read "given")
P(E | ¬H): how likely the evidence is if H is false; must be above 0
P: probability; probabilities are dimensionless and apply to measurable events
Conditioning: every event to the right of a given bar in this card has positive probability
In words: multiply your odds before the evidence by how much more the evidence favours H than not H.
```

For the test, prior odds are 1 : 99:

```formula
L_ratio = 0.99 / 0.05 = 19.8
O_post = (1/99) × 19.8 = 0.2
p = 0.2 / (1 + 0.2) = 1/6
where
L_ratio: the likelihood ratio, sensitivity 0.99 divided by false positive rate 0.05
O_post: the odds of being ill after one positive test; 0.2 is odds of 1 : 5
p: the matching probability of being ill
In words: one positive test multiplies the odds by about 20, from 1 : 99 to 1 : 5, which is a probability of 1 in 6.
```

Same answer as before, with no denominators to work out.

Likelihood ratios multiply when the evidence pieces are conditionally independent both given H and given not H. Under that assumption, a second positive test multiplies the odds by 19.8 again:

```formula
O_2 = 0.2 × 19.8 = 3.96
p_2 = 3.96 / (1 + 3.96) ≈ 0.80
where
O_2: the odds of being ill after two positive tests, about 4 : 1
0.2: the odds after the first test
19.8: the likelihood ratio of each test
p_2: the matching probability, about 80%
≈: approximately equal to
In words: a second independent positive multiplies the odds by about 20 again, from 1 : 5 to about 4 : 1, or about 80%.
```

Yesterday's posterior is today's prior. This sequential updating is the heart of Bayesian reasoning.

## Key takeaways
- Likelihood ratios multiply prior odds.
- Repeated evidence uses unchanged likelihood ratios only under conditional independence in both classes.

## Further reading
- [Introduction to Probability — Grinstead and Snell](https://math.dartmouth.edu/~prob/prob/prob.pdf)
