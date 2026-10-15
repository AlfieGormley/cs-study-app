---
id: io-driver-interrupt-contexts
title: Drivers and deferred interrupt work
level: basic
minutes: 4
summary: Character, block and network drivers expose different generic interfaces.
sourceLesson: io-hardware
---

## Device drivers

In the conventional in-kernel model, a **device driver** is code that knows one kind of controller's device registers and protocol, and presents it through a generic interface. On Linux:

- **Character devices** (`/dev/ttyS0`, `/dev/null`) expose device-specific file operations, often including `read`, `write` and `ioctl`; not every character device is a simple byte stream.
- **Block devices** (`/dev/nvme0n1`) are arrays of fixed-size blocks accessed through the block layer and its I/O scheduler. File systems sit on top (see the previous module).
- **Network devices** (`eth0`) do not appear in `/dev` at all; they plug into the networking stack and are reached through sockets.

The driver is where the generic `read()` turns into "write these device registers, program this DMA descriptor, sleep until the interrupt". In-kernel driver bugs can crash or compromise the kernel. Userspace driver frameworks provide a different execution model.

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
    /* Read device state through MMIO. */
    u32 st = readl(d->regs + STATUS);

    if (!(st & IRQ_PENDING))
        return IRQ_NONE;   /* not ours */
    /* Acknowledge before deferred work. */
    writel(st, d->regs + IRQ_ACK);
    /* Run the registered threaded part. */
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

This is a driver fragment, not a complete loadable module. The device-specific acknowledgement and interrupt-masking protocol must keep interrupt delivery and completion processing safe; production setup must check registration failure and arrange teardown.

Returning `IRQ_NONE` correctly reports that this device did not handle the interrupt. Shared-line dispatch calls the registered handlers regardless of one handler claiming it; return values also support unhandled-interrupt diagnosis.

> [!example] A network packet, end to end
> The NIC DMAs a frame into a ring buffer and raises an MSI-X interrupt. The top half masks that queue's interrupt and schedules NAPI. The `NET_RX` softirq then polls the ring, builds packet structures and pushes them up through IP and TCP. The later receive-path unit follows this in detail.

## Putting it together

An illustrative blocking buffered `read()` that misses the page cache on an interrupt-driven NVMe I/O path can proceed as follows:

1. The file system maps the file offset to a block; the block layer builds a request.
2. The NVMe driver writes a command into a submission queue in RAM (a descriptor ring) and writes the doorbell register via MMIO.
3. The process sleeps.
4. The SSD DMAs the data into the page cache and posts a completion entry.
5. An MSI-X interrupt fires; the handler reaps completions and wakes the process.
6. The kernel copies the data to the user buffer and `read()` returns.

## Key takeaways
- Character, block and network drivers expose different generic interfaces.
- Hard IRQ and softirq work cannot sleep; suitable threaded work can.
- A blocking NVMe read combines file mapping, command queues, DMA and completion handling.

## Further reading
- [I/O Devices — Operating Systems: Three Easy Pieces (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/file-devices.pdf)
- [Interrupt Handling — Linux Device Drivers, 3rd ed., ch. 10 (PDF)](https://static.lwn.net/images/pdf/LDD3/ch10.pdf)
- [Linux generic IRQ handling — kernel docs](https://www.kernel.org/doc/html/latest/core-api/genericirq.html)
- [Workqueue — kernel docs](https://www.kernel.org/doc/html/latest/core-api/workqueue.html)
- [Direct memory access — Wikipedia](https://en.wikipedia.org/wiki/Direct_memory_access)
- [Interrupt handler — Wikipedia](https://en.wikipedia.org/wiki/Interrupt_handler)
