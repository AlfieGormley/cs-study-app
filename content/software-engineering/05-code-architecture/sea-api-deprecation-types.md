---
id: sea-api-deprecation-types
sourceLesson: sea-api-design
title: Deprecation, warnings and typed packages
level: advanced
minutes: 4
summary: Migrate callers through a deprecation and make Python library types discoverable.
---

After defining the public surface, defaults, errors and compatibility policy, a library needs a practical path for users to migrate. This unit also covers type-information packaging.

## Deprecating safely

You'll eventually need to remove or change things. Do it in stages:

1. **Add the new way** alongside the old.
2. **Warn** when the old way is used, naming the replacement and the removal version.
3. **Wait** long enough for users to migrate.
4. **Remove** in the next major release.

```python
import warnings

# Distinguish omission from explicit None.
_UNSET = object()

def fetch(url, timeout=_UNSET, **kw):
    if "secs" in kw:
        if timeout is not _UNSET:
            raise TypeError("both supplied")
        warnings.warn(
            "secs= is deprecated; use "
            "timeout=. Removed in 3.0.",
            DeprecationWarning,
            # Attribute warning to our
            # caller.
            stacklevel=2,
        )
        # Consume the deprecated spelling.
        timeout = kw.pop("secs")
    if kw:
        raise TypeError("unknown option")
    if timeout is _UNSET:
        timeout = None
    return timeout  # boundary demo, no I/O
```

`stacklevel=2` makes the warning point at the **caller's** line rather than inside `fetch`, so users can find the code to change.

> [!warning] DeprecationWarning is quiet by default
> In ordinary release builds, Python’s default filters ignore `DeprecationWarning` unless it is attributed to `__main__` (PEP 565). Custom filters and debug builds differ. Test runners such as pytest do show them. Users who don't run tests with warnings visible may never see yours, so also announce deprecations in changelogs and release notes.

Python 3.13 added `@warnings.deprecated` (PEP 702), which also marks the function for static type checkers so editors can flag uses before the code even runs.

How long to wait? CPython's PEP 387 normally requires a deprecation period of at least two years across minor releases and prefers five years, with specified exceptions and additional replacement-support guidance. For an internal library, one or two release cycles plus a search across the company's repositories may be enough.

## Type hints and documentation

Type hints are part of a modern Python API. For a distributed package containing inline types, ship a py.typed marker as described by PEP 561. Stub-only packages and local source checking follow different discovery rules. Document every public function's behaviour, errors raised and stability. Anything not documented as public should be underscore-prefixed, so Hyrum's law has less to grab onto.

## Key takeaways
- Introduce the replacement, warn with a migration path, allow time and remove according to compatibility policy.
- stacklevel=2 attributes a warning to the caller.
- Default warning filters can hide library DeprecationWarning messages, so release notes also matter.
- PEP 702 deprecation metadata supports static tooling as well as runtime warnings.
- Distributed packages with inline types use a py.typed marker; stub-only packages follow separate rules.

## Further reading
- [warnings — Python documentation](https://docs.python.org/3/library/warnings.html)
- [PEP 387 — Backwards Compatibility Policy](https://peps.python.org/pep-0387/)
- [PEP 702 — Marking deprecations](https://peps.python.org/pep-0702/)
- [PEP 561 — Distributing type information](https://peps.python.org/pep-0561/)
