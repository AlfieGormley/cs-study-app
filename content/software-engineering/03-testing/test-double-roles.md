---
id: test-double-roles
sourceLesson: test-doubles
title: Choose doubles and control their responses
level: intermediate
minutes: 4
summary: Use real fast collaborators; double slow, uncontrolled or side-effecting boundaries.
---

Real code talks to things that are awkward in a test: a payment provider that charges real cards, an email service, a clock, a database, a third-party API that is slow and sometimes down. A **test double** is a stand-in for one of those collaborators, the way a stunt double stands in for an actor.

Doubles make tests fast, deterministic and safe. Used carelessly, they also make tests that pass while the real system is broken. This unit covers their roles and configured responses; the following units examine patching and drift.

## Why replace a collaborator?

Reach for a double when the real thing is:

- **Slow**: for an illustrative comparison, a network call might take 200 ms while a lightweight in-memory double avoids the network entirely. Timings depend on the operation and environment.
- **Nondeterministic**: the clock, random numbers, a flaky API.
- **Side-effecting**: charging a card, sending an email, deleting files.
- **Hard to provoke**: you need a timeout, a 503 or a declined card, which the real service rarely produces on demand.
- **Not built yet**: another team's service exists only as an API spec.

If the real collaborator is fast, deterministic and in-process (a pure function, a value object, a small in-memory class), just use it.

## The vocabulary

Gerard Meszaros's *xUnit Test Patterns* gave us the standard names. "Mock" is often used loosely for all of them, but the distinctions are useful.

| Double | What it does |
|---|---|
| Dummy | Fills a parameter; never used |
| Stub | Returns canned answers |
| Spy | Stub that records how it was called |
| Mock | Pre-programmed with expected calls; verifies them |
| Fake | Working but simplified implementation |

Some concrete examples:

- **Dummy object**: a `logger` argument you pass `None` or `Mock()` for because this code path never logs.
- **Test stub**: a rates service that always returns `1.17` for GBP to EUR.
- **Test spy**: a mailer that records every `send()` so the test can check one email went out.
- **Mock object**: an object that fails the test if `charge()` is not called exactly once with `(card, 10)`.
- **Fake object**: an in-memory dictionary that behaves like your user repository, including enforcing unique emails.

## Doubles in Python: `unittest.mock`

The snippets in this section are partial examples: assume `import pytest`; `convert` is your application’s conversion function.

Python's standard library ships `unittest.mock`. An unrestricted `Mock` accepts most ordinary attribute access and arbitrary call arguments (some special and misspelled assertion names are rejected), records it, and returns another `Mock` unless told otherwise.

```python
from unittest.mock import Mock

rates = Mock()
# Supply a known exchange rate.
rates.get.return_value = 1.17   # stub

assert convert(100, "GBP", "EUR",
               rates) == 117.0

# Check the local adapter-call contract.
rates.get.assert_called_once_with(
    "GBP", "EUR")               # verify
```

Key tools:

- `return_value`: what a call returns.
- `side_effect`: an exception to raise, an iterable of results to return in turn, or a function to call.
- `assert_called_once_with(...)`, `assert_not_called()`, `call_count`, `call_args_list`: interaction checks.
- `Mock(wraps=real)`: a spy that passes calls through to the real object while recording them.
- `MagicMock`: a `Mock` that also supports magic methods like `len()` and iteration.

```python
pay = Mock(side_effect=[
    TimeoutError, {"status": "paid"}])

# The first configured call raises.
with pytest.raises(TimeoutError):
    pay()                 # first call
# The next configured result is returned.
assert pay() == {"status": "paid"}
assert pay.call_count == 2
```

That is how you test retry logic without waiting for a real timeout.

An iterable `side_effect` is consumed one item per call. When it runs out, the next call raises `StopIteration`; a retry loop catching only `TimeoutError` will not catch that exhaustion. Supply enough exceptions, or use `side_effect=TimeoutError` to raise on every call.


## Key takeaways
- Use real fast collaborators; double slow, uncontrolled or side-effecting boundaries.
- Dummy, stub, spy, mock and fake describe the role a double plays in a test.
- An iterable side_effect supplies one result or exception per call, then raises StopIteration.

## Further reading
- [unittest.mock — Python docs](https://docs.python.org/3/library/unittest.mock.html)
- [Test Double — Martin Fowler](https://martinfowler.com/bliki/TestDouble.html)
- [Test Doubles — Software Engineering at Google, ch. 13](https://abseil.io/resources/swe-book/html/ch13.html)
