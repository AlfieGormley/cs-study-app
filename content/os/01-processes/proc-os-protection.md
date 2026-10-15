---
id: proc-os-protection
sourceLesson: proc-what-os-does
title: "Protection and the kernel boundary"
level: basic
minutes: 3
summary: "Hardware privilege levels and page permissions help enforce process isolation."
---

Hardware privilege levels and page permissions help enforce process isolation. This lesson focuses on protection and the kernel boundary.

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

User code requests kernel services through a narrow, controlled door: **system calls** (introduced in the syscall units). The available syscall set depends on architecture and kernel version. The C library (`glibc`, `musl`) wraps them in friendly functions like `printf` and `fopen`.

A common confusion: "the operating system" in casual use means the whole distribution (kernel, shell, utilities, desktop). In OS theory it usually means the kernel. Linux, strictly, is only a kernel; Ubuntu is an OS built on it.

## Key takeaways
- Hardware privilege levels and page permissions help enforce process isolation.
- User-space libraries request privileged services through controlled kernel entry points.

## Further reading
- [Introduction to Operating Systems — OSTEP (free textbook)](https://pages.cs.wisc.edu/~remzi/OSTEP/intro.pdf)
- [Kernel (operating system) — Wikipedia](https://en.wikipedia.org/wiki/Kernel_(operating_system))
- [Microkernel — Wikipedia](https://en.wikipedia.org/wiki/Microkernel)
- [Protection ring — Wikipedia](https://en.wikipedia.org/wiki/Protection_ring)
- [Tanenbaum–Torvalds debate — Wikipedia](https://en.wikipedia.org/wiki/Tanenbaum%E2%80%93Torvalds_debate)
- [L4 microkernel family — Wikipedia](https://en.wikipedia.org/wiki/L4_microkernel_family)
