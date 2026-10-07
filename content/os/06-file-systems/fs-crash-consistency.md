---
id: fs-crash-consistency
title: Crash consistency, journaling and fsync
level: intermediate
minutes: 15
summary: Why a power cut mid-update can corrupt a file system, how fsck, journaling (ext4's ordered mode) and copy-on-write (ZFS, Btrfs) defend against it, and the fsync pitfalls behind PostgreSQL's 2018 "fsyncgate".
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
3. **Checkpoint**: write the blocks to their real locations.
4. **Free**: after checkpointing, mark that journal space reusable.

On recovery, the file system scans the journal. A transaction with a valid commit block gets **replayed** (its blocks rewritten to their final locations; doing this twice is harmless). One without a commit block is **discarded**, as if it never happened.

Ordinary journal replay works over recoverable log transactions rather than performing a full metadata scan. Journal size, pending transactions, device speed and other recovery work determine its duration.

> [!note] Recovery measurement gap
> No reproducible timing record accompanies this lesson. Fixed seconds-versus-hours guarantees and an unversioned ext4 journal-size range are omitted.

> [!note] Why the commit block is written separately
> If TxB, the logged blocks and TxE were sent together, the disk could write TxE first. A crash would then leave a "committed" transaction full of garbage. So the file system waits for the first batch to complete, then writes TxE. Ext4's journal_async_commit mode uses journal checksums to permit a different submission ordering and reject incomplete transactions. Merely enabling checksums is not the same as enabling asynchronous commit, and acknowledged durability still requires the needed writes to persist.

### Data journaling vs metadata journaling

In the simple full-data-journaling model, payload is written to the journal and later home locations. This increases write traffic; achieved throughput is not necessarily halved because batching, layout and device behavior matter. So most systems journal **only metadata**, and the question becomes: when is the data block written?

ext4's three modes (the `data=` mount option):

| Mode | Journals | Guarantee |
|---|---|---|
| `journal` | data + metadata | Strongest; data written twice |
| `ordered` (default) | metadata only | Data on disk before its metadata commits |
| `writeback` | metadata only | No ordering; files can show old garbage |

In **ordered mode**, before committing a transaction that points an inode at new blocks, ext4 forces those data blocks to their final location. This ordering prevents exposing stale contents of newly allocated blocks through a committed metadata update, assuming a correctly functioning storage stack. It does not make arbitrary multi-block application writes atomic or guarantee only a complete old/new application state.

By default ext4 commits a transaction every **5 seconds** (`commit=5`). This controls transaction scheduling, not an application-level maximum loss window; delayed allocation, I/O delays and configuration matter. Use explicit synchronization for acknowledged durability.

> [!warning] Journaling protects the file system, not your data
> A journal guarantees the file system's own structures are consistent. It does not guarantee that the bytes your program `write()`-ed 3 seconds ago survived. For that, you need `fsync`.

## Fix 3: copy-on-write (ZFS, Btrfs)

The other approach: **never overwrite live data**. To change a block, write a new copy somewhere free, then update the pointer to it. That pointer lives in a parent block, which also gets copied, and so on up to the root.

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

- **Fragmentation.** Overwriting the middle of a file moves that block elsewhere, so databases doing random updates on CoW file systems see files scatter. Btrfs allows NOCOW for newly created/empty files, or inheritance from a directory via chattr +C; existing populated files are not retroactively converted. Shared snapshot extents still require COW on modification.
- **Write amplification.** One small change rewrites a path of blocks up to the root. Both systems batch many changes into each transaction (ZFS, every few seconds) to spread the cost, and ZFS adds an intent log (the ZIL) so `fsync` doesn't have to wait for a full transaction.

## Durability: what fsync really promises

Ordinary buffered regular-file write copies data into cache; direct and synchronous I/O have different paths and completion semantics. The kernel writes them out later (lesson 4). To force them to stable storage, you call:

- **`fsync(fd)`**: flush the file's data *and* metadata, and ask the device to flush its own write cache. Successful completion promises durability under the filesystem/device contract; errors must be checked and faulty hardware can violate it.
- **`fdatasync(fd)`**: the same, but skips metadata not needed to read the data back (such as mtime). It may avoid work; speed depends on workload and filesystem.

Three pitfalls catch nearly everyone.

### Pitfall 1: a new file's name needs its directory fsynced

`fsync` on a file makes its *contents* durable. Its *name* is an entry in the parent directory, which is a separate file. After creating or renaming a file, `fsync` the directory too, or the file can vanish after a crash.

### Pitfall 2: atomic replacement needs the whole dance

To replace `config.json` so a crash leaves either the old or the new version, never a half-written one:

```python
import os
import tempfile

def atomic_write(path, data):
    d = os.path.dirname(path) or "."
    fd, tmp = tempfile.mkstemp(dir=d)
    try:
        try:
            view = memoryview(data)
            while view:
                n = os.write(fd, view)
                if n <= 0:
                    raise OSError(
                        "no progress")
                view = view[n:]
            os.fsync(fd)
        finally:
            os.close(fd)
        os.replace(tmp, path)
        dfd = os.open(d, os.O_RDONLY)
        try:
            os.fsync(dfd)
        finally:
            os.close(dfd)
    finally:
        try:
            os.unlink(tmp)
        except FileNotFoundError:
            pass
```

This example assumes a trusted stable directory, no concurrent replacement, a previously durable old file, and filesystem/device support for the synchronization contract. It creates a mode-0600 replacement; preserving ownership, ACLs and other metadata needs explicit handling before fsync. If an error occurs after rename, the visible result may already be new even though durability is uncertain.

`rename` within one file system is atomic for namespace visibility: anyone looking sees the old file or the new one. But without step 1, the rename can reach disk *before* the data does.

> [!example] The ext4 zero-length file saga
> In 2009, ext4's delayed allocation exposed applications that skipped step 1. After crashes, users found config files that were zero bytes long: the rename had committed, but the new file's data blocks had never been allocated. Developers argued that POSIX never promised more. ext4 added the `auto_da_alloc` heuristic, which spots replace-via-rename and replace-via-truncate and forces the data out before the rename commits. Portable code still shouldn't rely on it.

### Pitfall 3: a failed fsync can't simply be retried

This was the core of **fsyncgate**. In 2018, Craig Ringer reported that PostgreSQL could silently lose data on Linux after a storage error.

PostgreSQL writes dirty pages with plain `write()`. Its checkpointer later calls `fsync()` on each file. If that succeeded, it considered the data durable and could recycle the write-ahead log (WAL) that would otherwise let it redo those changes.

What actually happened on Linux when write-back hit an I/O error (for example, a thin-provisioned volume running out of space):

1. The kernel failed to write a dirty page and reported `EIO` from the next `fsync`.
2. It then marked the page **clean**, even though it was never written. The data now existed only in a page the kernel could drop at any time.
3. The affected PostgreSQL behavior treated the failure as transient and retried at the next checkpoint.
4. The retried `fsync` had nothing dirty to flush, so it returned **success**.
5. PostgreSQL recycled the WAL. Recovery data could then be lost despite an earlier error having been reported.

Older kernels (before 4.13) could also lose the error altogether, or report it to a different descriptor than the one PostgreSQL later used. Linux 4.13 introduced improved writeback-error tracking using errseq_t. Relevant open file descriptions can observe newly recorded errors, but this is not an unbounded queue of every failure; sampling/coalescing and filesystem attribution matter. Improved reporting does not guarantee preservation of failed dirty data for a retry.

PostgreSQL changed the default to **PANIC on data-file synchronization failure**, documented in release 11.2 (14 February 2019), with data_sync_retry controlling the behavior. Restart and WAL recovery avoid blindly trusting a retry, subject to surviving WAL and storage. Unverified claims about other databases making the same change are omitted.

> [!tip] The rule fsyncgate taught
> A writeback-related fsync failure makes durability uncertain: data may have been lost, but the error does not prove every byte was lost. A successful retry alone is not recovery. Diagnose the error and use an application recovery/rewrite protocol or fail the operation. Errors such as EINTR have different semantics; do not replace error-specific handling with a claim that every failed fsync proves data loss.

### The device can lie too

A drive acknowledges a write when it reaches its volatile write cache, not the medium. File systems issue **cache flush** (and FUA, force unit access) commands to make journal commits truly durable. A device/controller that dishonors the durability contract can lose writes acknowledged as durable. Volatile caches without batteries can still be safe when correct flush/FUA handling persists data; power-loss protection is another mechanism, and its presence/scope must be checked per product.

## Key takeaways
- One logical update needs several block writes; a crash can leave any subset on disk.
- fsck repairs metadata by scanning everything: slow on big disks, and blind to wrong-but-consistent contents.
- Journaling logs changes first, commits, then checkpoints; recovery replays committed transactions and discards the rest.
- ext4's default ordered mode journals metadata only but writes data blocks before the metadata that references them.
- CoW designs commit new trees while retaining old state; real systems add logs, redundant commit records and configurable data/checksum policies.
- For durability: `fsync` the file, `rename` atomically, `fsync` the directory. Treat writeback-error durability as uncertain; a successful retry alone does not recover possibly lost data.

## Further reading
- [OSTEP: Crash Consistency: FSCK and Journaling (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/file-journaling.pdf)
- [ext4 mount options (data=ordered, commit, auto_da_alloc) — kernel.org](https://www.kernel.org/doc/html/latest/admin-guide/ext4.html)
- [Fsync Errors — PostgreSQL wiki](https://wiki.postgresql.org/wiki/Fsync_Errors)
- [PostgreSQL's fsync() surprise — LWN.net](https://lwn.net/Articles/752063/)
- [Can Applications Recover from fsync Failures? — USENIX ATC 2020](https://www.usenix.org/conference/atc20/presentation/rebello)
- [All File Systems Are Not Created Equal — OSDI 2014](https://www.usenix.org/conference/osdi14/technical-sessions/presentation/pillai)
- [Files are hard — Dan Luu](https://danluu.com/file-consistency/)
- [fsync(2) — Linux manual page](https://man7.org/linux/man-pages/man2/fsync.2.html)
