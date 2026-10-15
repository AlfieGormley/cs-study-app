---
id: fs-ext4-xfs-choices
title: ext4 and XFS allocation choices
level: advanced
minutes: 3
summary: Ext4 combines a journal, extents and block groups.
sourceLesson: fs-modern-distributed
---

The earlier lessons built a file system from parts: inodes, extents, a journal or filesystem copy-on-write, the page cache. Real systems pick different combinations of those parts, and the choices show up as concrete differences: whether you can shrink a volume, whether silent corruption is detected, how a database behaves on it.

Then we leave the single machine. NFS makes a remote disk look local; GFS and HDFS give up on looking local and build something new for huge files across thousands of machines.

## The local file systems you'll meet on Linux

| | ext4 | XFS | Btrfs | ZFS |
|---|---|---|---|---|
| Consistency | journal | journal | filesystem CoW | filesystem CoW |
| Checksums | metadata by configuration | metadata by format | data and metadata, with exclusions | data and metadata, configurable |
| Native filesystem snapshots | no | no | yes | yes |
| Built-in RAID | no | no | yes | yes |

### ext4

The descendant of ext2 and ext3. It combines a jbd2 journal (ordered mode by default), extents, delayed allocation and multi-block allocation, and htree directories.

- Uses `e2fsck` for offline consistency checking and repair.
- Each block group reserves an inode table. At a fixed filesystem size, tiny files can exhaust available inodes before data space; growing the filesystem can add groups and inodes.
- Can grow online; can shrink, but only unmounted.
- Metadata checksums (default in recent `mke2fs`) catch corrupt metadata, but ordinary mutable file payload is not protected by those metadata checksums.

### XFS

Designed by SGI for large files and parallel I/O.

- The disk is split into **allocation groups**, each with its own free-space and inode B+trees, so many threads can allocate at once without a global lock.
- Free space is indexed twice, by block number and by extent size, so "find me 1 GiB contiguous" is a tree lookup.
- Inodes are allocated dynamically: no fixed inode count.
- Supports **reflinks** (`cp --reflink`): two files share extents until one is modified, so supported reflink copies can avoid copying the whole payload; metadata work still takes time.
- **Shrink support is limited and version-dependent.** The current upstream `xfs_growfs` manual describes shrinking only the last allocation group without removing it, with additional single-group restrictions. This is not arbitrary volume shrinking: check installed kernel/tooling support and geometry before planning a resize.

## Key takeaways
- Ext4 combines a journal, extents and block groups.
- XFS uses allocation groups and dynamic inode allocation; resizing support is version-dependent.

## Further reading
- [ext4 data structures and algorithms — kernel.org](https://docs.kernel.org/filesystems/ext4/index.html)
- [XFS administration — Linux kernel documentation](https://docs.kernel.org/admin-guide/xfs.html)
- [Btrfs documentation](https://btrfs.readthedocs.io/en/latest/)
- [OpenZFS documentation](https://openzfs.github.io/openzfs-docs/)
- [OSTEP: Log-structured File Systems (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/file-lfs.pdf)
- [The Design and Implementation of a Log-Structured File System — Rosenblum and Ousterhout (PDF)](https://people.eecs.berkeley.edu/~brewer/cs262/LFS.pdf)
- [F2FS: A New File System for Flash Storage — FAST 2015 (PDF)](https://www.usenix.org/system/files/conference/fast15/fast15-paper-lee.pdf)
- [OSTEP: Sun's Network File System (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/dist-nfs.pdf)
- [nfs(5) — Linux manual page](https://man7.org/linux/man-pages/man5/nfs.5.html)
- [RFC 7530: NFS version 4 protocol](https://datatracker.ietf.org/doc/html/rfc7530)
- [The Google File System — SOSP 2003 (PDF)](https://storage.googleapis.com/gweb-research2023-media/pubtools/4446.pdf)
- [HDFS Architecture — Apache Hadoop](https://hadoop.apache.org/docs/stable/hadoop-project-dist/hadoop-hdfs/HdfsDesign.html)
- [HDFS Erasure Coding — Apache Hadoop](https://hadoop.apache.org/docs/stable/hadoop-project-dist/hadoop-hdfs/HDFSErasureCoding.html)
