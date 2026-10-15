---
id: proc-os-abstractions
sourceLesson: proc-what-os-does
title: "Abstractions and shared resources"
level: basic
minutes: 3
summary: "File descriptors hide many hardware details behind common operations, with resource-specific semantics."
---

Run `cat notes.txt` and a dozen things happen that `cat` never asks for. Something finds the file on a disk it has never heard of, loads the program into memory that another program might also want, gives it a slice of a CPU shared with hundreds of other processes, and stops it from reading your browser's memory. That something is the **operating system**.

An OS is the software layer between hardware and programs. It does three jobs, and almost every OS feature is one of them.

## Job 1: abstraction

Hardware is ugly. A disk is an array of numbered blocks with a vendor-specific command set. A network card is a ring of DMA buffers. A CPU is a set of registers and a program counter.

The OS turns these into clean, portable ideas:

| Hardware | Abstraction |
|---|---|
| CPU cores | Processes and threads |
| Physical RAM | Virtual address spaces |
| Disk blocks | Files and directories |
| NIC, packets | Sockets |
| Keyboard, screen | Terminals, file descriptors |

File descriptors give many resources a common `read`, `write` and `close` interface, though their semantics differ. Regular files are opened with `open`; pipes and sockets normally come from `pipe` and `socket`. Not every resource or operation fits this interface.

```c
#include <fcntl.h>
#include <unistd.h>

int main(void) {
    char buf[4096];
    int fd = open("notes.txt", O_RDONLY);
    ssize_t n;
    /* EOF ends the copy; errors need */
    /* care. */
    while ((n = read(fd, buf, 4096)) > 0)
        /* Emit only bytes read this */
        /* turn. */
        write(1, buf, n); /* 1 = stdout */
    close(fd);
    return 0;
}
```

This minimal illustration omits error handling and partial-write retries; a robust copy must handle both. It has no idea whether `notes.txt` lives on ext4, on NFS across the network, or in RAM on tmpfs. The OS hides it.

## Job 2: resource management

There is one set of hardware and many programs that want it. The OS is the referee.

- **CPU time**: the scheduler decides which runnable thread gets each core and for how long.
- **Memory**: the virtual memory system decides which pages live in RAM and which are evicted to disk or dropped.
- **I/O bandwidth**: the block layer queues and orders disk requests.
- **Everything else**: file descriptors, PIDs, network ports, GPU time.

Good resource management means **multiplexing**. In *time* (taking turns on a CPU) and in *space* (each process gets a share of RAM). The goals conflict: fairness, throughput, low latency and low power cannot all be maximised together. Much of OS design is choosing which to favour.

## Key takeaways
- File descriptors hide many hardware details behind common operations, with resource-specific semantics.
- Schedulers and memory managers divide scarce hardware among competing programs.

## Further reading
- [Introduction to Operating Systems — OSTEP (free textbook)](https://pages.cs.wisc.edu/~remzi/OSTEP/intro.pdf)
- [Kernel (operating system) — Wikipedia](https://en.wikipedia.org/wiki/Kernel_(operating_system))
- [Microkernel — Wikipedia](https://en.wikipedia.org/wiki/Microkernel)
- [Protection ring — Wikipedia](https://en.wikipedia.org/wiki/Protection_ring)
- [Tanenbaum–Torvalds debate — Wikipedia](https://en.wikipedia.org/wiki/Tanenbaum%E2%80%93Torvalds_debate)
- [L4 microkernel family — Wikipedia](https://en.wikipedia.org/wiki/L4_microkernel_family)
