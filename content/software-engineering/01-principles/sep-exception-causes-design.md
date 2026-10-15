---
id: sep-exception-causes-design
title: Translate errors without losing their cause
level: advanced
minutes: 3
summary: Explicit exception chaining preserves a low-level cause when exposing a domain error.
sourceLesson: sep-error-handling
---

Failure handling is part of a function’s contract. Keep the happy path clear while making each exceptional outcome deliberate.

## Chaining: keep the cause

When you translate a low-level error into a domain one, keep the original:

```python
# Expose the domain error; retain its cause.
try:
    row = db.fetch(uid)
except psycopg.OperationalError as e:
    raise UserLookupFailed(uid) from e
```

`from e` sets `__cause__`, and the traceback shows both, joined by "The above exception was the direct cause of the following exception". Raising inside an `except` *without* `from` still records the original as `__context__` ("During handling of the above exception, another exception occurred"), which reads like a second bug. `raise X from None` suppresses the context, appropriate only when the original is pure noise.

## Design your exceptions

- **A small hierarchy per module or library**: `class PaymentError(Exception)`, then `CardDeclined(PaymentError)`. Callers can catch broadly or narrowly.
- **Carry data, not just a message**: `CardDeclined(reason="insufficient_funds", retryable=False)`. Callers shouldn't have to parse strings.
- **Translate at boundaries.** Code calling your payments module shouldn't need to know you use Stripe, so do not expose a provider-specific exception class as your own stable contract; translate it while retaining its cause. The exact provider namespace depends on the installed SDK version.
- **Write messages for the person who'll read them**: what failed, with which input, and what to do. `ValueError("bad input")` is useless at 3 a.m.; `ValueError("quantity must be 1-99, got -3")` isn't.

## Key takeaways
- Explicit exception chaining preserves a low-level cause when exposing a domain error.
- An exception hierarchy lets callers handle a family or a specific outcome.
- Expose structured data and actionable messages rather than forcing callers to parse prose.

## Further reading
- [peps.python.org](https://peps.python.org/pep-3134/)
- [exceptions](https://docs.python.org/3/library/exceptions.html)
