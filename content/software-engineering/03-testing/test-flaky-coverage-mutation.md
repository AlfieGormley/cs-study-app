---
id: test-flaky-coverage-mutation
title: Flaky tests, coverage, mutation testing
level: advanced
minutes: 15
summary: Why tests flake and how to find and fix them, what line and branch coverage do and don't tell you, and how mutation testing measures whether your tests would actually catch a bug.
---

A test suite is only useful if people trust it. Two things destroy that trust. **Flaky tests** have inconsistent outcomes on unchanged code; they may reveal real intermittent defects as well as test or environment problems. **Weak tests** pass when something is wrong, so green means little. This lesson covers how to find and fix both, and how to measure suite quality without fooling yourself.

## Flaky tests

A **flaky test** passes and fails on the same code. Google's testing blog reported in 2016 that about 1.5% of all its test runs produced a flaky result, that almost 16% of its tests showed some flakiness, and that about 84% of the pass-to-fail transitions its CI observed involved a flaky test. Those figures describe that 2016 Google dataset. A transition involving a flaky test does not itself establish that no new product bug exists.

The damage compounds. If each of 200 tests independently flakes 0.5% of the time, the chance a full run is clean is `0.995^200`, about 37%. Most builds go red for no reason, so people hit "re-run" by reflex and real failures slip through with the noise.

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
    cart.append(item)
    return len(cart)

def test_add_returns_count():
    assert add("apple") == 1

def test_add_two():
    add("pear")
    assert add("plum") == 2
```

Run the file and `test_add_two` fails (`add("plum")` returns 3, because "apple" is still in the cart). Run `pytest test_order.py::test_add_two` alone and it passes. Reverse the order and the *other* test fails. Order-dependent tests often look stable for months, then break when someone adds a test, renames a file or turns on parallel execution.

Tools that expose them:

- **pytest-randomly** shuffles test order on every run (and reseeds `random`), so hidden dependencies surface quickly. It prints the seed, so a failing order can be replayed.
- **pytest-xdist** (`pytest -n 4`) runs tests in parallel processes, which exposes shared files, ports and database rows.

### Time, concretely

```python
def is_expired(token, now=None):
    now = now or datetime.now()
    return now >= token["expires_at"]
```

A test that creates a token "expiring in 1 second" and checks it is not expired is flaky on a slow CI machine. Passing the clock in makes it exact:

```python
def test_expiry_boundary():
    exp = datetime(2026, 1, 1, 12, 0)
    t = {"expires_at": exp}
    before = datetime(2026, 1, 1,
                      11, 59, 59)
    assert not is_expired(t, now=before)
    assert is_expired(t, now=exp)
```

Libraries such as `freezegun` or `time-machine` can freeze the clock for code you can't change, but injecting the clock is clearer. Also watch for time-zone assumptions (a test written in London fails in a CI region on UTC-8) and for tests that only fail on 29 February or across a daylight-saving change.

### What to do with a flaky test

1. **Reproduce**: run it many times in a loop, with random ordering and in parallel, until it fails. Record the seed.
2. **Find the root cause**, using the table above. Often the bug is in the code (a real race), not the test.
3. **Fix**: inject clocks and randomness, give each test its own data, wait on conditions instead of time, use ephemeral ports (port 0).
4. **If you can't fix it today, quarantine it**: move it out of the blocking suite, with an owner and a deadline, and keep running it to collect data.

> [!warning] Automatic retries
> Retrying failed tests (e.g. `pytest-rerunfailures`) turns red builds green, but it also hides real intermittent bugs, such as a race condition that will hit users. If you retry, track every test that needed a retry and treat that list as a bug backlog, not as a pass.

## Code coverage

**Coverage** measures which parts of the code ran while the tests ran. In Python the standard tool is **coverage.py** (`pytest --cov` via pytest-cov).

### Line versus branch coverage

```python
def shipping_cost(total, express):
    cost = 5
    if total >= 50:
        cost = 0
    if express:
        cost += 10
    return cost

def test_free_express():
    assert shipping_cost(60, True) == 10
```

Every line runs, so **line (statement) coverage is 100%**. Yet we never tested an order under £50, or a non-express order.

**Branch coverage** tracks alternatives between measured source lines; for these two if statements, each has a true and false outcome. It does not necessarily distinguish every short-circuited boolean subexpression. Each `if` has two outcomes, true and false. Our test only took the true side of both. If only the seven-statement function is in shipping.py and a separately measured driver invokes it, coverage.py can report the following. Including the test function or driver in the measured file changes the statement total:

```
Stmts Miss Branch BrPart Cover Missing
    7    0      4      2   82% 3->5, 5->7
```

`3->5` means "line 3's `if` never jumped straight to line 5" (the condition was never false), and similarly for `5->7`. coverage.py computes the total as (statements run + branches taken) over (statements + branches): (7 + 2) / (7 + 4) = 9/11, about 82%.

Even full branch coverage doesn't cover every **path**. Two independent `if`s give four paths (under or over £50, times express or not). Two tests, `(60, True)` and `(10, False)`, take all four branches but only two of the four paths. Independent decisions can produce exponentially many paths, and loops can produce unbounded paths. Full path coverage is often infeasible, though finite small regions can be exhaustively exercised.

### What coverage tells you, and what it doesn't

Coverage is excellent at one thing: showing code **no test executes**. If the error-handling branch for a failed payment has 0% coverage, you know it is untested.

It cannot tell you that covered code is well tested. Coverage counts execution, not checking. A test that calls every function and asserts nothing has high coverage and catches almost nothing.

> [!note] Goodhart's law
> "When a measure becomes a target, it ceases to be a good measure." Mandate 90% coverage and you get tests written to raise the number: assertion-free calls, tests of trivial getters, tests coupled to implementation. Google's published guidance offers 60% as "acceptable", 75% "commendable" and 90% "exemplary", but explicitly avoids top-down mandates.

Practical uses that work well:

- Look at **uncovered lines in the diff** during code review, and ask whether they matter.
- Watch for **coverage dropping** on a change, which often means new code arrived without tests.
- Use branch coverage, not just line coverage.

## Mutation testing

Coverage asks "did the tests run this code?" **Mutation testing** asks the question you actually care about: "if this code were wrong, would a test fail?"

The tool makes many small changes to your code, called **mutants**, one at a time, and runs the tests against each:

- `>=` becomes `>`, `<`, `<=` or `==`
- `+` becomes `-`, `and` becomes `or`
- a constant `18` becomes `19` or `17`
- `return x` becomes `return None`; a condition becomes `True`

If some test fails, the mutant is **killed**: your tests noticed the change. If all tests pass, the mutant **survived**: the suite did not detect that change; it may be a meaningful missed fault, an equivalent change or outside the required behaviour. The **mutation score** is killed mutants divided by total (non-equivalent) mutants.

### A surviving mutant

```python
def can_rent(age):
    return age >= 18

def test_adult():
    assert can_rent(30)

def test_child():
    assert not can_rent(10)
```

Coverage is 100%. Now mutate:

| Mutant | 30 | 10 | Result |
|---|---|---|---|
| `age > 18` | T | F | survives |
| `age >= 19` | T | F | survives |
| `age >= 17` | T | F | survives |
| `age < 18` | F | T | killed |
| `True` | T | T | killed |

Three mutants survive, all at the boundary. The tests cannot tell 18 from 17 or 19. One more test kills all three:

```python
def test_boundary():
    assert can_rent(18)
    assert not can_rent(17)
```

`age > 18` fails on 18, `age >= 19` fails on 18, `age >= 17` fails on 17. This is the boundary-testing advice from lesson 1, discovered mechanically.

### Equivalent mutants and cost

Some mutants don't change behaviour at all, so no test can kill them. These are **equivalent mutants**:

```python
def larger(a, b):
    if a > b:     # mutant: a >= b
        return a
    return b
```

For ordinary integer inputs under a value-only maximum contract, equal inputs give equal output values. The mutant is equivalent under that contract, but not universally in Python: callers can observe object identity, and equal-valued floats such as -0.0 and 0.0 have distinguishable signs. Deciding equivalence is undecidable in general, so a human has to judge surviving mutants, which takes time.

Mutation testing is also expensive: each mutant means re-running (part of) the suite, and a large codebase has hundreds of thousands of potential mutants. Tools reduce the cost by running only the tests that cover each mutated line, and by mutating only changed code.

Google's approach, described in *State of Mutation Testing at Google* (2018), mutates only lines changed in a code review, skips "arid" lines unlikely to matter (such as logging), and shows a few surviving mutants to the author and reviewer as review comments. That turns an expensive batch metric into targeted, actionable feedback.

Tools: **mutmut** and **cosmic-ray** for Python, **PIT** (Pitest) for the JVM, **Stryker** for JavaScript, C# and Scala.

## Putting it together

```
 coverage   -> what never runs?
 mutation   -> what runs but is
               never really checked?
 flake rate -> can we trust red?
```

A healthy team watches all three, uses them to find weak spots, and never turns any of them into a target to game.

## Key takeaways
- Flaky tests destroy trust; small per-test flake rates compound into mostly red builds across a large suite.
- Common causes are timing, order dependence, time, randomness, shared resources and real races; randomise order and run in parallel to expose them.
- Fix root causes (inject clocks, isolate data, wait on conditions); quarantine with an owner rather than retrying blindly.
- Line coverage shows what ran; branch coverage also checks both sides of each decision; neither shows that results were checked.
- Mutation testing measures whether tests detect injected faults; surviving mutants need triage: they may expose missing boundary tests, equivalent changes or behaviour outside the contract.

## Further reading
- [Flaky Tests at Google and How We Mitigate Them — Google Testing Blog](https://testing.googleblog.com/2016/05/flaky-tests-at-google-and-how-we.html)
- [Eradicating Non-Determinism in Tests — Martin Fowler](https://martinfowler.com/articles/nonDeterminism.html)
- [Flaky tests — pytest docs](https://docs.pytest.org/en/stable/explanation/flaky.html)
- [Branch coverage measurement — coverage.py](https://coverage.readthedocs.io/en/latest/branch.html)
- [Code Coverage Best Practices — Google Testing Blog](https://testing.googleblog.com/2020/08/code-coverage-best-practices.html)
- [Test Coverage — Martin Fowler](https://martinfowler.com/bliki/TestCoverage.html)
- [Mutation testing — Wikipedia](https://en.wikipedia.org/wiki/Mutation_testing)
- [State of Mutation Testing at Google — Google Research](https://research.google/pubs/state-of-mutation-testing-at-google/)
- [mutmut documentation](https://mutmut.readthedocs.io/)
