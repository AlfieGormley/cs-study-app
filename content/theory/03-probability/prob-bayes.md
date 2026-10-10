---
id: prob-bayes
title: Bayes' theorem and the base-rate fallacy
level: basic
minutes: 15
summary: How to turn the chance of the evidence given a cause into the chance of the cause given the evidence, how rare events and false-positive rates affect the meaning of an alert, and how naive Bayes spam filters work.
---

In a hypothetical example, your fraud model detects 98% of fraud and only flags 1% of honest payments. A payment is flagged. How likely is it to be fraud?

The 98% detection rate is not the answer. Under this model, if 1 in 1,000 payments is fraudulent, the answer is about **9%**. More than nine out of ten alerts are false alarms.

Ignoring the base rate when interpreting that detection rate is the base-rate fallacy, and Bayes' theorem is the tool that fixes it. It matters for monitoring, intrusion detection, spam filtering, medical tests, ML classifiers and debugging alike.

## The theorem

Bayes' theorem answers one question: you know how likely the evidence is if a cause is true, and you want how likely the cause is now that you have seen the evidence. It comes straight from the multiplication rule of the previous lesson, which writes the chance of "A and B" in two ways. Both events need positive probability for the conditionals to make sense.

```formula
P(A ∩ B) = P(A | B) × P(B)
P(A ∩ B) = P(B | A) × P(A)
P(A | B) = P(B | A) × P(A) / P(B)
where
A, B: two events, each with probability greater than 0
P(A): the probability of A, a number from 0 (never) to 1 (always)
P(A ∩ B): the probability that A and B both happen (∩ means "and")
P(A | B): the probability of A given B; the bar | is read "given", meaning "once we know B happened"
P(B | A): the probability of B given A, the conditional the other way round
In words: write "A and B" both ways round, set the two equal and divide by P(B); that turns "B given A" into "A given B".
```

Renamed for real use, with H a hypothesis (a possible cause) and E the evidence you observed, each part has a name:

```formula
P(H | E) = P(E | H) × P(H) / P(E)
where
H: the hypothesis, for example "this patient is ill" or "this payment is fraud"
E: the evidence, for example "the test came back positive"
P(H): the **prior probability** (the prior), your belief in H before seeing the evidence (often the base rate)
P(E | H): the **likelihood term** (the likelihood), how expected the evidence is if H is true (| is read "given")
P(E): the **evidence term**, how common the evidence is overall, from every cause
P(H | E): the **posterior**, your belief in H after seeing the evidence
P: probability, from 0 to 1
In words: belief after = how well H explains the evidence × belief before ÷ how common the evidence is anyway.
```

The denominator comes from the law of total probability: the evidence can arise when H is true or when it is false.

```formula
P(E) = P(E | H) × P(H)
     + P(E | ¬H) × P(¬H)
where
H: the hypothesis
¬H: "not H", the hypothesis is false (¬ is the symbol for "not")
E: the evidence
P(E | H): how often the evidence appears when H is true (| is read "given")
P(E | ¬H): how often the evidence appears when H is false, the false positive rate
P(H), P(¬H): the prior chances of H and of not H; they add up to 1
In words: evidence comes from true cases and from false alarms, so its overall chance is the sum of both routes.
```

That second term, the false positives from the huge "not H" population, is what intuition forgets.

## The classic test example

In a hypothetical probability model, a condition affects 1% of people and a test has:

- **Sensitivity** (true positive rate) 99%: an ill person tests positive 99% of the time.
- **False positive rate** 5%: a healthy person tests positive 5% of the time (so the **specificity**, the chance a healthy person tests negative, is 95%).

You test positive. What is the chance you are ill?

```formula
P(T) = P(T | I) × P(I) + P(T | ¬I) × P(¬I)
P(T) = 0.99 × 0.01 + 0.05 × 0.99
P(T) = 0.0099 + 0.0495 = 0.0594
P(I | T) = P(T | I) × P(I) / P(T)
P(I | T) = 0.0099 / 0.0594 ≈ 0.167
where
I: the event "the person is ill"; the prior P(I) = 0.01 (1% prevalence)
¬I: "not ill", healthy; P(¬I) = 0.99
T: the event "the test is positive"
P: probability
|: read "given"
P(T | I): the sensitivity, 0.99
P(T | ¬I): the false positive rate, 0.05
P(I | T): the posterior, the chance of being ill given a positive test
≈: approximately equal to
In words: positives come from 0.99% of people who are ill and 4.95% of people who are healthy, so only about one positive in six is ill.
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

```

The positives are 99 + 495 = 594 people, and 99 of them are ill:

```formula
P(I | T) = N_TP / (N_TP + N_FP)
P(I | T) = 99 / (99 + 495) = 99 / 594
P(I | T) ≈ 0.167 = 16.7%
where
N_TP: the expected number of **true positives**, ill people who test positive: 99 % of 100 = 99
N_FP: the expected number of **false positives**, healthy people who test positive: 5 % of 9,900 = 495
P(I | T): the chance a person is ill given a positive test (| is read "given")
P: probability
≈: approximately equal to
%: per cent, hundredths; 16.7% = 0.167
In words: of the 594 people who test positive, 99 are really ill, about one in six.
```

The 495 false positives swamp the 99 true positives because the healthy group is 99 times larger. The table of counts makes the numerator and denominator explicit; its entries are expected counts, not guaranteed outcomes in every sample.

> [!note] Evidence gap
> The previous broad claim about how much better people reason with counts is omitted here because its study populations, tasks and effect sizes were not established in this review. No population-wide claim is needed for the arithmetic.

## The base-rate fallacy in engineering

The same arithmetic applies to anything that detects rare events.

> [!example] Fraud alerts
> 1,000,000 payments, 0.1% fraudulent, the model catches 98% of fraud and flags 1% of legitimate ones.
>
> - Fraud: 1,000, of which 980 flagged.
> - Legitimate: 999,000, of which 9,990 flagged.

```formula
P(F | G) = N_TP / (N_TP + N_FP)
P(F | G) = 980 / (980 + 9,990)
P(F | G) = 980 / 10,970 ≈ 0.089
where
F: the event "the payment is fraud"
G: the event "the model flags the payment"
P(F | G): the chance a flagged payment is fraud (| is read "given"), the alert's precision
P: probability
N_TP: flagged fraud (true positives), 98% of 1,000 = 980
N_FP: flagged legitimate payments (false positives), 1% of 999,000 = 9,990
≈: approximately equal to
In words: only 980 of 10,970 alerts are real fraud, about 8.9%.
```

Under these fixed rates, a randomly selected alert has fraud probability about 8.9%; a finite queue need not match that fraction exactly.

The same shape shows up in:

- **Intrusion detection.** When attacks are rare enough relative to the false positive rate, benign connections can generate most alerts. The operational effect depends on traffic volume and triage capacity.
- **Pager alerts.** A noisy alert that fires on harmless blips teaches on-call engineers to dismiss it. The Google SRE book's advice to alert on symptoms that matter to users is partly a base-rate argument.
- **Flaky tests.** Suppose 1 in 500 builds contains a bug, the test detects every such bug, and it also fails on 2% of bug-free builds. Then only about 9% of failures mean a real bug (worked below). This is a hypothetical model, not a judgement about a particular failed build.
- **ML classifiers on imbalanced data.** A model that says "never fraud" is 99.9% accurate and useless. Report precision and recall, not accuracy.

```formula
P(B | X) = P(X | B) × P(B) / P(X)
P(B | X) = (1 × 0.002)
  / (1 × 0.002 + 0.02 × 0.998)
P(B | X) = 0.002 / 0.02196 ≈ 0.091
where
B: the event "the build contains a bug"; P(B) = 1/500 = 0.002
X: the event "the test fails"
P: probability
|: read "given"
P(X | B): the chance the test fails on a buggy build, 1 (it catches every bug)
0.02: the chance it fails on a bug-free build (2%)
0.998: the chance a build is bug-free, 1 − 0.002
≈: approximately equal to
In words: real bugs cause 0.2% of builds to fail and flakiness causes about 2%, so only about 9.1% of failures are real bugs.
```

> [!note] Precision is the posterior
> In **machine learning (ML)** terms, the chance a case is actually positive given that it was predicted positive is **precision** (also called positive predictive value), and the chance it is predicted positive given that it is actually positive is **recall** (sensitivity, the true positive rate). Holding sensitivity and false positive rate fixed, changing the base rate changes precision. Recall is a conditional rate; it can also change if the population shift changes the mix of positive cases.

## What actually improves an alert?

Take the hypothetical test (1% prevalence, 99% sensitivity, 5% false positive rate, posterior 16.7%) and vary one thing at a time, keeping the other conditional rates fixed:

| Change | Chance ill if positive |
|---|---|
| Baseline | 16.7% |
| Sensitivity 99% to 100% | 16.8% |
| False positives 5% to 1% | 50% |
| Test only a group with 10% prevalence | 68.8% |

In this example, false positives dominate and sensitivity is already near 100%, so that small sensitivity increase barely helps. Reducing the false positive rate or testing a higher-prevalence population raises precision if other rates stay fixed. A real filtering step can also change sensitivity and false positive rate; re-estimate them on the selected population. Low prevalence alone does not imply mostly false alerts: a detector with zero false positives is a counterexample.

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

In odds form Bayes becomes a single multiplication by the **likelihood ratio (LR)**, how many times more likely the evidence is when H is true than when it is false. This needs the false positive rate to be above 0.

```formula
O_post = O_prior × LR
LR = P(E | H) / P(E | ¬H)
where
O_prior: the odds of H before the evidence
O_post: the odds of H after the evidence
LR: the likelihood ratio
H: the hypothesis; ¬H means "H is false" (¬ is "not")
E: the evidence
P(E | H): how likely the evidence is if H is true (| is read "given")
P(E | ¬H): how likely the evidence is if H is false; must be above 0
P: probability
In words: multiply your odds before the evidence by how much more the evidence favours H than not H.
```

For the test, prior odds are 1 : 99:

```formula
LR = 0.99 / 0.05 = 19.8
O_post = (1/99) × 19.8 = 0.2
p = 0.2 / (1 + 0.2) = 1/6
where
LR: the likelihood ratio, sensitivity 0.99 divided by false positive rate 0.05
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

## Naive Bayes classifiers

A spam filter wants the chance an email is spam given the words in it. Bayes flips this round to the chance of those words given spam, which is easy to estimate by counting words in labelled email. **Ham** is the usual name for legitimate, non-spam email.

The **naive assumption** is that words are independent given the class. Then each word contributes its own factor, and the denominator (the same for both classes) can be dropped when you only want to know which class wins:

```formula
S_c = P(c) × Π_i P(w_i | c)
where
c: a class, here either spam or ham
S_c: the score for class c, proportional to the chance the email is in class c
P(c): the prior, the fraction of training email in class c
w_i: the i-th word of the email
i: a counter running over the words, 1, 2, 3, …
Π_i: capital pi, "multiply the following term together for every word i"
P(w_i | c): the chance of seeing word w_i in an email of class c (| is read "given"), estimated by counting
P: probability
In words: start with how common the class is, then multiply in how typical each word is of that class.
```

Compute the score for spam and for ham, and pick whichever is larger. Real words can remain correlated even within a class (for example, words in fixed phrases), so the naive assumption is an approximation and posterior scores may be poorly calibrated. Paul Graham’s 2002 "A Plan for Spam" describes a related Bayesian filter with token-selection and scoring choices beyond the simple model here.

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
2. **Smooth the counts.** If "invoice" never appeared in your spam training set, its estimated chance in spam is 0, and one word vetoes everything else. **Laplace (add-one) smoothing** adds 1 to each token count in a fixed vocabulary and normalises by the total count plus vocabulary size. Every token in that vocabulary then has positive probability in every class; out-of-vocabulary tokens need a separate policy.

The log step and the smoothing step, written out:

```formula
ln(S_c) = ln P(c) + Σ_i ln P(w_i | c)
P(w | c) = (n_{w,c} + 1) / (N_c + V)
where
ln: the natural logarithm; it turns products into sums, ln(a × b) = ln(a) + ln(b), and keeps the order of scores
S_c: the naive Bayes score for class c
P(c): the prior chance of class c
Σ_i: sigma, "add up the following term for every word i"
w_i, w: a word (token) from the email
P(w | c): the smoothed estimate of the chance of word w in class c (| is read "given")
n_{w,c}: how many times word w appears in the training email of class c
N_c: the total number of word occurrences in class c's training email
V: the vocabulary size, the number of distinct tokens in the fixed vocabulary
1: the "add-one" pseudo-count given to every token
P: probability
In words: add logs instead of multiplying probabilities, and pretend every word was seen once more than it was, so no word ever gets probability 0.
```

For example, if "invoice" appears 0 times in 50,000 spam words with a 10,000-token vocabulary, the smoothed estimate is (0 + 1) / (50,000 + 10,000) ≈ 0.0000167 instead of 0. A small number, but no longer a veto.

## Pitfalls

- **Confusing the inverse.** The chance of the evidence given the hypothesis and the chance of the hypothesis given the evidence are not equal in general. In court this is the **prosecutor's fallacy**: "the chance of a DNA match if innocent is 1 in a million, so the chance he is innocent is 1 in a million." In a hypothetical population of 10 million innocent people each with that marginal match probability, the expected number of matches is 10; the actual count and posterior need further assumptions.
- **Ignoring the prior.** "The test is 99% accurate" says nothing about the chance a positive person is ill until you know prevalence.
- **Assuming tests are independent.** Rerunning the same test on the same sample often repeats the same error. Using unchanged per-test likelihood ratios requires conditional independence both with and without the condition. Otherwise use the likelihood of the new evidence conditional on what was already observed.
- **Priors of exactly 0 or 1.** Within a fixed model, conditioning on positive-probability evidence preserves probability-zero and probability-one events. Evidence the model assigns probability zero makes the elementary update undefined; revise the model rather than dividing by zero.

## Key takeaways
- Bayes: the posterior equals the likelihood times the prior, divided by the overall chance of the evidence, which comes from the law of total probability.
- With rare events, even a small false positive rate can make most alerts false; calculate the posterior from all three rates.
- Natural frequencies (counts out of 10,000) make Bayesian reasoning easy to explain.
- Reducing false positives or raising prevalence improves precision when the other rates stay fixed; the size of a sensitivity improvement matters too.
- Odds form: posterior odds are prior odds times the likelihood ratio; likelihood ratios multiply under the appropriate conditional-independence assumptions.
- Naive Bayes multiplies per-feature likelihoods; compute in logs and smooth zero counts.

## Further reading
- [Bayes' theorem — Wikipedia](https://en.wikipedia.org/wiki/Bayes%27_theorem)
- [Base rate fallacy — Wikipedia](https://en.wikipedia.org/wiki/Base_rate_fallacy)
- [Naive Bayes classifier — Wikipedia](https://en.wikipedia.org/wiki/Naive_Bayes_classifier)
- [A Plan for Spam — Paul Graham](https://www.paulgraham.com/spam.html)
- [Monitoring Distributed Systems — Google SRE book](https://sre.google/sre-book/monitoring-distributed-systems/)

- [Naive Bayes — scikit-learn documentation](https://scikit-learn.org/stable/modules/naive_bayes.html)
