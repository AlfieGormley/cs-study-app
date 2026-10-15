---
id: fs-hdfs-data-path
title: GFS and HDFS metadata and data paths
level: advanced
minutes: 4
summary: Clients obtain locations from a metadata master and transfer payload directly with storage nodes.
sourceLesson: fs-modern-distributed
---

This unit focuses on GFS and HDFS metadata and data paths. The preceding units provide the file and storage concepts used here.

## GFS and HDFS: built for huge files

By 2003 Google was storing web crawls on thousands of cheap machines where disk and node failures were daily events. The **Google File System** paper made design choices that suited that workload rather than POSIX:

- Files are huge (multi-GB) and mostly **appended to** and read sequentially. Random overwrites are rare.
- Throughput matters far more than latency.
- Failure is normal, so redundancy is in software across machines, not in RAID.

**HDFS**, Hadoop's open-source system inspired by GFS, follows related design ideas:

```
            +-----------+
 client --->| NameNode  | 1. metadata:
    |       | (master)  | names, blocks,
    |       +-----------+ locations
    | 2. data directly
    v
 +--------+ +--------+ +--------+
 |DataNode| |DataNode| |DataNode|
 | blk A  | | blk A  | | blk A  |
 +--------+ +--------+ +--------+
```

| | GFS (2003) | HDFS |
|---|---|---|
| Master | master | NameNode |
| Storage nodes | chunkservers | DataNodes |
| Unit | 64 MB chunk (paper notation) | commonly 128 MiB block; configurable |
| Replicas | 3 | 3 (default) |

How it works (the block count for big blocks is worked out after the list):

- **A master serves each file system namespace**: it holds the directory tree, file-to-block mappings and reported replica locations in memory. Namespace mutations are logged and checkpointed. HDFS reconstructs block locations from DataNode reports rather than persisting every location in its edit log.
- **Data never flows through the master.** The client asks the master where blocks are, then reads or writes DataNodes directly. One master can then coordinate thousands of nodes.
- **Big blocks** keep the metadata small (a 1 TiB file is exactly 8,192 blocks of 128 MiB, worked out below) and make each read a long sequential stream.
- **Writes are pipelined**: the client sends data to the first replica, which forwards it to the second, which forwards to the third, so one payload copy travels along each hop; intermediate nodes receive and forward data, and acknowledgements travel back.
- **Rack-aware placement.** With replication 3 and enough eligible nodes across racks, the default policy puts one replica on the writer's node (or a random node in its rack), and two on different nodes in one other rack. That survives a whole rack failing while sending only one copy across racks.
- When a DataNode stops sending heartbeats, the NameNode re-replicates its blocks from the surviving copies.

The block count is the file size divided by the block size, rounded up:

```formula
n = ⌈S / B_blk⌉
n = 2^40 B / (2^27 B) = 2^13 = 8,192
where
n: the number of HDFS blocks the file is split into
S: the file size; here 1 TiB = 2^40 bytes (2^40 means 40 copies of 2 multiplied together)
B_blk: the HDFS block size; here 128 MiB = 2^27 bytes
⌈ ⌉: the ceiling: round up, because a part-filled last block is still a block
B: byte
TiB: tebibyte, 2^40 bytes
MiB: mebibyte, 2^20 bytes
In words: a 1 TiB file in 128 MiB blocks needs only 8,192 block records in the NameNode's memory; with 4 KiB blocks it would need 268 million.
```

## Key takeaways
- Clients obtain locations from a metadata master and transfer payload directly with storage nodes.
- Large blocks and pipelined rack-aware replication reduce metadata and cross-rack costs.

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
