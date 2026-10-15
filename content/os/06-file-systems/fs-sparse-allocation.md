---
id: fs-sparse-allocation
title: Sparse files and copy expansion
level: intermediate
minutes: 1
summary: A sparse hole reads as zeros without allocated payload blocks.
sourceLesson: fs-on-disk-structures
---

This unit focuses on sparse files and copy expansion. The preceding units provide the file and storage concepts used here.

## Sparse files

The block map can have holes. If you seek 1 GiB past the end of a file and write one byte, an ordinary non-inline 4 KiB ext4 configuration can represent the write with one data block plus metadata, while the gap reads as zeros. Delayed allocation, preallocation and bigalloc can affect observed allocation.

```
$ truncate -s 10G disk.img
$ ls -lh disk.img     # 10G
$ du -h disk.img      # 0
```

VM disk images and database files use this. The pitfall: naive copy tools may expand the holes into real zeros, so an image with 10 GiB logical size and almost no allocated payload can expand toward 10 GiB of destination allocation. `cp --sparse=always` and `rsync -S` avoid that.

## Key takeaways
- A sparse hole reads as zeros without allocated payload blocks.
- A byte-stream copy can turn holes into real allocation; use sparse-aware tools.

## Further reading
- [OSTEP: File System Implementation (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/file-implementation.pdf)
- [OSTEP: Locality and the Fast File System (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/file-ffs.pdf)
- [ext4 data structures: the inode block map — kernel.org](https://www.kernel.org/doc/html/latest/filesystems/ext4/ifork.html)
- [inode(7) — Linux manual page](https://man7.org/linux/man-pages/man7/inode.7.html)
- [symlink(7) — Linux manual page](https://man7.org/linux/man-pages/man7/symlink.7.html)
- [File Allocation Table — Wikipedia](https://en.wikipedia.org/wiki/File_Allocation_Table)
- [Extent (file systems) — Wikipedia](https://en.wikipedia.org/wiki/Extent_(file_systems))
