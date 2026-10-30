---
id: test-pytest-cases
sourceLesson: test-unit-testing
title: Check exceptions, floats and parameter combinations
level: basic
minutes: 3
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

`0.1 + 0.2` is `0.30000000000000004` in binary floating point, so exact `==` fails. `approx` instead accepts any value within a tolerance of the expected one. With the default settings, the allowed gap is the larger of two allowances: one millionth of the value you expected (the relative tolerance, `rel`) or 10⁻¹² (the absolute tolerance, `abs`). Here the gap is about 5.6 × 10⁻¹⁷, far inside one millionth of 0.3, so the test passes.

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

pytest generates three separate tests, each reported on its own, so one failing case does not hide the others. Stacking two `parametrize` decorators produces the **cross product of test parameters**: every value of one list paired with every value of the other. A list of 3 values stacked on a list of 2 gives 6 tests, and each extra decorator multiplies the count again: three stacked lists of 10 values give 1,000 tests. That is thorough but can make a suite slow, so keep stacked lists short and combine only the parameters that genuinely interact.

## Key takeaways
- Match the error message when an exception type alone could pass for the wrong reason.
- Use a deliberate float tolerance, and understand the default relative and absolute allowances.
- Stacked parametrisation generates a separately collected test for every combination.

## Further reading
- [How to parametrize tests — pytest docs](https://docs.pytest.org/en/stable/how-to/parametrize.html)
- [How to write and report assertions — pytest docs](https://docs.pytest.org/en/stable/how-to/assert.html)
