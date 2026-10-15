---
id: fs-writeback-errors
title: Writeback errors and device durability
level: intermediate
minutes: 3
summary: A successful fsync retry does not recover dirty data lost after an earlier writeback error.
sourceLesson: fs-crash-consistency
---

This unit focuses on writeback errors and device durability. The preceding units provide the file and storage concepts used here.

### Pitfall 3: a failed fsync can't simply be retried

This was the heart of **fsyncgate**. In 2018, Craig Ringer reported that PostgreSQL could silently lose data on Linux after a storage error.

PostgreSQL writes dirty pages with plain `write()`. Its checkpointer later calls `fsync()` on each file. If that succeeded, it considered the data durable and could recycle the write-ahead log (WAL) that would otherwise let it redo those changes.

What actually happened on Linux when write-back hit an I/O error (for example, a thin-provisioned volume running out of space):

1. The kernel failed to write a dirty page and reported `EIO` from the next `fsync`.
2. It then marked the page **clean**, even though it was never written. The data now existed only in a page the kernel could drop at any time.
3. The affected PostgreSQL behavior treated the failure as transient and retried at the next checkpoint.
4. The retried `fsync` had nothing dirty to flush, so it returned **success**.
5. PostgreSQL recycled the WAL. Recovery data could then be lost despite an earlier error having been reported.

Older kernels (before 4.13) could also lose the error altogether, or report it to a different descriptor than the one PostgreSQL later used. Linux 4.13 introduced improved writeback-error tracking using errseq_t. Relevant open file descriptions can observe newly recorded errors, but this is not an unbounded queue of every failure; sampling, merging of repeated errors and filesystem attribution matter. Improved reporting does not guarantee preservation of failed dirty data for a retry.

PostgreSQL changed the default to **PANIC on data-file synchronization failure**, documented in release 11.2 (14 February 2019), with data_sync_retry controlling the behavior. Restart and WAL recovery avoid blindly trusting a retry, subject to surviving WAL and storage. Unverified claims about other databases making the same change are omitted.

> [!tip] The rule fsyncgate taught
> A writeback-related fsync failure makes durability uncertain: data may have been lost, but the error does not prove every byte was lost. A successful retry alone is not recovery. Diagnose the error and use an application recovery/rewrite protocol or fail the operation. Errors such as EINTR have different semantics; do not replace error-specific handling with a claim that every failed fsync proves data loss.

### The device can lie too

A drive acknowledges a write when it reaches its volatile write cache, not the medium. File systems issue **cache flush** (and FUA, force unit access) commands to make journal commits truly durable. A device/controller that dishonors the durability contract can lose writes acknowledged as durable. Volatile caches without batteries can still be safe when correct flush/FUA handling persists data; power-loss protection is another mechanism, and its presence/scope must be checked per product.

## Key takeaways
- A successful fsync retry does not recover dirty data lost after an earlier writeback error.
- Filesystem durability also depends on the device honoring cache-flush and FUA contracts.

## Further reading
- [OSTEP: Crash Consistency: FSCK and Journaling (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/file-journaling.pdf)
- [ext4 mount options (data=ordered, commit, auto_da_alloc) — kernel.org](https://www.kernel.org/doc/html/latest/admin-guide/ext4.html)
- [Fsync Errors — PostgreSQL wiki](https://wiki.postgresql.org/wiki/Fsync_Errors)
- [PostgreSQL's fsync() surprise — LWN.net](https://lwn.net/Articles/752063/)
- [Can Applications Recover from fsync Failures? — USENIX ATC 2020](https://www.usenix.org/conference/atc20/presentation/rebello)
- [All File Systems Are Not Created Equal — OSDI 2014](https://www.usenix.org/conference/osdi14/technical-sessions/presentation/pillai)
- [Files are hard — Dan Luu](https://danluu.com/file-consistency/)
- [fsync(2) — Linux manual page](https://man7.org/linux/man-pages/man2/fsync.2.html)
