---
id: git-ci-flaky-tests
title: Flaky tests and compounded failure risk
level: intermediate
minutes: 3
sourceLesson: git-ci-pipelines
summary: A flaky test can pass and fail on unchanged code, sometimes revealing a real race.
---

A fast suite still needs trustworthy feedback. This unit distinguishes intermittent test outcomes from reliable evidence, then shows how many small flake risks combine.

## Flaky tests

A **flaky** test passes and fails on the same code. Google reported in 2016 that about **1.5% of all test runs** gave a flaky result, that almost **16% of tests** had some flakiness, and that about **84% of pass-to-fail transitions** they observed involved a flaky test.

That last number is the real damage: many transitions involved tests known to be flaky. This does not establish that most red builds were misleading alerts: intermittent failures can expose real races or other defects. Typical causes are timing (`sleep(1)` and hope), test order dependence, shared state, real network calls and unseeded randomness.

Why does a small flake rate per test hurt so much? A run goes red if *any* test flakes, so with many tests the chances compound. Suppose each of 200 tests independently flakes once in 200 runs (0.5 %). Each test usually passes, but all 200 pass together only about 37 % of the time, so nearly two runs in three go red on correct code. Even a 0.1 % flake rate per test leaves about 18 % of 200-test runs red.

```formula reference
P_red = 1 − (1 − p)^N
where
P_red: the probability that a run on correct code goes red because at least one test flaked, from 0 (never) to 1 (always)
p: the probability that one test flakes in one run, for example 0.005 for 0.5 %
N: the number of tests in the run
^: raise to a power: (1 − p)^N multiplies together N copies of the pass chance of one test, which is the chance that all N pass
In words: a run is red unless every test passes, so even rare per-test flakes make red runs common once there are hundreds of tests.
```

Real flakes are not perfectly independent, so treat this as a model of how the risk compounds, not a prediction. The practical consequence is trust: when most red runs are noise, people stop reading failures, and real ones slip through.

> [!analogy] Real-world analogy: a smoke alarm that goes off at random
> An office smoke alarm that sounds a few times a week for no visible reason soon gets ignored. People wave it away, and on the day there is real smoke nobody reacts quickly.
>
> **How it maps:** A flaky test is the unreliable alarm and a red build is the alarm sounding. When most red builds turn out to be flakes, engineers learn to re-run instead of investigate, so genuine failures are missed. Google's flaky-test write-up makes the same point about people ignoring alarms with a history of false signals.
>
> **Where it stops:** A false smoke alarm usually has a harmless cause, such as steam or an oversensitive detector. An intermittent test failure can instead be a real defect, such as a race condition that only shows up under some timings, so a flaky test deserves investigation rather than being written off as noise.

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
