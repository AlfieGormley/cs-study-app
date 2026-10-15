---
id: git-ci-flaky-tests
title: Flaky tests and compounded failure risk
level: intermediate
minutes: 3
sourceLesson: git-ci-pipelines
summary: A flaky test can pass and fail on unchanged code, sometimes revealing a real race.
---

A fast suite still needs trustworthy feedback. This unit distinguishes intermittent test outcomes from reliable evidence, then calculates how many small flake risks combine.

## Flaky tests

A **flaky** test passes and fails on the same code. Google reported in 2016 that about **1.5% of all test runs** gave a flaky result, that almost **16% of tests** had some flakiness, and that about **84% of pass-to-fail transitions** they observed involved a flaky test.

That last number is the real damage: many transitions involved tests known to be flaky. This does not establish that most red builds were misleading alerts: intermittent failures can expose real races or other defects. Typical causes are timing (`sleep(1)` and hope), test order dependence, shared state, real network calls and unseeded randomness.

Why does a small flake rate per test hurt so much? A run goes red if *any* test flakes, so with many tests the chances compound. If each test flakes independently:

```formula
P_red = 1 − (1 − p)^N
P_red = 1 − (1 − 0.005)^200
P_red = 1 − 0.995^200 ≈ 1 − 0.37 = 0.63
where
P_red: the probability that a run on correct code goes red because at least one test flaked, from 0 (never) to 1 (always)
p: the probability that one test flakes in one run; here 0.5 % = 0.005
N: the number of tests in the run; here 200
^: raise to a power: (1 − p)^N multiplies together N copies of the pass chance of one test, which is the chance that all N pass
≈: approximately equal to
In words: one minus the chance that every test passes; with 200 tests that each flake once in 200 runs, nearly two runs in three go red on good code.
```

Even a 0.1 % flake rate per test leaves about 18 % of 200-test runs red. Real flakes are not perfectly independent, so treat this as a model of how the risk compounds, not a prediction.

What to do:

- **Test quarantine**: move a known-flaky test out of the blocking suite, file a ticket and fix it soon.
- **Track flakiness** per test; many CI systems can detect pass-after-retry.
- **Do not blindly retry.** Automatic retries hide real race conditions, which then ship to production.

## Key takeaways

- A flaky test can pass and fail on unchanged code, sometimes revealing a real race.
- Independent per-test flake risks compound across a suite; correlation changes the model.
- Quarantine with a repair owner rather than silently retrying failures away.

## Further reading

- [The Practical Test Pyramid — Ham Vocke](https://martinfowler.com/articles/practical-test-pyramid.html)
- [Flaky Tests at Google and How We Mitigate Them](https://testing.googleblog.com/2016/05/flaky-tests-at-google-and-how-we.html)
