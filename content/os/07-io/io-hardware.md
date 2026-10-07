---
id: io-hardware
title: How I/O works
level: basic
minutes: 12
summary: Device controllers and registers, polling versus interrupts, DMA, what a device driver does, and how Linux splits interrupt handling into top and bottom halves.
---

A CPU on its own can only compute. Everything useful it does with the outside world (reading a disk, sending a packet, drawing a pixel, noticing a key press) goes through **I/O devices**. The OS's job is to make thousands of wildly different devices look like a few simple abstractions: files, sockets and block devices.

This lesson looks at the hardware side of that bargain: how the CPU actually talks to a device, and how it finds out that the device has finished.

## Devices, controllers and registers

A device is usually two things: the physical mechanism (flash chips, a radio, a motor) and a **device controller**, a small chip that drives it. The controller is what the CPU talks to. Modern controllers are serious computers: an NVMe SSD controller or a 100 Gb/s network card has its own processor cores, firmware and memory.

The CPU sees a controller through a handful of **registers**:

| Register | Purpose |
|---|---|
| Status | Is the device busy? Did it fail? |
| Command | What to do next |
| Data | Bytes going in or out |

The CPU reaches those registers in one of two ways:

- **Port-mapped I/O**: a separate address space with special instructions (`in` and `out` on x86). Mostly legacy today.
- **Memory-mapped I/O (MMIO)**: the registers appear at physical memory addresses. An appropriately mapped load/store can access the device rather than RAM. Kernel drivers use accessors such as `readl`/`writel` and follow ordering rules; a plain C pointer access is not a portable substitute. PCIe devices expose their registers this way through **BARs** (base address registers).

A simple protocol for writing one block to a device then looks like this:

```
1. while (STATUS == BUSY) ;  /* wait */
2. write data into DATA register
3. write WRITE into COMMAND register
4. while (STATUS == BUSY) ;  /* wait */
```

That is the canonical example from *Operating Systems: Three Easy Pieces*, and it has two problems. Steps 1 and 4 burn CPU while waiting, and in step 2 the CPU copies every byte itself. The rest of this lesson is about fixing both.

## Polling: just keep asking

Steps 1 and 4 are **polling** (busy-waiting here). Programmed I/O describes CPU-driven data transfer, a separate question from whether readiness is polled or interrupt-signalled. The CPU repeatedly reads the status register until the device is ready.

Polling sounds wasteful, and for slow devices it is. A disk that takes 5 ms to respond would have the CPU spin through millions of useless loop iterations. But polling has real advantages:

- **Avoid interrupt entry and wakeup overhead.** Polling still costs status reads, instructions, cache traffic and CPU time.
- **Potentially lower notification latency.** Detection depends on polling interval, device access cost and scheduling; no nanosecond guarantee follows.
- **Control over polling cadence.** Other interrupts and scheduling can still interrupt the polling CPU.

Examples include DPDK, SPDK and Linux NAPI. io_uring distinguishes `IOPOLL` (supported I/O completion polling) from `SQPOLL` (a kernel thread polling the software submission queue); the latter does not itself mean device completion polling.

> [!note] Timing evidence gap
> No identified device benchmark accompanies this lesson. Fixed interrupt/MMIO timings, universal fastest-path rankings and guaranteed nanosecond completion detection are omitted. Numeric quiz timings are explicit models.

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

On modern PCs the interrupt goes through an **interrupt controller** (the APIC on x86, the GIC on Arm), which routes it to a particular CPU. PCIe devices use **MSI/MSI-X** (message-signalled interrupts): instead of a dedicated wire, the device writes a small message to a special address. MSI-X lets one device have many independent interrupt vectors, so a network card can give each receive queue its own interrupt and its own CPU. You can see the counts per CPU in `/proc/interrupts`.

### When interrupts lose

Each interrupt costs something: saving state, running the handler, cache and TLB pollution, and returning. The cost depends on platform, handler and scheduling; use measured values for a particular workload.

That is nothing for a keyboard. At sufficiently high event rates, per-packet interrupts can consume the CPU budget. The CPU spends all its time entering and leaving handlers and never runs the code that consumes the packets. This is **receive livelock**: throughput collapses as load rises.

| Approach | Best when | Weakness |
|---|---|---|
| Polling | Device fast or busy | Wastes CPU when idle |
| Interrupts | Device slow or idle | Overhead per event |
| Hybrid | Load varies | More complex |

The standard fix is a **hybrid**: take an interrupt for the first event, then switch it off and poll while work keeps arriving, re-enabling interrupts when the queue drains. Linux's networking stack calls this **NAPI**. Devices can also **coalesce** interrupts, raising one per batch of events or according to configurable timer or event-count thresholds.

## DMA: stop copying bytes by hand

Interrupts fix the waiting problem but not the copying problem. If the CPU moves a 1 MiB transfer through a data register 8 bytes at a time, that is over 130,000 loads and stores of pure plumbing.

**Direct memory access (DMA)** hands the copy to hardware. The driver tells the device "transfer this many bytes to or from this DMA address", and the device (acting as a **bus master**) reads or writes RAM itself. Completion may be reported by an interrupt, a coalesced interrupt or polling; DMA does not require one interrupt per transfer.

```
         1. program DMA
  CPU ----------------> Device
   ^                      |
   |                      | 2. reads/writes
   | 3. interrupt         v    RAM directly
   +------------------- [ RAM buffer ]
```

High-performance devices go further and use **descriptor rings**: circular arrays in RAM, each entry describing a buffer. The driver fills in descriptors and bumps a "tail" register (a **doorbell**); the device consumes descriptors, does the DMA and marks them complete. NVMe queues and network card RX/TX rings both work this way, and io_uring borrowed the idea for software.

DMA brings its own concerns:

- **DMA addresses.** In the conventional DMA model, drivers supply mapped device-visible addresses using the DMA API (`dma_map_single` and related functions), check mapping failures and keep the memory valid for the transfer. User pages may require pinning; kernel allocations have different lifetime rules. Shared Virtual Addressing is a separate supported-device mechanism that can use process virtual addresses.
- **Cache coherence.** The CPU's cache may hold stale copies of a buffer the device just wrote. Coherency depends on the platform and mapping type. Drivers must obey DMA ownership/synchronization rules even on coherent systems; the DMA API provides platform-specific cache maintenance where required. Coherency does not remove ordering requirements.
- **Security.** A device that can write anywhere in RAM can overwrite the kernel. An **IOMMU** (Intel VT-d, AMD-Vi) gives devices their own page tables so they can only reach buffers mapped for them. This is one part of device-assignment isolation; safe passthrough also depends on isolation groups, interrupt handling, reset behavior and correct configuration.

## Device drivers

In the conventional in-kernel model, a **device driver** is code that knows one kind of controller's registers and protocol, and presents it through a generic interface. On Linux:

- **Character devices** (`/dev/ttyS0`, `/dev/null`) expose device-specific file operations, often including `read`, `write` and `ioctl`; not every character device is a simple byte stream.
- **Block devices** (`/dev/nvme0n1`) are arrays of fixed-size blocks accessed through the block layer and its I/O scheduler. File systems sit on top (see the previous module).
- **Network devices** (`eth0`) do not appear in `/dev` at all; they plug into the networking stack and are reached through sockets.

The driver is where the generic `read()` turns into "write these registers, program this DMA descriptor, sleep until the interrupt". In-kernel driver bugs can crash or compromise the kernel. Userspace driver frameworks provide a different execution model.

## Interrupt handling: top and bottom halves

A hard interrupt handler runs at an awkward moment. It has pre-empted whatever was running, often with further interrupts disabled on that CPU, and it **cannot sleep** (there is no process context to put to sleep). If it is slow, other interrupts wait and latency suffers everywhere.

So Linux splits the work in two:

- The **top half** (the hard IRQ handler) does the bare minimum, fast: check the device really raised the interrupt (lines can be shared), acknowledge it, grab any data that would otherwise be lost, and schedule the rest.
- Deferred work handles remaining processing later; its permitted operations depend on execution context.

Linux has several bottom-half mechanisms:

| Mechanism | Context | Can sleep? |
|---|---|---|
| Softirq | Interrupt | No |
| Tasklet | Interrupt | No |
| Threaded workqueue | Kernel thread | Yes, subject to locking rules |
| BH workqueue (`WQ_BH`) | Softirq | No |
| Threaded IRQ | Kernel thread | Yes |

**Softirqs** are a small fixed set (networking receive and transmit, block completion, timers and a few more). They run on return from an interrupt or, when they pile up, in the per-CPU `ksoftirqd` threads. **Tasklets** are built on softirqs and are being phased out in favour of BH workqueues. **Threaded IRQs** give each handler a dedicated kernel thread for its bottom half:

```c
static irqreturn_t top(int irq, void *p)
{
    struct mydev *d = p;
    u32 st = readl(d->regs + STATUS);

    if (!(st & IRQ_PENDING))
        return IRQ_NONE;   /* not ours */
    writel(st, d->regs + IRQ_ACK);
    return IRQ_WAKE_THREAD;
}

static irqreturn_t bottom(int irq, void *p)
{
    /* may sleep, take mutexes, etc. */
    process_completions(p);
    return IRQ_HANDLED;
}

/* During setup; check the return value. */
request_threaded_irq(irq, top, bottom,
        IRQF_SHARED, "mydev", d);
```

This is a driver fragment, not a complete loadable module. The device-specific acknowledgement/masking protocol must keep interrupt delivery and completion processing safe; production setup must check registration failure and arrange teardown.

Returning `IRQ_NONE` correctly reports that this device did not handle the interrupt. Shared-line dispatch calls the registered handlers regardless of one handler claiming it; return values also support unhandled-interrupt diagnosis.

> [!example] A network packet, end to end
> The NIC DMAs a frame into a ring buffer and raises an MSI-X interrupt. The top half masks that queue's interrupt and schedules NAPI. The `NET_RX` softirq then polls the ring, builds packet structures and pushes them up through IP and TCP. Lesson 6 follows this path in detail.

## Putting it together

An illustrative blocking buffered `read()` that misses the page cache on an interrupt-driven NVMe path can proceed as follows:

1. The file system maps the file offset to a block; the block layer builds a request.
2. The NVMe driver writes a command into a submission queue in RAM (a descriptor ring) and rings the doorbell register via MMIO.
3. The process sleeps.
4. The SSD DMAs the data into the page cache and posts a completion entry.
5. An MSI-X interrupt fires; the handler reaps completions and wakes the process.
6. The kernel copies the data to the user buffer and `read()` returns.

## Key takeaways
- The CPU talks to a device controller through registers, almost always memory-mapped (MMIO).
- Polling spends CPU to check readiness and can reduce notification latency; interrupts allow idle waiters to sleep. High-rate systems use a hybrid (NAPI) or interrupt coalescing.
- DMA lets the device move data to and from RAM itself. Descriptor rings plus doorbell registers are the standard high-performance interface. A correctly configured IOMMU restricts DMA mappings as part of device isolation.
- Drivers turn generic calls like `read()` into device-specific register and DMA operations; Linux groups them as character, block and network devices.
- Hard IRQ handlers cannot sleep and should be short. Deferred mechanisms differ: softirqs/tasklets/BH workqueues cannot sleep; suitable threaded workqueues and threaded IRQ handlers can.

## Further reading
- [I/O Devices — Operating Systems: Three Easy Pieces (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/file-devices.pdf)
- [Interrupt Handling — Linux Device Drivers, 3rd ed., ch. 10 (PDF)](https://static.lwn.net/images/pdf/LDD3/ch10.pdf)
- [Linux generic IRQ handling — kernel docs](https://www.kernel.org/doc/html/latest/core-api/genericirq.html)
- [Workqueue — kernel docs](https://www.kernel.org/doc/html/latest/core-api/workqueue.html)
- [Direct memory access — Wikipedia](https://en.wikipedia.org/wiki/Direct_memory_access)
- [Interrupt handler — Wikipedia](https://en.wikipedia.org/wiki/Interrupt_handler)
