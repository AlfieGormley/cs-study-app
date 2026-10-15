---
id: test-pytest-cases
sourceLesson: test-unit-testing
title: Check exceptions, floats and parameter combinations
level: basic
minutes: 4
summary: Match the error message when an exception type alone could pass for the wrong reason.
---

Assume `import pytest` for the examples in this unit. Beyond a plain assertion, useful tests need to distinguish the right failure, compare approximate values and run several input cases independently.

### Expected exceptions: `pytest.raises`

```python
def parse_age(s):
    # Conversion can fail before our rule.
    n = int(s)
    if n < 0:
        raise ValueError(
            f"age must be >= 0, got {n}")
    return n

def test_negative_age():
    with pytest.raises(ValueError,
                       match="must be"):
        parse_age("-3")
```

The test passes only if the block raises `ValueError` or a subclass and the message matches the regular expression in `match` (searched with `re.search`). If nothing is raised, pytest fails with `DID NOT RAISE`.

`match` matters more than it looks. `parse_age("abc")` also raises `ValueError`, from `int()`, with the message "invalid literal for int()...". Without `match`, a test meant to check the negative-age rule would pass for the wrong reason.

### Floating point: `pytest.approx`

```python
def test_float_naive():
    assert 0.1 + 0.2 == 0.3       # FAILS

def test_float_approx():
    # Compare within the chosen tolerance.
    assert 0.1 + 0.2 == pytest.approx(0.3)
```

`0.1 + 0.2` is `0.30000000000000004` in binary floating point. `approx` compares within a tolerance (by default a relative tolerance of one part in a million, with a tiny absolute floor). With the default settings, pytest treats the two numbers as equal when their gap is no bigger than the larger of two allowances:

```formula
|x − x_exp| ≤ max(r × |x_exp|, t_abs)
r × |x_exp| = 10^{−6} × 0.3 = 3 × 10^{−7}
|x − x_exp| ≈ 5.6 × 10^{−17}
where
x: the value the code actually produced, here 0.1 + 0.2 = 0.30000000000000004
x_exp: the expected test result passed to approx, here 0.3
|…|: absolute value: the size of a number with its sign dropped, so |−2| = 2
r: the relative tolerance, the `rel` argument; default 10^{−6}, one part in a million
t_abs: the absolute tolerance, the `abs` argument; default 10^{−12}, which matters only when the expected test result is very close to 0
max: the larger of the two values in the brackets
10^{−6}: ten to the power minus six, 0.000001
≤: less than or equal to
≈: approximately equal to (rounded)
In words: the actual value may differ from the expected one by up to one millionth of the expected test result; here the gap is about 5.6 × 10^−17, far below the 3 × 10^−7 allowed, so the test passes.
```

The absolute floor exists because a relative tolerance shrinks to nothing as the expected test result approaches 0: `approx(0.0)` would otherwise demand an exact match. If you pass only `abs=`, the relative tolerance is not used. For money, prefer `decimal.Decimal` or integer pennies in the code itself.

## Many cases, one test: `parametrize`

```python
@pytest.mark.parametrize("title, slug", [
    ("Hello World", "hello-world"),
    ("  Spaces  ", "spaces"),
    ("ALL CAPS", "all-caps"),
])
def test_slugify(title, slug):
    # Each input pair is a separate test.
    assert slugify(title) == slug
```

pytest generates three separate tests, each reported on its own, so one failing case does not hide the others. Stacking two `parametrize` decorators produces the **cross product of test parameters**: every value of one list paired with every value of the other.

```formula
N_tests = n_1 × n_2
N_tests = 3 × 2 = 6
where
N_tests: the number of separate tests pytest generates from one test function
n_1: the number of values in the first parametrize list, here 3
n_2: the number of values in the second parametrize list, here 2
In words: stacked parametrize decorators run every combination, so their list lengths multiply: 3 values × 2 values gives 6 tests.
```

The counts multiply with each extra decorator, so three stacked lists of 10 values each give 10 × 10 × 10 = 1,000 tests. That is thorough but can make a suite slow; keep stacked lists short.

## Key takeaways
- Match the error message when an exception type alone could pass for the wrong reason.
- Use a deliberate float tolerance, and understand the default relative and absolute allowances.
- Stacked parametrisation generates a separately collected test for every combination.

## Further reading
- [How to parametrize tests — pytest docs](https://docs.pytest.org/en/stable/how-to/parametrize.html)
- [How to write and report assertions — pytest docs](https://docs.pytest.org/en/stable/how-to/assert.html)
