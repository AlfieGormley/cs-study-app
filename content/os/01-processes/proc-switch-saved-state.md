---
id: proc-switch-saved-state
sourceLesson: proc-context-switching
title: "Switching tasks and saving state"
level: advanced
minutes: 4
summary: "A mode switch can return to the same task without scheduling another."
---

A 4-core laptop happily runs 400 processes. Each one behaves as if it had a CPU to itself. The illusion comes from **context switching**: the kernel stops one task, saves everything needed to resume it, loads another task's saved state, and lets that one run. Time-sharing creates concurrency even when only one task can execute on a particular logical CPU at an instant.

Picture a chef cooking four dishes on one hob. To switch dishes they have to note where they were in the recipe, clear the counter, and lay out the other dish's ingredients. Switching is necessary, but every switch is time not spent cooking, and the chef has to re-find everything they had to hand.

## When a switch happens

The kernel switches tasks only when it is already running: on a syscall, an exception or an interrupt. There are two kinds of switch:

- **Voluntary**: the task can't continue. It called `read` on an empty socket, waited on a lock, or called `sleep`. It enters a **blocked state**, and the scheduler picks someone else.
- **Involuntary** (preemption): the task could keep going but the kernel takes the CPU away. Usually the timer interrupt shows its time slice is used up, or a higher-priority task has just woken.

Linux counts both per task. These example counts are illustrative, not a healthy-rate threshold:

```
$ grep ctxt /proc/1234/status
voluntary_ctxt_switches:     84211
nonvoluntary_ctxt_switches:  1093
```

Frequent voluntary switches suggest blocking; frequent involuntary switches suggest preemption. Counts alone do not reveal elapsed time, time spent waiting, or a unique bottleneck.

## Mode switch is not a context switch

These terms are often mixed up:

| Event | What changes |
|---|---|
| Mode switch | user to kernel, same task |
| Thread switch | registers, stack, same address space |
| Process switch | all that plus the address space |

A `getpid` syscall is a *mode switch*: the CPU enters the kernel and returns to the same task. A *context switch* only happens when the kernel decides a *different* task should run next.

## What gets saved and restored

On Linux x86-64 the context-switch code path looks like this:

```
task A running in user mode
  | timer interrupt / blocking syscall
  v
entry code: push A's user registers
            onto A's kernel stack
  |
schedule(): pick next task B
  |
context_switch(A, B):
  switch_mm(): load B's page table
               (write CR3) if B has a
               different address space
  switch_to(): save A's kernel stack
               pointer and callee-saved
               registers; load B's
  |
now on B's kernel stack
  |
return path: pop B's user registers,
             restore FPU/SIMD state
  v
task B running in user mode
```

The state that must move:

- **General-purpose registers**, instruction pointer, stack pointer and flags. Small: a couple of hundred bytes.
- **FPU/SIMD state** (SSE, AVX, AVX-512). Large: the AVX-512 state is over 2 KiB. Saved with the appropriate `XSAVE`-family variant; optimised variants can avoid writing some components. Restore and save details depend on enabled features and the kernel.
- **The address-space root**: on x86 the `CR3` register points at the page-table tree. Loading a new value is what makes the new process's memory appear.
- **Thread-local storage base** (the `FS` register on x86-64), so `errno` and other thread locals point to the right place.
- Kernel bookkeeping: the per-CPU "current task" pointer, accounting of CPU time used.

Each task has its own **kernel stack** (typically 16 KiB on x86-64). That's where its user registers were pushed when it entered the kernel, so they're already "saved" by the time the scheduler runs. `switch_to` just swaps kernel stacks.

> [!note] Threads of the same process
> If A and B are threads in the *same* process, they share page tables. The scheduler need not change to another process's memory map. Translations remain valid, though cache/TLB entries may still be evicted and KPTI may switch page tables on kernel entry/exit. This can avoid work, not guarantee lower total latency.

## Key takeaways
- A mode switch can return to the same task without scheduling another.
- Task switches preserve execution state and may change the active address space.

## Further reading
- [Mechanism: Limited Direct Execution — OSTEP](https://pages.cs.wisc.edu/~remzi/OSTEP/cpu-mechanisms.pdf)
- [Context switch — Wikipedia](https://en.wikipedia.org/wiki/Context_switch)
- [Translation lookaside buffer — Wikipedia](https://en.wikipedia.org/wiki/Translation_lookaside_buffer)
- [Page Table Isolation (PTI) — Linux kernel docs](https://docs.kernel.org/arch/x86/pti.html)
- [proc(5): /proc/pid/status — Linux manual page](https://man7.org/linux/man-pages/man5/proc.5.html)
- [Thread (computing) — Wikipedia](https://en.wikipedia.org/wiki/Thread_(computing))
