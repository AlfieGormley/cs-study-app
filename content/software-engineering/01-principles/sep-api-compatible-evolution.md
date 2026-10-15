---
id: sep-api-compatible-evolution
title: Evolve observable API behaviour deliberately
level: advanced
minutes: 3
summary: Users can depend on observable behaviour beyond the written contract.
sourceLesson: sep-writing-for-others
---

Callers and maintainers need a reliable contract. State what they may rely on and preserve the reasons behind a decision.

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
# Attribute the warning to the caller.
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
- Users can depend on observable behaviour beyond the written contract.
- Semantic versions communicate public API compatibility after the unstable initial stage.
- Deprecation warnings need useful attribution, and distributed changes need an expand–migrate–contract plan.

## Further reading
- [www.hyrumslaw.com](https://www.hyrumslaw.com/)
- [semver.org](https://semver.org/)
- [rfc9413](https://www.rfc-editor.org/rfc/rfc9413.html)
- [warnings](https://docs.python.org/3/library/warnings.html)
