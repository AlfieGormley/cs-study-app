---
id: fs-modern-distributed
title: Real file systems, from ext4 to HDFS
level: advanced
minutes: 16
summary: How ext4, XFS, Btrfs and ZFS differ in practice, the log-structured idea behind LFS and F2FS, and how NFS, GFS and HDFS stretch a file system across a network.
---

The earlier lessons built a file system from parts: inodes, extents, a journal or copy-on-write, the page cache. Real systems pick different combinations of those parts, and the choices show up as concrete differences: whether you can shrink a volume, whether silent corruption is detected, how a database behaves on it.

Then we leave the single machine. NFS makes a remote disk look local; GFS and HDFS give up on looking local and build something new for huge files across thousands of machines.

## The local file systems you'll meet on Linux

| | ext4 | XFS | Btrfs | ZFS |
|---|---|---|---|---|
| Consistency | journal | journal | CoW | CoW |
| Checksums | metadata by configuration | metadata by format | data and metadata, with exceptions | data and metadata, configurable |
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

### Btrfs

A copy-on-write B-tree file system in the mainline kernel.

- Checksums metadata and, by default, file data. NOCOW/nodatasum files have exceptions; repair needs a valid redundant copy.
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
> Compare required resize operations, repair tooling, snapshots, redundancy and supported configurations. On CoW storage, database page size, record size, compression and update patterns interact. Benchmark the actual database and durability settings before selecting a record size; no fixed value is optimal for every deployment.

## Log-structured file systems

In their early-1990s LFS work, Mendel Rosenblum and John Ousterhout considered two trends. RAM was growing, so the page cache would absorb most **reads**. That left disk traffic dominated by **writes**, and small writes to scattered inodes, bitmaps and data blocks were dreadful on a disk whose random I/O is limited by seek and rotation.

Their answer, **LFS**, was radical: treat the whole disk as a log. Buffer every change (data, inodes, directory blocks) in memory, then write it out as one large sequential **segment** of several hundred KiB to a few MiB.

```
 disk: |seg 1  |seg 2  |seg 3  | free ...
         D D I   D I D   D D I M
                              ^
              new versions go at the end
 D = data, I = inode, M = imap piece
```

Nothing is overwritten in place, which raises two problems.

**Finding inodes.** An inode's location changes every time it's written. LFS adds an **inode map (imap)**: inode number → current disk address. The imap is itself written into the log in pieces, and a **checkpoint region** at a fixed place on disk points at the latest pieces. Recovery reads the checkpoint, then rolls forward through segments written after it.

**Reclaiming space.** Old versions of blocks become garbage, scattered through old segments. A **cleaner** reads partly-dead segments, writes their live blocks into a new segment, and frees the old ones. Each segment has a summary block recording which inode and offset every block belongs to, so the cleaner can check whether a block is still live.

Cleaning a segment that is a fraction *u* live requires reading it and rewriting its live fraction to reclaim (1 − *u*) of capacity. In a steady-state model excluding metadata, total writes per unit of new data are 1/(1 − *u*); counting reads as well is a different I/O-cost measure. LFS's **cost-benefit** policy balances segment age and utilization to favor reclaimed space likely to remain useful.

### Where the idea lives now

- **SSD firmware.** The FTL in the previous lesson is a log-structured system with a mapping table and a cleaner.
- **F2FS** (Flash-Friendly File System), from Samsung and merged in Linux 3.8, is log-structured and designed for flash. It separates hot and cold data into different logs and uses a **node address table** so that moving one block doesn't force rewrites all the way up the tree (the "wandering tree" problem).
- **Copy-on-write file systems** (ZFS, Btrfs, NetApp's WAFL) share the never-overwrite principle.
- **LSM trees** in RocksDB, Cassandra and LevelDB apply it to key-value stores: append-only sorted files plus compaction, which similarly reclaims obsolete versions but follows different structures and correctness rules.

## NFS: a remote file system that looks local

Sun's **Network File System** (1984) lets a client mount a directory exported by a server. Thanks to the VFS layer from the first lesson, programs use ordinary `open`, `read` and `write`; the NFS client turns them into RPCs to the server (commonly TCP port 2049; NFSv3 can use other transports and auxiliary RPC services).

### NFSv3: a stateless server

NFSv2 and v3 were designed so the core file-access protocol avoids per-client **open-file state**. Caches, unstable writes and separate locking services can still involve state. Every request carries everything needed to execute it:

```
READ(fh, offset=8192, count=4096)
```

- `fh` is a **file handle**: an opaque token, typically encoding the file system, inode number and a generation number (so a reused inode number doesn't resurrect a deleted file).
- There's no `open` or file position on the server. The client tracks offsets.
- Operations such as reading or writing a fixed byte range support simple retry models, but concurrent changes can alter read results or be overwritten by a repeated write. Lost replies require attention to operation semantics and duplicate handling.

Avoiding core open-file state simplifies crash recovery. A default **hard** mount retries timed-out requests indefinitely, subject to other error and interruption behavior; this does not mean the server has no persistent state to recover. A **soft** mount gives up after retries and returns an error, which the nfs(5) man page warns can cause silent data corruption.

Non-idempotent operations are the awkward edge: if a `REMOVE` succeeds but the reply is lost, re-executing it can return "no such file" when nobody recreates the name. Servers keep a duplicate request cache to paper over this.

### Caching and close-to-open consistency

Sending every `read` over the network would be painfully slow, so clients cache data and attributes, and NFS defines a weak but useful guarantee: **close-to-open consistency**.

1. On `close` (or `fsync`), the client flushes its dirty data to the server.
2. On `open`, the client checks the file's attributes (modification time, change attribute) with the server and discards stale cached data.

With close-to-open behavior enabled, successful writeback/close and no intervening writer, B's later open revalidates A's changes. Applications must check write, fsync and close errors. Between those points there are no promises. Attributes are cached for 3–60 seconds by default (`acregmin`/`acregmax`; 30–60 s for directories), so `ls` on one client can show stale sizes from another.

> [!warning] Classic NFS pitfalls
> - Two clients appending to the same log file interleave unpredictably; `O_APPEND` isn't atomic across clients in v3.
> - Lock files and `flock` behave differently than on local disks; v3 needs the separate NLM lock protocol.
> - A file handle that no longer identifies a valid server object can produce `ESTALE`; deletion and client-side open-file handling have implementation-dependent details.
> - SQLite and similar databases warn against running on NFS for these reasons.

### NFSv4

NFSv4 (RFC 3530, now RFC 7530) abandoned statelessness where it hurt:

- Explicit `OPEN` and `CLOSE`, with **leases**: the client must renew within the lease period, or the server reclaims its state. After a server reboot there's a **grace period** for clients to reclaim locks.
- Locking built into the protocol, one well-known port, and **COMPOUND** requests that batch several operations into one round trip.
- **Delegations**: the server can grant a read or write delegation, so it can cache aggressively until the server recalls the delegation.
- NFSv4.1 added sessions (duplicate-request handling within session, slot and replay-cache rules) and **pNFS**, where clients read data directly from storage nodes in parallel.

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
| Unit | 64 MiB chunk in the paper | commonly 128 MiB block; configurable |
| Replicas | 3 | 3 (default) |

How it works:

- **A master serves each namespace**: it holds the namespace, file-to-block mappings and reported replica locations in memory. Namespace mutations are logged and checkpointed. HDFS reconstructs block locations from DataNode reports rather than persisting every location in its edit log.
- **Data never flows through the master.** The client asks the master where blocks are, then reads or writes DataNodes directly. One master can then coordinate thousands of nodes.
- **Big blocks** keep the metadata small (a 1 TiB file is exactly 8,192 blocks of 128 MiB) and make each read a long sequential stream.
- **Writes are pipelined**: the client sends data to the first replica, which forwards it to the second, which forwards to the third, so one payload copy travels along each pipeline hop; intermediate nodes receive and forward data, and acknowledgements travel back.
- **Rack-aware placement.** With replication 3 and enough eligible nodes across racks, the default policy puts one replica on the writer's node (or a random node in its rack), and two on different nodes in one other rack. That survives a whole rack failing while sending only one copy across racks.
- When a DataNode stops sending heartbeats, the NameNode re-replicates its blocks from the surviving copies.

GFS's consistency model was deliberately relaxed. Its **record append** operation guarantees each record is written atomically **at least once**, so readers can see duplicates and padding and must use checksums and record IDs to filter them. HDFS uses a single-writer model, with supported append and truncate operations rather than arbitrary in-place byte updates.

The weak points follow from the single master:

- **Memory.** Namespace entries and blocks consume NameNode memory, with size depending on Hadoop version, JVM and metadata. A large small-file population can exhaust heap despite modest payload size. This is the **small-files problem**, and why HDFS wants big files.
- **Availability.** Early HDFS had a single point of failure. HDFS can use active/standby NameNodes with shared edits; a JournalNode quorum is one documented approach, and ZooKeeper supports automatic failover when configured. Federation splits the namespace across several NameNodes.
- **Cost of replication.** Three copies is 200% overhead. Hadoop 3 added **erasure coding**: the default RS-6-3 policy stores 6 data and 3 parity cells, can reconstruct any three missing cells in a stripe and has 50% ideal payload overhead for full stripes. Short files, metadata and placement affect actual capacity; reading missing data requires reconstruction work. In the cited Hadoop 3.3.5 documentation, striped EC files do not support append or truncate, and `hflush`/`hsync` do not provide ordinary replicated-file sync behavior.

Object stores can separate storage from compute, but their APIs are not interchangeable with POSIX filesystems. Capabilities depend on product and bucket type: S3 Express One Zone directory buckets support object append, and Cloud Storage hierarchical-namespace buckets support folder rename. Check the actual API instead of assuming every object store requires copying a whole prefix to rename it.

> [!note] Deployment evidence gap
> No measured NameNode heap profile or identified storage benchmark accompanies this lesson. Fixed bytes-per-object and guaranteed filesystem/SLOG latency claims are omitted. Quiz numbers explicitly marked as assumptions are arithmetic models, not observed deployments.

## Key takeaways
- ext4 and XFS journal metadata. XFS uses allocation groups for parallel allocation and has limited, version-dependent shrink support; their ordinary metadata checksums do not protect mutable file payload.
- ZFS and Btrfs offer CoW, configurable integrity protection, snapshots and integrated redundancy. ZFS adds a pool model, ARC and an intent log that may use separate log devices.
- LFS turns all writes into sequential segment writes, using an inode map and a cleaner; its ideas live on in SSD FTLs, F2FS, CoW file systems and LSM trees.
- NFSv3 avoids core open-file state and uses retries with duplicate handling, with close-to-open consistency; NFSv4 adds state, leases, locking and delegations.
- GFS and HDFS separate a single in-memory metadata master from data nodes, use huge blocks, pipelined triple replication and rack awareness, and pay for it with the small-files problem.

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
