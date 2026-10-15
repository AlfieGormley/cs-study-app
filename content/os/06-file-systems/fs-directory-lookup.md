---
id: fs-directory-lookup
title: Directory entries and cold path walks
level: intermediate
minutes: 2
summary: On-disk directory entries map names to inode numbers.
sourceLesson: fs-on-disk-structures
---

This unit focuses on directory entries and cold path walks. The preceding units provide the file and storage concepts used here.

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

Let n be the number of entries in a directory. A linear list makes looking up a name O(n) in Big-O notation: the work grows in proportion to n, because the lookup may have to compare against every entry. That is painful with 100,000 entries. ext4 uses **htree**, a shallow hash-indexed directory tree. The name hash selects a leaf range, then the filesystem compares candidate names. This usually avoids scanning every directory entry; hash collisions can require additional scanning, so a generic balanced-tree O(log n) bound is not a complete worst-case guarantee. XFS and Btrfs use B+trees.

### Walking a path

Opening `/home/alfie/notes.txt` with cold caches means:

1. Read inode 2 (the root) to find the root directory's data blocks.
2. Read those blocks and find `home` → inode 4000.
3. Read inode 4000, then its data, and find `alfie` → 5001.
4. Read inode 5001, then its data, and find `notes.txt` → 7342.
5. Read inode 7342. Now you can find the file's data.

In a toy layout with one block read per listed inode and directory data object, that is seven reads before file data. Real systems may cache the root, co-locate inodes, need multiple directory-index blocks or perform readahead, so this is not a fixed device-I/O count. This is why the VFS dentry and inode caches matter so much.

## Key takeaways
- On-disk directory entries map names to inode numbers.
- Cold path walks can require multiple metadata reads; caches and actual layout change that cost.

## Further reading
- [OSTEP: File System Implementation (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/file-implementation.pdf)
- [OSTEP: Locality and the Fast File System (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/file-ffs.pdf)
- [ext4 data structures: the inode block map — kernel.org](https://www.kernel.org/doc/html/latest/filesystems/ext4/ifork.html)
- [inode(7) — Linux manual page](https://man7.org/linux/man-pages/man7/inode.7.html)
- [symlink(7) — Linux manual page](https://man7.org/linux/man-pages/man7/symlink.7.html)
- [File Allocation Table — Wikipedia](https://en.wikipedia.org/wiki/File_Allocation_Table)
- [Extent (file systems) — Wikipedia](https://en.wikipedia.org/wiki/Extent_(file_systems))
