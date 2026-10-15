---
id: fs-nfs-retries
title: NFS retries, caching and protocol state
level: advanced
minutes: 4
summary: NFSv3 avoids server open-file state in its core access protocol.
sourceLesson: fs-modern-distributed
---

This unit focuses on NFS handles, retries and statelessness. The preceding units provide the file and storage concepts used here.

## NFS: a remote file system that looks local

Sun's **Network File System** (1984) lets a client mount a directory exported by a server. Thanks to the VFS layer from the first lesson, programs use ordinary `open`, `read` and `write`; the NFS client turns them into RPCs to the server (commonly TCP port 2049; NFSv3 can use other transports and auxiliary RPC services).

### NFSv3: a stateless server

NFSv2 and v3 were designed so the basic file-access protocol avoids per-client **open-file state**. Caches, unstable writes and separate locking services can still involve state. Every request carries everything needed to execute it:

```
READ(fh, offset=8192, count=4096)
```

- `fh` is a **file handle**: an opaque token, typically encoding the file system, inode number and a generation number (so a reused inode number doesn't resurrect a deleted file).
- There's no `open` or file position on the server. The client tracks offsets.
- Operations such as reading or writing a fixed byte range support simple retry models, but concurrent changes can alter read results or be overwritten by a repeated write. Lost replies require attention to operation semantics and duplicate handling.

Avoiding open-file state in the basic protocol simplifies crash recovery. A default **hard** mount retries timed-out requests indefinitely, subject to other error and interruption behavior; this does not mean the server has no persistent state to recover. A **soft** mount gives up after retries and returns an error, which the nfs(5) man page warns can cause silent data corruption.

Lost replies are an awkward edge: if a `REMOVE` succeeds but the reply is lost, re-executing it can return "no such file" when nobody recreates the name. That different reply does not by itself prove a second deletion changed the final state. If another client recreates the name, a retry can delete a different object. Duplicate request caches help avoid re-execution while a cached result remains available.

### Caching and close-to-open consistency

Sending every `read` over the network would be painfully slow, so clients cache data and attributes, and NFS defines a weak but useful guarantee: **close-to-open consistency**.

1. On `close` (or `fsync`), the client flushes its dirty data to the server.
2. On `open`, the client checks the file's attributes (modification time, change attribute) with the server and discards stale cached data.

With close-to-open behavior enabled, successful writeback/close and no intervening writer, B's later open revalidates A's changes. Applications must check write, fsync and close errors. Between those points there are no promises. Attributes are cached for 3–60 seconds by default (`acregmin`/`acregmax`; 30–60 s for directories), so `ls` on one client can show stale sizes from another.

> [!warning] Classic NFS pitfalls
> - Two clients appending to the same log file intermix unpredictably; `O_APPEND` isn't atomic across clients in v3.
> - Lock files and `flock` behave differently than on local disks; v3 needs the separate NLM lock protocol.
> - A file handle that no longer identifies a valid server object can produce `ESTALE`; deletion and client-side open-file handling have implementation-dependent details.
> - SQLite and similar databases warn against running on NFS for these reasons.

### NFSv4

NFSv4 (RFC 3530, now RFC 7530) abandoned statelessness where it hurt:

- Explicit `OPEN` and `CLOSE`, with **leases**: the client must renew within the lease period, or the server reclaims its state. After a server reboot there's an **NFS grace period** for clients to reclaim locks.
- Locking built into the protocol, one well-known port, and **COMPOUND** requests that batch several operations into one round trip.
- **Delegations**: the server can grant a read or write delegation, so it can cache aggressively until the server recalls the delegation.
- NFSv4.1 added sessions (duplicate-request handling within session, slot and replay-cache rules) and **pNFS**, where clients read data directly from storage nodes in parallel.


## Key takeaways
- NFSv3 avoids server open-file state in its core access protocol.
- Lost replies need duplicate handling; blind re-execution can return a different result.

- Close-to-open consistency does not provide continuous cross-client coherence.
- NFSv4 adds explicit state, leases, locking and delegations; later revisions add sessions and pNFS.


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
