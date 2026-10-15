---
id: test-properties-shrinking
sourceLesson: test-tdd-property
title: Find missing cases with properties and shrinking
level: intermediate
minutes: 3
summary: A property states an expected rule; generated cases try to falsify it.
---

Example tests check inputs you choose. Property-based testing lets a library generate inputs against a rule you expect to hold; it then simplifies failures so that you can understand them.

## Property-based testing

Example-based tests check specific inputs you chose. Their blind spot is the inputs you didn't think of. **Property-based testing** flips this: you state a rule that must hold for *all* inputs, and a library generates inputs trying to break it, within configured search limits.

The idea comes from Haskell's **QuickCheck** (Claessen and Hughes, 2000). In Python, the **Hypothesis library** provides it; it is third-party, so install it separately.

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
        # Bug: append once but consume
        # twice.
        else:   # equal: bug!
            out.append(a[i])
            i += 1
            j += 1
    # Preserve each unconsumed tail.
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
    # Give merge its sorted-input contract.
    a, b = sorted(a), sorted(b)
    # The oracle retains all duplicates.
    assert merge(a, b) == sorted(a + b)
```

A Hypothesis run can expose the error and shrink it to a simple counterexample such as the following; time needed to find a failure and the exact report are not guaranteed:

```
a=[0], b=[0]
assert [0] == [0, 0]
```

When both lists contain the same value, one copy is dropped.

### Shrinking

An illustrative first failure might use messy lists such as `a=[-91, 3, 3, 17]`, `b=[3, 40]`. It then **shrinks**: it repeatedly tries simpler inputs (shorter lists, smaller numbers) and keeps any that still fail. Shrinking seeks a simpler failure but does not guarantee a globally smallest input. Shrinking is a big part of why property testing is practical; a random 300-element failing list would be nearly useless.

With an example database enabled, Hypothesis saves useful failing inputs and reuses them on later runs. The default local profile uses a `.hypothesis/` database; current CI-profile settings can disable the database and use deterministic generation. Explicit `@example` cases are more durable regression checks.

## Key takeaways
- A property states an expected rule; generated cases try to falsify it.
- The buggy merge loses equal values even though its hand-picked examples pass.
- Shrinking simplifies failures; the example database can reuse them when enabled.

## Further reading
- [Hypothesis documentation](https://hypothesis.readthedocs.io/en/latest/)
- [What is property-based testing? — Hypothesis](https://hypothesis.works/articles/what-is-property-based-testing/)
