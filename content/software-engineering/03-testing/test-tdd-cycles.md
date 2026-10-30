---
id: test-tdd-cycles
sourceLesson: test-tdd-property
title: Build a duration parser with red, green, refactor
level: intermediate
minutes: 5
summary: Watch each new test fail for the intended reason, then implement enough to pass.
---

Earlier tests chose inputs for existing code. Test-driven development reverses the order: write one failing expectation, then add the behaviour. This worked session builds a duration parser in small steps. Assume `import pytest` in test snippets.

## Test-driven development

TDD was developed by Kent Beck in the late 1990s as part of Extreme Programming and set out in his book *Test-Driven Development: By Example*. It is a short loop repeated many times an hour:

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
    # Last character selects seconds per
    # unit.
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

Fails with `ValueError`: `int("1h30")` is not valid integer text. The single-token design no longer fits, so green needs a real parser: scan for number-unit pairs and add them up.

### Cycle 4: the unhappy paths

```python
@pytest.mark.parametrize("bad",
    ["", "h", "1x", "1h junk"])
def test_rejects_garbage(bad):
    # Success means the expected error
    # arose.
    with pytest.raises(ValueError):
        parse_duration(bad)
```

Against the cycle-2 code, `"1x"` fails with `KeyError: 'x'`, not `ValueError`, which is exactly the kind of inconsistent failure behaviour TDD drags into the open. The final version:

```python
import re

UNITS = {"h": 3600, "m": 60, "s": 1}
TOKEN = re.compile(r"(\d+)([hms])")

def parse_duration(text):
    pos, total = 0, 0
    # Scan number-unit tokens left to right.
    for m in TOKEN.finditer(text):
        # Reject gaps before the next token.
        if m.start() != pos:
            raise ValueError(text)
        # Accumulate this token in seconds.
        total += int(m[1]) * UNITS[m[2]]
        pos = m.end()
    # Reject trailing garbage and empty
    # input.
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
- Research on productivity and quality has mixed findings across tasks and study designs. Case studies of four industrial teams (three at Microsoft, one at IBM) reported 40–90 % lower defect density before release, with managers estimating 15–35 % more initial development time. A six-month study of 30 student developers found no effect on external quality or productivity, although the TDD group wrote more tests. Neither establishes a universal effect.

> [!tip] Outside-in TDD
> A popular variant starts with a failing acceptance test for a whole feature, then uses unit-level TDD to build the pieces until the outer test goes green. This is the "London school" style from the earlier interaction-verification unit, and it often uses mocks for collaborators not yet written.

## Key takeaways
- Watch each new test fail for the intended reason, then implement enough to pass.
- Fake it and triangulation motivate generalisation without uniquely specifying an implementation.
- TDD provides design feedback and regression checks, with limits for exploratory work.

## Further reading
- [Test Driven Development — Martin Fowler](https://martinfowler.com/bliki/TestDrivenDevelopment.html)
- [Self Testing Code — Martin Fowler](https://martinfowler.com/bliki/SelfTestingCode.html)
- [Industrial TDD case studies — IBM Research](https://research.ibm.com/publications/realizing-quality-improvement-through-test-driven-development-results-and-experiences-of-four-industrial-teams)
- [Studying TDD and its retainment over a six-month time span — Baldassarre et al.](https://arxiv.org/abs/2105.03312)
- [Equality and triangulation — Kent Beck](https://www.informit.com/articles/article.aspx?p=30641)
