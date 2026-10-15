---
id: proc-syscall-vdso-errors
sourceLesson: proc-syscalls
title: "The vDSO and robust I/O"
level: basic
minutes: 3
summary: "Supported vDSO fast paths can read time without entering the kernel."
---

Supported vDSO fast paths can read time without entering the kernel. This lesson focuses on the vdso and robust i/o.

## The vDSO: syscalls without the syscall

Some calls are made constantly but only *read* data the kernel maintains. The classic case is `clock_gettime`: logging libraries, profilers and databases call it millions of times a second.

Linux maps a small shared library called the **vDSO** (virtual dynamic shared object) into every process. It contains user-mode code for a few calls, plus a read-only page of data the kernel keeps updated (the current time base). On x86-64 it provides `clock_gettime`, `gettimeofday`, `time` and `getcpu`.

For example, the mapping can look like this; its addresses vary:

```
$ cat /proc/self/maps | grep vdso
7ffd8a5f2000-7ffd8a5f4000 r-xp ... [vdso]
```

On a supported x86-64 fast path, glibc's `clock_gettime(CLOCK_MONOTONIC, &ts)` uses the vDSO to combine kernel-maintained data with the CPU's timestamp counter in user mode; other architectures and clocksources use different counters or fall back. No mode switch, so it avoids kernel-entry overhead when that clock and clocksource support the fast path.

> [!warning] When the vDSO falls back
> If the system clock source can't be read from user mode (for example some virtual machines using a clock source the vDSO doesn't support), the vDSO quietly falls back to a real syscall. A service that suddenly spends a lot of time in `clock_gettime` after moving to new VMs is a known symptom. Check `/sys/devices/system/clocksource/clocksource0/current_clocksource`.

## Pitfalls

- **Assuming `errno` is always valid.** It's only meaningful when the call reported failure; successful calls may leave junk in it.
- **Ignoring `EINTR`.** A blocking syscall interrupted by a signal handler may return `-1` with `errno == EINTR`. Robust code retries (or uses `SA_RESTART`).
- **Short reads and writes.** `read` can return fewer bytes than asked, for example near EOF or when fewer bytes are currently available on a pipe or socket. Loop until you have what you need.
- **Counting syscalls in hot loops.** A per-request `stat()` or `gettimeofday` (on a system without vDSO support) can dominate a fast server's profile.

## Key takeaways
- Supported vDSO fast paths can read time without entering the kernel.
- Short transfers, interrupted calls and failure-only errno need explicit handling.

## Further reading
- [Mechanism: Limited Direct Execution — OSTEP](https://pages.cs.wisc.edu/~remzi/OSTEP/cpu-mechanisms.pdf)
- [Anatomy of a system call, part 1 — LWN](https://lwn.net/Articles/604287/)
- [Anatomy of a system call, part 2 — LWN](https://lwn.net/Articles/604515/)
- [syscall(2) — Linux manual page](https://man7.org/linux/man-pages/man2/syscall.2.html)
- [vdso(7) — Linux manual page](https://man7.org/linux/man-pages/man7/vdso.7.html)
- [Kernel page-table isolation — Wikipedia](https://en.wikipedia.org/wiki/Kernel_page-table_isolation)
