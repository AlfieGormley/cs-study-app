---
id: fs-btrfs-zfs-choices
title: Btrfs and ZFS integrity and logging
level: advanced
minutes: 3
summary: Checksums and recoverable redundancy serve different roles.
sourceLesson: fs-modern-distributed
---

This unit focuses on Btrfs and ZFS integrity and logging. The preceding units provide the file and storage concepts used here.

### Btrfs

A filesystem copy-on-write B-tree file system in the mainline kernel.

- Checksums metadata and, by default, file data. NOCOW/nodatasum files are excluded; repair needs a valid redundant copy.
- **Subvolumes** and cheap **snapshots**, which is how openSUSE rolls back failed upgrades.
- Transparent compression (zstd, lzo, zlib), reflinks, send/receive for incremental backup.
- Offers several redundancy profiles. Its official status documentation lists limitations for RAID 5/6; check those documented restrictions before choosing a profile.

### ZFS

Developed at Sun and released in 2005, now maintained as **OpenZFS**. It merges the volume manager, RAID and file system into one:

```
 datasets:  tank/db  tank/home  tank/vm
               \        |        /
 pool:          [  zpool "tank"  ]
                /        |       \
 vdevs:    raidz2      raidz2    mirror
          (6 disks)  (6 disks)  (SLOG)
```

- Checksums protect metadata and normally file data, subject to dataset settings. Checksums can detect mismatches, and valid redundancy can enable repair. `zpool scrub` checks allocated data covered by the pool's integrity mechanisms; it does not read every unused sector.
- **ARC**: ZFS's own adaptive replacement cache, separate from the Linux page cache. It uses recency and frequency information to improve resistance to scans; hot-set retention is not guaranteed.
- **ZIL / SLOG**: synchronous writes (`fsync`, NFS commits, databases) go to the ZFS intent log; a suitable low-latency separate log device (SLOG) can reduce log-commit latency when that is the bottleneck. It must honor durability requests; device power-loss protection can help meet that requirement with good performance.
- Compression (such as lz4 or zstd) trades CPU work for potentially less storage I/O; benefit depends on compressibility and workload.
- Deduplication maintains a deduplication table, with storage, memory-cache and processing costs that depend on the workload and implementation. Measure those costs and duplicate content before enabling it.
- On Linux, OpenZFS is deployed as a separate kernel module; packaging and supported versions depend on the distribution.

> [!tip] Choose features, then test the workload
> Compare required resize operations, repair tooling, snapshots, redundancy and supported configurations. On filesystem CoW storage, database page size, record size, compression and update patterns interact. Benchmark the actual database and durability settings before selecting a record size; no fixed value is optimal for every deployment.

## Key takeaways
- Checksums and recoverable redundancy serve different roles.
- ZFS uses pools, ARC and an intent log; a SLOG helps only when durable log I/O is the bottleneck.

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
