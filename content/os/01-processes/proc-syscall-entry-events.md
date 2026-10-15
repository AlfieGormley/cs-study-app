---
id: proc-syscall-entry-events
sourceLesson: proc-syscalls
title: "Modes, faults and interrupts"
level: basic
minutes: 3
summary: "User code cannot choose an arbitrary kernel entry address."
---

Ordinary programs normally access protected devices through the kernel; authorised user-space drivers are an exception. Yet `cat` reads files and `curl` sends packets. The trick is that programs don't do these things; they *ask the kernel to*. The asking mechanism is the **system call**.

The challenge is to let untrusted code ask for privileged work without letting it *become* privileged. The CPU solves this with modes and a small set of fixed entry points.

## User mode and kernel mode

At any moment a CPU core runs in one of (at least) two modes:

- **User mode**: privileged instructions fault. Only pages marked user-accessible can be touched.
- **Kernel mode**: privileged operations are available, but mappings, memory protections, hardware rules and any hypervisor still constrain accesses.

The only ways from user mode into kernel mode are events the hardware directs to **addresses the kernel chose in advance**. User code can't jump into the middle of the kernel. It can only knock on doors whose locations the kernel registered at boot.

This idea is called **limited direct execution**. Run the program directly on the CPU at full speed (direct execution), but limit what it can do, and make sure the kernel regains control when needed.

## Three ways into the kernel

| Event | Cause | Example |
|---|---|---|
| Trap (syscall) | Deliberate | `syscall`, `svc` |
| Exception (fault) | Error in current instruction | Page fault, divide by 0 |
| Interrupt | External hardware | Timer tick, NIC packet |

- **Traps** are *synchronous and intentional*: the program executes a special instruction to request a service.
- In this introductory classification, **faults** are synchronous conditions caused by the current instruction. Architectural terminology also includes deliberate traps among exceptions. Some are fixable (a page fault on a lazily allocated page; the kernel maps it and re-runs the instruction). Some are fatal (a segfault becomes `SIGSEGV`).
- **Interrupts** are *asynchronous*: a device signals the CPU regardless of what's running. The **timer interrupt** is vital, because it is how the kernel takes the CPU back from a program stuck in `while (1);`.

Terminology varies between textbooks and CPU vendors (Intel calls all of these "interrupts and exceptions"), but the distinction of deliberate versus error versus external is what matters.

## Key takeaways
- User code cannot choose an arbitrary kernel entry address.
- Deliberate service requests, synchronous faults and asynchronous device events have different causes.

## Further reading
- [Mechanism: Limited Direct Execution — OSTEP](https://pages.cs.wisc.edu/~remzi/OSTEP/cpu-mechanisms.pdf)
- [Anatomy of a system call, part 1 — LWN](https://lwn.net/Articles/604287/)
- [Anatomy of a system call, part 2 — LWN](https://lwn.net/Articles/604515/)
- [syscall(2) — Linux manual page](https://man7.org/linux/man-pages/man2/syscall.2.html)
- [vdso(7) — Linux manual page](https://man7.org/linux/man-pages/man7/vdso.7.html)
- [Kernel page-table isolation — Wikipedia](https://en.wikipedia.org/wiki/Kernel_page-table_isolation)
