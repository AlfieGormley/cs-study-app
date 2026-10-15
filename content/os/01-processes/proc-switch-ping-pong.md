---
id: proc-switch-ping-pong
sourceLesson: proc-context-switching
title: "Measuring a pipe hand-off"
level: advanced
minutes: 3
summary: "A pipe round trip includes communication, wake-ups and scheduler work."
---

A pipe round trip includes communication, wake-ups and scheduler work. This lesson focuses on measuring a pipe hand-off.

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
    /* Child replies once per received */
    /* byte. */
    if (fork() == 0) {
        for (int i = 0; i < N; i++) {
            read(a[0], &c, 1);
            write(b[1], &c, 1);
        }
        _exit(0);
    }
    struct timespec t0, t1;
    /* Time exchanges, not process */
    /* creation. */
    clock_gettime(CLOCK_MONOTONIC, &t0);
    for (int i = 0; i < N; i++) {
        write(a[1], &c, 1);
        read(b[0], &c, 1);
    }
    clock_gettime(CLOCK_MONOTONIC, &t1);
    /* Convert both timestamp fields to */
    /* ns. */
    double ns =
        (t1.tv_sec - t0.tv_sec) * 1e9 +
        (t1.tv_nsec - t0.tv_nsec);
    /* Includes IPC and syscall overhead. */
    printf("%.0f ns/half-trip\n", ns/N/2);
    return 0;
}
```

Under the same-logical-CPU alternating model, each round trip includes at least the parent-to-child and child-to-parent switches, plus four I/O syscalls. The minimal illustration omits failure/EINTR handling and child reaping. Pin both processes to the same core (`taskset -c 0 ./pp`) to measure a true switch; on different cores you measure cross-core wakeup latency instead. The measured half-trip includes IPC and wake-up overhead and is not an isolated scheduler instruction cost. The `lat_ctx` tool in lmbench does the same thing more carefully.

The program's last line turns the measured time into a cost per half-trip, one process handing the byte to the other:

```formula
t_half = T / (2N)
where
t_half: the time for one half-trip, in nanoseconds (ns)
T: the total measured time for all round trips, in nanoseconds (ns)
N: the number of round trips, 100,000 in the program
ns: nanosecond, one billionth of a second
In words: divide the total time by the number of one-way hand-offs, which is twice the number of round trips.
```

For example, if 100,000 round trips take 0.5 s (500,000,000 ns), each half-trip takes 500,000,000 ns divided by 200,000, which is 2,500 ns. Under this alternating model, it is an upper estimate of the average scheduler-switch contribution per hand-off because it also includes IPC and syscall work. It does not bound the duration of every individual switch.

## Key takeaways
- A pipe round trip includes communication, wake-ups and scheduler work.
- Affinity and CPU placement change what the benchmark measures.

## Further reading
- [Mechanism: Limited Direct Execution — OSTEP](https://pages.cs.wisc.edu/~remzi/OSTEP/cpu-mechanisms.pdf)
- [Context switch — Wikipedia](https://en.wikipedia.org/wiki/Context_switch)
- [Translation lookaside buffer — Wikipedia](https://en.wikipedia.org/wiki/Translation_lookaside_buffer)
- [Page Table Isolation (PTI) — Linux kernel docs](https://docs.kernel.org/arch/x86/pti.html)
- [proc(5): /proc/pid/status — Linux manual page](https://man7.org/linux/man-pages/man5/proc.5.html)
- [Thread (computing) — Wikipedia](https://en.wikipedia.org/wiki/Thread_(computing))
