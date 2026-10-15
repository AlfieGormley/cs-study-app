---
id: test-unit-structure
sourceLesson: test-unit-testing
title: Structure focused unit tests and assertions
level: basic
minutes: 3
summary: FIRST describes useful test qualities rather than a precise definition of unit.
---

Writing a unit test is easy. Writing unit tests that are still helping you two years later, instead of breaking every time someone refactors, takes some care. This lesson is about that care, using pytest.

## What counts as a "unit"?

There is no single agreed definition. Martin Fowler distinguishes two styles:

- **Solitary** unit tests isolate the code under test from all its collaborators, replacing them with test doubles (the later test-double units).
- **Sociable** unit tests let the code use its real collaborators, as long as they are fast and in-process (no network, no real database).

Both are fine. What every unit test should share is the set of properties often summarised as **FIRST**:

| Letter | Meaning |
|---|---|
| Fast | Quick enough to run constantly |
| Isolated | Failure points to one focused behaviour |
| Repeatable | Controlled inputs and environment |
| Self-validating | Passes or fails, no eyeballing |
| Timely | Written with the code, not months later |

Tests also need independent setup so their results do not depend on order.

A useful working definition here: a unit test exercises one **behaviour** through a public interface and is small in Google’s sense (one thread in one process, no sleeping or external I/O, with its documented in-memory filesystem exception).

## Structure: arrange, act, assert

Lay every test out in three visible steps.

```python
def test_cart_total_includes_vat():
    # Arrange
    # Two books cost 20 before 20% VAT.
    cart = Cart(vat_rate=0.2)
    cart.add("book", price=10.00, qty=2)

    # Act
    total = cart.total()

    # Assert
    assert total == 24.00
```

If you cannot find a clean "act" line, the test is probably checking several behaviours at once. Split it.

### Name tests after behaviour

A test name is the first thing you read when it fails. Compare:

- `test_total_2` tells you nothing.
- `test_cart_total_includes_vat` tells you which promise broke.

A good pattern is *unit, scenario, expected result*: `test_withdraw_more_than_balance_raises`.

## Plain assert, with rewriting

The `Cart` example is a partial sketch using an application class; the two deliberately incorrect assertions below demonstrate failure modes.

pytest rewrites `assert` statements at import time so that a failure shows the values involved:

```
>  assert slugify("A B") == "a_b"
E  AssertionError: assert 'a-b' == 'a_b'
```

You do not need `assertEqual` and friends. One trap: never wrap an assert in brackets with a message.

```python
# always passes: a non-empty tuple
# is truthy
# Demonstration: the tuple is truthy.
assert (1 == 2, "should fail")

# correct form
# Demonstration: this assertion fails.
assert 1 == 2, "should fail"
```

pytest does warn about the first form ("assertion is always true"), but warnings are easy to miss in a long run.

## Key takeaways
- FIRST describes useful test qualities rather than a precise definition of unit.
- Arrange, act, assert and behavioural names make failures easier to understand.
- Assert the condition directly; a non-empty tuple is always truthy.

## Further reading
- [How to write and report assertions — pytest docs](https://docs.pytest.org/en/stable/how-to/assert.html)
- [Unit Testing — Software Engineering at Google, ch. 12](https://abseil.io/resources/swe-book/html/ch12.html)
- [Unit Test — Martin Fowler](https://martinfowler.com/bliki/UnitTest.html)
