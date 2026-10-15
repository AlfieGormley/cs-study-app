---
id: test-flake-diagnosis
sourceLesson: test-flaky-coverage-mutation
title: Diagnose flaky suites and shared-state failures
level: advanced
minutes: 4
summary: A flaky outcome can arise from the test setup or a real intermittent product bug.
---

A test suite is only useful if people trust it. Two things destroy that trust. **Flaky tests** have inconsistent outcomes on unchanged code; they may reveal real intermittent defects as well as test or environment problems. **Weak tests** pass when something is wrong, so green means little. This unit diagnoses intermittent failures; the following units cover clock control, coverage and mutation testing.

## Flaky tests

A **flaky test** passes and fails on the same code. Google's testing blog reported in 2016 that about 1.5% of all its test runs produced a flaky result, that almost 16% of its tests showed some flakiness, and that about 84% of the pass-to-fail transitions its CI observed involved a flaky test. Those figures describe that 2016 Google dataset. A transition involving a flaky test does not itself establish that no new product bug exists.

The damage compounds. A full run is clean only if *every* test passes. When tests flake independently of each other, the chance of that is one copy of the per-test pass chance for each test, all multiplied together:

```formula
P_clean = (1 − p)^n
P_clean = (1 − 0.005)^200
P_clean = 0.995^200 ≈ 0.37
P_red = 1 − P_clean ≈ 0.63
where
P_clean: the probability that a full run has no spurious test failure, from 0 (never) to 1 (always)
p: the probability that one test fails spuriously on a run; here 0.5 % = 0.005
n: the number of tests in the suite, here 200
^: raise to a power: 0.995^200 means 200 copies of 0.995 multiplied together
P_red: the probability that at least one test fails spuriously, so the build goes red on correct code
≈: approximately equal to (rounded)
In words: if each of 200 tests flakes 0.5 % of the time, only about 37 % of runs are fully green, and about 63 % go red with nothing wrong.
```

Doubling the suite to 400 such tests drops the clean-run chance to 0.995 to the power 400, about 13 %. The formula assumes the flakes are independent. In practice many share a cause (a slow CI machine, a shared database), so they cluster, but the lesson holds: tiny per-test flake rates add up across a big suite. In the independent 200-test illustration, most runs contain a spurious test failure. Re-running by reflex can then hide real failures in the noise.

### Common causes

| Cause | Typical example |
|---|---|
| Async and timing | `sleep(1)` then assert |
| Order dependence | Shared module state |
| Time and dates | `now()`, midnight, DST |
| Randomness | Unseeded random data |
| Shared resources | Fixed port, shared DB row |
| Concurrency | Real race in the code |
| External services | Network, rate limits |

### Order dependence, concretely

```python
cart = []

def add(item):
    # Global state leaks into the next test.
    cart.append(item)
    return len(cart)

def test_add_returns_count():
    assert add("apple") == 1

def test_add_two():
    add("pear")
    # Fails after apple: the count is three.
    assert add("plum") == 2
```

Run the file and `test_add_two` fails (`add("plum")` returns 3, because "apple" is still in the cart). Run `pytest test_order.py::test_add_two` alone and it passes. Reverse the order and the *other* test fails. Order-dependent tests often look stable for months, then break when someone adds a test, renames a file or turns on parallel execution.

Tools that expose them:

- **pytest-randomly** shuffles test order on every run (and reseeds `random`), so hidden dependencies surface quickly. It prints the seed, so a failing order can be replayed.
- **pytest-xdist** (`pytest -n 4`) runs tests in parallel processes, which exposes shared files, ports and database rows.

## Key takeaways
- A flaky outcome can arise from the test setup or a real intermittent product bug.
- Independent small flake rates can make large suites mostly red.
- Shared state explains tests that pass alone but fail after another test.

## Further reading
- [Flaky Tests at Google — Google Testing Blog](https://testing.googleblog.com/2016/05/flaky-tests-at-google-and-how-we.html)
- [Flaky tests — pytest docs](https://docs.pytest.org/en/stable/explanation/flaky.html)
