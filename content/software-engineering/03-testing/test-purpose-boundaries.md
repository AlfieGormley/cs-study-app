---
id: test-purpose-boundaries
sourceLesson: test-why-pyramid
title: Why tests help, and what they miss
level: basic
minutes: 4
summary: A test suite protects the behaviours its cases and assertions actually check.
---

Every change you make to a program risks breaking something that used to work. You can check by hand: start the app, click around, try a few inputs. That works for a weekend project. It does not work for a codebase with 200,000 lines, ten engineers and a deploy every day, because nobody can re-check everything by hand every time.

An **automated test** is a small program that runs your code and checks the result. Small tests can run quickly and repeatedly, but execution resources, upkeep and diagnosis all have costs. A collection of them, a **test suite**, is how a team keeps the ability to change code quickly without breaking it.

## What tests actually buy you

It is tempting to think tests exist to "find bugs". They do, but that is not their main value.

- **Confidence to change code.** A fast, useful suite can give prompt feedback about whether its checked behaviour changed during a refactor. Without one, people stop touching old code, and it rots. Many practitioners rank this as the biggest benefit.
- **Regression protection.** A regression test can catch the same failure again, provided it still exercises the relevant path and runs with useful assertions. Without the test, someone reintroduces it six months later.
- **Executable documentation.** A test named `test_full_discount_is_free` tells a newcomer exactly what the code promises, and it can expose a mismatch between the tested expectation and implementation. A stale or incorrect expectation can still pass if the code agrees with it.
- **Design feedback.** Code that is painful to test (needs a database, a clock and three globals just to call one function) is usually painfully coupled. Tests surface that early.
- **Cheaper defects.** Catching a bug on your laptop can avoid a production incident, a rollback or harm to data and customers. The cost depends on the defect.

Google's *Software Engineering at Google* describes its web search server team before automated testing: at one point more than 80% of production pushes contained user-affecting bugs that had to be rolled back. Within a year of requiring tests with every change, emergency pushes had halved despite increased changes.

## Anatomy of a test

Here is a function and three tests, written with **pytest**, a widely used third-party Python test runner.

```python
# pricing.py
def apply_discount(price, percent):
    # Keep both valid endpoints included.
    if not 0 <= percent <= 100:
        raise ValueError("bad percent")
    # Convert percent off to fraction kept.
    factor = 1 - percent / 100
    # Return a price rounded to two places.
    return round(price * factor, 2)
```

```python
# test_pricing.py
import pytest
from pricing import apply_discount

def test_ten_percent_off():
    # A tenth off leaves 45 from 50.
    assert apply_discount(50.0, 10) == 45.0

def test_full_discount_is_free():
    assert apply_discount(50.0, 100) == 0.0

def test_rejects_negative_percent():
    # Success means the expected error
    # arose.
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

Edsger Dijkstra put it plainly in *Notes on Structured Programming*: testing can show the presence of bugs, but never their absence. An example suite checks the cases it executes; untested inputs and environments can still fail.

Suppose someone "tidies" the range check to `0 < percent <= 100`. All three tests above still pass. Yet `apply_discount(50.0, 0)` now raises `ValueError`, which will break every order without a discount. The suite missed it because no test sat on the boundary at 0. **Boundary testing** means checking the values at each limit and one step beyond it.

> [!tip] Test the edges
> Boundary cases are valuable targets: zero, one, empty, the maximum, off-by-one either side of a limit. When a function has a range check, test both ends of the range and one step outside each.

So a green suite means "nothing we check is broken", not "nothing is broken".

> [!analogy] Real-world analogy: a vehicle inspection checklist
> A garage inspects a car against a fixed checklist: lights, brakes, tyres. A pass tells you every listed item was fine on the day. It says nothing about the rattle nobody listed.
>
> **How it maps:** The checklist is the test suite, each item is a test case with its assertion, and the pass certificate is a green build. An unlisted fault is an untested input, like the 0 % discount above.
>
> **Where it stops:** A test suite is cheap to re-run on every change, and you can add an item the moment a fault is found (a regression test). An inspection is occasional, and a car can wear out between inspections, whereas code does not wear out: its behaviour changes only when the code, its inputs or its environment change.

The rest of this module is about making "what we check" as close to "what matters" as possible, at a sensible cost.

> [!note] The regression test habit
> When you fix a bug, first write a test that reproduces it and watch it fail. Then fix the code and watch it pass. You have evidence for the exercised case and a check that can detect that regression if it recurs on the covered path.

## Key takeaways
- A test suite protects the behaviours its cases and assertions actually check.
- Write a regression test before fixing a reported bug; check both sides of range boundaries.

## Further reading
- [Testing Overview — Software Engineering at Google, ch. 11](https://abseil.io/resources/swe-book/html/ch11.html)
- [pytest: Get started](https://docs.pytest.org/en/stable/getting-started.html)
- [Notes on Structured Programming — Edsger Dijkstra](https://www.cs.utexas.edu/~EWD/ewd02xx/EWD249.PDF)
