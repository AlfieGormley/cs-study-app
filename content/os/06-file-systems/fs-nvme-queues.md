---
id: fs-nvme-queues
title: SATA and NVMe queueing
level: advanced
minutes: 3
summary: NVMe supports multiple deep queues while AHCI has a smaller command list per port.
sourceLesson: fs-storage-devices
---

This unit focuses on SATA and NVMe queueing. The preceding units provide the file and storage concepts used here.

## SATA, SAS and NVMe

The interface between host and device mattered little when the device took 10 ms. Flash made it the bottleneck.

| | AHCI/SATA | NVMe |
|---|---|---|
| Link | SATA 6 Gb/s | PCIe lanes |
| Throughput | Device and workload dependent | Device, PCIe generation/width and workload dependent |
| I/O queues | one command list per AHCI port | protocol space for up to 65,535 I/O queues |
| Queue entries | up to 32 per AHCI port | up to 65,536 ring slots; at most 65,535 commands outstanding; device limits can be lower |

NVMe distinguishes queue storage slots from usable outstanding commands: a full circular queue must still be distinguishable from an empty one. The [NVM Express 2.1 specification](https://nvmexpress.org/wp-content/uploads/NVM-Express-Base-Specification-Revision-2.1-2024.08.05-Ratified.pdf) states the upper bound as 65,535 outstanding commands per I/O queue.

AHCI provides one command list per port with up to 32 outstanding commands. **NVMe** (2011) talks to flash over PCIe with many deep queues held in host memory:

```
 core 0  [SQ0][CQ0] --.
 core 1  [SQ1][CQ1] ---+--> NVMe controller
 core 2  [SQ2][CQ2] --'     (PCIe doorbell)
```

Drivers can map CPUs onto multiple hardware submission/completion queues, reducing shared contention. Queue counts depend on controller/driver limits; multiple CPUs can share a queue, and not every operation is lock-free. Linux's **blk-mq** block layer is built around this. Actual throughput and latency must be specified together with queue depth, workload and device; protocol queue capacity is not an achieved IOPS guarantee.

That changes the software picture. In an illustrative low-latency device workload, software submission and completion overhead can become a material fraction of total latency. That's why NVMe systems often use the `none` I/O scheduler (mechanical seek minimization is unnecessary, though merging, fairness and latency policy can still matter), why `io_uring` and polling exist, and why the next module looks at them.

## How much concurrency is needed?

Little’s law connects the average number of outstanding requests to throughput and mean time in the same stable system:

```formula
L = λW
L = 800,000 /s × 0.00008 s = 64
λ_max = L_max / W
λ_max = 32 / (0.00008 s) = 400,000 /s
where
L: mean requests in flight, dimensionless
λ: mean completed requests per second (/s), here 800,000
W: mean end-to-end request time in seconds (s), here 80 microseconds or 0.00008 s
L_max: the outstanding-command limit, here 32 for one AHCI port
λ_max: modeled queue-limited throughput per second
s: second
In words: at eighty microseconds per request, eight hundred thousand requests per second needs sixty-four requests outstanding on average.
```

The latency must hold at the target load, and meeting the average concurrency is necessary rather than sufficient. SATA bandwidth, device limits and software can impose tighter constraints. NVMe’s larger queue space does not establish that a device can achieve this workload.

## Key takeaways
- NVMe supports multiple deep queues while AHCI has a smaller command list per port.
- Protocol capacities do not promise achieved throughput or one queue per CPU.

## Further reading
- [OSTEP: Hard Disk Drives (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/file-disks.pdf)
- [OSTEP: Flash-based SSDs (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/file-ssd.pdf)
- [OSTEP: Redundant Arrays of Inexpensive Disks (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/file-raid.pdf)
- [Write amplification — Wikipedia](https://en.wikipedia.org/wiki/Write_amplification)
- [NVM Express — Wikipedia](https://en.wikipedia.org/wiki/NVM_Express)
- [Standard RAID levels — Wikipedia](https://en.wikipedia.org/wiki/Standard_RAID_levels)
- [RAID arrays (md) — Linux kernel documentation](https://docs.kernel.org/admin-guide/md.html)
- [Backblaze hard drive test data](https://www.backblaze.com/cloud-storage/resources/hard-drive-test-data)
