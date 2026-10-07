---
id: sep-writing-for-others
title: Writing code for others: comments, docs and APIs
level: advanced
minutes: 11
summary: When comments help and when they lie, docstrings and type hints, the four kinds of documentation, commit messages, and designing APIs that are hard to misuse and safe to evolve under Hyrum's Law.
---

Code that only its author can use is a liability. The moment anyone else touches it (a teammate, a library user, you in a year) everything not written down has to be rediscovered by reading, guessing or breaking things.

This lesson covers the layers through which code talks to other people, from the closest to the furthest away:

```
 inline comments   -> the next maintainer
 docstrings/types  -> callers of a function
 README/docs       -> users of a module
 commit messages   -> future debuggers
 public API        -> people you never meet
```

## Comments: explain why, not what

Code already says *what* it does. A comment that repeats it adds reading time and one more thing to keep in sync.

```python
# Bad: restates the code
i += 1  # increment i
```

Good comments carry information the code *can't*:

```python
# Stripe can deliver an event repeatedly.
# Dedupe by event id, not its timestamp.
if seen(event.id):
    return
```

```python
# Input is limited to 8 elements by the
# caller contract; keep this loop simple.
```

> [!note] Content gap
> The previous claim of a measured threefold speedup was removed because no benchmark or reproducible setup was available. No performance result is asserted here.

The webhook fragment only illustrates a comment. Production deduplication needs durable, atomic coordination with the effect. Stripe automatic retries last up to three days in live mode; manual CLI resends can occur up to 30 days later, so three days is not a universal deduplication-retention limit.

Useful kinds of comment:

- **Intent and reasons**: why this approach, why not the obvious one.
- **Warnings**: "not thread-safe", "called from a signal handler".
- **References**: a link to the spec, RFC, ticket or bug this works around.
- **TODOs with an owner or ticket**, so they can be found and finished.

### Comments rot

The compiler checks code; nothing checks comments. When code changes and the comment doesn't, the comment becomes a lie that's *more* convincing than no comment at all.

```python
# Retry up to 3 times
for _ in range(5):
    ...
```

So before writing a comment, see if a better name or a small function would make it unnecessary:

```python
# Before
# check if user can get free shipping
if u.orders > 10 and u.region in EU:

# After
if qualifies_for_free_shipping(u):
```

## Docstrings and type hints

A **docstring** documents a module, class or function for its *callers*. [PEP 257](https://peps.python.org/pep-0257/) sets the basics: a one-line summary in the imperative mood ("Return...", not "Returns..."), then a blank line, then detail.

The following is a documentation sketch, not an implemented retry helper:

```python
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

That's Google style; NumPy and reStructuredText styles are also common. Pick one per project so tools (Sphinx, IDE tooltips) render it consistently.

A good docstring answers what a caller needs and can't see: units, valid ranges, what's raised, side effects, thread-safety, and whether arguments are mutated. It doesn't narrate the implementation.

**Type hints** are documentation that configured static-analysis tools can check. Python does not enforce them at runtime:

```python
def find(users: list[User],
         email: str) -> User | None:
```

The signature alone says the result may be absent, and a suitably configured checker can flag unsafe use in code it checks. Types don't replace docstrings (they can't say "email is compared case-insensitively"), but they remove a whole category of prose that would otherwise go stale.

## The four kinds of documentation

The [Diátaxis](https://diataxis.fr/) framework observes that docs fail when they mix purposes. There are four:

| Type | Reader wants to | Example |
|---|---|---|
| Tutorial | learn by doing | "Build your first app" |
| How-to | solve a problem | "Rotate API keys" |
| Reference | look up facts | Function signatures |
| Explanation | understand why | "How caching works" |

A tutorial that stops to explain design history loses beginners; a reference page padded with narrative is slow to scan. A good **README** is usually a mini-tutorial (what it is, install, a working example in under a minute) plus links to the rest.

## Commit messages: notes for future debuggers

Months later, someone runs `git blame` on a strange line. The commit message is the only explanation they'll get. The widely used conventions:

- A subject line of about **50 characters**, in the imperative ("Fix rounding in VAT total").
- A blank line, then a body wrapped at about **72 characters** that explains **what and why**, not how. The diff already shows how.

```
Cap retry backoff at 30s

Unbounded exponential backoff meant a
client offline for an hour waited 34
minutes after reconnecting. Cap delay at
30s; see INC-482.
```

## Designing APIs for strangers

A public API (a library, an HTTP endpoint, a module others import) is the hardest code to change, because you can't see or fix its callers. Design for the user who reads nothing.

### Make it hard to misuse

```python
# Easy to misuse
resize(img, 800, 600, True, False)

# Hard to misuse
resize(img, width=800, height=600,
       keep_aspect=True)
```

- **Keyword-only arguments** (`*`) for anything a reader couldn't guess from position.
- **Types and enums instead of strings and booleans**: `Align.LEFT`, not `"left"`, which might be misspelt.
- **Make illegal states unrepresentable**: rather than `Order(status="paid", paid_at=None)` being possible, model `PaidOrder` with a required `paid_at` and validate boundary inputs. Python annotations alone still allow an explicitly supplied `None` at runtime.
- **Safe defaults**: TLS verification on, timeouts set. Python's `requests` has *no* default timeout, so a call can hang forever, a well-known pitfall.
- **Principle of least astonishment**: similar operations should behave similarly. If `list.sort()` sorts in place and returns `None`, then a `sorted()` that returns a new list must not also mutate.

### Hyrum's Law

> With a sufficient number of users of an API, it does not matter what you promise in the contract: all observable behaviours of your system will be depended on by somebody.

Hyrum Wright, at Google. If your function happens to return results sorted, someone relies on it. If an error message has a particular wording, someone parses it. Change it and you break them, contract or not.

Defences:

- Expose as little as possible; private by default (`_name`, no re-exports).
- Deliberately avoid accidental guarantees. Go randomises map iteration order partly so that nobody depends on it.
- Return structured errors (codes, fields) so nobody needs to parse messages.

### Versioning and deprecation

[Semantic versioning](https://semver.org/) encodes compatibility in `MAJOR.MINOR.PATCH`. For a declared public API at version 1.0.0 or later:

| Bump | Meaning |
|---|---|
| MAJOR | Incompatible API change |
| MINOR | New, backwards-compatible feature |
| PATCH | Backwards-compatible bug fix |

Versions `0.y.z` are explicitly unstable: anything may change.

To remove something, deprecate first and give users a release cycle or more to move:

```python
import warnings

def fetch(url, timeout=None):
    if timeout is None:
        warnings.warn(
            "timeout will be required "
            "in 3.0",
            DeprecationWarning,
            stacklevel=2,
        )
```

`stacklevel=2` makes the warning point at the *caller's* line, which is the code that needs changing. Note that Python hides `DeprecationWarning` by default unless it is triggered by code in `__main__` (PEP 565) or you run tests or `-W default`; for warnings aimed at end users of an application, `FutureWarning` is shown by default.

For changes across systems you don't deploy together, use **parallel change** (expand and contract): add the new form alongside the old, migrate callers, then remove the old.

### Be careful with "be liberal in what you accept"

Postel's robustness principle ("be conservative in what you send, liberal in what you accept") shaped early internet protocols. RFC 9413 (2023) argues that unchecked tolerance has a cost: once you silently accept malformed input, Hyrum's Law makes that tolerance a compatibility obligation that is costly to remove, and it can hide bugs and security holes. Many modern APIs prefer to **reject invalid input clearly** and evolve through explicit versioning.

## Key takeaways
- Comments should explain why, warn, or reference; they rot, so prefer names and small functions to comments that say what.
- Docstrings tell callers what they can't see (units, ranges, errors, side effects); type hints are documentation that tools check.
- Keep tutorials, how-tos, reference and explanation separate (Diátaxis).
- Commit messages explain what and why for the future debugger; the diff shows how.
- Design public APIs to be hard to misuse: keyword-only arguments, enums, safe defaults, illegal states unrepresentable.
- Hyrum's Law: every observable behaviour will be depended on, so expose little, version with semver, and deprecate with warnings before removing.

## Further reading
- [PEP 257: Docstring Conventions](https://peps.python.org/pep-0257/)
- [Diátaxis: a systematic approach to technical documentation](https://diataxis.fr/)
- [How to Write a Git Commit Message — Chris Beams](https://cbea.ms/git-commit/)
- [Hyrum's Law](https://www.hyrumslaw.com/)
- [Semantic Versioning 2.0.0](https://semver.org/)
- [RFC 9413: Maintaining Robust Protocols](https://www.rfc-editor.org/rfc/rfc9413.html)
- [warnings — Python docs](https://docs.python.org/3/library/warnings.html)
- [A Philosophy of Software Design — John Ousterhout](https://web.stanford.edu/~ouster/cgi-bin/book.php)
