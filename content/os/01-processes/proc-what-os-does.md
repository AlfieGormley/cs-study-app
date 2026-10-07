---
id: proc-what-os-does
title: What an operating system does
level: basic
minutes: 10
summary: The three jobs of an OS (abstraction, resource management, protection), the line between kernel and user space, and how monolithic, micro- and hybrid kernels draw it differently.
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
    while ((n = read(fd, buf, 4096)) > 0)
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

## Job 3: protection and isolation

If any program could write to any memory or talk to the disk controller directly, one buggy program could crash the machine, and one malicious program could read everyone's secrets.

The OS enforces boundaries:

- Each process gets its **own virtual address space**. An ordinary load in A uses A's mappings, not B's. Explicit shared mappings and authorised process-memory interfaces are exceptions.
- The kernel controls access to device registers, page tables and interrupt settings; it can delegate selected device mappings or I/O permissions to user-space drivers.
- Permissions (user IDs, file modes, capabilities) gate access to shared resources.

This needs **hardware help**. The CPU has at least two privilege levels. On x86 these are **rings**: ring 0 for the kernel, ring 3 for applications. ARM calls them exception levels (EL0 for user, EL1 for the kernel). Privileged instructions, like loading a new page table, fault if run from user mode.

> [!note] Protection is the foundation
> Abstraction and resource management are only enforceable because of protection. If a program could bypass the kernel, it could ignore the scheduler and the file permissions too.

## Kernel space and user space

The **kernel** is the part of the OS that runs in privileged mode. Everything else, including your shell, `systemd`, the desktop and your apps, runs in **user space**.

```
 +-------------------------------+
 | apps: bash, nginx, chrome     |  user
 | libraries: libc, libssl       |  space
 +---------- syscall API --------+  -------
 | kernel: scheduler, VM, VFS,   |  kernel
 | network stack, drivers        |  space
 +-------------------------------+
 | hardware: CPU, RAM, disk, NIC |
 +-------------------------------+
```

User code reaches the kernel only through a narrow, controlled door: **system calls** (next lesson). The available syscall set depends on architecture and kernel version. The C library (`glibc`, `musl`) wraps them in friendly functions like `printf` and `fopen`.

A common confusion: "the operating system" in casual use means the whole distribution (kernel, shell, utilities, desktop). In OS theory it usually means the kernel. Linux, strictly, is only a kernel; Ubuntu is an OS built on it.

## Where to draw the line: kernel designs

What belongs inside the privileged kernel? Every line of kernel code can crash the whole machine or open a security hole, so less is safer. But crossing the user/kernel boundary costs time, so more in the kernel is faster. Three answers have emerged.

### Monolithic kernels

Everything that is "OS" runs in kernel space as one big program: scheduler, memory manager, file systems, network stack, and device drivers. Components call each other with plain function calls.

- **Examples**: Linux, FreeBSD, traditional Unix.
- **Pro**: fast. A file read goes from the VFS to ext4 to the block layer to the NVMe driver without any boundary crossing.
- **Con**: a bug in any driver runs with full privilege. A bad GPU driver can corrupt file system memory and panic the kernel.

Linux softens this with **loadable kernel modules** (`modprobe`, `lsmod`), so drivers need not be compiled in. But a loaded module still runs in ring 0 with no isolation. It is a packaging trick, not a protection boundary. **eBPF** is a newer route: small programs checked by a verifier before the kernel runs them, constraining extensions according to the verifier and runtime rules; verifier or kernel bugs can still undermine that protection.

### Microkernels

Keep the kernel tiny: address spaces, threads, scheduling and **inter-process communication (IPC)**. Drivers, file systems and network stacks run as ordinary user-space **servers**.

```
  app      fs server   net server  driver
   |           |           |          |
 --+---- IPC --+---- IPC --+----------+--
 |  microkernel: threads, memory, IPC   |
 ---------------------------------------
```

- **Examples**: the L4 family (including **seL4**), QNX, MINIX 3. QNX runs in many car infotainment and industrial systems.
- **Pro**: isolation. A crashed driver is a crashed process; it can be restarted. A small kernel is easier to verify: seL4 has machine-checked functional-correctness proofs for specified configurations and assumptions, not a proof that every deployment and device is safe.
- **Con**: a file read that was one function call is now several IPC messages, each crossing into the kernel and switching address spaces. Early microkernels like Mach were notoriously slow because of this. L4 showed IPC can be made far cheaper, but the cost never reaches zero.

> [!example] The Tanenbaum–Torvalds debate
> In 1992 Andrew Tanenbaum, author of MINIX, posted that "Linux is obsolete" because it was monolithic. Linus Torvalds replied that the performance and simplicity of a monolithic design mattered more in practice. Three decades later both sides have a point: Both designs remain in use; their names alone do not establish performance, reliability or certification suitability.

### Hybrid kernels

Start from a microkernel design, then move performance-critical services back into kernel space.

- **Windows NT** (all modern Windows): a layered kernel and executive, with file systems, the network stack and most drivers running in kernel mode.
- **XNU** (macOS, iOS): the Mach microkernel combined with a large BSD layer and the IOKit driver framework, all running in kernel space.

Critics argue "hybrid" is mostly marketing: once the file system and drivers are in kernel space, the result behaves much like a monolithic kernel with a message-passing internal structure. Both macOS and Windows have since moved some drivers out to user space (Apple's DriverKit, Windows' User-Mode Driver Framework), which shows the trade-off is still live.

### Side by side

| | Monolithic | Micro | Hybrid |
|---|---|---|---|
| In kernel | Almost all | IPC, VM, sched | Most |
| Speed | Workload-dependent | IPC-sensitive | Workload-dependent |
| Fault isolation | Poor | Strong | Partial |
| Examples | Linux | seL4, QNX | NT, XNU |

## Real-world view

On a typical Linux server:

- Kernel image and module sizes depend on configuration, architecture, compression and installed drivers.
- Most "OS behaviour" you configure is policy in user space: `systemd` starts services, `udev` names devices, NetworkManager configures interfaces. The kernel provides mechanism; user space chooses policy.
- When you hit a kernel bug, you get a **kernel panic** or an **oops**, and with a monolithic kernel the safe response is often to reboot.

The **mechanism versus policy** split is worth remembering. The kernel provides "a process can be given a CPU for a time slice"; something decides *which* process and *how long*. Keeping these apart lets policy change without rewriting mechanism.

## Common misconceptions

- **"The OS is always running."** User code can run directly on the CPU until a system call, interrupt or exception transfers control. Kernel threads also execute scheduled background work; another core can be running kernel code at the same time. The OS is more like a referee who steps in when the whistle blows.
- **"User space is slower."** User instructions run at the same speed as kernel instructions. What costs time is *crossing* the boundary.
- **"Modules make Linux a microkernel."** No. Modules are loaded into the same privileged address space.

> [!note] Content gap: deployment assurances
> No benchmark, market-share survey or certified device design is supplied. Kernel categories alone do not guarantee speed or safety. seL4 guarantees depend on verified configuration and hardware assumptions, including DMA behaviour; fault isolation is not a complete safety case.

## Key takeaways
- An OS does three jobs: abstracts hardware into processes, files and sockets; manages shared resources; and protects programs from each other.
- Protection relies on hardware privilege levels (x86 rings, ARM exception levels) and per-process virtual address spaces.
- The kernel runs privileged; everything else runs in user space and enters the kernel only through system calls, interrupts and exceptions.
- Monolithic kernels (Linux) are fast but give every driver full privilege; microkernels (seL4, QNX) isolate services at the cost of IPC; hybrids (Windows NT, XNU) sit in between.
- The kernel provides mechanism; user space largely decides policy.

## Further reading
- [Introduction to Operating Systems — OSTEP (free textbook)](https://pages.cs.wisc.edu/~remzi/OSTEP/intro.pdf)
- [Kernel (operating system) — Wikipedia](https://en.wikipedia.org/wiki/Kernel_(operating_system))
- [Microkernel — Wikipedia](https://en.wikipedia.org/wiki/Microkernel)
- [Protection ring — Wikipedia](https://en.wikipedia.org/wiki/Protection_ring)
- [Tanenbaum–Torvalds debate — Wikipedia](https://en.wikipedia.org/wiki/Tanenbaum%E2%80%93Torvalds_debate)
- [L4 microkernel family — Wikipedia](https://en.wikipedia.org/wiki/L4_microkernel_family)
