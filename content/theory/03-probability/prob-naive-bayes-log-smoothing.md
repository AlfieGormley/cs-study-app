---
id: prob-naive-bayes-log-smoothing
title: Compute naive Bayes scores with logs and smoothing
level: basic
minutes: 3
sourceLesson: prob-bayes
summary: Logs preserve the ranking of positive scores and avoid product underflow.
---

Two different problems can make a naive Bayes score collapse: a genuinely zero estimated likelihood, or floating-point underflow from multiplying many small positive numbers. They need different fixes.

## Keep scores usable

**Laplace smoothing** adds one pseudo-count to every token in a fixed finite vocabulary and normalises by the adjusted total. A vocabulary token unseen in one class then has a small positive likelihood rather than vetoing that class. Tokens outside the vocabulary still need an explicit policy.

Taking **log scores** turns products into sums. The logarithm preserves the ordering of positive scores, so the mathematical winning class is unchanged. This avoids product underflow; rounding can still affect very close scores. Logs cannot repair a zero likelihood: the real logarithm of zero is undefined.

## Read the implementation

```python
from math import log

def classify(words, prior, like):
    # Nonempty classes; positive priors.
    # Positive, smoothed likelihoods for
    # each token in a fixed vocabulary.
    words = tuple(words)  # allow generators
    best, best_score = None, float("-inf")
    for c in prior:
        # Logs turn the product into a sum.
        s = log(prior[c])
        for w in words:
            s += log(like[c][w])
        # Keep the largest class score.
        if s > best_score:
            best, best_score = c, s
    return best
```

The inputs must contain a nonempty set of classes, positive priors and a positive likelihood for every supplied token in every class. Converting the words to a tuple lets each class see the same tokens even if the caller supplied a generator. Ties retain the first class encountered.

```formula reference
ln(S_c) = ln(P(c)) + Σ_i ln(P(w_i | c))
P(w | c) = (n_{w,c} + 1) / (N_c + V)
where
ln: the natural logarithm, defined here only for positive scores and probabilities; it turns products into sums and preserves order
S_c: the naive Bayes score for category c
P(c): the prior chance of category c
Σ_i: sigma, "add up the following term for every word i"
w_i, w: a word (token) from the email
P(w | c): the smoothed estimate of the chance of word w in category c (| is read "given")
n_{w,c}: the nonnegative integer count of token w in all training email of category c
N_c: the nonnegative integer total token count in category c’s training email, the sum of its vocabulary token counts
V: the positive integer vocabulary size, the number of distinct tokens in the fixed vocabulary
c: the class, with positive prior probability
i: an index over the finite sequence of email tokens
1: the "add-one" pseudo-count given to every token
P: probability; probabilities are dimensionless and apply to measurable events
In words: Add logarithms of positive likelihoods to preserve the score ordering; add-one smoothing gives each token in the fixed vocabulary a positive estimated probability.
```

These formulas document the scoring and smoothing operations. Smoothing prevents vocabulary zeros; logs avoid repeated multiplication. Neither establishes feature independence, repairs a misleading prior or makes the scores calibrated probabilities.

## Key takeaways
- Distinguish unseen-token zeros from numerical underflow.
- Smooth within a defined vocabulary and handle unknown tokens separately.
- Add logs of positive likelihoods while preserving the score ordering.

## Further reading
- [Naive Bayes — scikit-learn](https://scikit-learn.org/stable/modules/naive_bayes.html)
- [A Plan for Spam — Paul Graham](https://www.paulgraham.com/spam.html)
