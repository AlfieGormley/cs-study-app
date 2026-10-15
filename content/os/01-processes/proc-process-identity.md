---
id: proc-process-identity
sourceLesson: proc-process-abstraction
title: "Process identity and kernel records"
level: basic
minutes: 3
summary: "A process combines an address space, execution state, resources and identity."
---

A **program** is a file: instructions and data sitting on disk. A **process** is a program *running*: the instructions plus everything needed to execute them right now. Run `python3` in three terminals and you have one program and three processes.

The process is the OS's central abstraction. It gives each running program the illusion of its own CPU and its own private memory, even though dozens of processes share a few cores and one pool of RAM.

## What makes up a process

A process is roughly:

- **An address space**: the memory it can see, from its code to its stack.
- **Execution state**: the CPU registers, including the program counter (which instruction is next) and stack pointer.
- **OS resources**: open file descriptors, current directory, signal handlers, user and group IDs, resource limits.
- **Identity**: a process ID (PID), a parent PID, and accounting information like CPU time used.

One process can contain several **threads**. Threads share the address space and resources but each has its own registers and stack. Threads are a later module's subject; for now picture one thread per process.

## The process control block

The kernel needs a record of every process. Textbooks call it the **process control block (PCB)**. In Linux it's `struct task_struct`, a structure with hundreds of fields. The important ones:

| Field | Why |
|---|---|
| PID, parent, children | identity and family tree |
| State | running, sleeping, zombie... |
| Saved registers | to resume it later |
| Memory map (`mm`) | page tables, regions |
| Open files table | fd to file mapping |
| Credentials | UID, GID, capabilities |
| Scheduling info | priority, CPU time used |
| Signal state | handlers, pending, blocked |

When a process isn't running, its PCB holds everything needed to continue it later, exactly where it left off. This is what makes a **context switch** possible (covered in the context-switching units).

In Linux, every thread has its own `task_struct`. Threads of one process share the same `mm` (address space) and file table by pointing to the same structures. "Process" and "thread" are really just different sharing settings, a theme we'll return to.

Much of `task_struct` is visible in `/proc/<pid>/status`. The following output is illustrative: state, parent PID and memory usage vary between runs.

```
$ grep -E 'State|PPid|Threads|VmRSS' \
    /proc/self/status
State:  R (running)
PPid:   2817
Threads:        1
VmRSS:      1024 kB
```

## Key takeaways
- A process combines an address space, execution state, resources and identity.
- Linux tracks schedulable threads through task_struct and shared referenced structures.

## Further reading
- [The Abstraction: The Process — OSTEP](https://pages.cs.wisc.edu/~remzi/OSTEP/cpu-intro.pdf)
- [The Abstraction: Address Spaces — OSTEP](https://pages.cs.wisc.edu/~remzi/OSTEP/vm-intro.pdf)
- [proc(5) — Linux manual page](https://man7.org/linux/man-pages/man5/proc.5.html)
- [Process control block — Wikipedia](https://en.wikipedia.org/wiki/Process_control_block)
- [Process state — Wikipedia](https://en.wikipedia.org/wiki/Process_state)
- [Address space layout randomization — Wikipedia](https://en.wikipedia.org/wiki/Address_space_layout_randomization)
