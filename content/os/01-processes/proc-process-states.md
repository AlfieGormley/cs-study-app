---
id: proc-process-states
sourceLesson: proc-process-abstraction
title: "Ready, running and blocked tasks"
level: basic
minutes: 3
summary: "Ready tasks can run; blocked tasks wait for an event."
---

Ready tasks can run; blocked tasks wait for an event. This lesson focuses on ready, running and blocked tasks.

## Process states

A process moves between a few states. The classic textbook model:

```
        admit        dispatch
 new -------> ready ---------> running
               ^ ^              |  |
               | +--preempted---+  |
    event done |                   | wait
               |                   | (I/O,
               +---- blocked <-----+  lock)

 running ---exit---> terminated
```

- **Ready state**: could run, waiting for a CPU.
- **Running state**: on a CPU right now. At most one executing thread per logical CPU at an instant; an SMT core can execute several hardware threads.
- **Blocked state** (waiting, sleeping): can't run until something happens, such as disk I/O completing, a packet arriving, a lock being released or a timer expiring.
- **Terminated state**: finished, but not yet cleaned up.

Two transitions are important. **Running to ready** happens when the scheduler **preempts** a process (usually because the timer interrupt shows its time slice is used up). **Running to blocked** happens when the process asks for something that isn't available yet; it gives up the CPU voluntarily. A blocked process uses no CPU.

### Linux's states

`ps` and `top` show Linux's own letters:

| Letter | Meaning |
|---|---|
| R | running or runnable (ready) |
| S | interruptible sleep |
| D | uninterruptible sleep (usually I/O) |
| T | stopped (e.g. Ctrl-Z, `SIGSTOP`) |
| Z | zombie: exited, not yet reaped |
| I | idle kernel thread |

Linux doesn't distinguish ready from running: both are `R`. Sleeping is split in two. `S` sleeps can be woken by a signal. `D` sleeps can't, because the kernel is in the middle of something that must finish (often waiting on a disk or NFS server). A task in a truly uninterruptible wait cannot act on `SIGKILL` until the wait ends. The displayed `D` state can also cover killable waits that do respond to fatal signals; it is not a complete description of the wait primitive.



## Key takeaways
- Ready tasks can run; blocked tasks wait for an event.
- Linux R combines running and runnable; D does not by itself describe every signal-delivery detail.

## Further reading
- [The Abstraction: The Process — OSTEP](https://pages.cs.wisc.edu/~remzi/OSTEP/cpu-intro.pdf)
- [The Abstraction: Address Spaces — OSTEP](https://pages.cs.wisc.edu/~remzi/OSTEP/vm-intro.pdf)
- [proc(5) — Linux manual page](https://man7.org/linux/man-pages/man5/proc.5.html)
- [Process control block — Wikipedia](https://en.wikipedia.org/wiki/Process_control_block)
- [Process state — Wikipedia](https://en.wikipedia.org/wiki/Process_state)
- [Address space layout randomization — Wikipedia](https://en.wikipedia.org/wiki/Address_space_layout_randomization)
