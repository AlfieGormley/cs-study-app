---
id: fs-raid-write-costs
title: RAID small writes and the write hole
level: advanced
minutes: 4
summary: An isolated read-modify-write updates both data and parity.
sourceLesson: fs-storage-devices
---

This unit focuses on RAID small writes and the write hole. The preceding units provide the file and storage concepts used here.

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
R = nr
k = f_r + f_w w
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

If power fails after D1' is written but before P0', the stripe's parity is wrong, and nothing records that. If a disk later fails, the rebuild uses bad parity and silently produces garbage. This is the **RAID 5 write hole**. Fixes: a battery-backed controller cache, md's write journal or partial parity log, or ZFS's **RAID-Z**, which uses variable-width stripes and filesystem copy-on-write so it never updates a stripe in place.

## Key takeaways
- An isolated read-modify-write updates both data and parity.
- A crash between those writes can leave a write hole without a suitable protection mechanism.

## Further reading
- [OSTEP: Hard Disk Drives (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/file-disks.pdf)
- [OSTEP: Flash-based SSDs (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/file-ssd.pdf)
- [OSTEP: Redundant Arrays of Inexpensive Disks (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/file-raid.pdf)
- [Write amplification — Wikipedia](https://en.wikipedia.org/wiki/Write_amplification)
- [NVM Express — Wikipedia](https://en.wikipedia.org/wiki/NVM_Express)
- [Standard RAID levels — Wikipedia](https://en.wikipedia.org/wiki/Standard_RAID_levels)
- [RAID arrays (md) — Linux kernel documentation](https://docs.kernel.org/admin-guide/md.html)
- [Backblaze hard drive test data](https://www.backblaze.com/cloud-storage/resources/hard-drive-test-data)
