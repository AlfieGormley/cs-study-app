---
id: fs-lfs-cleaning
title: Log-structured placement and cleaning
level: advanced
minutes: 4
summary: An inode map tracks moving inodes, with checkpoints and roll-forward recovery.
sourceLesson: fs-modern-distributed
---

This unit focuses on log-structured placement and cleaning. The preceding units provide the file and storage concepts used here.

## Log-structured file systems

In their early-1990s LFS work, Mendel Rosenblum and John Ousterhout considered two trends. RAM was growing, so the page cache would absorb most **reads**. That left disk traffic dominated by **writes**, and small writes to scattered inodes, bitmaps and data blocks were dreadful on a disk whose random I/O is limited by seek and rotation.

Their answer, **LFS**, was radical: treat the whole disk as a log. Buffer every change (data, inodes, directory blocks) in memory, then write it out as one large sequential **log segment** of several hundred KiB to a few MiB.

```
 disk: |seg 1  |seg 2  |seg 3  | free ...
         D D I   D I D   D D I M
                              ^
              new versions go at the end
 D: data; I: inode; M: imap piece
```

Nothing is overwritten in place, which raises two problems.

**Finding inodes.** An inode's location changes every time it's written. LFS adds an **inode map (imap)**: inode number → current disk address. The imap is itself written into the log in pieces, and a **checkpoint region** at a fixed place on disk points at the latest pieces. Recovery reads the checkpoint, then rolls forward through segments written after it.

**Reclaiming space.** Old versions of blocks become garbage, scattered through old segments. A **segment cleaner** reads partly-dead segments, writes their live blocks into a new segment, and frees the old ones. Each segment has a summary block recording which inode and offset every block belongs to, so the cleaner can check whether a block is still live.

How expensive is cleaning? It depends on how full the cleaned segments still are. Cleaning a segment means rewriting its live blocks elsewhere, and only the dead part becomes free for new data:

```formula
W = (u + (1 − u)) / (1 − u)
W = 1 / (1 − u)
W = 1 / (1 − 0.8) = 5
where
W: total segment writes per segment of new data, counting the copied live blocks (cleaner reads not counted)
u: the fraction of a cleaned segment that is still live, from 0 to just under 1; here 0.8 (80%)
In words: each cleaned segment frees only 1 − u of a segment and costs u of a segment in copying, so writing one segment of new data costs 1 / (1 − u) segments of writes: five when segments are 80% live.
```

This is a steady-state model excluding metadata; counting the cleaner's reads as well is a different I/O-cost measure. It is the same formula as SSD write amplification in the FTL unit, because an FTL is a log-structured cleaner too. LFS's **cost-benefit** policy balances segment age and how full each segment is to favor reclaimed space likely to remain useful.

### Where the idea lives now

- **SSD firmware.** The FTL discussed earlier is a log-structured system with a mapping table and a cleaner.
- **F2FS** (Flash-Friendly File System), from Samsung and merged in Linux 3.8, is log-structured and designed for flash. It separates hot and cold data into different logs and uses a **node address table** so that moving one block doesn't force rewrites all the way up the tree (the "wandering tree" problem).
- **Copy-on-write file systems** (ZFS, Btrfs, NetApp's WAFL) share the never-overwrite principle.
- **LSM trees** in RocksDB, Cassandra and LevelDB apply it to key-value stores: append-only sorted files that are merged in the background, which similarly reclaims obsolete versions but follows different structures and correctness rules.

## Key takeaways
- An inode map tracks moving inodes, with checkpoints and roll-forward recovery.
- Cleaning copies live blocks, so segment utilization determines write amplification.

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
