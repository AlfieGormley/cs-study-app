---
id: fs-journal-protocol
title: Journal commit and replay
level: intermediate
minutes: 2
summary: Log blocks must satisfy the commit protocol before a transaction is treated as committed.
sourceLesson: fs-crash-consistency
---

This unit focuses on journal commit and replay. The preceding units provide the file and storage concepts used here.

## Fix 2: journaling (write-ahead logging)

The idea, borrowed from databases: before changing the structures in place, write a note describing the change to a reserved area, the **journal**. If you crash mid-update, replay the note.

```
 journal (on disk)
 +-----+-------+-------+------+-----+
 | TxB | inode | bitmap| data | TxE |
 +-----+-------+-------+------+-----+
  begin   logged blocks       commit
```

The protocol for one transaction:

1. **Journal write**: write the begin block (TxB) and copies of the blocks to be changed.
2. **Journal commit**: once those are on disk, write the commit block (TxE). The transaction is now durable.
3. **Checkpointing**: write the blocks to their real locations.
4. **Free**: after checkpointing, mark that journal space reusable.

On recovery, the file system scans the journal. A transaction with a valid commit block gets **replayed** (its blocks rewritten to their final locations; doing this twice is harmless). One without a commit block is **discarded**, as if it never happened.

Ordinary journal replay works over recoverable log transactions rather than performing a full metadata scan. Journal size, pending transactions, device speed and other recovery work determine its duration.

> [!note] Recovery measurement gap
> No reproducible timing record accompanies this lesson. Fixed seconds-versus-hours guarantees and an unversioned ext4 journal-size range are omitted.

> [!note] Why the commit block is written separately
> If TxB, the logged blocks and TxE were sent together, the disk could write TxE first. A crash would then leave a "committed" transaction full of garbage. So the file system waits for the first batch to complete, then writes TxE. Ext4's journal_async_commit mode uses journal checksums to permit a different submission ordering and reject incomplete transactions. Merely enabling checksums is not the same as enabling asynchronous commit, and acknowledged durability still requires the needed writes to persist.

## Key takeaways
- Log blocks must satisfy the commit protocol before a transaction is treated as committed.
- Recovery replays valid committed transactions and discards incomplete ones.

## Further reading
- [OSTEP: Crash Consistency: FSCK and Journaling (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/file-journaling.pdf)
- [ext4 mount options (data=ordered, commit, auto_da_alloc) — kernel.org](https://www.kernel.org/doc/html/latest/admin-guide/ext4.html)
- [Fsync Errors — PostgreSQL wiki](https://wiki.postgresql.org/wiki/Fsync_Errors)
- [PostgreSQL's fsync() surprise — LWN.net](https://lwn.net/Articles/752063/)
- [Can Applications Recover from fsync Failures? — USENIX ATC 2020](https://www.usenix.org/conference/atc20/presentation/rebello)
- [All File Systems Are Not Created Equal — OSDI 2014](https://www.usenix.org/conference/osdi14/technical-sessions/presentation/pillai)
- [Files are hard — Dan Luu](https://danluu.com/file-consistency/)
- [fsync(2) — Linux manual page](https://man7.org/linux/man-pages/man2/fsync.2.html)
