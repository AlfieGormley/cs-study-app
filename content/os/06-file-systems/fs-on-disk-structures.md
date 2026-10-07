---
id: fs-on-disk-structures
title: On-disk structures
level: intermediate
minutes: 14
summary: How a file system lays files out on a block device, from superblock, bitmaps and inodes to directory entries, hard and symbolic links, and the allocation strategies (contiguous, FAT, indexed and extents) that decide where the bytes go.
---

The previous lesson treated a file as a named array of bytes. Underneath, a storage device offers only numbered **blocks**. A file system is a data structure, stored on those blocks, that maps names to files and files to blocks.

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

`%b` counts 512-byte units, so 8 of them is one 4 KiB block.

## The overall layout

A simple Unix-style file system (as in OSTEP's teaching example, and roughly ext2/3/4) divides the disk like this:

```
+----+----+----+---------+------------+
| SB | IB | DB | inodes  | data blocks|
+----+----+----+---------+------------+
 SB = superblock
 IB = inode bitmap
 DB = data block bitmap
```

- **Superblock**: describes the whole file system: block size, how many inodes and blocks there are, where the tables start, a magic number. It is read at mount time. ext4 keeps backup copies.
- **Bitmaps**: one bit per inode and one bit per data block, saying which are free.
- **Inode table**: a fixed array of inodes, created when you run `mkfs`.
- **Data blocks**: file contents and directory contents.

A common ext4 configuration organizes these structures in **block groups** (128 MiB with 4 KiB blocks and one-block bitmaps); flex_bg, meta_bg, bigalloc and other features modify layout and allocation so that a file's inode and data can sit close together, which mattered a lot on spinning disks.

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

Each inode has a number, unique within its file system. `ls -i` shows it. On ext4 the root directory is always inode 2, and inodes are 256 bytes by default.

For a fixed-size ext4 filesystem, the configured inode tables can fill while data blocks remain free. Growing the filesystem can add block groups and inodes; an existing group does not dynamically add arbitrary inode slots. Millions of tiny files (mail queues, cache directories, `node_modules`) can do it:

```
$ df -h /var     # 40% used
$ df -i /var     # IUse% 100%
$ touch x
touch: No space left on device
```

## Directories

In this Unix-style on-disk model, a directory contains entries mapping names to inode numbers. These records are distinct from the VFS's in-memory dentry objects.

```
 directory /home/alfie (inode 5001)
 +-----------+--------+
 | name      | inode  |
 +-----------+--------+
 | .         | 5001   |
 | ..        | 4000   |
 | notes.txt | 7342   |
 | photos    | 6120   |
 +-----------+--------+
```

A linear list makes looking up a name O(n), which is painful with 100,000 entries. ext4 uses **htree**, a hashed B-tree-like index on the names, so lookups in big directories are roughly O(log n). XFS and Btrfs use B+trees.

### Walking a path

Opening `/home/alfie/notes.txt` with cold caches means:

1. Read inode 2 (the root) to find the root directory's data blocks.
2. Read those blocks and find `home` → inode 4000.
3. Read inode 4000, then its data, and find `alfie` → 5001.
4. Read inode 5001, then its data, and find `notes.txt` → 7342.
5. Read inode 7342. Now you can find the file's data.

In a toy layout with one block read per listed inode and directory data object, that is seven reads before file data. Real systems may cache the root, co-locate inodes, need multiple directory-index blocks or perform readahead, so this is not a fixed device-I/O count. This is why the VFS dentry and inode caches matter so much.

## Hard links and symbolic links

Since names live in directories and point to inode numbers, nothing stops two names pointing at the **same** inode. That is a **hard link**.

```
$ echo data > a
$ ln a b          # hard link
$ ln -s a c       # symbolic link
$ ls -li
7342 -rw-r--r-- 2 alfie a
7342 -rw-r--r-- 2 alfie b
7400 lrwxrwxrwx 1 alfie c -> a
```

`a` and `b` share inode 7342, and its **link count** is 2. Neither is "the original". `rm a` simply removes one name and drops the count to 1. Storage can be reclaimed after the last link and retaining open/mapping reference disappear; snapshots or other filesystem features can retain blocks further.

A **symbolic link** (symlink) is a different kind of file, with its own inode, whose content is a **path**. The kernel follows it during path resolution.

```python
import os
os.link("a", "b")
os.symlink("a", "c")
print(os.stat("a").st_nlink)   # 2
os.unlink("a")
print(os.stat("b").st_nlink)   # 1
print(os.path.exists("c"))     # False
with open("b") as f:
    print(f.read())           # data
```

After `a` is removed, `b` still works (it names the inode directly) but `c` is **dangling**: it points to a name that no longer exists.

| | Hard link | Symlink |
|---|---|---|
| Points to | inode | path |
| Own inode | no | yes |
| Across file systems | no | yes |
| To directories | no | yes |
| Survives target rm | yes | no (dangles) |

Hard links can't cross file systems because inode numbers are only unique within one. They aren't allowed to directories (except the special `.` and `..`) because that could create cycles in the tree and confuse tools like `find` and `fsck`.

> [!note] Directory link counts
> A new empty directory on ext4 has link count 2: its name in the parent, and its own `.` entry. Each subdirectory adds 1, because the child's `..` points back. So an ordinary small directory with three subdirectories has link count five. With dir_nlink and sufficiently large directory counts, ext4 can use one as an unknown-count marker.

ext4 stores short symlink targets (under 60 bytes) inside the inode itself, a **fast symlink**, so following them costs no extra block read.

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

### Indexed allocation (Unix inodes)

The inode holds an array of block pointers. ext2 and ext3 use 15: **12 direct** pointers, then one **single-indirect**, one **double-indirect** and one **triple-indirect**.

```
 inode
 [0..11] -> 12 data blocks
 [12] -> block of 1024 ptrs -> data
 [13] -> 1024 ptrs -> 1024 ptrs -> data
 [14] -> 3 levels of 1024 ptrs -> data
```

With 4 KiB blocks and 4-byte pointers, one block holds 1,024 pointers. The maximum number of addressable blocks is:

```
direct    12
single    1,024
double    1,024^2 = 1,048,576
triple    1,024^3 = 1,073,741,824
total   ~ 1.07 billion blocks
        x 4 KiB ~ 4 TiB
```

(Ext3's 32-bit allocated-sector accounting imposes a separate limit around 2 TiB in the traditional model; mapping metadata and kernel/filesystem limits must also be considered. The pointer-tree capacity alone is not the implemented maximum.)

This design is fast for small files: anything up to 48 KiB needs only direct pointers. But a large file needs one pointer *per block*. A 1 GiB file needs 262,144 pointers, about 1 MiB of indirect blocks, and near its end the double-indirect path adds two metadata-block reads if uncached. The triple-indirect range in a larger file can add three.

### Extents (ext4, XFS, Btrfs, NTFS)

An **extent** says "logical blocks *L* through *L + n − 1* live at physical blocks *P* through *P + n − 1*". A contiguous run can use far fewer extent records than per-block pointers, subject to the maximum extent length.

```
 extent: logical 0, len 3000,
         physical 81920
 -> blocks 81920..84919
```

In ext4, an initialized extent covers up to 32,768 blocks (128 MiB with 4 KiB blocks). The inode has room for **four** extents directly. Files with more extents grow an **extent tree**, a shallow B-tree whose leaves are extents.

So a contiguous initialized 1 GiB file can be represented with eight maximum-sized extents (1 GiB ÷ 128 MiB), stored in a tree only one level deep, rather than a megabyte of indirect pointers.

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

## Sparse files

The block map can have holes. If you seek 1 GiB past the end of a file and write one byte, an ordinary non-inline 4 KiB ext4 configuration can represent the write with one data block plus metadata, while the gap reads as zeros. Delayed allocation, preallocation and bigalloc can affect observed allocation.

```
$ truncate -s 10G disk.img
$ ls -lh disk.img     # 10G
$ du -h disk.img      # 0
```

VM disk images and database files use this. The pitfall: naive copy tools may expand the holes into real zeros, so an image with 10 GiB logical size and almost no allocated payload can expand toward 10 GiB of destination allocation. `cp --sparse=always` and `rsync -S` avoid that.

## Key takeaways
- A file system is an on-disk data structure: superblock, allocation bitmaps, an inode table and data blocks.
- An inode holds metadata and the block map, but not the name; directories map names to inode numbers.
- Hard links are extra names for the same inode (same file system only, no directories); symlinks are small files containing a path, and can dangle.
- A fixed-size ext4 filesystem can exhaust inode slots before data blocks; growing it can add groups and inodes.
- Allocation evolved from contiguous, to linked (FAT), to indexed pointers (ext2/3), to extents (ext4, XFS), which describe long runs compactly.
- Delayed allocation and `fallocate` help keep extents long; sparse files avoid allocating payload blocks for holes, although metadata still has a cost.

## Further reading
- [OSTEP: File System Implementation (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/file-implementation.pdf)
- [OSTEP: Locality and the Fast File System (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/file-ffs.pdf)
- [ext4 data structures: the inode block map — kernel.org](https://www.kernel.org/doc/html/latest/filesystems/ext4/ifork.html)
- [inode(7) — Linux manual page](https://man7.org/linux/man-pages/man7/inode.7.html)
- [symlink(7) — Linux manual page](https://man7.org/linux/man-pages/man7/symlink.7.html)
- [File Allocation Table — Wikipedia](https://en.wikipedia.org/wiki/File_Allocation_Table)
- [Extent (file systems) — Wikipedia](https://en.wikipedia.org/wiki/Extent_(file_systems))
