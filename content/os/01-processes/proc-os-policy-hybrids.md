---
id: proc-os-policy-hybrids
sourceLesson: proc-what-os-does
title: "Hybrid kernels and mechanism versus policy"
level: basic
minutes: 3
summary: "Hybrid is a broad design description, not a speed or safety guarantee."
---

Hybrid is a broad design description, not a speed or safety guarantee. This lesson focuses on hybrid kernels and mechanism versus policy.

## Hybrid kernels



Start from a microkernel design, then move performance-critical services back into kernel space.

- **Windows NT** (all modern Windows): a layered kernel and executive, with file systems, the network stack and most drivers running in kernel mode.
- **XNU** (macOS, iOS): the Mach microkernel combined with a large BSD layer and the IOKit driver framework, all running in kernel space.

Critics argue "hybrid" is mostly marketing: once the file system and drivers are in kernel space, the result behaves much like a monolithic kernel with a message-passing internal structure. Both macOS and Windows have since moved some drivers out to user space (Apple's DriverKit, Windows' User-Mode Driver Framework), which shows the trade-off is still live.

### Side by side

| | Monolithic | Micro | Hybrid |
|---|---|---|---|
| In kernel | Almost all | IPC, VM, sched | Most |
| Speed | Workload-dependent | IPC-sensitive | Workload-dependent |
| Service isolation | Shared kernel | Separate processes | Mostly shared kernel |
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
- Hybrid is a broad design description, not a speed or safety guarantee.
- Kernel mechanisms enable policies chosen by system software.

## Further reading
- [Introduction to Operating Systems — OSTEP (free textbook)](https://pages.cs.wisc.edu/~remzi/OSTEP/intro.pdf)
- [Kernel (operating system) — Wikipedia](https://en.wikipedia.org/wiki/Kernel_(operating_system))
- [Microkernel — Wikipedia](https://en.wikipedia.org/wiki/Microkernel)
- [Protection ring — Wikipedia](https://en.wikipedia.org/wiki/Protection_ring)
- [Tanenbaum–Torvalds debate — Wikipedia](https://en.wikipedia.org/wiki/Tanenbaum%E2%80%93Torvalds_debate)
- [L4 microkernel family — Wikipedia](https://en.wikipedia.org/wiki/L4_microkernel_family)
