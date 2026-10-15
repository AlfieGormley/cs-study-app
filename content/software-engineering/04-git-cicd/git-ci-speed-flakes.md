---
id: git-ci-speed-flakes
title: Fast suites and test layers
level: intermediate
minutes: 4
sourceLesson: git-ci-pipelines
summary: Test sharding reduces elapsed time while repeating setup on every runner.
---

A CI pipeline is useful when developers receive feedback soon enough to act on it. This unit studies test time, compute cost, test layers and intermittent failures.

## Speed is a feature

Extreme Programming's **ten-minute build** is still a good target: fast enough that developers wait for the result rather than context-switching. As pipelines slow down, people stop running them locally, batch changes and ignore results.

Techniques, roughly in order of effort:

1. **Cache dependencies** and build outputs. Key caches on lockfile hashes so they invalidate correctly.
2. **Parallelise the test suite.** Split a test suite into test shards that run on separate machines.
3. **Run only what changed.** Monorepo build tools (Bazel, Nx, Pants, Turborepo) compute which targets are affected by a change and skip the rest.
4. **Push slow tests later.** Run end-to-end suites after merge or on a schedule, not on every push, as long as failures are acted on.

How much does test sharding help? Splitting a suite into test shards divides the test time but not the setup each CI runner must do first, and you pay for every runner for the whole wait:

```formula
t_wall = N × t_test / S + t_setup
t_wall = 2400 × 0.5 s / 8 + 60 s
t_wall = 150 s + 60 s = 210 s = 3.5 min
C = S × t_wall
C = 8 × 210 s = 1680 s = 28 min
where
t_wall: the wall-clock time of the test stage, the time a developer actually waits, in seconds (s)
N: the number of tests in the suite
t_test: the average time one test takes, in seconds (s)
S: the number of test shards: CI runners the suite is split evenly across, all starting together
t_setup: the time each runner spends getting ready (checkout, installing dependencies) before testing, in seconds (s)
C: the total compute you pay for, in runner-minutes: every runner is busy for the whole of t_wall
s: seconds
min: minutes; 1 min = 60 s
In words: more test shards shrink elapsed test-stage duration towards the fixed CI setup duration, while the compute bill grows because every runner pays the setup.
```

> [!example] test sharding arithmetic
> A suite of 2,400 tests averaging 0.5 s each takes 1,200 s, or 20 minutes, on one runner; with 60 s of setup that is 1,260 s, or 21 runner-minutes. Split across 8 test shards the wait drops to about 3.5 minutes, at the price of 28 runner-minutes instead of 21. You trade compute for feedback time, usually a good deal. The sum assumes even test shards: one slow test file can make one test shard much longer than the rest, so balance test shards by measured duration.

## The test pyramid

Not all tests cost the same:

```
          /\        end-to-end
         /  \       few, slow, brittle
        /----\
       /      \     integration
      /        \    some
     /----------\
    /            \  unit
   /              \ many, fast, precise
  ------------------
```

Lots of fast unit tests, fewer integration tests, and a thin layer of end-to-end tests. A suite shaped like an ice-cream cone (mostly end-to-end) is slow and flaky, and when it fails it tells you little about *where* the problem is.

## Key takeaways

- Test sharding reduces elapsed test time while repeating setup on every runner.
- Balance test shards by measured duration and use caches keyed to declared inputs.
- Keep many focused unit tests, some integration tests and a small end-to-end layer.

## Further reading

- [The Practical Test Pyramid — Ham Vocke](https://martinfowler.com/articles/practical-test-pyramid.html)
- [Flaky Tests at Google and How We Mitigate Them](https://testing.googleblog.com/2016/05/flaky-tests-at-google-and-how-we.html)
