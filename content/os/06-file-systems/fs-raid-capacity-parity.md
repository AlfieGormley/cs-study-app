---
id: fs-raid-capacity-parity
title: RAID capacity and XOR parity
level: advanced
minutes: 4
summary: Mirrors spend space on copies while parity arrays reserve equivalent capacity for redundancy.
sourceLesson: fs-storage-devices
---

This unit focuses on RAID capacity and XOR parity. The preceding units provide the file and storage concepts used here.

## RAID: combining disks

**RAID** (redundant array of independent disks) spreads data over several devices for capacity, speed, survival, or all three. On Linux it's usually done in software with `md` (`mdadm`), by LVM, or inside ZFS and Btrfs.

Data is split into **stripe units** (chunks, often 64–512 KiB) laid across the disks. Usable capacity depends on how many disks' worth of space goes to copies or parity:

```formula
C_0 = NC
C_1 = C
C_10 = (NC) / 2
C_5 = (N − 1)C
C_6 = (N − 2)C
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
| RAID 0 | all raw capacity | no failures | 1 I/O |
| RAID 1 | one disk’s capacity | all but one disk | one write per mirror copy |
| RAID 10 | half the raw capacity | 1 per mirror | 2 I/Os |
| RAID 5 | all but one disk’s capacity | 1 | 4 I/Os |
| RAID 6 | all but two disks’ capacity | 2 | 6 I/Os |

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
⊕: XOR (exclusive or), applied bit by bit: a result bit is 1 when the two input bits differ, 0 when they match, so XORing any bit pattern with itself gives all-zero bits
In words: parity is the XOR of the data chunks, and because XORing the same value twice cancels it out, XORing the survivors with the parity gives back the missing chunk.
```

If disk1 dies, the second line rebuilds its chunk. XOR is its own inverse, so any one missing chunk can be rebuilt from the rest. For example, with 4-bit chunks 1011, 0110 and 0001, parity is 1100, and 1011 ⊕ 0001 ⊕ 1100 gives back 0110. RAID 6 adds a second, independent syndrome (Reed–Solomon style), so it survives any two failures.

## Key takeaways
- Mirrors spend space on copies while parity arrays reserve equivalent capacity for redundancy.
- XOR parity can reconstruct one missing chunk from the surviving data and parity.

## Further reading
- [OSTEP: Hard Disk Drives (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/file-disks.pdf)
- [OSTEP: Flash-based SSDs (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/file-ssd.pdf)
- [OSTEP: Redundant Arrays of Inexpensive Disks (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/file-raid.pdf)
- [Write amplification — Wikipedia](https://en.wikipedia.org/wiki/Write_amplification)
- [NVM Express — Wikipedia](https://en.wikipedia.org/wiki/NVM_Express)
- [Standard RAID levels — Wikipedia](https://en.wikipedia.org/wiki/Standard_RAID_levels)
- [RAID arrays (md) — Linux kernel documentation](https://docs.kernel.org/admin-guide/md.html)
- [Backblaze hard drive test data](https://www.backblaze.com/cloud-storage/resources/hard-drive-test-data)
