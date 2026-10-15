---
id: conc-runtime-mappings
title: Green threads and Go stack storage
level: intermediate
minutes: 4
sourceLesson: conc-coroutines-green-threads
summary: Many-to-many runtimes map many tasks onto a changing set of OS threads.
---

Stackful suspension can support blocking-looking user threads. This unit distinguishes runtime scheduling from kernel scheduling, then scopes Go’s stack arithmetic to an explicit implementation model.

## Green threads

Put stackful coroutines under a scheduler that *pretends they are threads* and you get **green threads**: threads managed by the language runtime rather than the kernel. The programmer writes ordinary, blocking-looking code; the runtime quietly switches threads whenever one would block.

The mapping between user threads and OS threads has three shapes:

```
1:1  (Java platform threads, C++)
 T1   T2   T3      user threads
 |    |    |
 K1   K2   K3      OS threads

M:1  (early Java, Python greenlet)
 T1   T2   T3
  \   |   /
     K1            one OS thread

M:N  (Go, Erlang, Java virtual threads)
 T1 T2 T3 T4 T5 T6
  \  |  \/  |  /
     K1   K2       a few OS threads
```

Read each label as a ratio of user threads to OS threads. In 1:1, every user thread gets its own OS thread. In M:1, many user threads (M of them) share one OS thread. In M:N, M user threads are spread over N OS threads, where M is usually far larger than N: a Go server might run 100,000 goroutines on 8 OS threads. (This M is just a count; Go's scheduler, below, uses the letter M for something else.)

M:1 cannot run those user threads on more than one core at once, and an unsupported blocking system call stalls the user threads sharing that OS thread. Other OS threads in the process can continue. Early Solaris JVMs used green threads and later adopted native Solaris threading. Historical Solaris native implementations also used a two-level many-to-many mapping; native did not universally mean one-to-one. The diagram’s Java platform-thread label describes the modern comparison, not every historical Solaris release. M:N gets both cheap threads and multicore, at the cost of a sophisticated runtime.

### Go: goroutines

`go f()` starts a **goroutine**. The fetched Go runtime has a 2 KiB minimum for Go-code stack space. Actual initial allocation can include platform overhead and an adaptive starting size computed from stack use at garbage collection. When a function’s stack check needs more space, the runtime chooses a larger stack and copies live stack state, fixing up pointers; it normally begins by doubling but can double repeatedly to fit a large frame. Large counts are possible, but memory, retained state and work per goroutine still limit scale.

For a simplified allocation model, assume an initial 2 KiB stack and count individual doublings, with no shrink or platform overhead. This models the arithmetic; it does not predict the number of runtime growth events or an actual process’s memory use:

```formula
S_k = S_0 2^k
S_k = 2 KiB × 2^3 = 16 KiB   for k = 3
where
S_k: modelled stack allocation after k individual doublings, in kibibytes (KiB)
S_0: assumed initial stack allocation in this model, 2 KiB; actual Go starting allocations can differ
k: number of individual doublings in this arithmetic model, not necessarily runtime growth events
2^k: k copies of 2 multiplied together (2^3 = 2 × 2 × 2 = 8)
KiB: kibibyte, 1,024 bytes
In words: in the stated doubling model, three doublings take 2 KiB to 16 KiB and nine take it to 1 MiB; actual stack growth and starting sizes depend on runtime state and platform.
```

The arithmetic needs nine doublings to reach 1 MiB (1,024 KiB) from 2 KiB. Runtime growth can skip intermediate sizes, and the garbage collector can shrink a mostly unused stack. Capacity depends on the actual distribution of live stack sizes, retained heap data and other runtime overhead, rather than either a universal starting size or the maximum possible stack alone.

The scheduler uses three structures, usually written **G, M, P**:

- **G**: a goroutine (its stack and state).
- **M**: an OS thread ("machine"), not the M of M:N above.
- **P**: a processor slot with a local run queue. There are `GOMAXPROCS` of them, with defaults based on available logical CPUs and, since Go 1.25 on Linux, container CPU limits; defaults can update as constraints change.

An M must hold a P to run Gs. An idle P can use **work stealing** to take roughly half another P’s local runnable queue in the cited scheduler; empty queues, rounding and other scheduler paths matter. When a goroutine reads a socket that has no data, the runtime adds it to the **netpoller** (epoll/kqueue) and parks the G; the M runs something else. When a goroutine enters a genuinely blocking system call, the M stays blocked with it, but a monitor thread (`sysmon`) hands the P to another M so the other goroutines keep running.

Scheduling is effectively **pre-emptive**. Before Go 1.14, pre-emption relied heavily on cooperative safe points such as function prologues, so a tight loop like `for {}` could stall the garbage collector. Go 1.14 added asynchronous pre-emption on supported platforms, implemented on Unix by sending the thread a signal.

## Key takeaways
- Many-to-many runtimes map many tasks onto a changing set of OS threads.
- Go stack-size examples are implementation-scoped models, not a universal initial allocation.
- Go code runs on an OS thread holding a processor slot.
- Network parking, blocking system calls and asynchronous pre-emption take different runtime paths.

## Further reading
- [Historical Solaris JVM threading models — Oracle](https://docs.oracle.com/cd/E19455-01/806-3461/6jck06gqe/index.html)
- [Primary source: peps.python.org](https://peps.python.org/pep-0342/)
- [Primary source: www.lua.org](https://www.lua.org/manual/5.4/manual.html#2.6)
- [Primary source: go.dev](https://go.dev/src/runtime/stack.go)
- [Primary source: openjdk.org](https://openjdk.org/jeps/444)
- [Primary source: openjdk.org](https://openjdk.org/jeps/491)
