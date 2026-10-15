---
id: fs-cow-commits
title: Copy-on-write trees and integrity
level: intermediate
minutes: 3
summary: Copy-on-write builds new blocks before selecting a durable new root.
sourceLesson: fs-crash-consistency
---

This unit focuses on filesystem copy-on-write trees and integrity. The preceding units provide the file and storage concepts used here.

## Fix 3: filesystem copy-on-write (ZFS, Btrfs)

The other approach, used by **copy-on-write file systems**: **never overwrite live data**. To change a block, write a new copy somewhere free, then update the pointer to it. That pointer lives in a parent block, which also gets copied, and so on up to the root.

```
 before          after modifying D
   R               R'  (new root)
  / \             /  \
 A   B           A    B'
    / \              /  \
   C   D            C    D'
```

The file system becomes a tree of blocks. All the new blocks (D', B', R') are written to free space. Conceptually, a durable commit selects the new root after its dependencies are stable. Real implementations use checksummed and redundant commit records rather than assuming every root-sector write is magically atomic. ZFS uses uberblocks to identify committed tree state.

- Crash before the root switch: the old tree R is untouched and fully consistent.
- Crash after: the new tree is complete.

Copy-on-write reduces reliance on in-place metadata repair, but these systems still have recovery machinery: ZFS uses an intent log for synchronous operations, and Btrfs has a tree log and btrfs check. Snapshots can initially share blocks cheaply; retained old versions consume space as data changes.

ZFS block-pointer checksums and Btrfs checksums can detect silent corruption within their configured protection scope. Btrfs metadata carries checksums, while data checksumming can be disabled, including for NOCOW data. Recoverable redundancy can let a read find and repair a valid copy; repair is not possible if every copy is bad. This protection is separate from ext4's metadata journal, which does not generally checksum ordinary file payload.

The costs:

- **File fragmentation.** Overwriting the middle of a file moves that block elsewhere, so databases doing random updates on copy-on-write file systems see files scatter. Btrfs allows NOCOW for newly created/empty files, or inheritance from a directory via chattr +C; existing populated files are not retroactively converted. Shared snapshot extents still require filesystem CoW on modification.
- **Write amplification.** One small change rewrites a path of blocks up to the root. Both systems batch many changes into each transaction (ZFS, every few seconds) to spread the cost, and ZFS adds an intent log (the ZIL) so `fsync` doesn't have to wait for a full transaction.

## Key takeaways
- Copy-on-write builds new blocks before selecting a durable new root.
- Checksums detect mismatches; repair requires a valid copy, and retained versions can fragment files.

## Further reading
- [OSTEP: Crash Consistency: FSCK and Journaling (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/file-journaling.pdf)
- [ext4 mount options (data=ordered, commit, auto_da_alloc) — kernel.org](https://www.kernel.org/doc/html/latest/admin-guide/ext4.html)
- [Fsync Errors — PostgreSQL wiki](https://wiki.postgresql.org/wiki/Fsync_Errors)
- [PostgreSQL's fsync() surprise — LWN.net](https://lwn.net/Articles/752063/)
- [Can Applications Recover from fsync Failures? — USENIX ATC 2020](https://www.usenix.org/conference/atc20/presentation/rebello)
- [All File Systems Are Not Created Equal — OSDI 2014](https://www.usenix.org/conference/osdi14/technical-sessions/presentation/pillai)
- [Files are hard — Dan Luu](https://danluu.com/file-consistency/)
- [fsync(2) — Linux manual page](https://man7.org/linux/man-pages/man2/fsync.2.html)
