---
id: sea-api-design
title: API and library design
level: advanced
minutes: 15
summary: Designing interfaces other code depends on, from Python signatures, defaults, errors and return types to Hyrum's law, semantic versioning, what counts as a breaking change and how to deprecate safely.
---

Inside your own module you can rename anything and fix every caller in one commit. Once other teams, or the whole internet, call your code, that freedom disappears. Every function signature, exception type and default becomes a promise. This lesson is about making promises you can keep.

The ideas apply to Python libraries, internal packages shared between teams and the public interface of each module in a modular monolith. (HTTP API design for services is covered in the System Design subject; most of the same principles carry over.)

## Principles

Joshua Bloch's well-known talk *How to Design a Good API and Why it Matters* lists "easy to use" and "hard to misuse" among the marks of a good API. Scott Meyers put it as: make interfaces **easy to use correctly and hard to use incorrectly**. A few consequences:

- **When in doubt, leave it out.** You can always add a function later; removing one breaks someone. Every public name is a maintenance commitment.
- **Make the common case trivial.** `requests.get(url)` covers most needs in one call. Sessions, adapters and hooks are there when you need them. This is **progressive disclosure**.
- **Be consistent.** If one function takes `(src, dst)`, don't make its sibling take `(dst, src)`.
- **Name things for callers, not implementers.** `client.charge(amount)` beats `client.execute_txn_v2(payload)`.

## Signatures that prevent mistakes

### Keyword-only arguments

```python
# Hard to read at the call site:
send(msg, True, False, 30)

# Better: everything after * is
# keyword-only (PEP 3102)
def send(msg, *, urgent=False,
         retry=True, timeout=30):
    ...

send(msg, urgent=True, timeout=10)
```

Bare booleans and numbers in positional arguments are the "boolean trap": nobody can tell what `True, False` means. Keyword-only arguments allow reordering without changing ordinary keyword calls. Adding optional arguments can preserve existing behavior; required additions, subclasses, wrappers and introspection need compatibility checks.

### Positional-only arguments

```python
def clamp(x, lo, hi, /):
    return max(lo, min(x, hi))
```

Parameters before `/` (PEP 570, Python 3.8) can't be passed by name. That sounds restrictive, but it means you are free to **rename** them later: nobody can have written `clamp(x=5, ...)`. Many built-ins work this way.

### Defaults and the mutable default trap

```python
def tag(item, tags=[]):
    tags.append(item)
    return tags

print(tag("a"))
print(tag("b"))
```

This prints `['a']` and then `['a', 'b']`. The default list is created **once**, when the function is defined, and shared by every call. Use `None` and create a fresh object inside:

```python
def tag(item, tags=None):
    if tags is None:
        tags = []
    tags.append(item)
    return tags
```

Choose defaults that are **safe**: verify TLS certificates by default, set a finite timeout, don't delete without confirmation. (`requests` has no default timeout, which is why a forgotten `timeout=` can hang a worker forever, so callers should choose explicit connect/read timeouts and any required overall deadline.)

### Accept general, return specific

Accept the broadest type that works (any iterable, any mapping, a `Protocol`) and return a concrete, documented type. A function that returns a `list` on success, `None` on "no results" and a `dict` on error forces every caller to branch on type. Return an empty list for "nothing", and raise for errors.

## Errors are part of the API

Callers write `except` clauses against your exception types, so design them:

```python
class PaymentError(Exception):
    """Base for all errors we raise."""

class CardDeclined(PaymentError):
    def __init__(self, code):
        super().__init__(code)
        self.code = code

class GatewayTimeout(PaymentError):
    pass
```

- A single **base exception** lets callers catch the expected library errors placed under that hierarchy. Programmer errors and unrelated exceptions may still propagate.
- **Specific subclasses** let them handle cases differently (apply a safe idempotent retry policy for an uncertain timeout, show an appropriate message for a decline).
- **Don't leak implementation exceptions.** If you raise `psycopg.OperationalError` today, you can never switch database drivers without breaking callers. Translate it into a semantically appropriate library error and preserve chaining. Do not label every OperationalError a timeout; failures such as unavailable storage or invalid connection settings differ.

## Hyrum's law

> With a sufficient number of users of an API, it does not matter what you promise in the contract: all observable behaviors of your system will be depended on by somebody.

Hyrum Wright, a Google engineer, named this after years of large-scale changes at Google. Examples:

- Code that parses your error *message text* breaks when you fix a typo.
- Tests that assert on the iteration order of a set break when the hash function changes.
- In CPython 3.6, dicts happened to preserve insertion order as an implementation detail. Python 3.7 subsequently made insertion order a language guarantee; this fact alone does not establish a single historical cause for the decision.

What to do about it:

- Keep observable surface small: fewer public names, fewer documented fields.
- Make unspecified behaviour visibly unspecified. Go randomises map iteration order deliberately to discourage reliance on one stable order; this does not logically prevent callers from depending on observed behavior.
- Treat *any* behaviour change as potentially breaking for someone, and release accordingly.

## Versioning

**Semantic Versioning** (SemVer) encodes compatibility in the number `MAJOR.MINOR.PATCH`:

| Bump | When |
|---|---|
| PATCH 1.4.2 → 1.4.3 | Backwards-compatible bug fix |
| MINOR 1.4.3 → 1.5.0 | Backwards-compatible addition |
| MAJOR 1.5.0 → 2.0.0 | Incompatible change |

Versions `0.y.z` are for initial development: "anything may change at any time". SemVer itself does not promise public-API stability during 0.x. Projects can document stricter compatibility policies; no particular maintainer motive or prevalence is inferred here.

Some projects use **calendar versioning** instead (pip uses `YY.N`, such as 24.0). CalVer says *when* a release happened, not how compatible it is.

### What counts as breaking in Python?

More than people think:

| Change | Breaking? |
|---|---|
| Add an optional keyword arg | No |
| Add a required argument | Yes |
| Rename a keyword-capable param | Yes |
| Change a default value | Usually |
| Raise a new exception type | Often |
| Return a tuple instead of a list | Yes |
| Remove a public name | Yes |
| Add a new function | No |

Changing a default is behaviour change for every caller who relied on it. Raising a new exception type breaks callers whose `except` clause no longer matches. Hyrum's law says even the "No" rows can break somebody; SemVer is about the *documented* contract.

## Deprecating safely

You'll eventually need to remove or change things. Do it in stages:

1. **Add the new way** alongside the old.
2. **Warn** when the old way is used, naming the replacement and the removal version.
3. **Wait** long enough for users to migrate.
4. **Remove** in the next major release.

```python
import warnings

_UNSET = object()

def fetch(url, timeout=_UNSET, **kw):
    if "secs" in kw:
        if timeout is not _UNSET:
            raise TypeError("both supplied")
        warnings.warn(
            "secs= is deprecated; use "
            "timeout=. Removed in 3.0.",
            DeprecationWarning,
            stacklevel=2,
        )
        timeout = kw.pop("secs")
    if kw:
        raise TypeError("unknown option")
    if timeout is _UNSET:
        timeout = None
    return timeout  # boundary demo, no I/O
```

`stacklevel=2` makes the warning point at the **caller's** line rather than inside `fetch`, so users can find the code to change.

> [!warning] DeprecationWarning is quiet by default
> Python ignores `DeprecationWarning` unless it's triggered by code in `__main__` (PEP 565). Test runners such as pytest do show them. Users who don't run tests with warnings visible may never see yours, so also announce deprecations in changelogs and release notes.

Python 3.13 added `@warnings.deprecated` (PEP 702), which also marks the function for static type checkers so editors can flag uses before the code even runs.

How long to wait? CPython's PEP 387 normally requires a deprecation period of at least two years across minor releases and prefers five years, with specified exceptions and additional replacement-support guidance. For an internal library, one or two release cycles plus a search across the company's repositories may be enough.

## Type hints and documentation

Type hints are part of a modern Python API. For a distributed package containing inline types, ship a py.typed marker as described by PEP 561. Stub-only packages and local source checking follow different discovery rules. Document every public function's behaviour, errors raised and stability. Anything not documented as public should be underscore-prefixed, so Hyrum's law has less to grab onto.

## Key takeaways
- Design APIs to be easy to use correctly and hard to misuse; you can always add, but removing breaks people.
- Use keyword-only arguments for options, positional-only where names are an implementation detail, and safe, immutable defaults.
- Exceptions are part of the contract: a base class, specific subclasses, and no leaked implementation exceptions.
- Hyrum's law: every observable behaviour gets depended on, so keep the surface small.
- SemVer signals compatibility; in Python, renamed params, new required args, changed defaults and new exception types can all be breaking.
- Deprecate in stages with `DeprecationWarning` and `stacklevel=2`, and give users time.

## Further reading
- [Hyrum's Law](https://www.hyrumslaw.com/)
- [Semantic Versioning 2.0.0](https://semver.org/)
- [PEP 387 — Backwards Compatibility Policy](https://peps.python.org/pep-0387/)
- [PEP 3102 — Keyword-Only Arguments](https://peps.python.org/pep-3102/)
- [PEP 570 — Python Positional-Only Parameters](https://peps.python.org/pep-0570/)
- [warnings — Python documentation](https://docs.python.org/3/library/warnings.html)
- [Published Interface — Martin Fowler](https://martinfowler.com/bliki/PublishedInterface.html)
