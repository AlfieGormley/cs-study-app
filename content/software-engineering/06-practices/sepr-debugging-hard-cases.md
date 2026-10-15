---
id: sepr-debugging-hard-cases
title: Investigate timing and environment bugs
level: intermediate
minutes: 3
summary: Handle heisenbugs, environment drift and production-only failures without confusing correlation for cause.
sourceLesson: sepr-debugging
---

Some failures resist a deterministic reproduction. Keep the same observe–hypothesise–test discipline, but make uncertainty and the failure rate explicit.

## The hard cases
### Heisenbugs

A **heisenbug** changes or disappears when you try to observe it. Adding a print or attaching a debugger alters timing, so a race condition stops happening. Typical causes are concurrency (data races, unsynchronised shared state), uninitialised memory in C and C++, and timing-dependent code.

Approaches:

- Use tools built for the job: ThreadSanitizer for supported C/C++ toolchains detects data races; AddressSanitizer detects classes of memory-safety errors. Go offers `-race` on supported platforms. Rust sanitizer support depends on the toolchain and target; none of these detects every bug.
- Increase the failure rate: run the test 10,000 times in a loop, add load, or insert deliberate sleeps to widen race windows.
- Consider a bounded, thread-safe in-memory event buffer to reduce synchronous I/O, while recognising that any instrumentation can alter timing.

### "Works on my machine"

The code is the same, so something else differs. Diff the environments methodically: dependency versions (compare lock files), OS and architecture, environment variables, configuration, locale and time zone, data, and file system case-sensitivity (default macOS volumes are commonly case-insensitive, while common Linux configurations are case-sensitive; inspect the actual mounted volume). Containers reduce this class of bug by making environments reproducible.

### Bugs only in production

You cannot attach a debugger to production easily, so you rely on what the system already records: structured logs with a request or trace ID, metrics, and traces. Correlate by time ("what changed at 14:05?"). Recent deploys and config changes are useful initial hypotheses; correlate them with evidence rather than assuming that a recent change caused the failure.

## Pitfalls
- **Shotgun debugging**: changing several things at once until it works. You learn nothing and may introduce new bugs.
- **Trusting assumptions.** "That function can't return `None`." Check it. Agans' "check the plug" rule: is the service you are testing the one you changed? Is the config file the one being loaded?
- **Stopping at the first plausible cause.** Confirm it: turn the bug off and on again by reverting and reapplying the fix.
- **Not asking for help.** Explaining the problem to someone (or to a rubber duck) forces you to state your assumptions, and the faulty one often jumps out. After an hour stuck, get a fresh view.

## Key takeaways
- Instrumentation can change timing; a disappearing failure is not evidence of a repair.
- Compare versions, configuration, data, locale and platform when environments disagree.
- Use logs tied together by request identifiers, metrics and traces in production, then test hypotheses one at a time.

## Further reading
- [ThreadSanitizer — Clang](https://clang.llvm.org/docs/ThreadSanitizer.html)
- [AddressSanitizer — Clang](https://clang.llvm.org/docs/AddressSanitizer.html)
- [Data race detector — Go](https://go.dev/doc/articles/race_detector)
- [Traces — OpenTelemetry](https://opentelemetry.io/docs/concepts/signals/traces/)
