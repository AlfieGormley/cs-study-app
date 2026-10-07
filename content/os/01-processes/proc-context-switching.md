---
id: proc-context-switching
title: Context switching
level: advanced
minutes: 13
summary: How the kernel pauses one task and resumes another, exactly what state is saved, what a switch costs directly and through caches and the TLB, and a first look at user versus kernel threads.
---

A 4-core laptop happily runs 400 processes. Each one behaves as if it had a CPU to itself. The illusion comes from **context switching**: the kernel stops one task, saves everything needed to resume it, loads another task's saved state, and lets that one run. Done hundreds or thousands of times a second, it looks like parallelism.

Picture a chef cooking four dishes on one hob. To switch dishes they have to note where they were in the recipe, clear the counter, and lay out the other dish's ingredients. Switching is necessary, but every switch is time not spent cooking, and the chef has to re-find everything they had to hand.

## When a switch happens

The kernel switches tasks only when it is already running: on a syscall, an exception or an interrupt. There are two kinds of switch:

- **Voluntary**: the task can't continue. It called `read` on an empty socket, waited on a lock, or called `sleep`. It **blocks**, and the scheduler picks someone else.
- **Involuntary** (preemption): the task could keep going but the kernel takes the CPU away. Usually the timer interrupt shows its time slice is used up, or a higher-priority task has just woken.

Linux counts both per task:

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

On Linux x86-64 the path looks like this:

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
- **FPU and SIMD registers** (SSE, AVX, AVX-512). Large: the AVX-512 state is over 2 KiB. Saved with `XSAVE`-family instructions, which skip parts that haven't been used.
- **The address-space root**: on x86 the `CR3` register points at the page-table tree. Loading a new value is what makes the new process's memory appear.
- **Thread-local storage base** (the `FS` register on x86-64), so `errno` and other thread locals point to the right place.
- **Kernel bookkeeping**: the per-CPU "current task" pointer, accounting of CPU time used.

Each task has its own **kernel stack** (typically 16 KiB on x86-64). That's where its user registers were pushed when it entered the kernel, so they're already "saved" by the time the scheduler runs. `switch_to` just swaps kernel stacks.

> [!note] Threads of the same process
> If A and B are threads in the *same* process, they share page tables. The scheduler need not change to another process's memory map. Translations remain valid, though cache/TLB entries may still be evicted and KPTI may switch page tables on kernel entry/exit. This can avoid work, not guarantee lower total latency.

## The direct cost

> [!note] Content gap: timing benchmarks
> No reproducible benchmark establishes universal context-switch, cache, memory-access or goroutine-switch times here. Those timing claims are omitted. Numerical exercises below use explicit hypothetical costs. A classic method is two processes bouncing a byte through a pair of pipes:

```c
#include <stdio.h>
#include <time.h>
#include <unistd.h>
#define N 100000

int main(void) {
    int a[2], b[2];
    char c = 'x';
    pipe(a);
    pipe(b);
    if (fork() == 0) {
        for (int i = 0; i < N; i++) {
            read(a[0], &c, 1);
            write(b[1], &c, 1);
        }
        _exit(0);
    }
    struct timespec t0, t1;
    clock_gettime(CLOCK_MONOTONIC, &t0);
    for (int i = 0; i < N; i++) {
        write(a[1], &c, 1);
        read(b[0], &c, 1);
    }
    clock_gettime(CLOCK_MONOTONIC, &t1);
    double ns =
        (t1.tv_sec - t0.tv_sec) * 1e9 +
        (t1.tv_nsec - t0.tv_nsec);
    /* Includes IPC and syscall overhead. */
    printf("%.0f ns/half-trip\n", ns/N/2);
    return 0;
}
```

Under the same-logical-CPU alternating model, each round trip includes at least the parent-to-child and child-to-parent switches, plus four I/O syscalls. The minimal illustration omits failure/EINTR handling and child reaping. Pin both processes to the same core (`taskset -c 0 ./pp`) to measure a true switch; on different cores you measure cross-core wakeup latency instead. The measured half-trip includes IPC and wake-up overhead and is not an isolated scheduler instruction cost. The `lat_ctx` tool in lmbench does the same thing more carefully.

## The indirect cost: caches and the TLB

The microseconds above are the visible part. The bigger cost often comes afterwards.

### Caches

Caches have finite, processor-specific capacities. Another task can evict useful code/data lines, making later accesses require a lower cache level or memory. The number and latency of misses depend on the working sets and memory-level parallelism.

> [!example] Paying for a cold cache
> Say A's hot working set is 512 KiB: 8,192 lines of 64 bytes. Assume every line was evicted, each refill takes a hypothetical 15 ns and refills are fully serialised. The sum is 8,192 × 15 ns = 122.88 µs. This is a simplified latency sum, not a prediction of real elapsed time; overlapping refills and bandwidth matter. Not every switch is that bad, but this is why a switch's true cost depends on the working set.

### The TLB

The **TLB** caches virtual-to-physical page translations. A miss means a page-table walk: several dependent memory reads. Switching to a different address space makes the old translations meaningless.

- **Without tagging**, writing `CR3` flushes all non-global TLB entries. The new task starts with a cold TLB.
- **With tagging**, entries carry an address-space ID: **PCID** on x86 (used by Linux since 4.14), **ASID** on ARM. Entries for several processes can coexist, so switching back to a recent process can find its translations still there.

PCID became much more important after Meltdown: KPTI switches page tables on every syscall, and without PCID each switch would flush the TLB.

### Migrations

Moving to another core can lose private-cache locality; shared caches, previously cached data and cache-coherence transfers complicate the actual cost. Linux tries to keep tasks where they last ran (cache affinity). `perf stat -e context-switches,cpu-migrations` shows both counts.

## Measuring switching in practice

| Tool | Shows |
|---|---|
| `vmstat 1` | `cs` column: switches/s system-wide |
| `pidstat -w 1` | per-task voluntary and involuntary |
| `perf stat` | switches, migrations, cache misses |
| `perf sched` | per-switch timeline, latency |

Compare switch rates with workload throughput, CPU time and measured latency. No universal healthy switch-count threshold applies.

## Real-world causes and fixes

- **Too many threads.** A thread-per-connection server with 10,000 mostly-idle connections is fine. With 10,000 *busy* ones on 16 cores, the scheduler juggles 625 runnable threads per core, and caches never stay warm. Fix: a small pool of threads (about one per core) using non-blocking I/O with `epoll` or `io_uring`. This is the nginx and Node model.
- **Lock contention.** Threads that block on a contended mutex switch out and back in repeatedly. Fix: reduce sharing, shorten critical sections, shard locks. (Linux kernel mutexes, and glibc's optional adaptive mutexes, spin briefly before sleeping, because a short spin is cheaper than two switches.)
- **Chatty pipelines.** Two processes passing tiny messages back and forth pay two switches per message. Fix: batch messages.
- **Latency-critical work.** Trading systems and DPDK packet processors pin threads to dedicated, isolated cores (`isolcpus`, `taskset`) and busy-poll, reducing scheduling interference while keeping cores busy. Affinity alone does not eliminate interrupts, kernel work or every context switch.

## Preview: user threads versus kernel threads

Everything so far concerns tasks the *kernel* knows about. Threads can also be managed in user space.

| Model | Mapping | Example |
|---|---|---|
| 1:1 | each thread is a kernel task | Linux pthreads (NPTL), Java platform threads |
| N:1 | many user threads, one kernel task | early "green threads" |
| M:N | many user threads over a pool of kernel threads | Go goroutines, Java virtual threads |

A **user-level switch** saves a few registers and swaps stacks in a library function, with no kernel entry and no page-table change, avoiding kernel-scheduler work on that path; the runtime and workload determine its cost. The catch: if a user thread makes a blocking syscall, the kernel thread under it blocks too, so M:N runtimes may use nonblocking I/O, park user threads or move runnable work to other OS threads around blocking calls. Threads, and how the scheduler chooses who runs next, are the subject of the next module.

## Key takeaways
- A context switch saves one task's registers, FPU/SIMD state, stack pointer and (for a different process) address-space root, and loads another's; a syscall alone is only a mode switch.
- Switches are voluntary (the task blocks) or involuntary (preemption by the timer or a higher-priority wake-up).
- Direct scheduler work and indirect cache/TLB effects are different costs; both require measurement on the chosen workload.
- Thread switches within one process skip the page-table switch; PCID and ASID tagging let TLB entries survive process switches.
- Too many runnable threads, lock contention and chatty IPC cause excessive switching; user-level threads (goroutines) switch far more cheaply.

## Further reading
- [Mechanism: Limited Direct Execution — OSTEP](https://pages.cs.wisc.edu/~remzi/OSTEP/cpu-mechanisms.pdf)
- [Context switch — Wikipedia](https://en.wikipedia.org/wiki/Context_switch)
- [Translation lookaside buffer — Wikipedia](https://en.wikipedia.org/wiki/Translation_lookaside_buffer)
- [Page Table Isolation (PTI) — Linux kernel docs](https://docs.kernel.org/arch/x86/pti.html)
- [proc(5): /proc/pid/status — Linux manual page](https://man7.org/linux/man-pages/man5/proc.5.html)
- [Thread (computing) — Wikipedia](https://en.wikipedia.org/wiki/Thread_(computing))
