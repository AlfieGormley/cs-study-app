---
id: fs-contiguous-fat
title: Contiguous allocation and FAT chains
level: intermediate
minutes: 2
summary: Contiguous allocation makes address calculation simple but complicates growth.
sourceLesson: fs-on-disk-structures
---

This unit focuses on contiguous allocation and FAT chains. The preceding units provide the file and storage concepts used here.

## Allocation: where do the data blocks go?

The inode's "block map" is the heart of the design. There are four classic strategies.

### Contiguous allocation

Store each file in one run of consecutive blocks. The inode records just *start* and *length*.

- Contiguous layout reduces mapping and seek overhead for sequential reads, and random access is just arithmetic.
- Files can't grow if their neighbour is in the way, and free space fragments into unusable holes (**external fragmentation**).

It survives where files are written once: ISO 9660 on CDs works this way.

### Linked allocation and FAT

Each block holds a pointer to the next one. Appending is easy, but reaching byte 1,000,000 means following a chain of pointers.

**FAT** (File Allocation Table, from MS-DOS) moves the pointers into one table at the start of the disk, with one entry per cluster:

```
 dir entry: "CAT.JPG" start=4
 FAT:  idx  next
        4 -> 7
        7 -> 2
        2 -> EOF
 file = clusters 4, 7, 2
```

The table can be cached in RAM, so seeking is a walk through memory rather than disk. FAT is still everywhere on USB sticks and SD cards because it has broad interoperability. Ordinary FAT lacks Unix-style per-file permission ownership and a native journal. FAT32's on-disk file-size field permits at most **4 GiB minus one byte**, not a full 4 GiB.

## Key takeaways
- Contiguous allocation makes address calculation simple but complicates growth.
- FAT stores cluster-chain pointers centrally, with a file-size limit and different semantics from Unix filesystems.

## Further reading
- [OSTEP: File System Implementation (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/file-implementation.pdf)
- [OSTEP: Locality and the Fast File System (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/file-ffs.pdf)
- [ext4 data structures: the inode block map — kernel.org](https://www.kernel.org/doc/html/latest/filesystems/ext4/ifork.html)
- [inode(7) — Linux manual page](https://man7.org/linux/man-pages/man7/inode.7.html)
- [symlink(7) — Linux manual page](https://man7.org/linux/man-pages/man7/symlink.7.html)
- [File Allocation Table — Wikipedia](https://en.wikipedia.org/wiki/File_Allocation_Table)
- [Extent (file systems) — Wikipedia](https://en.wikipedia.org/wiki/Extent_(file_systems))
