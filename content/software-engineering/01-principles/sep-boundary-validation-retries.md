---
id: sep-boundary-validation-retries
title: Validate at boundaries and retry with a plan
level: advanced
minutes: 3
summary: Boundary validation can establish a useful internal invariant.
sourceLesson: sep-error-handling
---

Failure handling is part of a function’s contract. Keep the happy path clear while making each exceptional outcome deliberate.

## Fail fast, at the boundary

Validate input where it enters the system (an HTTP handler, a CLI, a message consumer) and convert it to validated types. Deeper code can then assume valid data instead of re-checking everywhere.

```python
# Reject bool too: its exact type is bool.
from dataclasses import dataclass

@dataclass(frozen=True)
class Quantity:
    value: int

    def __post_init__(self):
        if type(self.value) is not int:
            raise TypeError(
                "integer required")
        if not 1 <= self.value <= 99:
            raise ValueError(
                f"quantity 1-99, got "
                f"{self.value}")
```

A failure close to its cause is generally easier to diagnose. A `None` that travels through five functions before blowing up is not.

### Collecting errors instead of stopping at the first

For user input, failing on the first problem is frustrating ("fix the email... now fix the postcode... now..."). Fowler's **notification pattern** collects all validation errors and returns them together:

```python
# Accumulate independent validation issues.
def validate(form):
    errors = []
    if "@" not in form.email:
        errors.append("email: invalid")
    if not form.postcode:
        errors.append("postcode: required")
    return errors
```

The email check here only illustrates collecting independent messages; an at-sign alone is not a complete check of email-address syntax.

Python 3.11 introduced `ExceptionGroup` and `except*` for grouping and handling exceptions, including failures collected by an `asyncio.TaskGroup`. That is a different mechanism from a validation notification: an ordinary task failure cancels the remaining tasks, and `KeyboardInterrupt` and `SystemExit` receive special treatment. It does not guarantee that every possible validation problem is collected.

## Anti-patterns

- **Swallowing**: `except: pass`. The failure still happened; you've just removed the evidence.
- **Log and re-raise at every layer**: the same error appears five times in the logs, each with a partial stack. Log once, where it's handled (or at the top level).
- **Exceptions for control flow** in hot paths, such as throwing to exit a loop: slow in many languages and confusing to read. (Python's own `StopIteration` is the idiomatic exception.)
- **Returning `None` for failure**: the caller forgets to check, and you get `AttributeError: 'NoneType' has no attribute ...` far away. Raise, or return an explicit result type.
- **Retrying non-idempotent operations**: retrying a timed-out "charge card" call may charge twice. Retry only idempotent operations, or use idempotency keys.
- **Retrying without backoff and jitter**: synchronised retries from thousands of clients can keep a recovering service down.

## Key takeaways
- Boundary validation can establish a useful internal invariant.
- A validation notification can report several independent input problems together.
- A timeout leaves an ambiguous outcome; safe retries need idempotency, limits and backoff.

## Further reading
- [Martin Fowler: Replacing Throwing Exceptions with Notification in Validations](https://martinfowler.com/articles/replaceThrowWithNotification.html)
- [Python docs: asyncio task groups](https://docs.python.org/3/library/asyncio-task.html#task-groups)
- [Stripe API: idempotent requests](https://docs.stripe.com/api/idempotent_requests)
