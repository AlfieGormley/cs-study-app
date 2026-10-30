---
id: sep-callable-documentation
title: Document the contract callers cannot infer
level: advanced
minutes: 3
summary: Document units, ranges, failure modes, mutation and return values for callers.
sourceLesson: sep-writing-for-others
---

Callers and maintainers need a reliable contract. State what they may rely on and preserve the reasons behind a decision.

## Docstrings and type hints

A **docstring** documents a module, class or function for its *callers*. [PEP 257](https://peps.python.org/pep-0257/) sets the basics: a one-line summary in the imperative mood ("Return...", not "Returns..."), then a blank line, then detail. Conventions differ here: Google's Python style guide accepts either the imperative or the descriptive mood, as long as a file is consistent.

The following is a documentation sketch, not an implemented retry helper:

```python
# Documentation sketch: no retry body here.
def retry(fn, *, attempts=3,
          backoff=0.5):
    """Call fn, retrying on failure.

    Waits backoff * 2**n seconds after
    failure indexed n = 0, 1, ...; no
    wait after the final failed attempt.

    Args:
        fn: Zero-argument callable.
        attempts: Total tries, >= 1.
        backoff: Base delay in seconds.

    Returns:
        Whatever fn returns.

    Raises:
        The last exception if every
        attempt fails.
    """
```

The delay rule in that docstring is **exponential backoff**: the first wait is the base delay, and each later wait is twice the one before, so a struggling service gets more and more breathing room.

With the defaults (`attempts=3`, `backoff=0.5`), the waits are 0.5 s after the first failure and 1 s after the second. The third attempt is the last, so if it also fails there is no wait: the exception is raised. Real retry helpers usually also cap the delay and add random jitter, which this sketch leaves out.

That docstring is in Google style; NumPy and reStructuredText styles are also common. Pick one per project so tools (Sphinx, IDE tooltips) render it consistently.

A good docstring answers what a caller needs and can't see: units, valid ranges, what's raised, side effects, thread-safety, and whether arguments are mutated. It doesn't narrate the implementation.

**Type hints** are documentation that configured static-analysis tools can check. Python does not enforce them at runtime:

```python
# Signature sketch; a body is not shown.
def find(users: list[User],
         email: str) -> User | None:
```

The signature alone says the result may be absent, and a suitably configured checker can flag unsafe use in code it checks. Types don't replace docstrings (they can't say "email is compared case-insensitively"), but they remove a whole category of prose that would otherwise go stale.

## Key takeaways
- Document units, ranges, failure modes, mutation and return values for callers.
- A retry docstring must distinguish total attempts from waits between attempts.
- Python type hints support configured analysis and do not validate values at runtime.

## Further reading
- [PEP 257: Docstring Conventions](https://peps.python.org/pep-0257/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- [Python docs: typing](https://docs.python.org/3/library/typing.html)
