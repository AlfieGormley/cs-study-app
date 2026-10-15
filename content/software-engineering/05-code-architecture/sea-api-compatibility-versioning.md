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

## Key takeaways
- Callers can depend on any observable behavior, including error text.
- SemVer patch releases fix compatibly, minor releases add compatibly and major releases change incompatibly.
- Initial-development 0.y.z versions have no SemVer stability promise unless the project adds one.
- Defaults, keyword names, return types and exceptions are compatibility concerns.
- Calendar versioning conveys release timing rather than compatibility.

## Further reading
- [Hyrum’s Law — Hyrum Wright](https://www.hyrumslaw.com/)
- [Semantic Versioning 2.0.0](https://semver.org/)
- [Go language specification](https://go.dev/ref/spec)
- [Python 3.7: dictionary insertion order](https://docs.python.org/3/whatsnew/3.7.html)
