---
id: proc-ipc-safe-signals
sourceLesson: proc-ipc
title: "Signal delivery and safe shutdown"
level: advanced
minutes: 4
summary: "Standard-signal coalescing can combine several notifications, so child reaping must drain all available statuses."
---

Standard-signal coalescing can combine several notifications, so child reaping must drain all available statuses. This lesson focuses on signal delivery and safe shutdown.

## Signals: asynchronous notifications

A **Unix signal** is a small integer delivered to a process to say "something happened". It identifies an event by number; `SA_SIGINFO` handlers can also inspect sender/event information and a value supplied through `sigqueue`. Signals are notifications rather than a bulk-data channel. Signals are how the kernel and other processes interrupt you.

| Signal | Typical cause | Default |
|---|---|---|
| `SIGINT` (2) | Ctrl-C | terminate |
| `SIGTERM` (15) | `kill`, shutdown | terminate |
| `SIGKILL` (9) | `kill -9`, OOM killer | terminate |
| `SIGSEGV` (11) | bad memory access | core dump |
| `SIGPIPE` (13) | write to dead pipe | terminate |
| `SIGCHLD` (17) | child exited | ignore |

(Numbers are for Linux on x86 and ARM.) A process can, for most signals, **ignore** it, **block** it (hold it pending), or install a **handler**. `SIGKILL` and `SIGSTOP` are the exceptions: they can't be caught, blocked or ignored, though permissions, init semantics and uninterruptible waits can prevent or delay the expected effect.

The kernel delivers a pending signal when the target next returns from kernel to user mode: after a syscall, an interrupt or being scheduled. If a handler is installed, the kernel arranges for the process to run it, then resume where it was.

### Writing a safe handler

A handler can run *between any two instructions* of your program, including in the middle of `malloc` or `printf`. If the handler calls `malloc` too, the allocator's internal state may be half-updated and you get corruption or deadlock. Only **async-signal-safe** functions (listed in `signal-safety(7)`: `write`, `_exit`, `kill` and others) may be called. The standard pattern is to set a flag and do the real work in the main loop:

```c
static volatile sig_atomic_t stop;

static void on_term(int sig) {
    (void)sig;
    /* Defer cleanup to ordinary */
    /* execution. */
    stop = 1;
}

int main(void) {
    struct sigaction sa = {0};
    sa.sa_handler = on_term;
    sigemptyset(&sa.sa_mask);
    sigaction(SIGTERM, &sa, NULL);
    while (!stop)
        do_work();
    cleanup();   /* flush, close */
    return 0;
}
```

This is a schematic shutdown loop: include `<signal.h>`, define the work and cleanup routines, check sigaction errors and ensure do_work returns or responds to shutdown. A flag alone does not wake an indefinitely blocked operation. On Linux, `docker stop` normally sends `SIGTERM`, waits its configured grace period (10 seconds by default for Linux containers), then sends `SIGKILL`; the image or command can configure another stop signal. Kubernetes normally allows a 30-second pod termination grace period, including shutdown hooks and runtime handling, with configurable signals and timing. A service that ignores `SIGTERM` gets killed mid-request.

> [!warning] Standard signals don't queue
> A standard signal is a single pending bit. If three children exit before your `SIGCHLD` handler runs, the handler may run once. Never count signals; reap in a `waitpid(-1, &st, WNOHANG)` loop while returns are positive; handle -1, including EINTR and ECHILD, as well as 0. Real-time signals (`SIGRTMIN` to `SIGRTMAX`) do queue.

Modern Linux code often avoids handlers altogether: `signalfd` turns signals into readable events on a file descriptor, which fits neatly into an `epoll` loop.

## Key takeaways
- Standard-signal coalescing can combine several notifications, so child reaping must drain all available statuses.
- Handlers must use documented async-signal-safe operations or defer work to the main loop.

## Further reading
- [pipe(7) — Linux manual page](https://man7.org/linux/man-pages/man7/pipe.7.html)
- [signal(7) — Linux manual page](https://man7.org/linux/man-pages/man7/signal.7.html)
- [signal-safety(7) — Linux manual page](https://man7.org/linux/man-pages/man7/signal-safety.7.html)
- [shm_overview(7) — Linux manual page](https://man7.org/linux/man-pages/man7/shm_overview.7.html)
- [mq_overview(7) — Linux manual page](https://man7.org/linux/man-pages/man7/mq_overview.7.html)
- [unix(7) — Linux manual page](https://man7.org/linux/man-pages/man7/unix.7.html)
- [Inter-process communication — Wikipedia](https://en.wikipedia.org/wiki/Inter-process_communication)
- [Kubernetes pod termination](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/)
