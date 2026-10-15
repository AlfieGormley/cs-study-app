---
id: pattern-subsystem-facades
title: Facades over complex subsystems
level: intermediate
minutes: 3
sourceLesson: pattern-structural
summary: A facade provides the common operation over a more capable subsystem.
---

## Facade pattern

### The problem

A subsystem has many classes and steps. Most callers want one common task done simply.

### The structure

```
 Client ---> Facade
             +do_task()
               |   |   |
               v   v   v
             [A]  [B]  [C]  subsystem
```

The subsystem stays available for callers who need the full power.

### In Python

```python
import subprocess

# Capture stdout rather than printing it
# directly from the child process.
result = subprocess.run(
    ["echo", "hi"],
    capture_output=True, text=True)
print(result.stdout.strip())
# hi
```

`subprocess.run` is a facade over `Popen`: it starts the process, wires up pipes, waits, collects output and returns one result object. When you need streaming or bidirectional pipes, you drop down to `Popen` directly.

### When not to use it

- When the facade becomes a **god object** that every feature is bolted onto. A facade should cover the common case, not everything.
- When it hides options that callers genuinely need, forcing them round it in awkward ways.

### In real libraries

- **requests**: `requests.get(url)` creates a session, picks an adapter, manages the connection pool, follows redirects and returns a Response. Text decoding and JSON parsing are accessed through the response API; a one-shot call does not share a persistent session pool across unrelated calls.
- **`subprocess.run`** over `Popen`; **`shutil.copytree`** over `os` and file operations.
- **SLF4J** stands for *Simple Logging Facade for Java*.

## Key takeaways
- A facade provides the common operation over a more capable subsystem.
- Callers can still use the lower-level API when they need finer control.
- Keep a facade focused instead of letting every unrelated responsibility accumulate in it.

## Further reading
- [subprocess — Python documentation](https://docs.python.org/3/library/subprocess.html)
- [Advanced usage — Requests documentation](https://requests.readthedocs.io/en/latest/user/advanced/)
