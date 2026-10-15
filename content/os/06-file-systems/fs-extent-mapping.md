---
id: fs-extent-mapping
title: Extent mappings and allocation policy
level: intermediate
minutes: 4
summary: An extent maps a consecutive logical range onto a physical run.
sourceLesson: fs-on-disk-structures
---

This unit focuses on extent mappings and allocation policy. The preceding units provide the file and storage concepts used here.

### Extents (ext4, XFS, Btrfs, NTFS)

An **extent** is one record describing a whole run of blocks: "this many logical blocks of the file, starting here, live in consecutive physical blocks on the device, starting there". A contiguous run can use far fewer extent records than per-block pointers, subject to the maximum extent length.

```
 extent: logical 0, len 3000,
         physical 81920
 -> blocks 81920..84919
```

To find where any block of the file lives, check which extent covers it, then add its distance into the extent to the extent's physical start:

```formula
b_phys = P + (l − L)
for L ≤ l ≤ L + (n − 1)
b_phys = 81,920 + (2,999 − 0) = 84,919
where
b_phys: the physical block number on the device that holds logical block l
P: the extent's first physical block (here 81,920)
l: the logical block number within the file: byte offset ÷ block size, counting from 0 (here 2,999, the extent's last block)
L: the extent's first logical block (here 0)
n: the extent's length in blocks (here 3,000)
≤: less than or equal to
In words: an extent maps a run of n consecutive file blocks onto n consecutive disk blocks, so one addition finds any block inside it.
```

In ext4, an initialized extent covers up to 32,768 blocks. The inode has room for **four** extents directly. Files with more extents grow an **extent tree**, a shallow B-tree whose leaves are extents. How many extents does a large contiguous file need?

```formula
E_max = 32,768B_blk
e = ⌈S / E_max⌉
E_max = 32,768 × 4 KiB = 128 MiB
e = 1,024 MiB / (128 MiB) = 8
where
E_max: the most data one ext4 extent can map
B_blk: the block size; here 4 KiB
e: the number of extents a perfectly contiguous file needs
S: the file size; here 1 GiB = 1,024 MiB
⌈ ⌉: the ceiling: round up to the next whole number, because a part-filled last extent is still a record
KiB: kibibyte, 1,024 bytes
MiB: mebibyte, 1,024 KiB
In words: one extent maps at most 128 MiB with 4 KiB blocks, so a contiguous 1 GiB file needs just eight extent records.
```

So a contiguous initialized 1 GiB file can be represented with eight maximum-sized extents, stored in a tree only one level deep, rather than a megabyte of indirect pointers.

The table compares how much work it takes to find one block at a random position in a file. It uses Big-O notation: n is the number of blocks in the file (for extents, the number of extents), O(1) means a fixed amount of work whatever n is, O(n) means work that grows in proportion to n, and O(log n) means work that grows with the logarithm of n, the depth of a tree.

| Strategy | Random access | Grows easily | Used by |
|---|---|---|---|
| Contiguous | O(1) | no | ISO 9660 |
| Linked/FAT | O(n) chain | yes | FAT32, exFAT |
| Indexed | O(1), up to 4 reads | yes | ext2/3 |
| Extents | O(log n) | yes | ext4, XFS, NTFS |

Extents only pay off if the file system can find **long free runs**. ext4 and XFS help themselves with:

- **Delayed allocation**: don't choose blocks at `write()` time; wait until the data is flushed, when the final size is better known.
- **Multi-block allocation**: allocate many blocks in one request.
- **Preallocation**: supported fallocate modes can reserve space up front, which helps avoid later allocation failure and can improve layout. Preallocation does not guarantee physical contiguity.

## Key takeaways
- An extent maps a consecutive logical range onto a physical run.
- Delayed allocation and preallocation can improve layout; they do not guarantee contiguity.

## Further reading
- [OSTEP: File System Implementation (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/file-implementation.pdf)
- [OSTEP: Locality and the Fast File System (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/file-ffs.pdf)
- [ext4 data structures: the inode block map — kernel.org](https://www.kernel.org/doc/html/latest/filesystems/ext4/ifork.html)
- [inode(7) — Linux manual page](https://man7.org/linux/man-pages/man7/inode.7.html)
- [symlink(7) — Linux manual page](https://man7.org/linux/man-pages/man7/symlink.7.html)
- [File Allocation Table — Wikipedia](https://en.wikipedia.org/wiki/File_Allocation_Table)
- [Extent (file systems) — Wikipedia](https://en.wikipedia.org/wiki/Extent_(file_systems))
