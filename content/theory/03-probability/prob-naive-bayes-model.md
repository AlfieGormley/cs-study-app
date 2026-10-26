---
id: prob-naive-bayes-model
title: Model feature evidence with naive Bayes
level: basic
minutes: 3
sourceLesson: prob-bayes
summary: Conditional independence within each class turns feature likelihoods into a product.
---

A **naive Bayes classifier** compares explanations for a set of features. In email, the classes might be spam and **ham**, meaning legitimate email. A word common in spam and uncommon in ham is evidence towards spam; its rate within spam alone is not a posterior probability.

## Combine prior and feature evidence

For each class, start from its prior frequency and combine how typical the observed features are within that class. The naive assumption makes those features conditionally independent given the class, so their likelihood factors multiply. Compare class scores; a common normalising denominator can be omitted when only the winning class matters.

```formula reference
S_c = P(c) × Π_i P(w_i | c)
where
c: a class, here either spam or ham
S_c: the score for category c, proportional to the chance the email is in category c
P(c): the prior, the fraction of training email in category c
w_i: the i-th word of the email
i: a counter running over the words, 1, 2, 3, …
Π_i: the product sign Π, "multiply the following term together for every word i"
P(w_i | c): the probability of token w_i at position i in the class-c token model (| is read "given"), estimated from token counts
P: probability; probabilities are dimensionless and apply to measurable events
In words: start with how common the class is, then multiply in how typical each word is of that class.
```

This token model treats word positions as independent draws from a class-specific vocabulary distribution. A document-presence model instead asks whether a word occurs anywhere in the email. Token frequencies and document-presence probabilities are different inputs and cannot be interchanged.

## Useful classification is not calibrated certainty

Two words may occur together in a phrase even within spam messages. Treating them as independent may count overlapping evidence twice and produce overly extreme probabilities. The model can still classify usefully, but a good spam/ham ranking does not demonstrate that a reported probability is calibrated.

When comparing two positive indicators, a second word more characteristic of spam strengthens the spam score under the stated independence model. In practice, check dependence and evaluate predictions on held-out labelled examples.

## Key takeaways
- Compare evidence under competing classes and include their priors.
- Conditional independence simplifies scoring but needs scrutiny.
- Specify whether features describe token occurrences or document presence.

## Further reading
- [Naive Bayes — scikit-learn](https://scikit-learn.org/stable/modules/naive_bayes.html)
- [A Plan for Spam — Paul Graham](https://www.paulgraham.com/spam.html)
