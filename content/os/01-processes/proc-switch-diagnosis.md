---
id: proc-switch-diagnosis
sourceLesson: proc-context-switching
title: "Diagnosing too much switching"
level: advanced
minutes: 2
summary: "Switch counts need workload and latency context to guide diagnosis."
---

Switch counts need workload and latency context to guide diagnosis. This lesson focuses on diagnosing too much switching.

## Measuring switching in practice

| Tool | Shows |
|---|---|
| `vmstat 1` | `cs` column: switches/s system-wide |
| `pidstat -w 1` | per-task voluntary and involuntary |
| `perf stat` | switches, migrations, cache misses |
| `perf sched` | per-switch timeline, latency |

Compare switch rates with workload throughput, CPU time and measured latency. No universal healthy switch-count threshold applies.

## Real-world causes and fixes

- **Too many threads.** A thread-per-connection server with 10,000 mostly-idle connections is fine. With 10,000 *busy* ones on 16 cores, that averages 625 runnable threads per core, which can hurt cache locality and scheduling latency. Consider bounded CPU worker pools and non-blocking I/O with `epoll` or `io_uring`; size pools from measurements. nginx and Node use event-driven I/O, but their runtime and worker-pool details differ.
- **Lock contention.** Threads that block on a contended mutex switch out and back in repeatedly. Fix: reduce sharing, shorten critical sections, shard locks. (Linux kernel mutexes, and glibc's optional adaptive mutexes, spin briefly before sleeping, because a short spin is cheaper than two switches.)
- **Chatty pipelines.** Two processes passing tiny messages back and forth can incur frequent scheduling and wake-up work; CPU placement and batching determine actual switch counts. Fix: batch messages.
- **Latency-critical work.** Trading systems and DPDK packet processors pin threads to dedicated, isolated cores (`isolcpus`, `taskset`) and busy-poll, reducing scheduling interference while keeping cores busy. Affinity alone does not eliminate interrupts, kernel work or every context switch.

## Key takeaways
- Switch counts need workload and latency context to guide diagnosis.
- Batching, less contention and bounded runnable work can reduce scheduling overhead.

## Further reading
- [Mechanism: Limited Direct Execution — OSTEP](https://pages.cs.wisc.edu/~remzi/OSTEP/cpu-mechanisms.pdf)
- [Context switch — Wikipedia](https://en.wikipedia.org/wiki/Context_switch)
- [Translation lookaside buffer — Wikipedia](https://en.wikipedia.org/wiki/Translation_lookaside_buffer)
- [Page Table Isolation (PTI) — Linux kernel docs](https://docs.kernel.org/arch/x86/pti.html)
- [proc(5): /proc/pid/status — Linux manual page](https://man7.org/linux/man-pages/man5/proc.5.html)
- [Thread (computing) — Wikipedia](https://en.wikipedia.org/wiki/Thread_(computing))
