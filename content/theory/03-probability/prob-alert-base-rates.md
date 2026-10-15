---
id: prob-alert-base-rates
title: Interpret rare-event alerts
level: basic
minutes: 4
sourceLesson: prob-bayes
summary: Precision depends on prevalence as well as conditional detection rates.
---

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
P: probability; probabilities are dimensionless and apply to measurable events
N_TP: flagged fraud (true positives), 98% of 1,000 = 980
N_FP: flagged legitimate payments (false positives), 1% of 999,000 = 9,990
≈: approximately equal to
Conditioning: every event to the right of a given bar in this card has positive probability
In words: only 980 of 10,970 alerts are real fraud, about 8.9%.
```

Under these fixed rates, a randomly selected alert has fraud probability about 8.9%; a finite queue need not match that fraction exactly.

The same shape shows up in:

- **Intrusion detection.** When attacks are rare enough relative to the false positive rate, benign connections can generate most alerts. The operational effect depends on traffic volume and triage capacity.
- **Pager alerts.** A noisy alert that fires on harmless blips teaches on-call engineers to dismiss it. The Google SRE book's advice to alert on symptoms that matter to users is partly a base-rate argument.
- **Flaky tests.** Suppose 1 in 500 builds contains a bug, the test detects every such bug, and it also fails on 2% of bug-free builds. Then only about 9% of failures mean a real bug (worked below). This is a hypothetical model, not a judgement about a particular failed build.
- **ML classifiers on imbalanced data.** A model that says "never fraud" is 99.9% accurate and useless. Report precision and recall, not accuracy.

```formula
P(B | X) = (P(X | B)P(B)) / P(X)
P(B | X) = (1 × 0.002)
  / (1 × 0.002 + 0.02 × 0.998)
P(B | X) = 0.002 / 0.02196 ≈ 0.091
where
B: the event "the build contains a bug"; P(B) = 1/500 = 0.002
X: the event "the test fails"
P: probability; probabilities are dimensionless and apply to measurable events
|: read "given"
P(X | B): the chance the test fails on a buggy build, 1 (it catches every bug)
0.02: the chance it fails on a bug-free build (2%)
0.998: the chance a build is bug-free, 1 − 0.002
≈: approximately equal to
Conditioning: every event to the right of a given bar in this card has positive probability
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

## Key takeaways
- Precision depends on prevalence as well as conditional detection rates.
- Re-estimate rates when selecting a different population.

## Further reading
- [Introduction to Probability — Grinstead and Snell](https://math.dartmouth.edu/~prob/prob/prob.pdf)
