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

A hard disk holds several rotating magnetic platters on one spindle, with a read/write head on an actuator arm for each surface.

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

1. **Seek**: move the actuator arm to the right track. The cost depends on the drive, request distance and scheduling; use a measured or specified seek time for calculations.
2. **Rotational latency**: wait for the sector to come round under the head. On average half a revolution.
3. **Transfer**: read the bits as they pass. Fast once you're there: throughput depends on the drive and track location.

The rotational wait follows from the spin speed. Speeds are quoted in rpm (revolutions per minute), so divide 60 seconds by the rpm to get the time for one turn. A sector is equally likely to be anywhere on the track, so on average you wait half a turn:

```formula
t_rev = 60 s / ω
t_rot = t_rev / 2
t_rev = 60 s / 7,200 = 8.33 ms
t_rot = 8.33 ms / 2 = 4.17 ms
where
t_rev: the time for one full revolution of the platter, in milliseconds (ms)
ω: the spin speed, in revolutions per minute (rpm); typically 5,400 or 7,200 for desktop drives, 10,000 or 15,000 for fast server drives
t_rot: the average rotational latency: the expected wait for the sector to come round under the head
s: second
ms: millisecond, a thousandth of a second
rpm: revolutions per minute
In words: a 7,200 rpm disk turns once every 8.33 ms, so on average a request waits half of that, about 4.17 ms, for its sector to arrive.
```

Doubling the spin speed halves the rotational wait: 15,000 rpm gives 2 ms. Add the seek and transfer, and you get the cost of one random read, and from that how many random reads per second the drive can do:

```formula
t_IO = t_seek + t_rot + t_xfer
t_xfer = S / R
IOPS = 1 / t_IO
t_xfer = 4,096 B / (2 × 10^8 B/s)
t_xfer ≈ 0.00002 s = 0.02 ms
t_IO ≈ 8 ms + 4.2 ms + 0.02 ms ≈ 12 ms
IOPS ≈ 1 / 0.012 s ≈ 80
X = IOPS × S ≈ 80 × 4 KiB/s ≈ 0.33 MB/s
where
t_IO: the time for one random read, in milliseconds (ms)
t_seek: the mean seek time, moving the arm to the right track; here an assumed 8 ms
t_rot: the average rotational latency; here 4.2 ms (7,200 rpm, rounded)
t_xfer: the time to read the data once it is under the head
S: the request size; here 4 KiB = 4,096 bytes (B)
R: the drive's transfer rate; here an assumed 200 MB/s = 2 × 10^8 bytes per second (B/s)
IOPS: I/O operations per second, here random reads served one at a time
X: the resulting throughput for random reads, in megabytes per second (MB/s)
≈: approximately equal to
ms: millisecond, a thousandth of a second
s: second
B: byte
KiB: kibibyte, 1,024 bytes
MB: megabyte, 10^6 bytes
In words: a random 4 KiB read spends about 12 ms getting to the data and only 0.02 ms reading it, so the disk manages about 80 random reads a second, a third of a megabyte per second.
```

> [!example] Random vs sequential on one disk
> The model above is an illustrative queue-depth-one calculation: one request at a time. Reading sequentially, the drive pays the seek once and then streams at ~200 MB/s. Those assumed rates give a sequential/random throughput ratio of about 200 ÷ 0.33 ≈ 600; this is an arithmetic model, not a benchmark of an identified disk.

That ratio drove decades of file system design: block groups to keep an inode near its data, extents and delayed allocation for long runs, read-ahead, I/O schedulers that sort requests by position, and log-structured designs that turn random writes into sequential ones.

Two more details matter in practice:

- **Sector size.** Many drives use 4 KiB physical sectors; verify the actual model's logical and physical sizes. Many still present 512-byte logical sectors (**512e**), so a misaligned 4 KiB write straddles two physical sectors and turns into a read-modify-write. Partitions should start on a 1 MiB boundary, which modern tools do by default.
- **SMR** (shingled magnetic recording) overlaps tracks like roof tiles to fit more data. Rewriting one track disturbs its neighbours, so random writes are very slow once the drive's cache region fills. Suitability depends on host-managed versus drive-managed SMR, workload and controller support. Sustained random writes or rebuilds can encounter expensive band rewriting; do not assume every SMR deployment has the same behavior.

## Flash: how NAND works

An SSD stores bits as charge trapped in **NAND flash** cells. Storing more bits per cell raises density but lowers speed and endurance:

| Type | Bits/cell |
|---|---|
| SLC flash | 1 |
| MLC flash (usual two-bit usage) | 2 |
| TLC flash | 3 |
| QLC flash | 4 |

> [!note] Device-specific evidence gap
> No identified NAND datasheets or reproducible drive benchmarks accompany this lesson. Generic P/E-cycle ranges, guaranteed latency/throughput classes and universal power-loss-protection claims are omitted. Cell generation, controller, workload and device specifications determine those values.

Flash has three rules that shape everything else:

1. You read a **flash page**, and write one with a page program (flash's name for a write); the page size is device-specific.
2. For the teaching overwrite model, a flash page must first be **erased**; real NAND has device-specific partial/multi-pass programming restrictions, and you can only **erase** a whole **block**, containing multiple flash pages; geometry varies by device.
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

- **Out-of-place writes.** A write to LBA 7 goes to the next free flash page. The FTL updates a **mapping table** (LBA 7 → block 52, page 3) and marks the old flash page **invalid**.
- **Garbage collection (GC).** When free blocks run low, the FTL picks a block with many invalid pages, copies its still-valid flash pages elsewhere, and erases it.
- **Wear levelling.** It spreads erases evenly, occasionally moving cold data so that its blocks get their share of wear.
- **Mapping table.** A page-level map with a 4-byte entry per 4 KiB is about 1 GiB per TiB of flash (worked out below), illustrating why mapping metadata can be large. Controllers use varied mapping granularities and caches; some DRAM-less NVMe designs use optional host-memory-buffer support. Performance depends on the implementation and workload.

How big is a page-level mapping table? One entry per mapped unit, times the entry size:

```formula
T = (C / U) × e
T = (2^40 B / 2^12 B) × 4 B
T = 2^28 × 4 B = 2^30 B = 1 GiB
where
T: the size of the mapping table, in bytes (B)
C: the flash capacity being mapped; here 1 TiB = 2^40 bytes (2^40 means 40 copies of 2 multiplied together; 2^10 = 1,024)
U: the mapping unit, the amount of data one entry describes; here 4 KiB = 2^12 bytes
e: the size of one entry; here 4 bytes, enough to name a physical page
B: byte
TiB: tebibyte, 2^40 bytes
KiB: kibibyte, 2^10 bytes
GiB: gibibyte, 2^30 bytes
In words: a terabyte of flash is about 268 million 4 KiB units, and a 4-byte entry for each one needs about a gigabyte of fast memory.
```

### Write amplification

GC copies live data, so the flash absorbs more writes than the host sent. The ratio is **write amplification (WA)**. To predict it, look at what one GC pass costs: if the victim block still has a fraction of valid flash pages, those must be copied before the erase, and only the rest of the block becomes free for new data.

```formula
WA = W_flash / W_host
WA ≈ (u + (1 − u)) / (1 − u)
WA ≈ 1 / (1 − u)
WA ≈ 1 / (1 − 0.75) = 4
where
WA: write amplification, how many bytes reach the flash for each byte the host writes; 1 is ideal
W_flash: bytes actually programmed into the flash, including GC copies
W_host: bytes the host (the computer) asked the drive to write
u: the fraction of flash pages still valid in the blocks GC cleans, from 0 (all invalid) to just under 1 (almost all live)
≈: approximately equal to (a steady-state model that ignores metadata and compression)
In words: cleaning a block copies u of a block of old data to free 1 − u of a block for new data, so each page of new data costs 1 / (1 − u) page writes: at 75% valid, four flash writes per host write.
```

The same formula gives the table below. Notice how fast it grows as the victims get fuller:

| Valid when cleaned (u) | WA |
|---|---|
| 0.25 | 1.33 |
| 0.50 | 2 |
| 0.80 | 5 |
| 0.90 | 10 |

A drive that is nearly full of live data has to clean blocks with high u, so WA soars, throughput falls and the flash wears faster. Two things keep u down:

- **Over-provisioning.** Drives keep spare flash the host can't see (in an amount specified by the device design). Additional never-written or successfully discarded LBAs can provide spare space to the FTL. Merely deleting a partition does not necessarily invalidate previously written LBAs.
- **TRIM / discard.** When a file is deleted, the file system tells the drive which LBAs are now unused. Without TRIM the FTL must assume they're still live and keep copying them. On Linux, run `fstrim` periodically (most distributions ship an `fstrim.timer`) or mount with `discard`.

> [!warning] The SSD performance cliff
> A prepared SSD may initially have substantial erased capacity and/or an SLC cache. Factory state and firmware vary. Under sustained random writes, free blocks run out, GC kicks in, and write throughput can drop to a fraction of the headline figure, with latency spikes when the host's write waits behind GC. Benchmark SSDs in a **steady state**, after filling them, not fresh out of the box.

### Endurance and power loss

Drives are rated in **TBW** (terabytes written) or **DWPD** (drive writes per day over the warranty). The two are linked by the capacity and the warranty length:

```formula
TBW = C × DWPD × 365 × Y
TBW = 1 TB × 0.3 × 365 × 5 = 547.5 TB
where
TBW: terabytes written, the total host writes the drive is rated for, in terabytes (TB)
C: the drive's capacity, in terabytes; here 1 TB
DWPD: drive writes per day, how many times the full capacity may be written each day of the warranty; here 0.3
Y: the warranty period, in years; here 5 (each year counted as 365 days, hence the × 365)
TB: terabyte, 10^12 bytes
In words: writing 30% of a 1 TB drive every day for five years adds up to 547.5 TB of rated writes.
```

This is a rating under defined workload/warranty conditions, not an exact failure threshold. Internal WA affects physical wear, but do not divide a host-TBW rating by WA again as though it were a raw-flash budget.

Some SSDs buffer data or mapping metadata in volatile memory. Power-loss protection can preserve specified state, but its coverage and presence vary. A compliant unprotected device can still honor flushes by persisting data before completion; one that dishonors the durability contract can lose acknowledged data. No universal fsync-speed ordering of enterprise versus desktop drives is implied.

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

Data is split into **stripe units** (chunks, often 64–512 KiB) laid across the disks. Usable capacity depends on how many disks' worth of space goes to copies or parity:

```formula
C_0 = N × C
C_1 = C
C_10 = N × C / 2
C_5 = (N − 1) × C
C_6 = (N − 2) × C
C_5 = (6 − 1) × 4 TB = 20 TB
where
N: the number of active disks in the array
C: the capacity of one disk (all disks equal), e.g. in terabytes (TB)
C_0, C_1, C_10, C_5, C_6: the usable capacity of RAID 0, RAID 1, RAID 10, RAID 5 and RAID 6
TB: terabyte, 10^12 bytes
In words: striping alone keeps every disk's space, a mirror keeps one disk's worth (or half, with mirrored pairs), and parity costs one disk's worth per parity: RAID 5 loses one disk, RAID 6 two.
```

The table summarises capacity, how many failed disks each level survives and the number of disk I/Os one isolated small write costs, ignoring metadata/reserves, caching and assuming a healthy array. RAID10 here means conventional two-way mirrored pairs:

| Level | Usable | Survives | Small-write cost |
|---|---|---|---|
| RAID 0 | N × C | no failures | 1 I/O |
| RAID 1 | C (N copies) | N − 1 | N I/Os |
| RAID 10 | N × C / 2 | 1 per mirror | 2 I/Os |
| RAID 5 | (N − 1) × C | 1 | 4 I/Os |
| RAID 6 | (N − 2) × C | 2 | 6 I/Os |

RAID 5 stores parity: the XOR of the data chunks in a stripe, rotating which disk holds it. In the layout below, D0 to D8 are data chunks and P0 to P2 are the parity chunks for each stripe.

```
        disk0 disk1 disk2 disk3
stripe0  D0    D1    D2    P0
stripe1  D3    D4    P1    D5
stripe2  D6    P2    D7    D8
```

```formula
P_0 = D_0 ⊕ D_1 ⊕ D_2
D_1 = D_0 ⊕ D_2 ⊕ P_0
where
P_0: the parity chunk of stripe 0
D_0, D_1, D_2: the three data chunks of stripe 0, on disks 0, 1 and 2
⊕: XOR (exclusive or), applied bit by bit: a result bit is 1 when the two input bits differ, 0 when they match, so x ⊕ x = 0
In words: parity is the XOR of the data chunks, and because XORing the same value twice cancels it out, XORing the survivors with the parity gives back the missing chunk.
```

If disk1 dies, the second line rebuilds its chunk. XOR is its own inverse, so any one missing chunk can be rebuilt from the rest. For example, with 4-bit chunks 1011, 0110 and 0001, parity is 1100, and 1011 ⊕ 0110 ⊕ 1100 gives back 0001. RAID 6 adds a second, independent syndrome (Reed–Solomon style), so it survives any two failures.

### The small-write penalty

Updating one 4 KiB chunk in RAID 5 means keeping parity correct without reading the whole stripe. XOR the old data out of the parity and the new data in:

```formula
P_0' = P_0 ⊕ D_1 ⊕ D_1'
where
P_0', P_0: the new and old parity chunk of the stripe
D_1, D_1': the old and new contents of the data chunk being updated
⊕: XOR (exclusive or), bit by bit; XORing a value in twice cancels it
In words: the new parity is the old parity with the old data cancelled out and the new data mixed in, so the other data chunks never need to be read.
```

The steps are:

1. Read old D1.
2. Read old P0.
3. Compute the new parity with the formula above.
4. Write the new D1 and the new P0.

That is **4 I/Os** for one logical write (RAID 6 needs 6, because two parities change). A full-stripe write avoids it: compute parity from the new data and write all chunks once.

To estimate what an array delivers, add up the disks' raw IOPS, then divide by the average number of disk I/Os each logical operation costs:

```formula
R = n × r
k = f_r × 1 + f_w × w
IOPS = R / k
R = 8 × 150 = 1,200
k = 0.7 × 1 + 0.3 × 4 = 1.9
IOPS = 1,200 / 1.9 ≈ 630
where
R: the array's raw capacity, in disk I/O operations per second
n: the number of disks; here 8 HDDs
r: random IOPS one disk delivers for this workload; here 150
k: the average number of disk I/Os per logical operation
f_r, f_w: the fractions of operations that are reads and writes (they add up to 1); here 0.7 and 0.3
w: the disk I/Os one small write costs: 2 on RAID 10, 4 on RAID 5, 6 on RAID 6 (a read costs 1)
IOPS: I/O operations per second, here logical operations the array delivers
≈: approximately equal to
In words: eight disks give 1,200 raw IOPS, and a 70/30 mix on RAID 5 spends 1.9 disk I/Os per operation on average, so the array delivers about 630.
```

> [!example] IOPS calculation
> Assume eight HDDs each deliver 150 random IOPS for this workload, with perfect balance and enough concurrency: 1,200 raw IOPS.
>
> - Random reads in an ideal balanced workload: up to about **1,200** IOPS; actual scheduling and layout can reduce this.
> - Random writes, RAID 10: 1,200 / 2 = **600**.
> - Random writes, RAID 5: 1,200 / 4 = **300**.
> - Random writes, RAID 6: 1,200 / 6 = **200**.
> - A 70/30 read/write mix on RAID 5: about **630** (the formula above).

### The write hole

If power fails after D1' is written but before P0', the stripe's parity is wrong, and nothing records that. If a disk later fails, the rebuild uses bad parity and silently produces garbage. This is the **RAID 5 write hole**. Fixes: a battery-backed controller cache, md's write journal or partial parity log, or ZFS's **RAID-Z**, which uses variable-width stripes and copy-on-write so it never updates a stripe in place.

### Rebuilds and unrecoverable read errors

When one disk in a RAID 5 dies, the array is running with no redundancy until the rebuild finishes, and a conventional full-device rebuild reconstructs the failed member by reading the corresponding allocated array stripes on surviving members. Optimized/partial rebuilds and filesystem-aware layouts can skip unused or known-clean ranges.

Device specifications can state nonrecoverable-read-error limits over bits read, an unrecoverable read error (URE) being a sector the drive cannot read back. Such a limit is not, by itself, an observed independent per-bit probability model. For unit conversion, 10¹⁴ bits equals 12.5 TB.

Rebuilding a 4 × 16 TB RAID 5 after one failure means reading the three survivors in full. Purely as a mathematical scenario, suppose read errors arrive independently at random, which is a **Poisson model**: then the chance of reading everything with no error falls exponentially with the expected number of errors.

```formula
b = 3 × 16 TB × 8 = 3.84 × 10^14
λ = b × q
λ = 3.84 × 10^14 × 10^−14 = 3.84
P_none = e^{−λ}
P_none = e^{−3.84} ≈ 0.0215 = 2.15%
where
b: the number of bits the rebuild reads: three surviving 16 TB disks, times 8 bits per byte
TB: terabyte, 10^12 bytes
λ: lambda, the expected (average) number of read errors during the rebuild
q: the assumed error rate per bit read; here 1 per 10^14 bits = 10^−14
P_none: the probability of zero errors over the whole rebuild
e: Euler's number, about 2.718; e^{−λ} is the Poisson probability of no events when λ are expected
≈: approximately equal to
%: per cent, hundredths
In words: if errors strike at random at 1 per 10^14 bits, reading 3.84 × 10^14 bits expects 3.84 errors, and the chance of none at all is only about 2%.
```

A datasheet limit alone does not justify this distribution, and no empirical rebuild-failure probability follows without measured error behavior and rebuild details. The rebuild also takes a long time, which is how long the array runs with no redundancy:

```formula
t = V / R
t_1 = 16 × 10^12 B / (150 × 10^6 B/s)
t_1 ≈ 106,700 s ≈ 29.6 h
t_2 = 48 × 10^12 B / (150 × 10^6 B/s)
t_2 = 320,000 s ≈ 88.9 h
where
t: the rebuild time, ignoring overhead
V: the bytes that must move through one bottleneck, in bytes (B)
R: the rate of that bottleneck, in bytes per second (B/s); here 150 MB/s
t_1: the time if each disk streams 150 MB/s in parallel, so the 16 TB written to the replacement sets the pace
t_2: the time if 150 MB/s is the whole array's read bandwidth, shared by all 48 TB read
B: byte
s: second
h: hour, 3,600 s
≈: approximately equal to
In words: even streaming flat out, a 16 TB rebuild takes more than a day, and up to almost four days if the 48 TB of reads share one 150 MB/s pipe.
```

Another complete member failure in that window exceeds RAID 5 redundancy, while a URE can affect a stripe or abort recovery depending on implementation.

That is why large-capacity arrays use RAID 6, RAID-Z2/Z3 or mirrors, and why big storage systems (Ceph, HDFS, S3) replicate or erasure-code across machines instead.

Last pitfalls:

- **RAID is not a backup.** It faithfully replicates `rm -rf`, ransomware and file system corruption.
- **Correlated failures matter.** Shared environment, age, firmware and workload can invalidate independence assumptions; this does not establish that a particular batch will fail together.
- **RAID 0 multiplies risk.** A member failure can make a striped RAID0 volume unusable even though some surviving sectors remain readable. With independent, equal and small per-disk failure probabilities, the array's risk grows almost in proportion to the number of disks (the formula follows this list); correlation and repair alter reliability models.

The RAID 0 risk comes from requiring every disk to survive:

```formula
F = 1 − (1 − p)^N
F ≈ N × p   for p ≪ 1
F = 1 − (1 − 0.01)^4 ≈ 0.039 ≈ 4 × 0.01
where
F: the probability that the RAID 0 array fails during the chosen interval (any one member failing loses it)
p: the probability that one disk fails during that interval, assumed independent and equal for every disk; here an illustrative 0.01 (1%)
N: the number of disks in the array; here 4
≪: much less than; the shortcut F ≈ N × p only holds when p is tiny
≈: approximately equal to
In words: the array survives only if all N disks survive, so with small risks the chance of losing it is about N times the risk for one disk: four disks, four times the risk.
```

## Key takeaways
- HDD seek and rotation make access locality important; use identified device/workload measurements rather than a universal IOPS range.
- NAND flash is read and written (programmed) in flash pages, erased only in whole blocks, and wears out; the FTL hides this with out-of-place writes, a mapping table, garbage collection and wear levelling.
- Write amplification is about one divided by the free fraction of the blocks GC cleans (4× when victims are 75% valid); over-provisioning and TRIM keep it low, and full drives fall off a performance cliff.
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
