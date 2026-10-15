---
id: fs-durable-replacement
title: Durable files and atomic replacement
level: intermediate
minutes: 3
summary: A file sync does not necessarily persist its newly created directory entry.
sourceLesson: fs-crash-consistency
---

This unit focuses on durable files and atomic replacement. The preceding units provide the file and storage concepts used here.

## Durability: what fsync really promises

Ordinary buffered regular-file write copies data into cache; direct and synchronous I/O have different paths and completion semantics. The kernel writes them out later (covered in the page-cache units). To force them to stable storage, you call:

- **`fsync(fd)`**: flush the file's data *and* metadata, and ask the device to flush its own write cache. Successful completion promises durability under the filesystem/device contract; errors must be checked and faulty hardware can violate it.
- **`fdatasync(fd)`**: the same, but skips metadata not needed to read the data back (such as mtime). It may avoid work; speed depends on workload and filesystem.

Three pitfalls catch nearly everyone.

### Pitfall 1: a new file's name needs its directory fsynced

`fsync` on a file makes its *contents* durable. Its *name* is an entry in the parent directory, which is a separate file. After creating or renaming a file, `fsync` the directory too, or the file can vanish after a crash.

### Pitfall 2: atomic replacement needs the whole dance

To replace `settings.json` so a crash leaves either the old or the new version, never a half-written one:

```python
import os
import tempfile

def atomic_write(path, data):
    d = os.path.dirname(path) or "."
    # Same directory keeps rename local.
    fd, tmp = tempfile.mkstemp(dir=d)
    try:
        try:
            view = memoryview(data)
            # Complete short writes first.
            while view:
                n = os.write(fd, view)
                if n <= 0:
                    raise OSError(
                        "no progress")
                view = view[n:]
            # Persist bytes before rename.
            os.fsync(fd)
        finally:
            os.close(fd)
        # Publish the complete replacement.
        os.replace(tmp, path)
        dfd = os.open(d, os.O_RDONLY)
        try:
            # Persist the name replacement.
            os.fsync(dfd)
        finally:
            os.close(dfd)
    finally:
        try:
            os.unlink(tmp)
        except FileNotFoundError:
            # Rename already removed tmp.
            pass
```

This example assumes a trusted stable directory, no concurrent replacement, a previously durable old file, and filesystem/device support for the synchronization contract. It creates a mode-0600 replacement; preserving ownership, ACLs and other metadata needs explicit handling before fsync. If an error occurs after rename, the visible result may already be new even though durability is uncertain.

`rename` within one file system is atomic as far as name lookups are concerned: anyone looking sees the old file or the new one. But without synchronizing the temporary file, the rename can reach disk *before* the data does.

> [!example] The ext4 zero-length file saga
> In 2009, ext4's delayed allocation exposed applications that skipped the temporary-file synchronization. After crashes, users found config files that were zero bytes long: the rename had committed, but the new file's data blocks had never been allocated. Developers argued that POSIX never promised more. ext4 added the `auto_da_alloc` heuristic, which spots replace-via-rename and replace-via-truncate and forces the data out before the rename commits. Portable code still shouldn't rely on it.

## Key takeaways
- A file sync does not necessarily persist its newly created directory entry.
- Durable replacement needs synchronized temporary contents, atomic rename and directory synchronization.

## Further reading
- [OSTEP: Crash Consistency: FSCK and Journaling (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/file-journaling.pdf)
- [ext4 mount options (data=ordered, commit, auto_da_alloc) — kernel.org](https://www.kernel.org/doc/html/latest/admin-guide/ext4.html)
- [Fsync Errors — PostgreSQL wiki](https://wiki.postgresql.org/wiki/Fsync_Errors)
- [PostgreSQL's fsync() surprise — LWN.net](https://lwn.net/Articles/752063/)
- [Can Applications Recover from fsync Failures? — USENIX ATC 2020](https://www.usenix.org/conference/atc20/presentation/rebello)
- [All File Systems Are Not Created Equal — OSDI 2014](https://www.usenix.org/conference/osdi14/technical-sessions/presentation/pillai)
- [Files are hard — Dan Luu](https://danluu.com/file-consistency/)
- [fsync(2) — Linux manual page](https://man7.org/linux/man-pages/man2/fsync.2.html)
