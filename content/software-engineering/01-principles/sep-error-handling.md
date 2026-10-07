---
id: sep-error-handling
title: Error handling
level: advanced
minutes: 12
summary: Classifying failures, exceptions versus result values, Python's try/except/else/finally in depth, chaining, fail-fast validation, and the anti-patterns that turn small faults into outages.
---

Most code is written for the happy path. Failure paths deserve explicit design: the timeout nobody expected, the exception swallowed three layers down, the retry storm that turned a blip into an outage.

Good error handling isn't about catching everything. It's about deciding, deliberately, **who** should deal with each failure and **what** they need to know to do it.

## Three kinds of failure

Different failures need different responses. Mixing them up is the root of most bad error handling.

| Kind | Example | Right response |
|---|---|---|
| Bug | `None` where a user was expected | Crash loudly, fix the code |
| Expected failure | Card declined, file missing | Handle as normal logic |
| Environmental | Network timeout, disk full | Retry, degrade, or report |

- **Bugs** need diagnosis and correction. Do not silently continue as though the operation succeeded. A service may safely contain a failing request or worker, roll back its changes and report the error; process termination is not always necessary.
- **Expected failures** are part of the domain. "Insufficient funds" isn't exceptional to a bank. These deserve explicit types and handling.
- **Environmental failures** are transient or external. They often call for retries with backoff, timeouts, fallbacks or circuit breakers, at a layer that can make that decision.

## Exceptions versus error values

Languages take two broad approaches.

**Exceptions** (Python, Java, C#) separate the error path from the normal path. An error propagates up the stack until something catches it.

- Pro: the happy path reads cleanly, and errors can't be silently ignored by forgetting to check a return value.
- Con: the error path is invisible at the call site. Any line might throw, and you can't tell from reading it.

**Error values** (Go's `(value, err)`, Rust's `Result<T, E>`) make failure part of the return type.

```
// Go
f, err := os.Open(path)
if err != nil {
    return fmt.Errorf("open %s: %w",
                      path, err)
}
```

- Pro: every failure point is visible, and Rust normally warns when a `Result` marked `must_use` is discarded. This is a lint, not an unconditional compilation error; code can explicitly discard it, so meaningful handling still needs review.
- Con: more ceremony; in Go nothing stops you ignoring `err` (linters help).

Java adds a twist: **checked exceptions** must be caught or declared (`throws IOException`) by code that can propagate them, which makes failures visible in signatures. In practice many teams found them noisy, wrapping them in unchecked exceptions, and later JVM languages such as Kotlin dropped them. A common guideline from Oracle's own tutorial: use checked exceptions for conditions a caller can reasonably recover from, and unchecked (`RuntimeException`) for programming errors.

In Python, exceptions are the idiom. Use them, but make the expected ones explicit types.

## Python's try statement in full

```python
try:
    data = load(path)
except FileNotFoundError:
    data = DEFAULTS
except json.JSONDecodeError as e:
    raise ConfigError(path) from e
else:
    validate(data)
finally:
    log.debug("load attempted")
```

| Clause | Runs when |
|---|---|
| `try` | always first |
| `except` | a matching exception is raised in `try` |
| `else` | `try` completed normally, without an exception or exiting via `return`, `break` or `continue` |
| `finally` | on normal Python control-flow exit, including exceptions and returns; abrupt process termination can prevent cleanup |

Why `else`? Code in `else` isn't protected by the `except` clauses. If `validate` raised `FileNotFoundError` for an unrelated reason, you don't want it mistaken for "config missing". Keep the `try` block as small as the operation you actually expect to fail.

### `finally` and its trap

`finally` runs even when `try` returns or raises. That makes it right for cleanup, but a `return` inside `finally` **overrides** whatever was happening, including discarding an in-flight exception:

```python
def f():
    try:
        raise ValueError("lost")
    finally:
        return "ok"

f()  # returns "ok"; error vanished
```

CPython 3.14 now emits a `SyntaxWarning` for this (PEP 765). Never return, `break` or `continue` out of `finally`.

For cleanup, prefer **context managers**, which invoke their cleanup protocol on ordinary scope exit, including exceptions (not abrupt process termination):

```python
with open(path) as f, db.transaction():
    process(f)
```

### Catch narrowly

```python
# Dangerous
try:
    user = repo.get(uid)
    send(user.email)
except:
    pass
```

A bare `except:` catches `BaseException`, which includes `KeyboardInterrupt` and `SystemExit`, so Ctrl+C stops working. It also hides typos (`NameError`), bugs (`AttributeError`) and genuine failures alike. `except Exception:` is only a little better.

Catch the specific exceptions you expect and can do something about. Let everything else propagate to a top-level handler that logs and reports it.

### EAFP and LBYL

Python style favours **EAFP** ("easier to ask forgiveness than permission") over **LBYL** ("look before you leap"):

```python
# LBYL: race between check and use
if os.path.exists(p):
    with open(p) as f: ...

# EAFP: just try it
try:
    with open(p) as f: ...
except FileNotFoundError:
    ...
```

The LBYL version has a **time-of-check to time-of-use** (TOCTOU) race: the file can disappear between `exists` and `open`. With files, locks and networks, the only reliable check is attempting the operation.

## Chaining: keep the cause

When you translate a low-level error into a domain one, keep the original:

```python
try:
    row = db.fetch(uid)
except psycopg.OperationalError as e:
    raise UserLookupFailed(uid) from e
```

`from e` sets `__cause__`, and the traceback shows both, joined by "The above exception was the direct cause of the following exception". Raising inside an `except` *without* `from` still records the original as `__context__` ("During handling of the above exception, another exception occurred"), which reads like a second bug. `raise X from None` suppresses the context, appropriate only when the original is pure noise.

## Design your exceptions

- **A small hierarchy per module or library**: `class PaymentError(Exception)`, then `CardDeclined(PaymentError)`. Callers can catch broadly or narrowly.
- **Carry data, not just a message**: `CardDeclined(reason="insufficient_funds", retryable=False)`. Callers shouldn't have to parse strings.
- **Translate at boundaries.** Code calling your payments module shouldn't need to know you use Stripe, so don't leak `stripe.error.CardError`; wrap it.
- **Write messages for the person who'll read them**: what failed, with which input, and what to do. `ValueError("bad input")` is useless at 3 a.m.; `ValueError("quantity must be 1-99, got -3")` isn't.

## Fail fast, at the boundary

Validate input where it enters the system (an HTTP handler, a CLI, a message consumer) and convert it to trusted types. Deeper code can then assume valid data instead of re-checking everywhere.

```python
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

A failure close to its cause is cheap to diagnose. A `None` that travels through five functions before blowing up is not.

### Collecting errors instead of stopping at the first

For user input, failing on the first problem is frustrating ("fix the email... now fix the postcode... now..."). Fowler's **notification** pattern collects all validation errors and returns them together:

```python
def validate(form):
    errors = []
    if "@" not in form.email:
        errors.append("email: invalid")
    if not form.postcode:
        errors.append("postcode: required")
    return errors
```

Python 3.11's `ExceptionGroup` and `except*` do something similar for concurrent failures, such as several tasks in an `asyncio.TaskGroup` failing at once.

## Anti-patterns

- **Swallowing**: `except: pass`. The failure still happened; you've just removed the evidence.
- **Log and re-raise at every layer**: the same error appears five times in the logs, each with a partial stack. Log once, where it's handled (or at the top level).
- **Exceptions for control flow** in hot paths, such as throwing to exit a loop: slow in many languages and confusing to read. (Python's own `StopIteration` is the idiomatic exception.)
- **Returning `None` for failure**: the caller forgets to check, and you get `AttributeError: 'NoneType' has no attribute ...` far away. Raise, or return an explicit result type.
- **Retrying non-idempotent operations**: retrying a timed-out "charge card" call may charge twice. Retry only idempotent operations, or use idempotency keys.
- **Retrying without backoff and jitter**: synchronised retries from thousands of clients can keep a recovering service down.

## Key takeaways
- Distinguish bugs (fail loudly), expected failures (model explicitly) and environmental failures (retry, degrade or report).
- Exceptions keep the happy path clean but hide failure points; result types make them visible at the cost of ceremony.
- Keep `try` blocks small, use `else` for code that shouldn't be guarded, and never return from `finally`.
- Catch specific exceptions; bare `except:` even catches `KeyboardInterrupt`.
- Chain with `raise ... from e` when translating errors, and design small exception hierarchies that carry data.
- Validate at the boundary and fail fast; for user input, collect all errors at once.
- Log once, don't swallow, and only retry idempotent operations, with backoff.

## Further reading
- [Errors and Exceptions — Python tutorial](https://docs.python.org/3/tutorial/errors.html)
- [Built-in Exceptions — Python docs](https://docs.python.org/3/library/exceptions.html)
- [PEP 3134: Exception Chaining and Embedded Tracebacks](https://peps.python.org/pep-3134/)
- [Replacing Throwing Exceptions with Notification in Validations — Martin Fowler](https://martinfowler.com/articles/replaceThrowWithNotification.html)
- [Unchecked Exceptions: The Controversy — Oracle Java tutorial](https://docs.oracle.com/javase/tutorial/essential/exceptions/runtime.html)
- [Error Handling — The Rust Programming Language](https://doc.rust-lang.org/book/ch09-00-error-handling.html)
- [Error handling and Go — The Go Blog](https://go.dev/blog/error-handling-and-go)
