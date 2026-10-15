---
id: fs-ftl-amplification
title: FTL mapping, cleaning and write amplification
level: advanced
minutes: 5
summary: The FTL maps logical addresses onto changing flash locations.
sourceLesson: fs-storage-devices
---

This unit focuses on FTL mapping, cleaning and write amplification. The preceding units provide the file and storage concepts used here.

## The flash translation layer

The SSD's controller hides all of this behind the same interface a disk has: read or write logical block address (LBA) N. The firmware that does the hiding is the **flash translation layer (FTL)**. It is a little log-structured file system inside the drive.

- **Out-of-place writes.** A write to LBA 7 goes to the next free flash page. The FTL updates a **mapping table** (LBA 7 → block 52, page 3) and marks the old flash page **invalid**.
- **Garbage collection (GC).** When free blocks run low, the FTL picks a block with many invalid pages, copies its still-valid flash pages elsewhere, and erases it.
- **Wear levelling.** It spreads erases evenly, occasionally moving cold data so that its blocks get their share of wear.
- **Mapping table.** A page-level map with a 4-byte entry per 4 KiB is about 1 GiB per TiB of flash (worked out below), illustrating why mapping metadata can be large. Controllers use varied mapping granularities and caches; some DRAM-less NVMe designs use optional host-memory-buffer support. Performance depends on the implementation and workload.

How big is a page-level mapping table? One entry per mapped unit, times the entry size:

```formula
T = (C / U)e
T = (2^40 B / (2^12 B)) × 4 B
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
In words: a tebibyte of flash is about 268 million 4 KiB units, and a 4-byte entry for each one needs about a gigabyte of fast memory.
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

## Key takeaways
- The FTL maps logical addresses onto changing flash locations.
- Cleaning live pages increases writes; spare capacity and successful discard can reduce that cost.

## Further reading
- [OSTEP: Hard Disk Drives (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/file-disks.pdf)
- [OSTEP: Flash-based SSDs (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/file-ssd.pdf)
- [OSTEP: Redundant Arrays of Inexpensive Disks (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/file-raid.pdf)
- [Write amplification — Wikipedia](https://en.wikipedia.org/wiki/Write_amplification)
- [NVM Express — Wikipedia](https://en.wikipedia.org/wiki/NVM_Express)
- [Standard RAID levels — Wikipedia](https://en.wikipedia.org/wiki/Standard_RAID_levels)
- [RAID arrays (md) — Linux kernel documentation](https://docs.kernel.org/admin-guide/md.html)
- [Backblaze hard drive test data](https://www.backblaze.com/cloud-storage/resources/hard-drive-test-data)
