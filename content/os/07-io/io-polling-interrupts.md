---
id: io-polling-interrupts
title: Polling, interrupts and receive livelock
level: basic
minutes: 4
summary: Polling trades CPU time for active readiness checks.
sourceLesson: io-hardware
---

## Polling: just keep asking

Steps 1 and 4 are **polling** (busy-waiting here). Programmed I/O describes CPU-driven data transfer, a separate question from whether readiness is polled or reported by an interrupt. The CPU repeatedly reads the status register until the device is ready.

Polling sounds wasteful, and for slow devices it is. A disk that takes 5 ms to respond would have the CPU spin through millions of useless loop iterations. But polling has real advantages:

- **Avoid interrupt entry and wakeup overhead.** Polling still costs status reads, instructions, cache traffic and CPU time.
- **Potentially lower notification latency.** Detection depends on polling interval, device access cost and scheduling; no nanosecond guarantee follows.
- **Control over polling cadence.** Other interrupts and scheduling can still interrupt the polling CPU.

Examples include DPDK, SPDK and Linux NAPI. io_uring distinguishes `IOPOLL` (supported I/O completion polling) from `SQPOLL` (a kernel thread polling the software submission queue); the latter does not itself mean device completion polling.

> [!note] Timing evidence gap
> No identified device benchmark accompanies this lesson. Fixed interrupt/MMIO timings, universal rankings of the fastest code path and guaranteed nanosecond completion detection are omitted. Numeric quiz timings are explicit models.

## Interrupts: let the device tell you

The alternative is for the device to **interrupt** the CPU when it finishes. The sequence is:

1. In a blocking-I/O example, the driver issues the command and the requesting process may **sleep** (block). The scheduler runs something else.
2. The device finishes and raises an interrupt signal.
3. The CPU, between instructions, saves a little state and jumps to the **interrupt handler** registered for that interrupt vector (on x86, via the Interrupt Descriptor Table).
4. The handler acknowledges the device, records the result and wakes the sleeping process.
5. Execution resumes according to interrupt-return and scheduling rules; a newly woken process need not run immediately.

```
CPU:  [ proc A ][ proc B ......][ISR][ A ]
Disk:      [ seek + read ..... ]^
                         interrupt
```

On modern PCs the interrupt goes through an **interrupt controller** (the APIC on x86, the GIC on Arm), which delivers it to a particular CPU. PCIe devices use **MSI/MSI-X** (message-signalled interrupts): instead of a dedicated wire, the device writes a small message to a special address. MSI-X lets one device have many independent interrupt vectors, so a network card can give each receive queue its own interrupt and its own CPU. You can see the counts per CPU in `/proc/interrupts`.

### When interrupts lose

Each interrupt costs something: saving state, running the handler, cache and TLB pollution, and returning. The cost depends on platform, handler and scheduling; use measured values for a particular workload.

That is nothing for a keyboard. At sufficiently high event rates, per-packet interrupts can consume the CPU budget. The CPU spends all its time entering and leaving handlers and never runs the code that consumes the packets. This is **receive livelock**: throughput collapses as load rises.

| Approach | Best when | Weakness |
|---|---|---|
| Polling | Device fast or busy | Wastes CPU when idle |
| Interrupts | Device slow or idle | Overhead per event |
| Interrupts, then polling | Load varies | More complex |

The standard fix is a **hybrid of interrupts and polling**: take an interrupt for the first event, then switch it off and poll while work keeps arriving, re-enabling interrupts when the queue drains. Linux's networking stack calls this **NAPI**. Devices can also use **interrupt coalescing**, raising one interrupt per batch of events or according to configurable timer or event-count thresholds.

## Key takeaways
- Polling trades CPU time for active readiness checks.
- Interrupts allow other work during waits; high event rates motivate batching and NAPI.

## Further reading
- [I/O Devices — Operating Systems: Three Easy Pieces (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/file-devices.pdf)
- [Interrupt Handling — Linux Device Drivers, 3rd ed., ch. 10 (PDF)](https://static.lwn.net/images/pdf/LDD3/ch10.pdf)
- [Linux generic IRQ handling — kernel docs](https://www.kernel.org/doc/html/latest/core-api/genericirq.html)
- [Workqueue — kernel docs](https://www.kernel.org/doc/html/latest/core-api/workqueue.html)
- [Direct memory access — Wikipedia](https://en.wikipedia.org/wiki/Direct_memory_access)
- [Interrupt handler — Wikipedia](https://en.wikipedia.org/wiki/Interrupt_handler)
