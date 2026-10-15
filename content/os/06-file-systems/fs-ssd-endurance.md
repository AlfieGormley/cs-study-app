---
id: fs-ssd-endurance
title: Endurance ratings and power loss
level: advanced
minutes: 2
summary: TBW and DWPD describe host-write ratings under specified conditions.
sourceLesson: fs-storage-devices
---

This unit focuses on endurance ratings and power loss. The preceding units provide the file and storage concepts used here.

### Endurance and power loss

Drives are rated in **TBW** (terabytes written) or **DWPD** (drive writes per day over the warranty). The two are linked by the capacity and the warranty length:

```formula
TBW = 365 C DWPD Y
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

The [Kioxia endurance technical brief](https://americas.kioxia.com/content/dam/kioxia/en-us/business/memory/asset/KIOXIA-SSD-NAND-Endurance-Tech-Brief.pdf) gives the TBW/DWPD conversion and explains why endurance ratings depend on workload.

## Key takeaways
- TBW and DWPD describe host-write ratings under specified conditions.
- Power-loss protection and correct flush handling must be checked for the actual device.

## Further reading
- [OSTEP: Hard Disk Drives (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/file-disks.pdf)
- [OSTEP: Flash-based SSDs (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/file-ssd.pdf)
- [OSTEP: Redundant Arrays of Inexpensive Disks (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/file-raid.pdf)
- [Write amplification — Wikipedia](https://en.wikipedia.org/wiki/Write_amplification)
- [NVM Express — Wikipedia](https://en.wikipedia.org/wiki/NVM_Express)
- [Standard RAID levels — Wikipedia](https://en.wikipedia.org/wiki/Standard_RAID_levels)
- [RAID arrays (md) — Linux kernel documentation](https://docs.kernel.org/admin-guide/md.html)
- [Backblaze hard drive test data](https://www.backblaze.com/cloud-storage/resources/hard-drive-test-data)
