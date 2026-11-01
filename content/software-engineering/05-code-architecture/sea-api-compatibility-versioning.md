---
id: sea-api-compatibility-versioning
sourceLesson: sea-api-design
title: Observable behavior and versioning
level: advanced
minutes: 4
summary: Apply Hyrum’s law and SemVer to Python API changes, including initial-development versions.
---

Earlier units treated signatures, defaults and exceptions as promises. This unit asks what happens when those promises—or other observable behaviors—change.

## Hyrum's law

> With a sufficient number of users of an API, it does not matter what you promise in the contract: all observable behaviors of your system will be depended on by somebody.

Hyrum Wright, a Google engineer, named this after years of large-scale changes at Google. Examples:

- Code that parses your error *message text* breaks when you fix a typo.
- Tests that assert on the iteration order of a set break when the hash function changes.
- In CPython 3.6, dicts happened to preserve insertion order, and the release notes warned that this was an implementation detail that "should not be relied upon". Python 3.7 then made insertion order an official part of the language.

What to do about it:

- Keep observable surface small: fewer public names, fewer documented fields.
- Make unspecified behaviour visibly unspecified. Before Go 1, map iteration order was undefined but in practice differed between hardware platforms, so a test that relied on it could always pass on one machine and fail on another. Go 1 made the order deliberately unpredictable, even between two loops over the same map, so such code breaks early in testing instead.
- Treat *any* behaviour change as potentially breaking for someone, and release accordingly.

## Versioning

**Semantic Versioning** (SemVer) encodes compatibility in the number `MAJOR.MINOR.PATCH`:

| Bump | When |
|---|---|
| PATCH 1.4.2 → 1.4.3 | Backwards-compatible bug fix |
| MINOR 1.4.3 → 1.5.0 | Backwards-compatible addition |
| MAJOR 1.5.0 → 2.0.0 | Incompatible change |

Versions `0.y.z` are for initial development: "anything MAY change at any time" and the public API should not be considered stable. A project can promise more in its own documentation, but SemVer itself doesn't.

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

## Key takeaways
- Callers can depend on any observable behavior, including error text.
- SemVer patch releases fix compatibly, minor releases add compatibly and major releases change incompatibly.
- Initial-development 0.y.z versions have no SemVer stability promise unless the project adds one.
- Defaults, keyword names, return types and exceptions are compatibility concerns.
- Calendar versioning conveys release timing rather than compatibility.

## Further reading
- [Hyrum’s Law — Hyrum Wright](https://www.hyrumslaw.com/)
- [Semantic Versioning 2.0.0](https://semver.org/)
- [Go 1 release notes: iterating in maps](https://go.dev/doc/go1#iteration)
- [Python 3.7: dictionary insertion order](https://docs.python.org/3/whatsnew/3.7.html)
