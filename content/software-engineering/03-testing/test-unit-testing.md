---
id: test-unit-testing
title: Unit testing well
level: basic
minutes: 13
summary: What a good unit test looks like, the pytest tools that make them easy (assert, raises, approx, parametrize, fixtures), and the habits that keep tests valuable rather than brittle.
---

Writing a unit test is easy. Writing unit tests that are still helping you two years later, instead of breaking every time someone refactors, takes some care. This lesson is about that care, using pytest.

## What counts as a "unit"?

There is no single agreed definition. Martin Fowler distinguishes two styles:

- **Solitary** unit tests isolate the code under test from all its collaborators, replacing them with test doubles (lesson 3).
- **Sociable** unit tests let the code use its real collaborators, as long as they are fast and in-process (no network, no real database).

Both are fine. What every unit test should share is the set of properties often summarised as **FIRST**:

| Letter | Meaning |
|---|---|
| Fast | Milliseconds, so you run it constantly |
| Independent | No reliance on other tests or order |
| Repeatable | Same result on any machine, any run |
| Self-validating | Passes or fails, no eyeballing |
| Timely | Written with the code, not months later |

A useful working definition: a unit test exercises one **behaviour** through a public interface, and is small in Google's sense (single process, no I/O).

## Structure: arrange, act, assert

Lay every test out in three visible steps.

```python
def test_cart_total_includes_vat():
    # Arrange
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

## pytest's toolbox

### Plain assert, with rewriting

pytest rewrites `assert` statements at import time so that a failure shows the values involved:

```
>  assert slugify("A B") == "a_b"
E  AssertionError: assert 'a-b' == 'a_b'
```

You do not need `assertEqual` and friends. One trap: never wrap an assert in brackets with a message.

```python
# always passes: a non-empty tuple
# is truthy
assert (1 == 2, "should fail")

# correct form
assert 1 == 2, "should fail"
```

pytest does warn about the first form ("assertion is always true"), but warnings are easy to miss in a long run.

### Expected exceptions: `pytest.raises`

```python
def parse_age(s):
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
    assert 0.1 + 0.2 == pytest.approx(0.3)
```

`0.1 + 0.2` is `0.30000000000000004` in binary floating point. `approx` compares within a tolerance (by default a relative tolerance of one part in a million, with a tiny absolute floor). For money, prefer `decimal.Decimal` or integer pennies in the code itself.

### Many cases, one test: `parametrize`

```python
@pytest.mark.parametrize("title, slug", [
    ("Hello World", "hello-world"),
    ("  Spaces  ", "spaces"),
    ("ALL CAPS", "all-caps"),
])
def test_slugify(title, slug):
    assert slugify(title) == slug
```

pytest generates three separate tests, each reported on its own, so one failing case does not hide the others. Stacking two `parametrize` decorators produces the **cross product**: 3 values × 2 values gives 6 tests.

### Setup and teardown: fixtures

A **fixture** is a function that provides something a test needs. A test asks for it by naming it as a parameter.

```python
@pytest.fixture
def account():
    return Account(balance=100)

def test_withdraw(account):
    account.withdraw(30)
    assert account.balance == 70
```

Once a fixture reaches `yield`, its teardown normally runs even if the test fails. Setup failure before the yield and abrupt process termination need separate handling:

```python
@pytest.fixture
def conn():
    c = open_connection()
    yield c
    c.close()
```

By default a fixture is **function-scoped**: it runs fresh for every test that uses it. `scope="module"` or `scope="session"` shares one instance across many tests, which is faster for expensive setup but risks tests leaking state into each other.

```
scope="function"  setup/teardown per test
scope="module"    once per test file
scope="session"   once per whole run
```

Fixtures can depend on other fixtures. A common pattern is a session-scoped database connection plus a function-scoped transaction that is rolled back after each test (lesson 4).

pytest ships useful built-in fixtures too:

- `tmp_path`: a fresh temporary directory (a `pathlib.Path`) per test.
- `monkeypatch`: temporarily set environment variables or attributes, undone after the test.
- `capsys`: capture what the code prints.

```python
def test_default_db_url(monkeypatch):
    monkeypatch.delenv("DB_URL",
                       raising=False)
    assert db_url() == "sqlite://"
```

## Test behaviour, not implementation

The most common way unit tests go bad is by checking *how* the code works instead of *what* it does.

```python
# Brittle: reaches into internals
def test_price_cache():
    svc = PriceService()
    svc.price("ABC")
    assert "ABC" in svc._cache

# Robust: checks observable behaviour
def test_price_is_stable():
    svc = PriceService()
    assert svc.price("ABC") == \
        svc.price("ABC")
```

The second example checks repeated output equality; it does not prove that caching occurs. If avoiding repeat source calls is part of the contract, inject a recording source and verify that requirement. The first test breaks if someone renames `_cache`, swaps the dict for an LRU, or moves caching into a decorator, even though nothing a caller can see has changed. A test that fails when behaviour is unchanged is a **false alarm**, and false alarms train people to "fix the test" without thinking.

A test broken by a behaviour-preserving refactor is a prompt to inspect implementation coupling, including dependencies that the test patches.

> [!warning] Private methods
> Wanting to test a private helper directly is often a sign it is a separate unit waiting to be extracted. Either test it through the public method that uses it, or move it into its own module with its own public interface.

## One behaviour per test

"One assert per test" is a myth. Several asserts that together check one behaviour are fine:

```python
def test_split_name():
    first, last = split_name("Ada Lovelace")
    assert first == "Ada"
    assert last == "Lovelace"
```

What you want to avoid is one test that checks registration, login and password reset in sequence. When it fails, you do not know which behaviour broke, and the later checks never run.

## DAMP over DRY

In production code, you remove duplication (DRY: don't repeat yourself). In tests, readability wins: prefer **DAMP** (descriptive and meaningful phrases). A reader should understand a test without jumping through three helper functions and a base class.

- Inline the values that matter to this test, so the reader can see them.
- Hide the values that don't matter in helpers or factories.
- Avoid loops and `if` statements in tests. Logic in a test can have bugs of its own, and nobody tests the tests.

## Common pitfalls

- **No assertion.** A test that calls code and checks nothing passes as long as no exception escapes. It looks like coverage but verifies almost nothing.
- **Shared mutable state.** A module-level list or a module-scoped fixture that tests modify makes results depend on order (lesson 6).
- **Hidden time and randomness.** Code that calls `datetime.now()` or `random()` directly gives different results each run. Pass the clock or the random generator in, so the test can control it.
- **Over-specified expectations.** Comparing a whole 40-field JSON blob when the test is about one field means 39 unrelated reasons to fail.
- **Testing the framework.** You do not need to check that Django saves a model; test your logic.

## Key takeaways
- Good unit tests are fast, independent, repeatable, self-validating and written alongside the code.
- Structure tests as arrange, act, assert, and name them after the behaviour they check.
- Use `pytest.raises(..., match=...)`, `pytest.approx`, `parametrize` and fixtures; know that fixture scope trades speed for isolation.
- Test observable behaviour through public interfaces; a test that breaks on a pure refactor is a liability.
- Prefer clear, slightly repetitive tests (DAMP) to clever, abstract ones; avoid logic in tests.

## Further reading
- [How to use fixtures — pytest docs](https://docs.pytest.org/en/stable/how-to/fixtures.html)
- [How to parametrize tests — pytest docs](https://docs.pytest.org/en/stable/how-to/parametrize.html)
- [How to write and report assertions — pytest docs](https://docs.pytest.org/en/stable/how-to/assert.html)
- [How to monkeypatch — pytest docs](https://docs.pytest.org/en/stable/how-to/monkeypatch.html)
- [Unit Testing — Software Engineering at Google, ch. 12](https://abseil.io/resources/swe-book/html/ch12.html)
- [Unit Test — Martin Fowler](https://martinfowler.com/bliki/UnitTest.html)
