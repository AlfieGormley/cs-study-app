---
id: test-doubles
title: Test doubles (mocks, stubs, fakes)
level: intermediate
minutes: 14
summary: Dummies, stubs, spies, mocks and fakes, how to use unittest.mock correctly (including where to patch and autospec), and how over-mocking produces tests that pass while production breaks.
---

Real code talks to things that are awkward in a test: a payment provider that charges real cards, an email service, a clock, a database, a third-party API that is slow and sometimes down. A **test double** is a stand-in for one of those collaborators, the way a stunt double stands in for an actor.

Doubles make tests fast, deterministic and safe. Used carelessly, they also make tests that pass while the real system is broken. This lesson covers both sides.

## Why replace a collaborator?

Reach for a double when the real thing is:

- **Slow**: a network call takes 200 ms; a double takes microseconds.
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

- **Dummy**: a `logger` argument you pass `None` or `Mock()` for because this code path never logs.
- **Stub**: a rates service that always returns `1.17` for GBP to EUR.
- **Spy**: a mailer that records every `send()` so the test can check one email went out.
- **Mock**: an object that fails the test if `charge()` is not called exactly once with `(card, 10)`.
- **Fake**: an in-memory dictionary that behaves like your user repository, including enforcing unique emails.

## Doubles in Python: `unittest.mock`

Python's standard library ships `unittest.mock`. An unrestricted `Mock` accepts most ordinary attribute access and arbitrary call arguments (some special and misspelled assertion names are rejected), records it, and returns another `Mock` unless told otherwise.

```python
from unittest.mock import Mock

rates = Mock()
rates.get.return_value = 1.17   # stub

assert convert(100, "GBP", "EUR",
               rates) == 117.0

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

with pytest.raises(TimeoutError):
    pay()                 # first call
assert pay() == {"status": "paid"}
assert pay.call_count == 2
```

That is how you test retry logic without waiting for a real timeout.

## Patch where it is looked up

`unittest.mock.patch` temporarily replaces a name while a test runs. The most common mistake is patching the wrong name.

```python
# payments.py
def charge(card, amount):
    ...  # real network call

# checkout.py
from payments import charge

def place_order(card, total):
    r = charge(card, total)
    if r["status"] == "paid":
        return "ok"
    return "declined"
```

`from payments import charge` copies a reference to the function into `checkout`'s namespace when `checkout` is imported. So:

```python
# WRONG: checkout still holds the
# original charge, so the real call runs
with patch("payments.charge") as f:
    f.return_value = {"status": "paid"}
    place_order("4242", 10)

# RIGHT: replace the name checkout uses
with patch("checkout.charge") as f:
    f.return_value = {"status": "paid"}
    assert place_order("4242", 10) == "ok"
```

The rule from the Python docs: **patch where an object is looked up, not where it is defined.** If `checkout.py` instead did `import payments` and called `payments.charge(...)`, then patching `"payments.charge"` would work, because the lookup happens on the `payments` module at call time.

```
from payments import charge
  checkout.charge -> original function
  patch "checkout.charge"

import payments
  checkout -> payments module
  patch "payments.charge"
```

## Mocks lie: spec and autospec

A bare `Mock` accepts most ordinary method names and arbitrary call arguments, which means it cannot tell you when you have used it wrongly.

```python
m = Mock()
m.chrage("4242", 10)       # typo
m.charge.assert_not_called()   # passes
```

Worse, when the real API changes (say `charge` gains a required `currency` argument), every test using a bare `Mock` keeps passing while production fails.

Two defences:

- `Mock(spec=Mailer)` restricts attribute lookup to names on the spec, so unknown method lookups raise `AttributeError`. Use `spec_set` to restrict setting unknown attributes too. It does not check the arguments passed to methods.
- `create_autospec(Mailer)` or `patch(..., autospec=True)` also checks **call signatures**, so a missing argument raises `TypeError`.

```python
fake = create_autospec(payments.charge)
fake("4242")      # TypeError: missing
                  # 'amount'
```

> [!warning] Misspelled assertions
> `m.assert_called_once()` checks something; `m.asert_called_once()` used to silently do nothing and return a new `Mock`. Recent Python versions raise `AttributeError` for names starting with `assert`, `assret`, `asert`, `aseert` or `assrt`, and for a few common slips such as `called_once_with`. Other typos, like `asssert_called_once`, still pass silently. Prefer `spec` or `autospec`.

## Fakes: the underrated double

A **fake** is a real, working implementation that takes a shortcut, usually keeping data in memory.

```python
class InMemoryUsers:
    def __init__(self):
        self._rows = {}

    def add(self, user_id, email):
        if email in self._rows.values():
            raise ValueError("duplicate")
        self._rows[user_id] = email

    def get(self, user_id):
        return self._rows.get(user_id)
```

```python
def test_duplicate_sends_no_email():
    users = InMemoryUsers()
    mailer = Mock()
    svc = SignupService(users, mailer)
    svc.sign_up(1, "a@x.io")
    with pytest.raises(ValueError):
        svc.sign_up(2, "a@x.io")
    assert mailer.send.call_count == 1
```

The fake enforces the uniqueness rule, so the test checks real behaviour rather than a script of expected calls. Fakes are reusable across hundreds of tests, and Google's testing guidance prefers them to mocks where a good fake exists.

The risk is that a fake drifts from the real thing. Keep it honest by running the **same contract test suite** against both the fake and the real implementation (lesson 4).

## State versus interaction verification

There are two ways to check a result:

- **State verification**: do the thing, then inspect the resulting state. "After signing up, the repository contains the user."
- **Interaction verification**: check which calls were made. "`repo.add` was called once with `(1, 'a@x.io')`."

Martin Fowler's *Mocks Aren't Stubs* describes two schools that follow from this:

- **Classicists** (Detroit school) use real objects where possible, doubles only for awkward collaborators, and prefer state verification.
- **Mockists** (London school) isolate every class, mock all its collaborators, and verify interactions. This drives design outside-in.

Interaction checks are the right tool when the interaction *is* the behaviour: "an email was sent", "the payment adapter was invoked once in this scenario". A call-count assertion does not prove that a remote payment occurred exactly once; provider idempotency and failure-path integration tests address that separate concern. They are the wrong tool for internal plumbing, because they couple tests to implementation.

## When mocking goes wrong

### Over-mocking

```python
def test_place_order():
    repo = Mock(); pricer = Mock()
    tax = Mock(); pay = Mock()
    pricer.price.return_value = 10
    tax.add.return_value = 12
    ...
    pay.charge.assert_called_once_with(
        "card", 12)
```

When every collaborator is mocked, the test mostly re-states the implementation. Refactor how tax is applied and it breaks; introduce a real bug in the tax rules and it still passes, because the tax rules are mocked out.

Warning signs: more lines of mock setup than of test, mocks returning mocks, and tests that break on every refactor.

### Mocking what you don't own

Mocking `requests.get` or the AWS SDK directly encodes *your guess* of how they behave. If the guess is wrong, the test is wrong. A better approach is to wrap the third-party API in a thin adapter you own (`PaymentGateway.charge`), double the adapter in unit tests, and test the adapter itself with integration tests against the real thing or a realistic sandbox.

### Mocking values

Never mock simple data objects (`Money`, `Address`, a dataclass). Construct real ones. They are fast and deterministic, and mocks of them drift from reality.

## Injection beats patching

Patching module globals works, but it is a sign of hidden dependencies. If a collaborator is passed in (constructor or function argument), the test just passes a double:

```python
class SignupService:
    def __init__(self, users, mailer):
        self.users = users
        self.mailer = mailer
```

No `patch`, no worrying about where names are looked up, and the dependency is visible in the signature. The same applies to clocks: accept a `now` function or a `Clock` object instead of calling `datetime.now()` internally.

## Key takeaways
- Use a double when the real collaborator is slow, nondeterministic, side-effecting or hard to provoke; otherwise use the real thing.
- Dummy, stub, spy, mock and fake differ in whether they return canned data, record calls, verify expectations or actually work.
- Patch where a name is looked up, not where it is defined; `from x import f` needs `patch("yourmodule.f")`.
- Bare mocks accept anything; use `spec` or `autospec` so typos and signature changes fail loudly.
- Prefer fakes and state verification; reserve interaction checks for calls that are the behaviour, and wrap third-party APIs before doubling them.

## Further reading
- [unittest.mock — Python docs](https://docs.python.org/3/library/unittest.mock.html)
- [Mocks Aren't Stubs — Martin Fowler](https://martinfowler.com/articles/mocksArentStubs.html)
- [Test Double — Martin Fowler](https://martinfowler.com/bliki/TestDouble.html)
- [Test Doubles — Software Engineering at Google, ch. 13](https://abseil.io/resources/swe-book/html/ch13.html)
- [How to monkeypatch — pytest docs](https://docs.pytest.org/en/stable/how-to/monkeypatch.html)
