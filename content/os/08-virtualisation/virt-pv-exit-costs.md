---
id: virt-pv-exit-costs
title: Paravirtualisation, exits and CPU contention
level: basic
minutes: 4
sourceLesson: virt-hypervisors
summary: Xen PV changes the guest kernel; paravirtual drivers can also accompany hardware-assisted guests.
---

This unit focuses on paravirtualisation, exits and CPU contention. It builds on the earlier virtualisation units in this module.

## Workaround 2: paravirtualisation

The **Xen** project (Cambridge, 2003) took a different route: if the guest is trouble, change the guest. In **paravirtualisation**, the guest kernel is modified to know it is virtualised:

- Instead of executing sensitive instructions, it makes explicit **hypercalls**, the VM equivalent of system calls.
- Instead of loading its own page tables, it asks Xen to validate and install updates, often batched into one hypercall.
- Instead of emulated hardware devices, it uses simple **split drivers**: a front end in the guest passes requests through shared memory rings to a back end in a privileged domain.

```
 guest kernel             Xen
 ------------             ---
 hypercall(mmu_update,
   [pte1, pte2, pte3]) --> validate, apply
                      <--  return
```

The 2003 Xen paper reported low overhead for its evaluated workloads. Kernel adaptation was required; its Windows XP port was incomplete but already ran some user-space programs. Unmodified Windows was not supported by that PV interface.

## Where things stand today

Since 2005–2006, Intel VT-x and AMD-V have made x86 satisfy the spirit of Popek–Goldberg in hardware (next lesson). Binary translation is mostly gone from x86 servers.

Paravirtualisation survived in a different form. Instead of rewriting the whole kernel, modern guests run unmodified on hardware support but use **paravirtual drivers** (virtio, Xen PV drivers, Hyper-V's VMBus), paravirtual clocks and paravirtual spinlocks. Emulating a real network card register by register is slow; a driver that knows it is talking to a hypervisor is fast.

| Technique | Guest changes? | Main cost |
|---|---|---|
| Interpretation | None | Per-instruction software work |
| Trap-and-emulate | None | Needs a virtualisable CPU |
| Binary translation | None | Complexity |
| Paravirtualisation | Kernel adapted | Porting and maintenance |
| Hardware assist | None | Exit cost |


## A toy exit-cost budget

Exit count and per-exit cost combine into CPU time. This hypothetical one-second observation holds both costs and workload fixed; it predicts no real platform benchmark.

```formula
T = N c
T = 50000 × 2 µs = 100000 µs
F = T / Δt
F = 100 ms / 1000 ms = 0.10
where
T: total CPU time spent handling exits during the observation
N: the number of exits observed, here 50000
c: CPU time per exit, here 2 microseconds (µs)
Δt: observation duration, here one second or 1000 milliseconds (ms)
F: the fraction of one CPU-second spent handling exits, with no unit
µs: microsecond, one millionth of a second
ms: millisecond, one thousandth of a second
In words: Fifty thousand two-microsecond exits use one tenth of one CPU-second. Halving the count saves five percentage points only under the fixed-cost assumptions.
```

Steal time instead measures host scheduling time unavailable to a guest vCPU under the platform's accounting. It does not by itself identify a neighbour or promise that moving to a larger instance helps.

## Pitfalls and misconceptions

- **"VMs are slow."** CPU-bound code can approach native speed, but there is no universal overhead percentage. The costs show up in I/O, in memory-heavy workloads (address translation) and in anything that causes many exits.
- **Timing is not virtualised perfectly.** Popek and Goldberg exempted timing from equivalence on purpose. A guest can detect it is virtualised by timing instructions, which malware uses to hide from sandboxes.
- **Overcommit.** Hypervisors can promise more vCPUs or memory than exist. Overcommit can improve utilisation but is not required for consolidation. CPU contention can produce noisy-neighbour effects and steal time: reported periods when a vCPU was runnable but not scheduled.

> [!note] Evidence gaps
> No reproducible benchmark supports a universal VM overhead, interpretation slowdown or historical server-utilisation percentage here, so those figures are omitted. Snapshot/live-migration support and isolation depend on the actual platform and configuration.

## Key takeaways

- Xen PV changes the guest kernel; paravirtual drivers can also accompany hardware-assisted guests.
- Exit work and host scheduling contention are different costs; measure them separately.

## Further reading

- [Formal requirements — Popek and Goldberg (1974, PDF)](https://www.cs.columbia.edu/~cdall/candidacy/pdf/Popek.pdf)
- [Software and hardware virtualisation — Adams and Agesen (2006, PDF)](https://iitd-plos.github.io/col718/ref/asplos235_adams.pdf)
- [Virtual Machine Monitors — OSTEP appendix (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/vmm-intro.pdf)
- [Popek and Goldberg virtualization requirements — Wikipedia](https://en.wikipedia.org/wiki/Popek_and_Goldberg_virtualization_requirements)
- [Xen and the Art of Virtualization (SOSP 2003, PDF)](https://www.cl.cam.ac.uk/research/srg/netos/papers/2003-xensosp.pdf)
- [Hypervisor — Wikipedia](https://en.wikipedia.org/wiki/Hypervisor)
- [x86 virtualization — Wikipedia](https://en.wikipedia.org/wiki/X86_virtualization)
