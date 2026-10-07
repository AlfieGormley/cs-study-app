---
id: test-why-pyramid
title: Why test, and the test pyramid
level: basic
minutes: 10
summary: What automated tests buy you, what they can never prove, and how to balance fast unit tests against slower, more realistic integration and end-to-end tests.
---

Every change you make to a program risks breaking something that used to work. You can check by hand: start the app, click around, try a few inputs. That works for a weekend project. It does not work for a codebase with 200,000 lines, ten engineers and a deploy every day, because nobody can re-check everything by hand every time.

An **automated test** is a small program that runs your code and checks the result. Small tests can run quickly and repeatedly, but execution resources, upkeep and diagnosis all have costs. A collection of them, a **test suite**, is how a team keeps the ability to change code quickly without breaking it.

## What tests actually buy you

It is tempting to think tests exist to "find bugs". They do, but that is not their main value.

- **Confidence to change code.** With a good suite, you can refactor a tangled module and know within a minute whether behaviour changed. Without one, people stop touching old code, and it rots. This is the biggest benefit.
- **Regression protection.** A regression test can catch the same failure again, provided it still exercises the relevant path and runs with useful assertions. Without the test, someone reintroduces it six months later.
- **Executable documentation.** A test named `test_full_discount_is_free` tells a newcomer exactly what the code promises, and it can expose a mismatch between the tested expectation and implementation. A stale or incorrect expectation can still pass if the code agrees with it.
- **Design feedback.** Code that is painful to test (needs a database, a clock and three globals just to call one function) is usually painfully coupled. Tests surface that early.
- **Cheaper defects.** A bug caught by a test on your laptop costs minutes. The same bug caught in production costs an incident, a rollback, perhaps lost data or customers.

Google's *Software Engineering at Google* describes its web search server team before automated testing: at one point more than 80% of production pushes contained user-affecting bugs that had to be rolled back. Requiring tests with every change turned that around within a year.

## Anatomy of a test

Here is a function and three tests, written with **pytest**, the de facto standard Python test runner.

```python
# pricing.py
def apply_discount(price, percent):
    if not 0 <= percent <= 100:
        raise ValueError("bad percent")
    factor = 1 - percent / 100
    return round(price * factor, 2)
```

```python
# test_pricing.py
import pytest
from pricing import apply_discount

def test_ten_percent_off():
    assert apply_discount(50.0, 10) == 45.0

def test_full_discount_is_free():
    assert apply_discount(50.0, 100) == 0.0

def test_rejects_negative_percent():
    with pytest.raises(ValueError):
        apply_discount(50.0, -5)
```

By default, pytest collects `test_*.py` and `*_test.py` files and eligible test-prefixed functions and methods; configuration can change discovery. It runs the collected tests and treats a plain `assert` as the check. For these three tests, illustrative `pytest -q` output is (elapsed time varies):

```
...                          [100%]
3 passed in 0.05s
```

Each test follows the same shape, often called **Arrange, Act, Assert**: set up inputs, call the code, check the outcome. Here the arrange step is just the literal arguments.

## What tests cannot do

Edsger Dijkstra put it plainly in 1970: testing can show the presence of bugs, but never their absence. A test checks the inputs you thought of and nothing else.

Suppose someone "tidies" the range check to `0 < percent <= 100`. All three tests above still pass. Yet `apply_discount(50.0, 0)` now raises `ValueError`, which will break every order without a discount. The suite missed it because nobody tested the **boundary** at 0.

> [!tip] Test the edges
> Boundary cases are valuable targets: zero, one, empty, the maximum, off-by-one either side of a limit. When a function has a range check, test both ends of the range and one step outside each.

So a green suite means "nothing we check is broken", not "nothing is broken". The rest of this module is about making "what we check" as close to "what matters" as possible, at a sensible cost.

## Kinds of test, by scope

Tests differ in how much of the system they exercise.

- **Unit tests** check one small piece (a function, a class) in isolation. They run in-process, touch no network or disk, and take microseconds to milliseconds.
- **Integration tests** check that a piece works with something real next to it: your repository code against a real Postgres, your HTTP client against a real (local) server.
- **End-to-end (E2E) tests** drive the whole deployed system the way a user would: a browser clicks "Buy", and the test checks the order appears.

Broader tests often exercise more real components and can cost more time and effort to diagnose. These are tendencies, not guaranteed timings or failure rates. The table is illustrative:

| | Unit | Integration | E2E |
|---|---|---|---|
| Speed | ms | 100s of ms | seconds+ |
| Flakiness | Rare | Some | Common |
| Realism | Low | Medium | High |
| Failure points to | A line | A seam | "Something" |

That last row matters more than people expect. When a unit test fails, its name and traceback usually point at the bug. When an E2E checkout test fails, the cause could be the front end, the payments service, a slow database, an expired test card or the network. Someone has to go digging.

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

Two principles behind the shape are more useful than any ratio:

1. **Push each check as low as it can go.** If the rounding rule in `apply_discount` can be tested with a unit test, do not test it through a browser.
2. **Use higher-level tests for what lower ones cannot see**: wiring, configuration, serialisation, real SQL, the happy path of the most important user journeys.

### The ice-cream cone anti-pattern

Many teams end up with the pyramid upside down: a handful of unit tests, some integration tests, and hundreds of slow browser tests or manual QA scripts on top. This is the **ice-cream cone**.

```
   ____________________
  \   manual / E2E     /  hours, flaky
   \------------------/
    \  integration   /
     \--------------/
      \    unit    /      barely any
       \__________/
```

Symptoms: the suite takes an hour, fails randomly, and engineers re-run it until it goes green. Nobody trusts a red build, so real failures slip through.

### Other shapes

The pyramid was drawn for monoliths with lots of business logic. Other shapes suit other systems:

- **Testing trophy** (Kent C. Dodds, for front ends): static analysis at the base and a big middle of integration tests that render components with their real children, because that is where UI bugs live.
- **Testing honeycomb** (Spotify, for microservices): mostly integration tests per service, since a typical microservice has little logic of its own and most of its risk is in talking to its database and neighbours.

The common thread is the same: pick the cheapest test that would catch the bug you are worried about.

## Test size versus test scope

Google separates two ideas that the word "unit" blurs.

- **Scope** is how much code is exercised (one function or the whole system).
- **Size** is what resources the test may use. Under the Google scheme described here, small tests use one thread in one process, without sleeping or external I/O; hermetic in-memory filesystem access is an exception. Medium tests may use multiple processes and localhost networking on one machine. Large tests may span machines.

The constraint on size is what makes tests fast and deterministic. A narrow-scope test that secretly calls a real API is "unit" in name only.

## What makes a suite good

- **Fast.** If the suite takes 30 seconds, people run it constantly. If it takes 30 minutes, they push and hope.
- **Deterministic.** The same code gives the same result every run. A test that sometimes fails is worse than no test, because it teaches people to ignore red.
- **Behaviour-focused.** Tests check what the code does through its public interface, not how it does it internally, so refactoring does not break them.
- **Clear when failing.** A failure message should tell you what was expected and what happened.
- **Part of the workflow.** Tests run on every change in CI, and a red build blocks merging.

> [!note] The regression test habit
> When you fix a bug, first write a test that reproduces it and watch it fail. Then fix the code and watch it pass. You have evidence for the exercised case and a check that can detect that regression if it recurs on the covered path.

## Key takeaways
- Tests' main value is confidence to change code, plus regression protection, documentation and design feedback.
- A passing suite proves only that the cases you check work; boundaries are where untested bugs hide.
- Unit tests are fast and precise, E2E tests realistic but slow and flaky; integration tests sit between.
- The pyramid says: many low-level tests, few high-level ones, and push each check as low as it will go.
- Avoid the ice-cream cone; adapt the shape (trophy, honeycomb) to where your system's risk actually lives.

## Further reading
- [The Practical Test Pyramid — martinfowler.com](https://martinfowler.com/articles/practical-test-pyramid.html)
- [Test Pyramid — Martin Fowler](https://martinfowler.com/bliki/TestPyramid.html)
- [Testing Overview — Software Engineering at Google, ch. 11](https://abseil.io/resources/swe-book/html/ch11.html)
- [Just Say No to More End-to-End Tests — Google Testing Blog](https://testing.googleblog.com/2015/04/just-say-no-to-more-end-to-end-tests.html)
- [The Testing Trophy — Kent C. Dodds](https://kentcdodds.com/blog/the-testing-trophy-and-testing-classifications)
- [Testing of Microservices — Spotify Engineering](https://engineering.atspotify.com/2018/01/testing-of-microservices)
- [pytest: Get started](https://docs.pytest.org/en/stable/getting-started.html)
