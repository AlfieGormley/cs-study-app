---
id: io-controller-registers
title: Controllers and device registers
level: basic
minutes: 2
summary: Device registers expose controller status, commands and data.
sourceLesson: io-hardware
---

A CPU on its own can only compute. Everything useful it does with the outside world (reading a disk, sending a packet, drawing a pixel, noticing a key press) goes through **I/O devices**. The OS's job is to make thousands of wildly different devices look like a few simple abstractions: files, sockets and block devices.

This lesson looks at the hardware side of that bargain: how the CPU actually talks to a device, and how it finds out that the device has finished.

## Devices, controllers and device registers

A device is usually two things: the physical mechanism (flash chips, a radio, a motor) and a **device controller**, a small chip that drives it. The controller is what the CPU talks to. Modern controllers are serious computers: an NVMe SSD controller or a 100 Gb/s network card has its own processor cores, firmware and memory.

The CPU sees a controller through a handful of **device registers**:

| Device register | Purpose |
|---|---|
| Status | Is the device busy? Did it fail? |
| Command | What to do next |
| Data | Bytes going in or out |

The CPU reaches those device registers in one of two ways:

- **Port-mapped I/O**: a separate address space with special instructions (`in` and `out` on x86). Mostly legacy today.
- **Memory-mapped I/O (MMIO)**: the device registers appear at physical memory addresses. An appropriately mapped load/store can access the device rather than RAM. Kernel drivers use accessors such as `readl`/`writel` and follow ordering rules; a plain C pointer access is not a portable substitute. PCIe devices expose their device registers this way through **BARs** (base address registers).

A simple protocol for writing one block to a device then looks like this:

```
1. while (STATUS == BUSY) ;  /* wait */
2. write data into DATA register
3. write WRITE into COMMAND register
4. while (STATUS == BUSY) ;  /* wait */
```

That is the canonical example from *Operating Systems: Three Easy Pieces*, and it has two problems. Steps 1 and 4 burn CPU while waiting, and in step 2 the CPU copies every byte itself. The next hardware units address both.

## Key takeaways
- Device registers expose controller status, commands and data.
- MMIO needs platform accessors and ordering rules, rather than ordinary pointer assumptions.

## Further reading
- [I/O Devices — Operating Systems: Three Easy Pieces (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/file-devices.pdf)
- [Interrupt Handling — Linux Device Drivers, 3rd ed., ch. 10 (PDF)](https://static.lwn.net/images/pdf/LDD3/ch10.pdf)
- [Linux generic IRQ handling — kernel docs](https://www.kernel.org/doc/html/latest/core-api/genericirq.html)
- [Workqueue — kernel docs](https://www.kernel.org/doc/html/latest/core-api/workqueue.html)
- [Direct memory access — Wikipedia](https://en.wikipedia.org/wiki/Direct_memory_access)
- [Interrupt handler — Wikipedia](https://en.wikipedia.org/wiki/Interrupt_handler)
