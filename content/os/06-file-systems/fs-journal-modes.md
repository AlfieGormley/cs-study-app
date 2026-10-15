---
id: fs-journal-modes
title: Data journaling and ext4 ordering
level: intermediate
minutes: 3
summary: Data journaling writes payload to the log and its home location; metadata journaling avoids that duplicate payload.
sourceLesson: fs-crash-consistency
---

This unit focuses on data journaling and ext4 ordering. The preceding units provide the file and storage concepts used here.

### Data journaling vs metadata journaling

In the simple full-data-journaling model, payload is written to the journal and later to its home location, so every byte is written twice:

```formula
W_journal ≈ 2D + m
W_ordered ≈ D + m
W_journal ≈ 2 × 1 GB = 2 GB
W_ordered ≈ 1 GB
where
W_journal: total bytes written to the device when data is journaled too, in gigabytes (GB)
W_ordered: total bytes written when only metadata is journaled
D: the amount of new file data the application writes; here 1 GB
m: the extra metadata traffic (journal blocks for inodes, bitmaps and extents), small next to D for large sequential writes and left out of the numeric lines
≈: approximately equal to
GB: gigabyte, 10^9 bytes
In words: journaling the data doubles the payload traffic, because each block goes to the journal first and then to its real place; journaling only metadata writes the payload once.
```

This is a traffic model, not a speed measurement: achieved throughput is not necessarily halved, because batching, layout and device behavior matter. Still, the doubling is why most systems journal **only metadata**, and the question becomes: when is the data block written?

ext4's three modes (the `data=` mount option):

| Mode | Journals | Guarantee |
|---|---|---|
| `journal` | data + metadata | Strongest; data written twice |
| `ordered` (default) | metadata only | Data on disk before its metadata commits |
| `writeback` | metadata only | No ordering; files can show old garbage |

In **ordered mode**, before committing a transaction that points an inode at new blocks, ext4 forces those data blocks to their final location. This ordering prevents exposing stale contents of newly allocated blocks through a committed metadata update, assuming correctly functioning storage hardware and drivers. It does not make arbitrary multi-block application writes atomic or guarantee only a complete old/new application state.

By default ext4 commits a transaction every **5 seconds** (`commit=5`). This controls transaction scheduling, not an application-level maximum loss window; delayed allocation, I/O delays and configuration matter. Use explicit synchronization for acknowledged durability.

> [!warning] Journaling protects the file system, not your data
> A journal guarantees the file system's own structures are consistent. It does not guarantee that the bytes your program `write()`-ed 3 seconds ago survived. For that, you need `fsync`.

## Key takeaways
- Data journaling writes payload to the log and its home location; metadata journaling avoids that duplicate payload.
- Ordered mode protects allocation ordering, while fsync is still needed for acknowledged application durability.

## Further reading
- [OSTEP: Crash Consistency: FSCK and Journaling (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/file-journaling.pdf)
- [ext4 mount options (data=ordered, commit, auto_da_alloc) — kernel.org](https://www.kernel.org/doc/html/latest/admin-guide/ext4.html)
- [Fsync Errors — PostgreSQL wiki](https://wiki.postgresql.org/wiki/Fsync_Errors)
- [PostgreSQL's fsync() surprise — LWN.net](https://lwn.net/Articles/752063/)
- [Can Applications Recover from fsync Failures? — USENIX ATC 2020](https://www.usenix.org/conference/atc20/presentation/rebello)
- [All File Systems Are Not Created Equal — OSDI 2014](https://www.usenix.org/conference/osdi14/technical-sessions/presentation/pillai)
- [Files are hard — Dan Luu](https://danluu.com/file-consistency/)
- [fsync(2) — Linux manual page](https://man7.org/linux/man-pages/man2/fsync.2.html)
