---
id: fs-hdfs-consistency-cost
title: Distributed-file consistency and redundancy costs
level: advanced
minutes: 3
summary: GFS record append permits duplicate records and padding; HDFS uses a single-writer model.
sourceLesson: fs-modern-distributed
---

This unit focuses on distributed-file consistency and redundancy costs. The preceding units provide the file and storage concepts used here.

## Consistency and metadata costs

GFS's consistency model was deliberately relaxed. A successful **record append** operation guarantees the record is written atomically **at least once**, so readers can see duplicates and padding and must use checksums and record IDs to filter them. HDFS uses a single-writer model, with supported append and truncate operations rather than arbitrary in-place byte updates.

The weak points follow from the single master:

- **Memory.** File system filesystem namespace entries and blocks consume NameNode memory, with size depending on Hadoop version, JVM and metadata. A large small-file population can exhaust the JVM heap despite modest payload size. This is the **small-files problem**, and why HDFS wants big files.
- **Availability.** Early HDFS had a single point of failure. HDFS can use active/standby NameNodes with shared edits; a JournalNode quorum is one documented approach, and ZooKeeper supports automatic failover when configured. Federation splits the file system namespace across several NameNodes.
- **Cost of replication.** Three copies is 200% overhead (worked out below). Hadoop 3 added **erasure coding**: the default RS-6-3 policy stores 6 data and 3 parity cells, can reconstruct any three missing cells in a stripe and has 50% ideal payload overhead for full stripes. Short files, metadata and placement affect actual capacity; reading missing data requires reconstruction work. In the cited Hadoop 3.3.5 documentation, striped EC files do not support append or truncate, and `hflush`/`hsync` do not provide ordinary replicated-file sync behavior.

Storage overhead is the extra space spent on redundancy, as a share of the payload:

```formula
O = (S_raw − D) / D
O_rep = (3D − D) / D = 2 = 200%
O_EC = ((9 / 6)D − D) / D = 0.5 = 50%
where
O: the storage overhead, extra bytes stored per byte of payload
S_raw: the raw bytes actually stored, payload plus redundancy
D: the payload (the data itself)
O_rep: the overhead of three-way replication, which stores 3 copies of everything
O_EC: the overhead of RS-6-3 erasure coding, which stores 9 cells (6 data + 3 parity) for every 6 cells of data
%: per cent; 2 = 200%
In words: three replicas store three times the data, 200% extra, while RS-6-3 stores 1.5 times, only 50% extra, and still survives three lost cells per stripe.
```

Object stores can separate storage from compute, but their APIs are not interchangeable with POSIX filesystems. Features depend on product and bucket type: S3 Express One Zone directory buckets support object append, and Cloud Storage hierarchical-filesystem namespace buckets support folder rename. Check the actual API instead of assuming every object store requires copying a whole prefix to rename it.

> [!note] Deployment evidence gap
> No measured NameNode JVM heap profile or identified storage benchmark accompanies this lesson. Fixed bytes-per-object and guaranteed filesystem/SLOG latency claims are omitted. Quiz numbers explicitly marked as assumptions are arithmetic models, not observed deployments.

## Key takeaways
- GFS record append permits duplicate records and padding; HDFS uses a single-writer model.
- Small files strain filesystem namespace memory, while erasure coding changes storage overhead and supported operations.

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
