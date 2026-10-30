---
id: sep-narrow-handlers-races
title: Catch the intended operation and handle races
level: advanced
minutes: 3
summary: Catch only exceptions you understand at a scope where you can respond.
sourceLesson: sep-error-handling
---

Failure handling is part of a function’s contract. Keep the happy path clear while making each exceptional outcome deliberate.

### Catch narrowly

```python
# Any failure here is silently discarded.
# Dangerous
try:
    user = repo.get(uid)
    send(user.email)
except:
    pass
```

A bare `except:` catches `BaseException`, which includes `KeyboardInterrupt` and `SystemExit`, so it can swallow an interruption or exit raised inside that protected suite. It also hides typos (`NameError`), bugs (`AttributeError`) and genuine failures alike. `except Exception:` is only a little better.

Catch the specific exceptions you expect and can do something about. Let everything else propagate to a top-level handler that logs and reports it.

Keep the protected operation narrow. For example, catch `KeyError` around the cache lookup alone; if the same `try` also reads an email field, that unrelated missing key can be mistaken for a cache miss. Code in `else` is outside the cache-lookup handlers. If a missing record is reloaded in `except` and both paths must send, place the send after the whole `try`/`except`; an else-only send would skip the reload path.

### EAFP and LBYL

Python style favours **EAFP** ("easier to ask forgiveness than permission") over **LBYL** ("look before you leap"):

```python
# Existence can change before open runs.
# LBYL: race between check and use
if os.path.exists(p):
    with open(p) as f: ...

# EAFP: just try it
try:
    with open(p) as f: ...
except FileNotFoundError:
    ...
```

The LBYL version has a **time-of-check to time-of-use** (TOCTOU) race: the file can disappear between `exists` and `open`. For this file-opening case, attempting `open` and handling its actual outcome avoids trusting a stale existence check. This is not a complete defence against malicious path replacement: security-sensitive code may also need directory-relative operations and appropriate symlink handling.

> [!analogy] Real-world analogy: a parking space seen from the corner
> You spot an empty parking space from the end of the street, drive round the block, and find someone has taken it. Seeing it free did not reserve it.
>
> **How it maps:** Spotting the space is the existence check (`os.path.exists`); parking is the use (`open`). In between, another driver (another process) changed the state, so the check was stale. The reliable approach is to try to park and deal with "taken" when it happens: attempt the operation and handle its failure.
>
> **Where it stops:** A driver can at least see the other car arrive; a program usually cannot see the change. And an attacker may swap a file on purpose, which needs the further defences mentioned above.

## Key takeaways
- Catch only exceptions you understand at a scope where you can respond.
- A broad try suite can mistake an unrelated lookup failure for the expected one.
- Checking existence does not reserve a file; attempt the operation and handle its actual outcome.

## Further reading
- [Python tutorial: Errors and Exceptions](https://docs.python.org/3/tutorial/errors.html)
- [Python glossary: EAFP](https://docs.python.org/3/glossary.html#term-EAFP)
