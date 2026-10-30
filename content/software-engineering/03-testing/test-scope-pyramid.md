---
id: test-scope-pyramid
sourceLesson: test-why-pyramid
title: Choose test scope and balance the pyramid
level: basic
minutes: 4
summary: Choose the narrowest check that exercises the failure you fear.
---

A passing unit check is useful only for the boundary it exercises. This unit compares test scopes, then uses the pyramid to balance their cost and feedback. The earlier discount function has a rounding rule that can be checked without a browser.

## Kinds of test, by scope

Tests differ in how much of the system they exercise.

- **Unit tests** check one small piece (a function, a class) in isolation. Here we use fast in-process unit tests without network or disk access; exact timings vary and terminology differs between teams.
- **Integration tests** check that a piece works with something real next to it: your repository code against a real Postgres, your HTTP client against a real (local) server.
- **End-to-end (E2E) tests** drive the whole running system the way a user would: a browser clicks "Buy", and the test checks the order appears.

Broader tests often exercise more real components and can cost more time and effort to diagnose. These are tendencies, not guaranteed timings or failure rates. The table is illustrative:

| | Unit | Integration | E2E |
|---|---|---|---|
| Speed | ms | 100s of ms | seconds+ |
| Flakiness | Rare | Some | Common |
| Realism | Low | Medium | High |
| Failure points to | A line | A seam | "Something" |

That last row matters more than people expect. When a unit test fails, its name and traceback usually point at the bug. When an E2E checkout test fails, the cause could be the front end, the payments service, a slow database, an expired test card or the network. Someone has to go digging.

> [!analogy] Real-world analogy: bench tests and a test drive
> A mechanic can test a car's alternator on a bench, then take the whole car for a test drive. The bench test is quick and, if it fails, names the part. A failed test drive tells you only that something is wrong somewhere in the car.
>
> **How it maps:** Bench tests are unit tests (one part, in isolation); fitting the alternator and checking it charges the battery is an integration test (one part with a real neighbour); the test drive is an end-to-end test (the whole system used as a driver would). The drive is the only one that catches a loose connector between parts, which is why you still do a few.
>
> **Where it stops:** Software tests are automated and repeatable, so you can run thousands of "bench tests" on every change for almost nothing. An E2E test can also fail because of its test environment (a slow network, shared test data, another team's half-deployed service) when the product itself is fine, which is a much more common way for an automated test to go wrong than for a test drive.

## The test pyramid

Mike Cohn popularised the **test pyramid** in *Succeeding with Agile* (2009). The idea: write lots of fast, focused unit tests, fewer integration tests, and a small number of end-to-end tests at the top.

```
            /\
           /E2E\       few, slow,
          /------\     realistic
         /  Integ \
        /----------\
       /    Unit    \  many, fast,
      /--------------\ precise
```

The pyramid is a heuristic about cost, not a law. Google's testing blog suggested a 70/20/10 split (unit/integration/E2E) as a first guess in 2015, and *Software Engineering at Google* describes aiming for roughly 80/15/5 by test count. Treat these as rough starting points, not targets to hit.

These shares count tests, not time. In a 1,000-test suite, a 70/20/10 split means roughly 700 unit, 200 integration and 100 end-to-end tests, but one browser test can take as long as thousands of unit tests. So even a thin E2E layer can dominate how long the suite takes, which is why the top of the pyramid stays small.

Two principles behind the shape are more useful than any ratio:

1. **Push each check as low as it can go.** If the rounding rule in `apply_discount` can be tested with a unit test, do not test it through a browser.
2. **Use higher-level tests for what lower ones cannot see**: wiring, configuration, serialisation, real SQL, the happy path of the most important user journeys.

## Key takeaways
- Choose the narrowest check that exercises the failure you fear.
- Pyramid ratios count tests, not execution duration; a small browser layer can dominate total time.

## Further reading
- [The Practical Test Pyramid — martinfowler.com](https://martinfowler.com/articles/practical-test-pyramid.html)
- [Test Pyramid — Martin Fowler](https://martinfowler.com/bliki/TestPyramid.html)
- [Testing Overview — Software Engineering at Google, ch. 11](https://abseil.io/resources/swe-book/html/ch11.html)
- [Just Say No to More End-to-End Tests — Google Testing Blog](https://testing.googleblog.com/2015/04/just-say-no-to-more-end-to-end-tests.html)
