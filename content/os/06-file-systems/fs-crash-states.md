---
id: fs-crash-states
title: Partial updates and filesystem checking
level: intermediate
minutes: 3
summary: A multi-block update can leave metadata and data inconsistent after a crash.
sourceLesson: fs-crash-consistency
---

A single logical change to a file system usually needs **several** block writes. Storage can execute multiple writes concurrently; it does not ordinarily make an arbitrary multi-block filesystem update atomic. Power can fail with only part persisted. Whatever state the disk is left in, the file system must be able to make sense of it on the next boot.

That is the **crash consistency** problem. It shapes the design of every file system, and of every database that sits on top of one.

## The problem: one append, three writes

In a teaching model, appending one newly allocated 4 KiB block updates three structures (real filesystems may update more):

1. The **data block** itself (the new bytes).
2. The **inode** (new size, new block pointer).
3. The **data bitmap** (mark the block as used).

The kernel and the disk may reorder these writes for speed. If the system crashes after only some of them reach the disk:

| Only these persisted | Result |
|---|---|
| Data | Harmless; the write is just lost |
| Inode | Inode points at garbage; bitmap disagrees |
| Bitmap | Block leaked: used but owned by no one |
| Inode + bitmap | Consistent metadata, garbage contents |
| Inode + data | Bitmap says free: block may be reused |
| Bitmap + data | Leaked block containing data |

The worst cases are when **metadata** points somewhere wrong. A file can expose another user's old data, or two files can end up sharing a block.

## Fix 1: fsck, check everything after a crash

The early answer was to let inconsistencies happen and repair them at boot. A classic full filesystem checker scans relevant metadata across the filesystem:

- Rebuilds the bitmaps from the inodes that are actually in use.
- Checks that no block is claimed by two inodes.
- Recomputes link counts by walking every directory.
- Puts orphaned inodes in `lost+found`.

It works, but it has two flaws:

- **It's slow.** Work depends heavily on metadata volume, layout and checking algorithms rather than only the damaged portion. On a multi-terabyte array of spinning disks it can take hours.
- **It only restores consistency, not correctness.** In the "inode + bitmap" case, fsck sees nothing wrong, and the file quietly contains garbage.

## Key takeaways
- A multi-block update can leave metadata and data inconsistent after a crash.
- A checker can repair structure while failing to identify wrong-but-consistent file contents.

## Further reading
- [OSTEP: Crash Consistency: FSCK and Journaling (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/file-journaling.pdf)
- [ext4 mount options (data=ordered, commit, auto_da_alloc) — kernel.org](https://www.kernel.org/doc/html/latest/admin-guide/ext4.html)
- [Fsync Errors — PostgreSQL wiki](https://wiki.postgresql.org/wiki/Fsync_Errors)
- [PostgreSQL's fsync() surprise — LWN.net](https://lwn.net/Articles/752063/)
- [Can Applications Recover from fsync Failures? — USENIX ATC 2020](https://www.usenix.org/conference/atc20/presentation/rebello)
- [All File Systems Are Not Created Equal — OSDI 2014](https://www.usenix.org/conference/osdi14/technical-sessions/presentation/pillai)
- [Files are hard — Dan Luu](https://danluu.com/file-consistency/)
- [fsync(2) — Linux manual page](https://man7.org/linux/man-pages/man2/fsync.2.html)
