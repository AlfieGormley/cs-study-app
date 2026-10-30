---
id: test-behaviour-readability
sourceLesson: test-unit-testing
title: Keep unit tests robust and readable
level: basic
minutes: 4
summary: Check public behaviour and keep expectations focused on one promise.
---

The following sketches use application classes such as `PriceService`. They compare test design rather than provide a complete application. A useful test survives changes to internals when the public promise is unchanged.

## Test behaviour, not implementation

The most common way unit tests go bad is by checking *how* the code works instead of *what* it does.

```python
# Brittle: reaches into internals
def test_price_cache():
    svc = PriceService()
    svc.price("ABC")
    # This couples the test to private data.
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
> Wanting to test a private helper directly is often a sign it is a separate unit waiting to be extracted. Either test it through the public method that uses it, or move it into its own module with its own public interface when that is a useful design boundary.

## One behaviour per test

"One assert per test" is too strict to follow literally. Several asserts that together check one behaviour are fine:

```python
def test_split_name():
    # Both assertions check one split
    # result.
    first, last = split_name("Ada Lovelace")
    assert first == "Ada"
    assert last == "Lovelace"
```

What you want to avoid is one test that checks registration, login and password reset in sequence. When it fails, you do not know which behaviour broke, and the later checks never run.

## DAMP over DRY

In production code, you remove duplication (DRY: don't repeat yourself). In tests, readability wins: prefer **DAMP** (descriptive and meaningful phrases). A reader should understand a test without jumping through three helper functions and a base class.

- Inline the values that matter to this test, so the reader can see them.
- Hide the values that don't matter in helpers or factories.
- Keep loops and `if` statements out of tests where you can (*Software Engineering at Google* puts it as "don't put logic in tests"). Logic in a test can have bugs of its own, and nothing tests the tests. Use `parametrize` for several literal cases instead.

## Common pitfalls

- **No assertion.** A test that calls code and checks nothing passes as long as no exception escapes. It looks like coverage but verifies almost nothing.
- **Shared mutable state.** A module-level list or a module-scoped fixture that tests modify makes results depend on order (the later flaky-test unit).
- **Hidden time and randomness.** Code that calls `datetime.now()` or `random()` directly gives different results each run. Pass the clock or the random generator in, so the test can control it.
- **Over-specified expectations.** Comparing a whole 40-field JSON document when the test is about one field means 39 unrelated reasons to fail.
- **Testing the framework.** You do not need to check that Django saves a model; test your logic.

## Key takeaways
- Check public behaviour and keep expectations focused on one promise.
- Several assertions can check one behaviour; unrelated workflow stages deserve separate tests.
- Make important inputs visible and hide only incidental setup.

## Further reading
- [Unit Testing — Software Engineering at Google, ch. 12](https://abseil.io/resources/swe-book/html/ch12.html)
- [Unit Test — Martin Fowler](https://martinfowler.com/bliki/UnitTest.html)
