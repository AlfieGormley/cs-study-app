---
id: fs-hdd-access-model
title: HDD seek, rotation and throughput
level: advanced
minutes: 5
summary: Random HDD access pays seek and rotation before transfer.
sourceLesson: fs-storage-devices
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
IOPS ≈ 1 / (0.012 s) ≈ 80
X = IOPS S ≈ 80 × 4 KiB/s ≈ 0.33 MB/s
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

## Key takeaways
- Random HDD access pays seek and rotation before transfer.
- Queue-depth-one arithmetic is a model; actual device and workload measurements are needed.

## Further reading
- [OSTEP: Hard Disk Drives (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/file-disks.pdf)
- [OSTEP: Flash-based SSDs (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/file-ssd.pdf)
- [OSTEP: Redundant Arrays of Inexpensive Disks (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/file-raid.pdf)
- [Write amplification — Wikipedia](https://en.wikipedia.org/wiki/Write_amplification)
- [NVM Express — Wikipedia](https://en.wikipedia.org/wiki/NVM_Express)
- [Standard RAID levels — Wikipedia](https://en.wikipedia.org/wiki/Standard_RAID_levels)
- [RAID arrays (md) — Linux kernel documentation](https://docs.kernel.org/admin-guide/md.html)
- [Backblaze hard drive test data](https://www.backblaze.com/cloud-storage/resources/hard-drive-test-data)
