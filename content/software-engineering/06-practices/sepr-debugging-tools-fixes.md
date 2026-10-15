---
id: sepr-debugging-tools-fixes
title: Inspect state and fix the cause
level: intermediate
minutes: 3
summary: Use debugger stops and regression tests to explain and repair a failure.
sourceLesson: sepr-debugging
---

After reproducing and localising a failure, inspect actual values. A debugger and a small failing test help distinguish the cause from a plausible patch.

## Tools: print, logs and debuggers
**Print debugging** is fine. It is quick, works everywhere, and leaves a trail. Use `logging` rather than `print` for anything that may stay, and print `repr()` so you can tell `"1"` from `1` and spot trailing whitespace.

A **debugger** lets you stop the program and inspect everything without recompiling or adding prints. In Python, put `breakpoint()` (Python 3.7+) where you want to stop:

| pdb command | Does |
|---|---|
| `n` | Next line (step over) |
| `s` | Step into a call |
| `c` | Continue to next breakpoint |
| `p expr` | Print an expression |
| `w` | Where: show the stack |
| `u` / `d` | Move up / down the stack |
| `b file:line, cond` | Conditional breakpoint |

**Post-mortem debugging** is underused. Run `python -m pdb script.py`, then enter `c` at the initial stop; after an uncaught exception, you land in the frame that raised, with every local variable available. In a REPL, `import pdb; pdb.pm()` does the same after an exception.

Conditional breakpoints filter execution stops: `b pricing.py:12, n == 0` stops only on the bad iteration out of thousands.

## Step 4: fix the cause, not the symptom
Once you have found the bad line, resist the quickest patch. Ask *why* the value was wrong.

1. **Write a failing test** that reproduces the bug.
2. **Fix the root cause.** If an empty basket should be impossible, reject it at the boundary, rather than adding `if n == 0: return 0` deep inside pricing.
3. **Watch the test pass**, and run the full suite.
4. **Look for siblings.** The same mistake is often made in several places. Search for the pattern.
5. **Explain it.** If you cannot say why the bug happened and why the fix works, you have probably found a coincidence. "If you didn't fix it, it ain't fixed."

### Example: a classic Python trap

Default arguments are evaluated once, when the function is defined, so a mutable default is shared between calls.

```python
def add_tag(tag, tags=[]):
    # Mutates the shared default list.
    tags.append(tag)
    return tags

# These calls return lists; a script
# does not display returned values.
add_tag("a")   # returns ['a']
add_tag("b")   # returns ['a', 'b']
```

> [!warning] Symptom versus cause
> The symptom (a list "remembering" earlier values) looks like a caching bug. Knowing the language's evaluation rules finds it in seconds. The fix is `tags=None`, then `if tags is None: tags = []` inside the function.

## Key takeaways
- A conditional breakpoint stops at the interesting state rather than every iteration.
- Post-mortem debugging inspects the failure frame after an uncaught exception.
- A fix should satisfy the intended rule, pass its regression test and address similar mistakes.

## Further reading
- [pdb — The Python Debugger](https://docs.python.org/3.14/library/pdb.html)
- [Default argument values — Python tutorial](https://docs.python.org/3/tutorial/controlflow.html#default-argument-values)
