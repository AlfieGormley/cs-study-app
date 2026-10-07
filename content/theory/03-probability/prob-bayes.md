---
id: prob-bayes
title: Bayes' theorem and the base-rate fallacy
level: basic
minutes: 12
summary: How to turn P(evidence | cause) into P(cause | evidence), how rare events and false-positive rates affect the meaning of an alert, and how naive Bayes spam filters work.
---

In a hypothetical example, your fraud model detects 98% of fraud and only flags 1% of honest transactions. A transaction is flagged. How likely is it to be fraud?

The 98% detection rate is not the answer. Under this model, if 1 in 1,000 transactions is fraudulent, the answer is about **9%**. More than nine out of ten alerts are false alarms.

Ignoring the base rate when interpreting that detection rate is the base-rate fallacy, and Bayes' theorem is the tool that fixes it. It matters for monitoring, intrusion detection, spam filtering, medical tests, ML classifiers and debugging alike.

## The theorem

From the previous lesson, P(A ∩ B) = P(A | B) P(B) = P(B | A) P(A). Assume P(A) > 0 and P(B) > 0 for the displayed elementary conditionals, then divide by P(B):

```
           P(B | A) × P(A)
P(A | B) = ---------------
                P(B)
```

In words, with H a hypothesis and E the evidence:

| Term | Name | Meaning |
|---|---|---|
| P(H) | prior | belief before evidence |
| P(E \| H) | likelihood | how expected E is if H |
| P(E) | evidence | how common E is overall |
| P(H \| E) | posterior | belief after evidence |

The denominator comes from the law of total probability:

```
P(E) = P(E | H) P(H) + P(E | not H) P(not H)
```

That second term, the false positives from the huge "not H" population, is what intuition forgets.

## The classic test example

In a hypothetical probability model, a condition affects 1% of people and a test has:

- **Sensitivity** (true positive rate) 99%: P(+ | ill) = 0.99.
- **False positive rate** 5%: P(+ | healthy) = 0.05 (specificity 95%).

You test positive. What is P(ill | +)?

```
P(+) = 0.99 × 0.01 + 0.05 × 0.99
     = 0.0099 + 0.0495 = 0.0594

P(ill | +) = 0.0099 / 0.0594 ≈ 0.167
```

Only about **1 in 6** positives is genuinely ill, despite 99% sensitivity. Sensitivity and overall accuracy are different quantities.

### Natural frequencies make it obvious

Use expected counts in a hypothetical group of 10,000 people:

```
          10,000 people
         /             \
    100 ill          9,900 healthy
    /     \           /         \
 99 +     1 -     495 +      9,405 -

positives = 99 + 495 = 594
P(ill | +) = 99 / 594 ≈ 16.7%
```

The 495 false positives swamp the 99 true positives because the healthy group is 99 times larger. The count table makes the numerator and denominator explicit; its entries are expected counts, not guaranteed outcomes in every sample.

> [!note] Evidence gap
> The previous broad claim about how much better people reason with counts is omitted here because its study populations, tasks and effect sizes were not established in this review. No population-wide claim is needed for the arithmetic.

## The base-rate fallacy in engineering

The same arithmetic applies to anything that detects rare events.

> [!example] Fraud alerts
> 1,000,000 transactions, 0.1% fraudulent, the model catches 98% of fraud and flags 1% of legitimate ones.
>
> - Fraud: 1,000, of which 980 flagged.
> - Legitimate: 999,000, of which 9,990 flagged.
> - P(fraud | flagged) = 980 / 10,970 ≈ 8.9%.
>
> Under these fixed rates, a randomly selected alert has fraud probability about 8.9%; a finite queue need not match that fraction exactly.

The same shape shows up in:

- **Intrusion detection.** When attacks are rare enough relative to the false positive rate, benign connections can generate most alerts. The operational effect depends on traffic volume and triage capacity.
- **Pager alerts.** A noisy alert that fires on harmless blips teaches on-call engineers to dismiss it. The Google SRE book's advice to alert on symptoms that matter to users is partly a base-rate argument.
- **Flaky tests.** Suppose 1 in 500 builds contains a bug, the test detects every such bug, and it also fails on 2% of bug-free builds. Then P(bug | failure) = 0.002 / (0.002 + 0.998 × 0.02) ≈ 9.1%. This is a hypothetical model, not a judgement about a particular failed build.
- **ML classifiers on imbalanced data.** A model that says "never fraud" is 99.9% accurate and useless. Report precision and recall, not accuracy.

> [!note] Precision is the posterior
> In ML terms, P(actually positive | predicted positive) is **precision** (also called positive predictive value), and P(predicted positive | actually positive) is **recall** (sensitivity). Holding sensitivity and false positive rate fixed, changing the base rate changes precision. Recall is a conditional rate; it can also change if the population shift changes the mix of positive cases.

## What actually improves an alert?

Take the hypothetical test (1% prevalence, 99% sensitivity, 5% false positive rate, posterior 16.7%) and vary one thing at a time, keeping the other conditional rates fixed:

| Change | P(ill \| +) |
|---|---|
| Baseline | 16.7% |
| Sensitivity 99% → 100% | 16.8% |
| False positives 5% → 1% | 50% |
| Test only a group with 10% prevalence | 68.8% |

In this example, false positives dominate and sensitivity is already near 100%, so that small sensitivity increase barely helps. Reducing the false positive rate or testing a higher-prevalence population raises precision if other rates stay fixed. A real pre-filter can also change sensitivity and false positive rate; re-estimate them on the selected population. Low prevalence alone does not imply mostly false alerts: a detector with zero false positives is a counterexample.

## The odds form: Bayes in your head

For 0 < P < 1, finite positive odds are P / (1 − P). The likelihood ratio below also assumes P(E | not H) > 0. A probability of 1% is odds of 1 : 99. In odds form Bayes becomes a single multiplication:

```
posterior odds = prior odds × LR

LR (likelihood ratio)
   = P(E | H) / P(E | not H)
```

For the test: LR = 0.99 / 0.05 = 19.8. Prior odds 1 : 99, so posterior odds are 19.8 : 99 = 1 : 5. Odds of 1 : 5 mean a probability of 1/6. Same answer, no denominators.

Likelihood ratios multiply when the evidence pieces are conditionally independent both given H and given not H. Under that assumption, a second positive test multiplies the odds by 19.8 again: 19.8 : 5 ≈ 4 : 1, so P ≈ 80%. Yesterday's posterior is today's prior. This sequential updating is the heart of Bayesian reasoning.

## Naive Bayes classifiers

A spam filter wants P(spam | words in the email). Bayes flips it to P(words | spam), which is easy to estimate by counting words in labelled email.

The **naive** assumption is that words are independent given the class. Then each word contributes its own likelihood ratio:

```
score(spam) = P(spam) × Π P(wᵢ | spam)
score(ham)  = P(ham)  × Π P(wᵢ | ham)
```

Pick whichever score is larger. Real words can remain correlated even within a class (for example, words in fixed phrases), so the naive assumption is an approximation and posterior scores may be poorly calibrated. Paul Graham’s 2002 "A Plan for Spam" describes a related Bayesian filter with token-selection and scoring choices beyond the simple model here.

```python
from math import log

def classify(words, prior, like):
    # Nonempty classes; positive priors.
    # Positive, smoothed likelihoods for
    # each token in a fixed vocabulary.
    words = tuple(words)  # allow generators
    best, best_score = None, float("-inf")
    for c in prior:
        s = log(prior[c])
        for w in words:
            s += log(like[c][w])
        if s > best_score:
            best, best_score = c, s
    return best
```

Two practical details matter:

1. **Work in logs.** Multiplying hundreds of small probabilities underflows to 0.0 in floating point. Summing finite logs avoids that product underflow and preserves the mathematical ranking; floating-point rounding can still affect close scores.
2. **Smooth the counts.** If "invoice" never appeared in your spam training set, P(invoice | spam) = 0 and one word vetoes everything else. **Laplace (add-one) smoothing** adds 1 to each token count in a fixed vocabulary and normalises by the total count plus vocabulary size. Every token in that vocabulary then has positive probability in every class; out-of-vocabulary tokens need a separate policy.

## Pitfalls

- **Confusing the inverse.** P(E | H) and P(H | E) are not equal in general. In court this is the **prosecutor's fallacy**: "the chance of a DNA match if innocent is 1 in a million, so the chance he is innocent is 1 in a million." In a hypothetical population of 10 million innocent people each with that marginal match probability, the expected number of matches is 10; the actual count and posterior need further assumptions.
- **Ignoring the prior.** "The test is 99% accurate" says nothing about P(ill | +) until you know prevalence.
- **Assuming tests are independent.** Rerunning the same test on the same sample often repeats the same error. Using unchanged per-test likelihood ratios requires conditional independence both with and without the condition. Otherwise use the likelihood of the new evidence conditional on what was already observed.
- **Priors of exactly 0 or 1.** Within a fixed model, conditioning on positive-probability evidence preserves probability-zero and probability-one events. Evidence the model assigns probability zero makes the elementary update undefined; revise the model rather than dividing by zero.

## Key takeaways
- Bayes: P(H | E) = P(E | H) P(H) / P(E), with P(E) from the law of total probability.
- With rare events, even a small false positive rate can make most alerts false; calculate the posterior from all three rates.
- Natural frequencies (counts out of 10,000) make Bayesian reasoning easy to explain.
- Reducing false positives or raising prevalence improves precision when the other rates stay fixed; the size of a sensitivity improvement matters too.
- Odds form: posterior odds = prior odds × likelihood ratio; likelihood ratios multiply under the appropriate conditional-independence assumptions.
- Naive Bayes multiplies per-feature likelihoods; compute in logs and smooth zero counts.

## Further reading
- [Bayes' theorem — Wikipedia](https://en.wikipedia.org/wiki/Bayes%27_theorem)
- [Base rate fallacy — Wikipedia](https://en.wikipedia.org/wiki/Base_rate_fallacy)
- [Naive Bayes classifier — Wikipedia](https://en.wikipedia.org/wiki/Naive_Bayes_classifier)
- [A Plan for Spam — Paul Graham](https://www.paulgraham.com/spam.html)
- [Monitoring Distributed Systems — Google SRE book](https://sre.google/sre-book/monitoring-distributed-systems/)

- [Naive Bayes — scikit-learn documentation](https://scikit-learn.org/stable/modules/naive_bayes.html)
