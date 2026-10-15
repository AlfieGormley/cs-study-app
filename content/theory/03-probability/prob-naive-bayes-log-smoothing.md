---
id: prob-naive-bayes-log-smoothing
title: Compute naive Bayes scores with logs and smoothing
level: basic
minutes: 4
sourceLesson: prob-bayes
summary: Logs preserve the ranking of positive scores and avoid product underflow.
---

The preceding model scores a class by multiplying its prior and token likelihoods. This unit computes that score without multiplying a long chain of small floating-point numbers. The function assumes a nonempty collection of classes, positive priors and positive smoothed probabilities for every supplied token.

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

Two practical details matter:

1. **Work in logs.** Multiplying enough small probabilities can underflow to zero in floating point. Summing finite logs avoids that product underflow and preserves the mathematical ranking; floating-point rounding can still affect close scores.
2. **Smooth the counts.** If "invoice" never appeared in your spam training set, its estimated chance in spam is 0, and one word vetoes everything else. **Laplace (add-one) smoothing** adds 1 to each token count in a fixed vocabulary and normalises by the total count plus vocabulary size. Every token in that vocabulary then has positive probability in every class; out-of-vocabulary tokens need a separate policy.

The log step and the smoothing step, written out:

```formula
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
Conditioning: every event to the right of a given bar in this card has positive probability
In words: add logs instead of multiplying probabilities, and pretend every word was seen once more than it was, so no word ever gets probability 0.
```

For example, if "invoice" appears 0 times in 50,000 spam words with a 10,000-token vocabulary, the smoothed estimate is (0 + 1) / (50,000 + 10,000) ≈ 0.0000167 instead of 0. A small number, but no longer a veto.

## Pitfalls

- **Confusing the inverse.** The chance of the evidence given the hypothesis and the chance of the hypothesis given the evidence are not equal in general. In court this is the **prosecutor's fallacy**: "the chance of a DNA match if innocent is 1 in a million, so the chance he is innocent is 1 in a million." In a hypothetical population of 10 million innocent people each with that marginal match probability, the expected number of matches is 10; the actual count and posterior need further assumptions.
- **Ignoring the prior.** "The test is 99% accurate" says nothing about the chance a positive person is ill until you know prevalence.
- **Assuming tests are independent.** Rerunning the same test on the same sample often repeats the same error. Using unchanged per-test likelihood ratios requires conditional independence both with and without the condition. Otherwise use the likelihood of the new evidence conditional on what was already observed.
- **Priors of exactly 0 or 1.** Within a fixed model, conditioning on positive-probability evidence preserves probability-zero and probability-one events. Evidence the model assigns probability zero makes the elementary update undefined; revise the model rather than dividing by zero.

## Key takeaways
- Logs preserve the ranking of positive scores and avoid product underflow.
- Add-one smoothing is defined over a fixed finite vocabulary.
- Repeated evidence and probability-zero priors need explicit modelling assumptions.

## Further reading
- [Naive Bayes — scikit-learn](https://scikit-learn.org/stable/modules/naive_bayes.html)
- [A Plan for Spam — Paul Graham](https://www.paulgraham.com/spam.html)
