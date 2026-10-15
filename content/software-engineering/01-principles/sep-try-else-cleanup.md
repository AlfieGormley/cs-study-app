---
id: sep-try-else-cleanup
title: Follow try, else and cleanup control flow
level: advanced
minutes: 3
summary: The else suite runs only after normal completion of try and is outside its handlers.
sourceLesson: sep-error-handling
---

Failure handling is part of a function’s contract. Keep the happy path clear while making each exceptional outcome deliberate.

## Python's try statement in full

```python
# Only load errors enter these handlers.
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
# The return replaces the pending error.
def f():
    try:
        raise ValueError("lost")
    finally:
        return "ok"

f()  # returns "ok"; error vanished
```

CPython 3.14 introduced a `SyntaxWarning` when `return`, `break` or `continue` exits a `finally` block (PEP 765). This is a compile-time warning and can be promoted to an error by warning settings. Avoid those control-flow exits; a loop wholly inside `finally` may still use its own `break` or `continue`.

For cleanup, prefer **context managers**, which invoke their cleanup methods when leaving the with suite through ordinary Python control flow, including exceptions (not abrupt process termination):

```python
# Both contexts exit on ordinary failure.
with open(path) as f, db.transaction():
    process(f)
```

## Key takeaways
- The else suite runs only after normal completion of try and is outside its handlers.
- Finally participates in normal Python exits, including returns and exceptions.
- A return from finally can discard a pending error; prefer explicit cleanup protocols.

## Further reading
- [compound_stmts](https://docs.python.org/3/reference/compound_stmts.html#the-try-statement)
- [peps.python.org](https://peps.python.org/pep-0765/)
