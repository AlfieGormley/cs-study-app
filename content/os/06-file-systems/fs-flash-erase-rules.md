---
id: fs-flash-erase-rules
title: Flash pages, erase blocks and wear
level: advanced
minutes: 2
summary: NAND programming and erase operate at different granularities.
sourceLesson: fs-storage-devices
---

This unit focuses on flash pages, erase blocks and wear. The preceding units provide the file and storage concepts used here.

## Flash: how NAND works

An SSD stores bits as charge trapped in **NAND flash** cells. Storing more bits per cell increases density. Within comparable technology it generally makes programming more complex and reduces endurance margins; whole-device speed and lifetime also depend on NAND generation, controller and workload:

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

This illustrative erase block contains 256 flash pages, numbered zero through 255; its 16 KiB page size is an example rather than a universal NAND geometry.

```
 block (erase unit, e.g. 256 pages)
 +------+------+------+-----+------+
 | pg 0 | pg 1 | pg 2 | ... | pg255 |
 +------+------+------+-----+------+
  page: read/program unit (16 KiB)
```

So flash can't overwrite in place. Changing 4 KiB inside a block that's full of live data would mean copying the whole block out, erasing it, and writing it all back: slow, and it wears the flash.

## Key takeaways
- NAND programming and erase operate at different granularities.
- Erase limits and programming restrictions motivate out-of-place updates.

## Further reading
- [OSTEP: Hard Disk Drives (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/file-disks.pdf)
- [OSTEP: Flash-based SSDs (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/file-ssd.pdf)
- [OSTEP: Redundant Arrays of Inexpensive Disks (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/file-raid.pdf)
- [Write amplification — Wikipedia](https://en.wikipedia.org/wiki/Write_amplification)
- [NVM Express — Wikipedia](https://en.wikipedia.org/wiki/NVM_Express)
- [Standard RAID levels — Wikipedia](https://en.wikipedia.org/wiki/Standard_RAID_levels)
- [RAID arrays (md) — Linux kernel documentation](https://docs.kernel.org/admin-guide/md.html)
- [Backblaze hard drive test data](https://www.backblaze.com/cloud-storage/resources/hard-drive-test-data)
