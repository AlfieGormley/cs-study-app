---
id: sepr-debugging
title: Debugging methodically
level: intermediate
minutes: 12
summary: Debugging as the scientific method - reproduce, minimise, binary-search the cause with tools like git bisect and pdb, fix the cause rather than the symptom, and handle the nasty cases such as heisenbugs.
---

Debugging can consume substantial engineering time. The usual approach is to stare at the code, guess, change something, and rerun. Sometimes it works. When it does not, you can lose a day.

Methodical debugging replaces guessing with a process. A structured investigation can reduce wasted experiments; its benefit depends on the problem.

## Debugging is the scientific method

A bug is a gap between what you expect the program to do and what it actually does. Somewhere, one of your beliefs about the system is false. Debugging is finding which one.

The loop:

1. **Observe**: gather facts. What exactly happens? What did you expect?
2. **Hypothesise**: propose a specific cause. "The cache returns a stale price after an update."
3. **Predict**: if that is true, what else must be true? "Clearing the cache should fix it; the database row should be correct."
4. **Test**: run the experiment that would *disprove* the hypothesis.
5. **Conclude**: keep or discard it, and loop.

Two habits make this work. First, **change one thing at a time**, to make the effect easier to attribute. Second, **write things down**: hypotheses tried, results, commands run. After two hours you will not remember whether you tested with the cache off.

David Agans' book *Debugging* condenses this into nine rules worth memorising: understand the system; make it fail; quit thinking and look; divide and conquer; change one thing at a time; keep an audit trail; check the plug; get a fresh view; and if you didn't fix it, it ain't fixed.

## Step 1: reproduce it

A reliable reproduction provides strong evidence for evaluating a fix; without one, confidence must come from other evidence and remains harder to establish. Aim for a reproduction that is:

- **Reliable**: fails every time, or at a known rate.
- **Fast**: seconds, not a 20-minute deploy.
- **Automated**: ideally a failing test.

Collect everything: the exact error message, the full stack trace, inputs, versions, environment and time. "It's broken" is not a bug report; "POST /orders with an empty basket returns 500 since Tuesday's deploy" is.

### Read the stack trace properly

Python prints frames oldest first and says so: `Traceback (most recent call last)`. The bottom line is the exception; the frame just above it is where it was raised. Work upwards to find the first frame in *your* code, which is usually where the wrong value came from or was passed in.

```
Traceback (most recent call last):
  File "app.py", line 30, in handle
    total = order_total(basket)
  File "pricing.py", line 12, in order_total
    return sum(i.price for i in items) / n
ZeroDivisionError: division by zero
```

Here the crash is in `order_total`, but the real question is why `n` was zero, and whether `handle` should have rejected an empty basket before calling it.

## Step 2: minimise it

A bug that appears with a 3 MB input file and 40 config flags is hard to reason about. Shrink it: remove half the input; if it still fails, keep the smaller version; if not, try the other half. If neither half fails, test smaller removals from the original failing input; an interaction may require pieces from both halves. Continue until no individual remaining piece can be removed while preserving the failure.

This is **delta debugging**, formalised by Andreas Zeller, and tools automate it. Property-based testing libraries like Hypothesis do the same thing automatically, "shrinking" a failing random input toward simpler cases that still fail; shrinking does not guarantee the globally smallest case.

A minimal reproduction often makes the cause obvious. It also makes a perfect regression test.

## Step 3: localise it by binary search

When you do not know where the bug is, halve the search space with each experiment. In an ideal binary search, 20 yes/no tests distinguish roughly a million candidates. Arbitrary code, configuration interactions and non-monotonic failures need not provide such a partitioning oracle.

You can binary-search almost anything:

- **Code path**: log or assert at the midpoint of the pipeline. Is the value already wrong there?
- **Data**: does it fail on the first half of the records or the second?
- **Configuration**: revert half the changed settings.
- **History**: which commit introduced it?

### git bisect

If something used to work, `git bisect` finds the commit that broke it by binary search over history.

```
git bisect start
git bisect bad HEAD
git bisect good v2.3.0
# git checks out a midpoint commit;
# test it, then mark it:
git bisect good    # or: git bisect bad
# ...repeat until git names the commit
git bisect reset
```

For a linear history with one deterministic good-to-bad transition and no skipped commits, N candidate commits need about log2(N) tests. Merges, flaky tests, reversions and untestable commits complicate this bound. For 1,000 commits that is about 10 tests, since 2^10 = 1,024.

Better still, automate it with a script whose exit code tells git the answer:

```
git bisect run pytest tests/test_tax.py
```

Exit code 0 means good, 1 to 127 (except 125) means bad, and **125** means "cannot test this commit, skip it" (for example, when it does not build). With pytest, exit codes for interruption, internal errors, usage errors or no collected tests must not be interpreted as evidence of the target regression. Use a wrapper that maps an untestable revision to 125 or aborts the run, and returns 1 only for the relevant test failure.

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
    tags.append(tag)
    return tags

add_tag("a")   # ['a']
add_tag("b")   # ['a', 'b']  !
```

> [!warning] Symptom versus cause
> The symptom (a list "remembering" earlier values) looks like a caching bug. Knowing the language's evaluation rules finds it in seconds. The fix is `tags=None`, then `if tags is None: tags = []` inside the function.

## The hard cases

### Heisenbugs

A **heisenbug** changes or disappears when you try to observe it. Adding a print or attaching a debugger alters timing, so a race condition stops happening. Typical causes are concurrency (data races, unsynchronised shared state), uninitialised memory in C and C++, and timing-dependent code.

Approaches:

- Use tools built for the job: ThreadSanitizer for supported C/C++ toolchains detects data races; AddressSanitizer detects classes of memory-safety errors. Go offers `-race` on supported platforms. Rust sanitizer support depends on the toolchain and target; none of these detects every bug.
- Increase the failure rate: run the test 10,000 times in a loop, add load, or insert deliberate sleeps to widen race windows.
- Consider a bounded, thread-safe in-memory event buffer to reduce synchronous I/O, while recognising that any instrumentation can alter timing.

### "Works on my machine"

The code is the same, so something else differs. Diff the environments methodically: dependency versions (compare lock files), OS and architecture, environment variables, configuration, locale and time zone, data, and file system case-sensitivity (macOS is usually case-insensitive, Linux is not). Containers reduce this class of bug by making environments reproducible.

### Bugs only in production

You cannot attach a debugger to production easily, so you rely on what the system already records: structured logs with a request or trace ID, metrics, and traces. Correlate by time ("what changed at 14:05?"). Recent deploys and config changes are useful initial hypotheses; correlate them with evidence rather than assuming that a recent change caused the failure.

## Pitfalls

- **Shotgun debugging**: changing several things at once until it works. You learn nothing and may introduce new bugs.
- **Trusting assumptions.** "That function can't return `None`." Check it. Agans' "check the plug" rule: is the service you are testing the one you changed? Is the config file the one being loaded?
- **Stopping at the first plausible cause.** Confirm it: turn the bug off and on again by reverting and reapplying the fix.
- **Not asking for help.** Explaining the problem to someone (or to a rubber duck) forces you to state your assumptions, and the faulty one often jumps out. After an hour stuck, get a fresh view.

## Key takeaways
- Debugging is the scientific method: observe, hypothesise, predict, test, and change one thing at a time.
- Get a reliable, fast, ideally automated reproduction first, then minimise it.
- Binary-search the cause in code, data, config or history; `git bisect run` automates a roughly logarithmic search under deterministic, monotonic history assumptions.
- Use debuggers, conditional breakpoints and post-mortem mode; read stack traces from the bottom up.
- Fix the root cause with a regression test, look for siblings, and make sure you can explain the fix.

## Further reading
- [git-bisect documentation — Git](https://git-scm.com/docs/git-bisect)
- [pdb — The Python Debugger](https://docs.python.org/3/library/pdb.html)
- [Delta debugging — Wikipedia](https://en.wikipedia.org/wiki/Delta_debugging)
- [Heisenbug — Wikipedia](https://en.wikipedia.org/wiki/Heisenbug)
- [Rubber duck debugging — Wikipedia](https://en.wikipedia.org/wiki/Rubber_duck_debugging)
