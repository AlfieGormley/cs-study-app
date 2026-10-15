---
id: fs-indexed-blocks
title: Direct and indirect block pointers
level: intermediate
minutes: 4
summary: Each level of indirect pointers multiplies the reachable blocks.
sourceLesson: fs-on-disk-structures
---

This unit focuses on direct and indirect block pointers. The preceding units provide the file and storage concepts used here.

### Indexed allocation (Unix inodes)

The inode holds an array of block pointers. ext2 and ext3 use 15: **12 direct** pointers, then one **single-indirect**, one **double-indirect** and one **triple-indirect**.

```
 inode
 [0..11] -> 12 data blocks
 [12] -> block of 1024 ptrs -> data
 [13] -> 1024 ptrs -> 1024 ptrs -> data
 [14] -> 3 levels of 1024 ptrs -> data
```

How big a file can this tree describe? Each indirect block is just an array of pointers, so first work out how many pointers fit in one block. Each extra level of indirection multiplies the reach by that number:

```formula
k = B_blk / p
N_max = 12 + k + k^2 + k^3
S_max = N_max B_blk
k = 4,096 B / (4 B) = 1,024
k^2 = 1,048,576
k^3 = 1,073,741,824
N_max = 1,074,791,436 ≈ 1.07 × 10^9
S_max ≈ 1.07 × 10^9 × 4 KiB ≈ 4 TiB
where
k: the number of block pointers that fit in one indirect block
B_blk: the block size, in bytes; here 4 KiB = 4,096 B
p: the size of one block pointer, in bytes; here 4 B (a 32-bit block number)
N_max: the most data blocks one inode can reach: 12 direct, k through the single-indirect block, k^2 through the double-indirect tree and k^3 through the triple-indirect tree
k^2, k^3: k squared (k × k) and k cubed (k × k × k)
S_max: the largest file the pointer tree can describe, in bytes
B: byte, 8 bits
KiB: kibibyte, 1,024 bytes
TiB: tebibyte, 1,024^4 bytes, about 1.1 trillion bytes
≈: approximately equal to
In words: a 4 KiB block holds 1,024 four-byte pointers, so each level of indirection multiplies the reach by 1,024, and three levels reach about a billion blocks, roughly 4 TiB.
```

The levels cover consecutive ranges of file block numbers (block 0 is the first 4 KiB of the file): blocks 0–11 use direct pointers, 12–1,035 go through the single-indirect block, 1,036–1,049,611 through the double-indirect tree, and everything after that through the triple-indirect tree.

(Ext3's 32-bit allocated-sector accounting imposes a separate limit around 2 TiB in the traditional model; mapping metadata and kernel/filesystem limits must also be considered. The pointer-tree capacity alone is not the implemented maximum.)

With twelve direct pointers and 4 KiB blocks, the first 48 KiB needs no indirect-block lookup. But a large file needs one pointer *per block*, so its mapping metadata grows in step with its size:

```formula
n = S / B_blk
M = np
n = 1 GiB / (4 KiB) = 262,144
M = 262,144 × 4 B = 1,048,576 B = 1 MiB
where
n: the number of data blocks in the file, which is also the number of block pointers it needs
S: the file size, in bytes; here 1 GiB
B_blk: the block size; here 4 KiB
M: the space taken by those pointers, in bytes
p: the size of one pointer; here 4 bytes (B)
GiB: gibibyte, 1,024^3 bytes
KiB: kibibyte, 1,024 bytes
MiB: mebibyte, 1,024^2 bytes
B: byte, 8 bits
In words: a 1 GiB file is 262,144 blocks, so it needs 262,144 four-byte pointers: about a mebibyte of data-block pointers just to say where the data is.
```

This pointer-payload estimate omits interior pointer blocks, unused slots in the final leaf and inode-resident pointers. The actual mapping allocation is slightly larger.

The file's last block is number 262,143, well inside the double-indirect range, so reading near its end adds two metadata-block reads if they are uncached. The triple-indirect range in a larger file can add three.

## Key takeaways
- Each level of indirect pointers multiplies the reachable blocks.
- Pointer-tree capacity and implemented filesystem size limits are separate constraints.

## Further reading
- [OSTEP: File System Implementation (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/file-implementation.pdf)
- [OSTEP: Locality and the Fast File System (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/file-ffs.pdf)
- [ext4 data structures: the inode block map — kernel.org](https://www.kernel.org/doc/html/latest/filesystems/ext4/ifork.html)
- [inode(7) — Linux manual page](https://man7.org/linux/man-pages/man7/inode.7.html)
- [symlink(7) — Linux manual page](https://man7.org/linux/man-pages/man7/symlink.7.html)
- [File Allocation Table — Wikipedia](https://en.wikipedia.org/wiki/File_Allocation_Table)
- [Extent (file systems) — Wikipedia](https://en.wikipedia.org/wiki/Extent_(file_systems))
