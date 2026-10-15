---
id: sea-api-signatures
sourceLesson: sea-api-design
title: Small APIs and clear signatures
level: advanced
minutes: 3
summary: Design a focused interface and use keyword-only and positional-only parameters deliberately.
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

The first call below illustrates an older positional API, assuming a message and an existing send implementation. The keyword-only definition that follows is its replacement, with its body omitted for the signature example.

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

Bare booleans and numbers in positional arguments are the "boolean trap": nobody can tell what `True, False` means. Keyword-only arguments allow reordering without changing ordinary keyword calls. Adding optional arguments can preserve existing behavior; required additions, subclasses, wrappers and introspection need an API compatibility review.

### Positional-only arguments

```python
def clamp(x, lo, hi, /):
    # Bound x to the supplied lower/upper
    # limits.
    return max(lo, min(x, hi))
```

Parameters before `/` (PEP 570, Python 3.8) can't be passed by name. That sounds restrictive, but it means you are free to **rename** them later: nobody can have written `clamp(x=5, ...)`. Many built-ins work this way.

## Key takeaways
- Every public name becomes a maintenance promise.
- Make the common case simple and call sites easy to read.
- Keyword-only options avoid ambiguous positional booleans.
- Positional-only parameters keep names out of ordinary calls; documented introspection and wrappers still matter.

## Further reading
- [PEP 3102 — Keyword-Only Arguments](https://peps.python.org/pep-3102/)
- [PEP 570 — Positional-Only Parameters](https://peps.python.org/pep-0570/)
- [Published Interface — Martin Fowler](https://martinfowler.com/bliki/PublishedInterface.html)
