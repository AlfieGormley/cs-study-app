---
id: test-tdd-property
title: TDD and property-based testing
level: intermediate
minutes: 15
summary: The red-green-refactor cycle worked through step by step, what TDD is and isn't good for, and how property-based testing with Hypothesis generates and shrinks inputs to find bugs you would never have thought to test.
---

So far we have written tests after (or alongside) the code, and chosen the inputs ourselves. This lesson covers two ideas that change both of those habits. **Test-driven development** writes the test *first*. **Property-based testing** lets the computer choose the inputs.

## Test-driven development

TDD, as described by Kent Beck in *Test-Driven Development: By Example* (2002), is a short loop repeated many times an hour:

```
   +--------+    +---------+
   |  RED   |--->|  GREEN  |
   | failing|    | simplest|
   |  test  |    |  code   |
   +--------+    +---------+
        ^             |
        |  +--------+ |
        +--|REFACTOR|<+
           | tidy up|
           +--------+
```

1. **Red**: write one small test for behaviour that does not exist yet. Run it and watch it fail.
2. **Green**: write the simplest code that makes it pass. Simplicity beats elegance here.
3. **Refactor**: with all tests green, clean up code and tests. The tests provide feedback about the behaviours they actually check.

Watching the test fail first is not ceremony. It shows that the test can fail. Inspect the failure reason to confirm it concerns the intended missing behaviour, rather than an unrelated setup or import error.

## A worked TDD session

Goal: `parse_duration("1h30m")` returns seconds.

### Cycle 1

Red:

```python
def test_hours():
    assert parse_duration("1h") == 3600
```

It fails: `parse_duration` does not exist. Green, with the simplest thing that works:

```python
def parse_duration(text):
    return 3600
```

This looks silly, and it is meant to. Beck calls it **fake it till you make it**. The test passes, and the next test forces the real logic.

### Cycle 2

Red:

```python
def test_minutes():
    assert parse_duration("90m") == 5400
```

Fails: 3600 is not 5400. Green:

```python
def parse_duration(text):
    n, unit = int(text[:-1]), text[-1]
    return n * {"h": 3600, "m": 60}[unit]
```

Both tests pass. This step is **triangulation**: a second example forces you to generalise.

### Cycle 3

Red:

```python
def test_combined():
    assert parse_duration("1h30m") == 5400
```

Fails with `ValueError`: `int("1h30")` is not a number. The single-token design no longer fits, so green needs a real parser: scan for number-unit pairs and add them up.

### Cycle 4: the unhappy paths

```python
@pytest.mark.parametrize("bad",
    ["", "h", "1x", "1h junk"])
def test_rejects_garbage(bad):
    with pytest.raises(ValueError):
        parse_duration(bad)
```

Against the cycle-2 code, `"1x"` fails with `KeyError: 'x'`, not `ValueError`, which is exactly the kind of sloppy error handling TDD drags into the open. The final version:

```python
import re

UNITS = {"h": 3600, "m": 60, "s": 1}
TOKEN = re.compile(r"(\d+)([hms])")

def parse_duration(text):
    pos, total = 0, 0
    for m in TOKEN.finditer(text):
        if m.start() != pos:
            raise ValueError(text)
        total += int(m[1]) * UNITS[m[2]]
        pos = m.end()
    if pos != len(text) or not text:
        raise ValueError(text)
    return total
```

All seven tests pass. The `pos` checks reject anything between or after tokens. Refactor step: rename, extract the units table, tidy tests, all under the safety net of a green suite.

## What TDD is good for, and what it isn't

Benefits people report:

- **Test-first feedback** connects new behaviour to a failing example; it does not guarantee every line or branch is covered or every assertion is adequate.
- **Design pressure.** Writing the call before the implementation makes you design the interface from the caller's side. Hard-to-test code shows up immediately.
- **Small steps.** You are never more than a few minutes from green, so debugging is cheap: if it broke, it was the last thing you typed.
- **Regression checks develop alongside implementation**, with writing and maintenance costs.

Limits and criticisms:

- It fits well-understood logic (parsers, pricing rules, state machines). It fits less well for exploratory work, UI layout or spikes where you do not yet know what you want. Many practitioners write a throwaway spike, then TDD the real version.
- It does not by itself produce good design or good tests. Tests written in tiny steps can still couple to implementation.
- Research on its productivity and quality effects is mixed; claims either way should be held loosely.

> [!tip] Outside-in TDD
> A popular variant starts with a failing acceptance test for a whole feature, then uses unit-level TDD to build the pieces until the outer test goes green. This is the "London school" style from lesson 3, and it often uses mocks for collaborators not yet written.

## Property-based testing

Example-based tests check specific inputs you chose. Their blind spot is the inputs you didn't think of. **Property-based testing** flips this: you state a rule that must hold for *all* inputs, and a library generates hundreds of inputs trying to break it.

The idea comes from Haskell's **QuickCheck** (Claessen and Hughes, 2000). In Python, **Hypothesis** is a third-party library; install it separately.

### A bug examples miss

Here is a merge of two sorted lists with a subtle bug:

```python
def merge(a, b):
    out, i, j = [], 0, 0
    while i < len(a) and j < len(b):
        if a[i] < b[j]:
            out.append(a[i])
            i += 1
        elif a[i] > b[j]:
            out.append(b[j])
            j += 1
        else:   # equal: bug!
            out.append(a[i])
            i += 1
            j += 1
    return out + a[i:] + b[j:]
```

The obvious example tests pass:

```python
def test_examples():
    assert merge([1, 3], [2, 4]) == \
        [1, 2, 3, 4]
    assert merge([], [5]) == [5]
```

Now state a property: merging two sorted lists must give the same as sorting their concatenation.

```python
from hypothesis import given
from hypothesis import strategies as st

ints = st.lists(st.integers())

@given(ints, ints)
def test_merge_matches_sorted(a, b):
    a, b = sorted(a), sorted(b)
    assert merge(a, b) == sorted(a + b)
```

A Hypothesis run can expose the error and shrink it to a simple counterexample such as the following; discovery time and the exact report are not guaranteed:

```
a=[0], b=[0]
assert [0] == [0, 0]
```

When both lists contain the same value, one copy is dropped.

### Shrinking

Hypothesis probably first failed on something messy, like `a=[-91, 3, 3, 17]`, `b=[3, 40]`. It then **shrinks**: it repeatedly tries simpler inputs (shorter lists, smaller numbers) and keeps any that still fail. The report is close to minimal, which makes the bug obvious. Shrinking is a big part of why property testing is practical; a random 300-element failing list would be nearly useless.

With an example database enabled, Hypothesis saves useful failing inputs and reuses them on later runs. The default local profile uses a `.hypothesis/` database; current CI-profile settings can disable the database and use deterministic generation. Explicit `@example` cases are more durable regression checks.

### Strategies

A **strategy** describes how to generate values:

- `st.integers(min_value=0)`, `st.floats(allow_nan=False)`, `st.text()`, `st.booleans()`
- `st.lists(st.integers(), max_size=50)`, `st.dictionaries(...)`, `st.tuples(...)`
- `st.sampled_from(["GBP", "EUR"])`, `st.builds(User, age=st.integers(0, 120))`
- `.map(...)` and `.filter(...)` to transform; `assume(cond)` inside a test to discard unsuitable inputs.

### Finding good properties

"What property?" is the hard part. Common patterns:

| Pattern | Example |
|---|---|
| Round trip | `decode(encode(x)) == x` |
| Oracle | fast impl == slow simple impl |
| Invariant | sort keeps length and items |
| Idempotence | `f(f(x)) == f(x)` |
| Metamorphic | add a filter: results shrink |

The **oracle** pattern used for `merge` is particularly strong: a simple, obviously correct implementation (here `sorted`) checks a fast, clever one.

## Limits of property-based testing

Generation is strategy-guided, not uniform random sampling, and can be deterministic under the CI profile or explicit settings. The default `max_examples=100` limits satisfying generated cases in a successful search, not necessarily all calls including rejected inputs and shrinking. Some bugs need rare inputs.

A run-length encoder that writes `"aaab"` as `"3a1b"`, with a decoder that reads one digit then one character, breaks on any run of 10 or more (`"10a"` is read as `"1"` and `"0"`). The round-trip property is useful, but a generic text strategy is not a guarantee of reaching long repeated runs. Generate such runs deliberately and pin the known counterexample. No measured discovery rate is asserted here.

Remedies:

- Design strategies that reach the interesting region (small alphabets, boundary values, long runs).
- Pin known-tricky cases with `@example("a" * 10)`, which always runs alongside generated inputs.
- Raise `max_examples` for important properties, perhaps in a nightly run.

Property tests also run slower than single examples and need more thought to write. They complement example tests rather than replace them: examples document specific expectations clearly, properties hunt for what you forgot.

> [!example] Stateful testing
> Hypothesis can also generate *sequences of operations* (add, remove, query) against a system and a simple model of it, checking they agree after every step. This is how bugs in caches, databases and data structures that only appear after a particular series of calls get found.

## Key takeaways
- TDD is red, green, refactor in tiny steps; watching each test fail first proves it can fail.
- "Fake it" and triangulation let the tests drive the generality of the code.
- TDD works best for well-understood logic; spike first when exploring.
- Property-based testing states rules for all inputs; Hypothesis generates inputs and shrinks failures towards simpler examples, without guaranteeing a globally minimal counterexample.
- Good properties: round trip, oracle, invariant, idempotence, metamorphic. Steer generators to the interesting inputs and pin known cases with `@example`.

## Further reading
- [Test Driven Development — Martin Fowler](https://martinfowler.com/bliki/TestDrivenDevelopment.html)
- [Test-driven development — Wikipedia](https://en.wikipedia.org/wiki/Test-driven_development)
- [Hypothesis documentation](https://hypothesis.readthedocs.io/en/latest/)
- [What is property-based testing? — Hypothesis](https://hypothesis.works/articles/what-is-property-based-testing/)
- [Self Testing Code — Martin Fowler](https://martinfowler.com/bliki/SelfTestingCode.html)
