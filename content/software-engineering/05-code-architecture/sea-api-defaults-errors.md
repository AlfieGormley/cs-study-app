---
id: sea-api-defaults-errors
sourceLesson: sea-api-design
title: Safe defaults and useful exceptions
level: advanced
minutes: 4
summary: Avoid shared mutable defaults and expose stable return types and semantically useful library errors.
---

Good signatures are only part of an API contract. Defaults, return types and errors also shape what callers can safely assume.

### Defaults and the mutable default trap

```python
def tag(item, tags=[]):
    # Mutates whichever list this call
    # received.
    tags.append(item)
    return tags

# First call mutates the shared default.
print(tag("a"))  # ['a']
# Both calls retain the same default list.
print(tag("b"))  # ['a', 'b']
```

This prints `['a']` and then `['a', 'b']`. The default list is created **once**, when the function is defined, and shared by calls that omit the tags argument. Use `None` and create a fresh object inside:

```python
def tag(item, tags=None):
    if tags is None:
        # Allocate a fresh list for this
        # call.
        tags = []
    # Mutates whichever list this call
    # received.
    tags.append(item)
    return tags
```

Choose **safe defaults**: verify TLS certificates by default, set a finite timeout, don't delete without confirmation. (`requests` has no default timeout, which is why a forgotten `timeout=` can hang a worker forever, so callers should choose explicit connect/read timeouts and any required overall deadline.)

### Accept general, return specific

Accept the broadest type that works (any iterable, any mapping, a `Protocol`) and return a concrete, documented type. A function that returns a `list` on success, `None` on "no results" and a `dict` on error forces every caller to branch on type. Return an empty list for "nothing", and raise for errors.

## Errors are part of the API

Callers write `except` clauses against your exception types, so design them:

```python
class PaymentError(Exception):
    """Base for all errors we raise."""

class CardDeclined(PaymentError):
    def __init__(self, code):
        # Retain the decline code for
        # callers.
        super().__init__(code)
        self.code = code

class GatewayTimeout(PaymentError):
    pass
```

- A single **base exception** lets callers catch the expected library errors placed under that hierarchy. Programmer errors and unrelated exceptions may still propagate.
- **Specific subclasses** let them handle cases differently (apply a safe idempotent retry policy for an uncertain timeout, show an appropriate message for a decline).
- **Don't leak implementation exceptions.** If you raise `psycopg.OperationalError` today, you can never switch database drivers without breaking callers. Translate it into a semantically appropriate library error and preserve chaining. Do not label every OperationalError a timeout; failures such as unavailable storage or invalid connection settings differ.

## Key takeaways
- Mutable default objects are created once and reused across calls.
- Use a sentinel such as None to create a fresh list per call.
- Choose explicit timeout and security policies rather than relying on accidental defaults.
- A documented return type and exception hierarchy make callers simpler.
- Translate driver errors by their meaning and preserve exception chaining.

## Further reading
- [Python tutorial: default argument values](https://docs.python.org/3/tutorial/controlflow.html#default-argument-values)
- [Requests: timeouts](https://requests.readthedocs.io/en/latest/user/advanced/#timeouts)
- [Psycopg errors](https://www.psycopg.org/psycopg3/docs/api/errors.html)
