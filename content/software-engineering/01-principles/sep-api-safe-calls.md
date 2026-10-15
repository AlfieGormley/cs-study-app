---
id: sep-api-safe-calls
title: Design public calls that are hard to misuse
level: advanced
minutes: 3
summary: Keyword-only parameters and specific types make call sites easier to interpret.
sourceLesson: sep-writing-for-others
---

Callers and maintainers need a reliable contract. State what they may rely on and preserve the reasons behind a decision.

## Designing APIs for strangers

A public API (a library, an HTTP endpoint, a module others import) is the hardest code to change, because you can't see or fix its callers. Design for the user who reads nothing.

### Make it hard to misuse

```python
# Names reveal the units and chosen mode.
# Easy to misuse
resize(img, 800, 600, True, False)

# Hard to misuse
resize(img, width=800, height=600,
       keep_aspect=True)
```

- **Keyword-only arguments** (`*`) for anything a reader couldn't guess from position.
- **Types and enums instead of strings and booleans**: `Align.LEFT`, not `"left"`, which might be misspelt.
- **Make illegal states unrepresentable**: rather than `Order(status="paid", paid_at=None)` being possible, model `PaidOrder` with a required `paid_at` and validate boundary inputs. Python annotations alone still allow an explicitly supplied `None` at runtime.
- **Safe defaults**: TLS verification on, timeouts set. Python’s Requests library supplies no default timeout; without one, a call may wait indefinitely. A configured Requests timeout limits socket inactivity, not necessarily the total wall-clock duration of a complete response.
- **Principle of least astonishment**: similar operations should behave similarly. If `list.sort()` sorts in place and returns `None`, then a `sorted()` that returns a new list ought to leave its input unchanged.

## Key takeaways
- Keyword-only parameters and specific types make call sites easier to interpret.
- Validate boundary inputs even when the Python annotation excludes None.
- Choose defaults explicitly: Requests does not supply a default timeout.

## Further reading
- [requests.readthedocs.io](https://requests.readthedocs.io/en/latest/user/quickstart/#timeouts)
- [peps.python.org](https://peps.python.org/pep-3102/)
- [dataclasses](https://docs.python.org/3/library/dataclasses.html)
