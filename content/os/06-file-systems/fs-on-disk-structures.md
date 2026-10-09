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
 SB = superblock
 IB = inode bitmap
 DB = data block bitmap
```

- **Superblock**: describes the whole file system: block size, how many inodes and blocks there are, where the tables start, a magic number. It is read at mount time. ext4 keeps backup copies.
- **Bitmaps**: one bit per inode and one bit per data block, saying which are free.
- **Inode table**: a fixed array of inodes, created when you run `mkfs`.
- **Data blocks**: file contents and directory contents.

A common ext4 configuration organizes these structures in **block groups**. The group size comes from the bitmap: one bitmap block has one bit for each data block in its group.

```formula
G = 8 × B_blk
S_group = G × B_blk
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

Let n be the number of entries in a directory. A linear list makes looking up a name O(n) in Big-O notation: the work grows in proportion to n, because the lookup may have to compare against every entry. That is painful with 100,000 entries. ext4 uses **htree**, a hashed B-tree-like index on the names, so lookups in big directories are roughly O(log n): the work grows with the logarithm of n, the number of tree levels, which stays small even for millions of entries. XFS and Btrfs use B+trees.

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

### Directory link counts

Directories have link counts too, and they follow a simple rule. A new empty directory on ext4 has link count 2: its name in the parent, and its own `.` entry. Each subdirectory adds 1, because the subdirectory's `..` points back. Ordinary files inside the directory add nothing, because their entries point at their own inodes.

```formula
L_dir = 2 + d
L_dir = 2 + 3 = 5
where
L_dir: the link count of a directory: how many directory entries point at its inode
d: the number of immediate subdirectories it contains (here 3)
In words: two links for the directory's own name and its "." entry, plus one for each subdirectory's ".." entry.
```

So an ordinary small directory with three subdirectories has link count five. With dir_nlink and sufficiently large directory counts, ext4 can use one as an unknown-count marker, and some file systems (Btrfs) always report 1 for directories, so scripts shouldn't rely on the rule.

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

How big a file can this tree describe? Each indirect block is just an array of pointers, so first work out how many pointers fit in one block. Each extra level of indirection multiplies the reach by that number:

```formula
k = B_blk / p
N_max = 12 + k + k^2 + k^3
S_max = N_max × B_blk
k = 4,096 B / 4 B = 1,024
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

This design is fast for small files: anything up to 12 × 4 KiB = 48 KiB needs only direct pointers. But a large file needs one pointer *per block*, so its mapping metadata grows in step with its size:

```formula
n = S / B_blk
M = n × p
n = 1 GiB / 4 KiB = 262,144
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
In words: a 1 GiB file is 262,144 blocks, so it needs 262,144 four-byte pointers: a whole mebibyte of indirect blocks just to say where the data is.
```

The file's last block is number 262,143, well inside the double-indirect range, so reading near its end adds two metadata-block reads if they are uncached. The triple-indirect range in a larger file can add three.

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
for L ≤ l ≤ L + n − 1
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
E_max = 32,768 × B_blk
e = ⌈S / E_max⌉
E_max = 32,768 × 4 KiB = 128 MiB
e = 1,024 MiB / 128 MiB = 8
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
