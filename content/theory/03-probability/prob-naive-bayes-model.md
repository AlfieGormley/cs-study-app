---
id: prob-naive-bayes-model
title: Model feature evidence with naive Bayes
level: basic
minutes: 3
sourceLesson: prob-bayes
summary: Conditional independence within each class turns feature likelihoods into a product.
---

## Naive Bayes classifiers

A spam filter wants the chance an email is spam given the words in it. Bayes flips this round to the chance of those words given spam, which is easy to estimate by counting words in labelled email. **Ham** is the usual name for legitimate, non-spam email.

The **naive assumption** is conditional independence of the chosen features given the class. In the token model used by the later code and smoothing formula, tokens at the email’s positions are modelled as independent draws from a class-specific vocabulary distribution. Then each word contributes its own factor, and the denominator (the same for both classes) can be dropped when you only want to know which class wins:

```formula
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
Conditioning: every event to the right of a given bar in this card has positive probability
In words: start with how common the class is, then multiply in how typical each word is of that class.
```

A different presence-feature model uses the probability that an entire email contains a word, rather than the probability of a token draw. The questions below supply document-presence probabilities and assume those presence features are conditionally independent. Do not substitute token-frequency estimates for document-presence probabilities.

Compute the score for spam and for ham, and pick whichever is larger. Real words can remain correlated even within a class (for example, words in fixed phrases), so the naive assumption is an approximation and posterior scores may be poorly calibrated. Paul Graham’s 2002 "A Plan for Spam" describes a related Bayesian filter with token-selection and scoring choices beyond the simple model here.

## Key takeaways
- Conditional independence within each class turns feature likelihoods into a product.
- Compare class scores to classify; useful rankings do not guarantee calibrated probabilities.

## Further reading
- [Naive Bayes — scikit-learn](https://scikit-learn.org/stable/modules/naive_bayes.html)
- [A Plan for Spam — Paul Graham](https://www.paulgraham.com/spam.html)
