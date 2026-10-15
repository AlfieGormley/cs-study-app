---
id: proc-os-kernel-designs
sourceLesson: proc-what-os-does
title: "Monolithic kernels and microkernels"
level: basic
minutes: 3
summary: "A loadable Linux module remains inside the privileged kernel."
---

A loadable Linux module remains inside the privileged kernel. This lesson focuses on monolithic kernels and microkernels.

## Where to draw the line: kernel designs

What belongs inside the privileged kernel? Every line of kernel code can crash the whole machine or open a security hole, so reducing the trusted code can make isolation and review easier. Crossing protection boundaries adds work, but actual performance depends on the workload and implementation. Three answers have emerged.

### Monolithic kernels

Everything that is "OS" runs in kernel space as one big program: scheduler, memory manager, file systems, network stack, and device drivers. Components call each other with plain function calls.

- **Examples**: Linux, FreeBSD, traditional Unix.
- **Pro**: direct internal calls. A file read goes from the VFS to ext4 to the block layer to the NVMe driver without any boundary crossing.
- **Con**: a bug in any driver runs with full privilege. A bad GPU driver can corrupt file system memory and panic the kernel.

Linux softens this with **loadable kernel modules** (`modprobe`, `lsmod`), so drivers need not be compiled in. But a loaded module still runs in ring 0 with no isolation. It is a packaging trick, not a protection boundary. **eBPF** is a newer route: small programs checked by a verifier before the kernel runs them, constraining these kernel extensions according to the verifier and runtime rules; verifier or kernel bugs can still undermine that protection.

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
- **Con**: a file read can require several IPC messages between services through the kernel. The exact path and number of address-space changes depend on caching and implementation. Early microkernels like Mach were notoriously slow because of this. L4 showed IPC can be made far cheaper, but the cost never reaches zero.

> [!example] The Tanenbaum–Torvalds debate
> In 1992 Andrew Tanenbaum, author of MINIX, posted that "Linux is obsolete" because it was monolithic. Linus Torvalds replied that the performance and simplicity of a monolithic design mattered more in practice. Three decades later both sides have a point: Both designs remain in use; their names alone do not establish performance, reliability or certification suitability.



## Key takeaways
- A loadable Linux module remains inside the privileged kernel.
- Microkernels isolate services in separate processes, with IPC and deployment-specific assurance trade-offs.

## Further reading
- [Introduction to Operating Systems — OSTEP (free textbook)](https://pages.cs.wisc.edu/~remzi/OSTEP/intro.pdf)
- [Kernel (operating system) — Wikipedia](https://en.wikipedia.org/wiki/Kernel_(operating_system))
- [Microkernel — Wikipedia](https://en.wikipedia.org/wiki/Microkernel)
- [Protection ring — Wikipedia](https://en.wikipedia.org/wiki/Protection_ring)
- [Tanenbaum–Torvalds debate — Wikipedia](https://en.wikipedia.org/wiki/Tanenbaum%E2%80%93Torvalds_debate)
- [L4 microkernel family — Wikipedia](https://en.wikipedia.org/wiki/L4_microkernel_family)
- [seL4 proof scope](https://sel4.systems/Verification/proofs.html)
