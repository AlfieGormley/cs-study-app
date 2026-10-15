---
id: fs-blocks-inode-layout
title: Blocks, allocation maps and inodes
level: intermediate
minutes: 5
summary: Logical size differs from allocated space; a filesystem may run out of inodes before data blocks.
sourceLesson: fs-on-disk-structures
---

The earlier file-abstraction units treated a file as a named array of bytes. Underneath, a storage device offers only numbered **blocks**. A file system is a data structure, stored on those blocks, that maps names to files and files to blocks.

Every design has to answer three questions:

1. Where is a file's **metadata** (size, owner, permissions)?
2. Which **blocks** hold its data?
3. How do **names** map to files?

We'll use ext4, the default on many Linux distributions, as the running example, and compare it with older and alternative designs.

## Blocks

The device is addressed in **sectors** (traditionally 512 bytes; many modern drives use 4 KiB physical sectors while logical sector sizes vary). File systems group these into **blocks**, typically **4 KiB** to match the memory page size.

The block is the unit of allocation. In a 4 KiB-block model without inline data, compression or larger allocation clusters, a nonempty one-byte file can occupy a whole data block, which is **internal fragmentation**. Larger blocks waste more space on small files but need less metadata for big ones.

```
$ stat -c '%s bytes, %b blocks' tiny.txt
1 bytes, 8 blocks
```

`stat`'s `%b` field counts allocated space in 512-byte units, whatever the file system's own block size. To turn it into bytes, multiply by 512:

```formula
A = b × 512 B
A = 8 × 512 B = 4,096 B = 4 KiB
where
A: the space actually allocated to the file on disk, in bytes (B)
b: the number `stat` prints for `%b`: allocated 512-byte units (here 8)
B: byte, 8 bits
KiB: kibibyte, 1,024 bytes, so 4 KiB = 4,096 B
In words: eight 512-byte units is exactly one 4 KiB block, so a 1-byte file still occupies a whole block.
```

The file's *size* (`%s`, 1 byte) and its *allocation* (4,096 bytes) are different numbers; the gap is the internal fragmentation.

## The overall layout

A simple Unix-style file system (as in OSTEP's teaching example, and roughly ext2/3/4) divides the disk like this:

```
+----+----+----+---------+------------+
| SB | IB | DB | inodes  | data blocks|
+----+----+----+---------+------------+
 SB: superblock
 IB: inode bitmap
 DB: data block bitmap
```

- **Superblock**: describes the whole file system: block size, how many inodes and blocks there are, where the tables start, a magic number. It is read at mount time. ext4 keeps backup copies.
- **Bitmaps**: one bit per inode and one bit per data block, saying which are free.
- **Inode table**: a fixed array of inodes, created when you run `mkfs`.
- **Data blocks**: file contents and directory contents.

A common ext4 configuration organizes these structures in **block groups**. The group size comes from the bitmap: one bitmap block has one bit for each data block in its group.

```formula
G = 8B_blk
S_group = G B_blk
G = 8 × 4,096 = 32,768
S_group = 32,768 × 4 KiB = 128 MiB
where
G: the number of blocks one block group can hold: one per bit of a one-block bitmap (a byte has 8 bits, hence the 8)
B_blk: the block size, in bytes (here 4 KiB = 4,096 bytes)
S_group: the size of one block group
KiB: kibibyte, 1,024 bytes
MiB: mebibyte, 1,024 KiB = 1,048,576 bytes
In words: a 4 KiB bitmap has 32,768 bits, each tracking one 4 KiB block, so one group spans 128 MiB.
```

Grouping lets a file's inode and data sit close together, which mattered a lot on spinning disks. The 128 MiB figure assumes plain one-block bitmaps; flex_bg, meta_bg, bigalloc and other features modify layout and allocation.

## Inodes

An **inode** (index node) holds everything about a file *except its name*:

| Field | Example |
|---|---|
| type and permissions | regular, `0644` |
| owner, group | uid 1000, gid 1000 |
| size | 10,240 bytes |
| timestamps | atime, mtime, ctime |
| link count | 1 |
| block map | where the data is |

Each inode has a number, unique within its file system. `ls -i` shows it. On ext4 the root directory is always inode 2, and the ext4 documentation describes 256-byte inodes as the usual default; the on-disk inode size is configurable at creation.

For a fixed-size ext4 filesystem, the configured inode tables can fill while data blocks remain free. Growing the filesystem can add block groups and inodes; an existing group does not dynamically add arbitrary inode slots. Millions of tiny files (mail queues, cache directories, `node_modules`) can do it:

```
$ df -h /var     # 40% used
$ df -i /var     # IUse% 100%
$ touch x
touch: No space left on device
```

## Key takeaways
- Logical size differs from allocated space; a filesystem may run out of inodes before data blocks.
- Superblocks, allocation bitmaps and inode tables describe and locate stored files.

## Further reading
- [OSTEP: File System Implementation (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/file-implementation.pdf)
- [OSTEP: Locality and the Fast File System (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/file-ffs.pdf)
- [ext4 data structures: the inode block map — kernel.org](https://www.kernel.org/doc/html/latest/filesystems/ext4/ifork.html)
- [inode(7) — Linux manual page](https://man7.org/linux/man-pages/man7/inode.7.html)
- [symlink(7) — Linux manual page](https://man7.org/linux/man-pages/man7/symlink.7.html)
- [File Allocation Table — Wikipedia](https://en.wikipedia.org/wiki/File_Allocation_Table)
- [Extent (file systems) — Wikipedia](https://en.wikipedia.org/wiki/Extent_(file_systems))
