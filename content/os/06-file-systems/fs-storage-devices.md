---
id: fs-storage-devices
title: HDDs, SSDs, NVMe and RAID
level: advanced
minutes: 15
summary: How spinning disks and flash actually store data, what the flash translation layer hides, why NVMe replaced SATA, and the capacity, performance and failure maths of RAID.
---

Everything above this point (page cache, journals, extents) exists to cope with the device underneath. Device-specific tuning can perform differently on flash and spinning disks, and a RAID layout chosen without doing the maths can lose data during its own repair.

This lesson works from the physics up: what a hard disk and an SSD physically do, the numbers that follow from that, and how RAID combines devices.

## Hard disk drives

A hard disk is a stack of spinning magnetic platters with a read/write head on an arm for each surface.

```
   platter (spins at 7,200 rpm)
  .---------------------------.
 /  track = one ring of data   \
|     .-----------------.       |
|    /   sector (4 KiB)  \      |
|   |         o  <- spindle     |
|    \                   /      |
|     '-----------------'       |
 \            ^                /
  '-----------|---------------'
        head on actuator arm
```

To read a sector, three things happen in turn:

1. **Seek**: move the arm to the right track. The cost depends on the drive, request distance and scheduling; use a measured or specified seek time for calculations.
2. **Rotational latency**: wait for the sector to come round under the head. On average half a revolution.
3. **Transfer**: read the bits as they pass. Fast once you're there: throughput depends on the drive and track location.

At 7,200 rpm one revolution takes 60 / 7200 s = 8.33 ms, so the average rotational wait is **4.17 ms**.

> [!example] Random vs sequential on one disk
> In an illustrative queue-depth-one model with an 8 ms mean seek and 200 MB/s transfer rate, a random 4 KiB read costs about 8 ms seek + 4.2 ms rotation + 0.02 ms transfer ≈ **12 ms**. That's about **80 random IOPS**, or 0.33 MB/s.
>
> Reading sequentially, the drive pays the seek once and then streams at ~200 MB/s. Those assumed rates give a sequential/random throughput ratio around 600; this is an arithmetic model, not a benchmark of an identified disk.

That ratio drove decades of file system design: block groups to keep an inode near its data, extents and delayed allocation for long runs, read-ahead, I/O schedulers that sort requests by position, and log-structured designs that turn random writes into sequential ones.

Two more details matter in practice:

- **Sector size.** Many drives use 4 KiB physical sectors; verify the actual model's logical and physical sizes. Many still present 512-byte logical sectors (**512e**), so a misaligned 4 KiB write straddles two physical sectors and turns into a read-modify-write. Partitions should start on a 1 MiB boundary, which modern tools do by default.
- **SMR** (shingled magnetic recording) overlaps tracks like roof tiles to fit more data. Rewriting one track disturbs its neighbours, so random writes are very slow once the drive's cache region fills. Suitability depends on host-managed versus drive-managed SMR, workload and controller support. Sustained random writes or rebuilds can encounter expensive band rewriting; do not assume every SMR deployment has the same behavior.

## Flash: how NAND works

An SSD stores bits as charge trapped in **NAND flash** cells. Storing more bits per cell raises density but lowers speed and endurance:

| Type | Bits/cell |
|---|---|
| SLC | 1 |
| MLC (usual two-bit usage) | 2 |
| TLC | 3 |
| QLC | 4 |

> [!note] Device-specific evidence gap
> No identified NAND datasheets or reproducible drive benchmarks accompany this lesson. Generic P/E-cycle ranges, guaranteed latency/throughput classes and universal power-loss-protection claims are omitted. Cell generation, controller, workload and device specifications determine those values.

Flash has three rules that shape everything else:

1. You **read** and **program** (write) a **page**, with a device-specific page size.
2. For the teaching overwrite model, a page must first be **erased**; real NAND has device-specific partial/multi-pass programming restrictions, and you can only **erase** a whole **block**, containing multiple pages; geometry varies by device.
3. Each block survives a limited number of **program/erase (P/E) cycles** before it wears out.

```
 block (erase unit, e.g. 256 pages)
 +------+------+------+-----+------+
 | pg 0 | pg 1 | pg 2 | ... | pg N |
 +------+------+------+-----+------+
  page = read/program unit (16 KiB)
```

So flash can't overwrite in place. Changing 4 KiB inside a block that's full of live data would mean copying the whole block out, erasing it, and writing it all back: slow, and it wears the flash.

## The flash translation layer

The SSD's controller hides all of this behind the same interface a disk has: read or write logical block address (LBA) N. The firmware that does the hiding is the **flash translation layer (FTL)**. It is a little log-structured file system inside the drive.

- **Out-of-place writes.** A write to LBA 7 goes to the next free page. The FTL updates a **mapping table** (LBA 7 → block 52, page 3) and marks the old page **invalid**.
- **Garbage collection (GC).** When free blocks run low, the FTL picks a block with many invalid pages, copies its still-valid pages elsewhere, and erases it.
- **Wear levelling.** It spreads erases evenly, occasionally moving cold data so that its blocks get their share of wear.
- **Mapping table.** A page-level map with a 4-byte entry per 4 KiB is about 1 GiB per TiB of flash, illustrating why mapping metadata can be large. Controllers use varied mapping granularities and caches; some DRAM-less NVMe designs use optional host-memory-buffer support. Performance depends on the implementation and workload.

### Write amplification

GC copies live data, so the flash absorbs more writes than the host sent. The ratio is **write amplification (WA)**:

```
WA = flash bytes written
     / host bytes written
```

If GC reclaims a block in which a fraction *u* of pages are still valid, it must copy *u* of a block to free (1 − *u*) of a block. Every page of new host data then costs roughly 1 / (1 − *u*) page writes:

| Valid when cleaned (u) | WA |
|---|---|
| 0.25 | 1.33 |
| 0.50 | 2 |
| 0.80 | 5 |
| 0.90 | 10 |

A drive that is nearly full of live data has to clean blocks with high *u*, so WA soars, throughput falls and the flash wears faster. Two things keep *u* down:

- **Over-provisioning.** Drives keep spare flash the host can't see (in an amount specified by the device design). Additional never-written or successfully discarded LBAs can provide spare space to the FTL. Merely deleting a partition does not necessarily invalidate previously written LBAs.
- **TRIM / discard.** When a file is deleted, the file system tells the drive which LBAs are now unused. Without TRIM the FTL must assume they're still live and keep copying them. On Linux, run `fstrim` periodically (most distributions ship an `fstrim.timer`) or mount with `discard`.

> [!warning] The SSD performance cliff
> A prepared SSD may initially have substantial erased capacity and/or an SLC cache. Factory state and firmware vary. Under sustained random writes, free blocks run out, GC kicks in, and write throughput can drop to a fraction of the headline figure, with latency spikes when the host's write waits behind GC. Benchmark SSDs in a **steady state**, after filling them, not fresh out of the box.

### Endurance and power loss

Drives are rated in **TBW** (terabytes written) or **DWPD** (drive writes per day over the warranty). A hypothetical 1 TB drive rated 0.3 DWPD for five365-day years corresponds to **547.5 TB** of rated host writes. This is a rating under defined workload/warranty conditions, not an exact failure threshold. Internal WA affects physical wear, but do not divide a host-TBW rating by WA again as though it were a raw-flash budget.

Some SSDs buffer data or mapping metadata in volatile memory. Power-loss protection can preserve specified state, but its coverage and presence vary. A compliant unprotected device can still honor flushes by persisting data before completion; one that dishonors the durability contract can lose acknowledged data. No universal enterprise/consumer fsync-speed ordering is implied.

## SATA, SAS and NVMe

The interface between host and device mattered little when the device took 10 ms. Flash made it the bottleneck.

| | AHCI/SATA | NVMe |
|---|---|---|
| Link | SATA 6 Gb/s | PCIe lanes |
| Throughput | Device and workload dependent | Device, PCIe generation/width and workload dependent |
| I/O queues | one command list per AHCI port | protocol space for up to 65,535 I/O queues |
| Queue entries | up to 32 per AHCI port | protocol limit up to 65,536 per I/O queue; device limits can be much lower |

AHCI provides one command list per port with up to 32 outstanding commands. **NVMe** (2011) talks to flash over PCIe with many deep queues held in host memory:

```
 core 0  [SQ0][CQ0] --.
 core 1  [SQ1][CQ1] ---+--> NVMe controller
 core 2  [SQ2][CQ2] --'     (PCIe doorbell)
```

Drivers can map CPUs onto multiple hardware submission/completion queues, reducing shared contention. Queue counts depend on controller/driver limits; multiple CPUs can share a queue, and not every operation is lock-free. Linux's **blk-mq** block layer is built around this. Actual throughput and latency must be specified together with queue depth, workload and device; protocol queue capacity is not an achieved IOPS guarantee.

That changes the software picture. In an illustrative low-latency device workload, software submission and completion overhead can become a material fraction of total latency. That's why NVMe systems often use the `none` I/O scheduler (mechanical seek minimization is unnecessary, though merging, fairness and latency policy can still matter), why `io_uring` and polling exist, and why the next module looks at them.

## RAID: combining disks

**RAID** (redundant array of independent disks) spreads data over several devices for capacity, speed, survival, or all three. On Linux it's usually done in software with `md` (`mdadm`), by LVM, or inside ZFS and Btrfs.

Data is split into **stripe units** (chunks, often 64–512 KiB) laid across the disks. For equal disks of capacity C and N active disks, ignoring metadata/reserves and assuming healthy arrays, the table gives ideal capacity and isolated uncached small-write operations. RAID10 here means conventional two-way mirrored pairs:

| Level | Usable | Survives | Small-write cost |
|---|---|---|---|
| RAID 0 | N·C | no failures | 1 I/O |
| RAID 1 | C (N copies) | N − 1 | N I/Os |
| RAID 10 | N·C / 2 | 1 per mirror | 2 I/Os |
| RAID 5 | (N − 1)·C | 1 | 4 I/Os |
| RAID 6 | (N − 2)·C | 2 | 6 I/Os |

RAID 5 stores parity: the XOR of the data chunks in a stripe, rotating which disk holds it.

```
        disk0 disk1 disk2 disk3
stripe0  D0    D1    D2    P0
stripe1  D3    D4    P1    D5
stripe2  D6    P2    D7    D8

P0 = D0 xor D1 xor D2
```

If disk1 dies, D1 = D0 ⊕ D2 ⊕ P0. XOR is its own inverse, so any one missing chunk can be rebuilt from the rest. RAID 6 adds a second, independent syndrome (Reed–Solomon style), so it survives any two failures.

### The small-write penalty

Updating one 4 KiB chunk in RAID 5 means keeping parity correct without reading the whole stripe:

```
1. read old D1
2. read old P0
3. P0' = P0 xor D1 xor D1'
4. write D1', write P0'
```

That is **4 I/Os** for one logical write (RAID 6 needs 6, because two parities change). A full-stripe write avoids it: compute parity from the new data and write all chunks once.

> [!example] IOPS calculation
> Assume eight HDDs each deliver150 random IOPS for this workload, with perfect balance and enough concurrency:1,200 raw IOPS.
>
> - Random reads in an ideal balanced workload: up to about **1,200** IOPS; actual scheduling and layout can reduce this.
> - Random writes, RAID 10: 1,200 / 2 = **600**.
> - Random writes, RAID 5: 1,200 / 4 = **300**.
> - Random writes, RAID 6: 1,200 / 6 = **200**.
>
> For a 70/30 read/write mix on RAID 5, each logical I/O costs 0.7 × 1 + 0.3 × 4 = 1.9 disk I/Os, so the array delivers about 1,200 / 1.9 ≈ **630** IOPS.

### The write hole

If power fails after D1' is written but before P0', the stripe's parity is wrong, and nothing records that. If a disk later fails, the rebuild uses bad parity and silently produces garbage. This is the **RAID 5 write hole**. Fixes: a battery-backed controller cache, md's write journal or partial parity log, or ZFS's **RAID-Z**, which uses variable-width stripes and copy-on-write so it never updates a stripe in place.

### Rebuilds and unrecoverable read errors

When one disk in a RAID 5 dies, the array is running with no redundancy until the rebuild finishes, and a conventional full-device rebuild reconstructs the failed member by reading the corresponding allocated array stripes on surviving members. Optimized/partial rebuilds and filesystem-aware layouts can skip unused or known-clean ranges.

Device specifications can state nonrecoverable-read-error limits over bits read. Such a limit is not, by itself, an observed independent per-bit probability model. For unit conversion, 10¹⁴ bits equals 12.5 TB.

> [!example] Rebuilding 4 × 16 TB in RAID 5
> The rebuild reads 3 × 16 TB = 48 TB = 3.84 × 10¹⁴ bits.
>
> If, purely for a mathematical scenario, errors follow an independent Poisson model with mean rate 1 per 10¹⁴ bits, the expected count is 3.84 and P(zero)=e^−3.84≈**2.15%**. A datasheet limit alone does not justify this distribution.
>
> No empirical rebuild-failure probability follows without measured error behavior and rebuild details. At150 MB/s per parallel survivor/replacement stream,16 TB takes about29.6 hours before overhead; treating150 MB/s as aggregate48 TB read bandwidth instead gives about88.9 hours. Another complete member failure exceeds RAID5 redundancy, while a URE can affect a stripe or abort recovery depending on implementation.

That is why large-capacity arrays use RAID 6, RAID-Z2/Z3 or mirrors, and why big storage systems (Ceph, HDFS, S3) replicate or erasure-code across machines instead.

Last pitfalls:

- **RAID is not a backup.** It faithfully replicates `rm -rf`, ransomware and file system corruption.
- **Correlated failures matter.** Shared environment, age, firmware and workload can invalidate independence assumptions; this does not establish that a particular batch will fail together.
- **RAID 0 multiplies risk.** A member failure can make a striped RAID0 volume unusable even though some surviving sectors remain readable. With independent equal small failure probability p over a chosen interval, array failure probability is 1−(1−p)^4≈4p; correlation and repair alter reliability models.

## Key takeaways
- HDD seek and rotation make access locality important; use identified device/workload measurements rather than a universal IOPS range.
- NAND flash reads and programs pages, erases whole blocks and wears out; the FTL hides this with out-of-place writes, a mapping table, garbage collection and wear levelling.
- Write amplification is about 1 / (1 − u) for GC victims with valid fraction u; over-provisioning and TRIM keep it low, and full drives fall off a performance cliff.
- NVMe supports multiple deep I/O queues; actual CPU-to-queue mapping and latency depend on implementation and workload.
- RAID 5/6 trade capacity for parity, with a 4/6-I/O small-write penalty and a write hole; long rebuilds on large disks are risky, so large arrays favour double parity or mirrors.

## Further reading
- [OSTEP: Hard Disk Drives (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/file-disks.pdf)
- [OSTEP: Flash-based SSDs (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/file-ssd.pdf)
- [OSTEP: Redundant Arrays of Inexpensive Disks (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/file-raid.pdf)
- [Write amplification — Wikipedia](https://en.wikipedia.org/wiki/Write_amplification)
- [NVM Express — Wikipedia](https://en.wikipedia.org/wiki/NVM_Express)
- [Standard RAID levels — Wikipedia](https://en.wikipedia.org/wiki/Standard_RAID_levels)
- [RAID arrays (md) — Linux kernel documentation](https://docs.kernel.org/admin-guide/md.html)
- [Backblaze hard drive test data](https://www.backblaze.com/cloud-storage/resources/hard-drive-test-data)
