---
id: test-fakes-interactions
sourceLesson: test-doubles
title: Keep fakes honest and verify useful interactions
level: intermediate
minutes: 4
summary: A fake provides simplified working behaviour; shared contract checks help detect drift.
---

Assume `import pytest` and `from unittest.mock import Mock`. The fake below is complete; examples using `SignupService` are application sketches. A double earns trust only for the behaviour it models and checks.

## Fakes: the underrated double

A **fake object** (usually just called a fake) is a real, working implementation that takes a shortcut, usually keeping data in memory.

```python
class InMemoryUsers:
    def __init__(self):
        self._rows = {}

    def add(self, user_id, email):
        # Model the email-uniqueness rule.
        if email in self._rows.values():
            raise ValueError("duplicate")
        # Store state for later reads.
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
    # Success means the expected error
    # arose.
    with pytest.raises(ValueError):
        svc.sign_up(2, "a@x.io")
    # Failed signup must not send again.
    assert mailer.send.call_count == 1
```

The fake enforces the uniqueness rule, so the test checks real behaviour rather than a script of expected calls. Fakes are reusable across hundreds of tests, and Google's testing guidance prefers them to mocks where a good fake exists.

The risk is that a fake drifts from the real thing. Keep it honest by running the **same contract test suite** against both the fake and the real implementation (the later database and contract units).

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
    # This checks mocked plumbing only.
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
- A fake provides simplified working behaviour; shared contract checks help detect drift.
- Use interactions for observable adapter-call requirements, not private plumbing.
- Inject dependencies and wrap external APIs in an interface you own.

## Further reading
- [unittest.mock — Python docs](https://docs.python.org/3/library/unittest.mock.html)
- [Mocks Aren't Stubs — Martin Fowler](https://martinfowler.com/articles/mocksArentStubs.html)
- [Test Doubles — Software Engineering at Google, ch. 13](https://abseil.io/resources/swe-book/html/ch13.html)
