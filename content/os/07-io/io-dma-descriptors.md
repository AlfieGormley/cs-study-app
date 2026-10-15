---
id: io-dma-descriptors
title: DMA, descriptor rings and isolation
level: basic
minutes: 3
summary: DMA moves payloads without a CPU transfer for every data-register access.
sourceLesson: io-hardware
---

## DMA: stop copying bytes by hand

Interrupts fix the waiting problem but not the copying problem. When the CPU itself moves the data (programmed I/O), the number of transfers through the data register is simply the transfer size divided by how many bytes one load or store can carry:

```formula
N = S / w
N = 1,048,576 B / 8 B
N = 131,072
where
N: the number of separate CPU transfers through the data register (a plain count, no unit)
S: the size of the whole transfer, in bytes (B); here 1 MiB = 1,048,576 B
w: the width of one access to the data register, in bytes (B); here 8 B, a 64-bit load or store
B: byte, a group of 8 bits
MiB: mebibyte, 1,048,576 bytes
In words: copying 1 MiB eight bytes at a time takes 131,072 separate CPU transfers, and each one is a load from the device paired with a store to RAM (or the reverse).
```

So a single 1 MiB read costs over 130,000 loads and stores of pure plumbing. The count assumes the data register is 8 bytes wide and ignores the extra copy from the kernel into the application's buffer; a narrower data register makes it larger still.

**Direct memory access (DMA)** hands the copy to hardware. The driver tells the device "transfer this many bytes to or from this DMA address", and the device (acting as a **bus master**) reads or writes RAM itself. Completion may be reported by an interrupt, a coalesced interrupt or polling; DMA does not require one interrupt per transfer.

```
         1. program DMA
  CPU ----------------> Device
   ^                      |
   |                      | 2. reads/writes
   | 3. interrupt         v    RAM directly
   +------------------- [ RAM buffer ]
```

High-performance devices go further and use **descriptor rings**: circular arrays in RAM, each entry describing a buffer. The driver fills in descriptors and bumps a "tail" device register (a **doorbell**); the device consumes descriptors, does the DMA and marks them complete. NVMe queues and network card RX/TX rings both work this way, and io_uring borrowed the idea for software.

DMA brings its own concerns:

- **DMA addresses.** In the conventional DMA model, drivers supply mapped device-visible addresses using the DMA API (`dma_map_single` and related functions), check mapping failures and keep the memory valid for the transfer. User pages may require page pinning; kernel allocations have different lifetime rules. Shared Virtual Addressing is a separate supported-device mechanism that can use process virtual addresses.
- **Cache coherence.** The CPU's cache may hold stale copies of a buffer the device just wrote. Coherency depends on the platform and mapping type. Drivers must obey DMA ownership/synchronization rules even on coherent systems; the DMA API provides platform-specific cache maintenance where required. Coherency does not remove ordering requirements.
- **Security.** A device that can write anywhere in RAM can overwrite the kernel. An **IOMMU** (Intel VT-d, AMD-Vi) gives devices their own page tables so they can only reach buffers mapped for them. This is one part of device-assignment isolation; safe passthrough also depends on isolation groups, interrupt handling, reset behavior and correct configuration.

## Key takeaways
- DMA moves payloads without a CPU transfer for every data-register access.
- Mapping, ownership, ordering and isolation remain driver responsibilities.

## Further reading
- [I/O Devices — Operating Systems: Three Easy Pieces (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/file-devices.pdf)
- [Interrupt Handling — Linux Device Drivers, 3rd ed., ch. 10 (PDF)](https://static.lwn.net/images/pdf/LDD3/ch10.pdf)
- [Linux generic IRQ handling — kernel docs](https://www.kernel.org/doc/html/latest/core-api/genericirq.html)
- [Workqueue — kernel docs](https://www.kernel.org/doc/html/latest/core-api/workqueue.html)
- [Direct memory access — Wikipedia](https://en.wikipedia.org/wiki/Direct_memory_access)
- [Interrupt handler — Wikipedia](https://en.wikipedia.org/wiki/Interrupt_handler)
