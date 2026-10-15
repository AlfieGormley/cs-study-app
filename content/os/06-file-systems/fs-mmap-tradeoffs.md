---
id: fs-mmap-tradeoffs
title: Mapped files and fault handling
level: intermediate
minutes: 3
summary: Mapped access can avoid a read-buffer copy while exposing fault and truncation risks.
sourceLesson: fs-page-cache
---

This unit focuses on mapped files and fault handling. The preceding units provide the file and storage concepts used here.

## mmap vs read

`mmap` maps a file into your address space. Instead of copying from the page cache into your buffer, ordinary file-backed mappings can initially reference the file's cached pages; private writes can create COW copies. Language-level operations such as Python slicing may still copy data.

```python
import mmap

with open("big.bin", "rb") as f:
    # Map this existing nonempty file.
    m = mmap.mmap(f.fileno(), 0,
                  access=mmap.ACCESS_READ)
    header = m[:16]   # copies 16 bytes
    # Byte offset, or -1 when not found.
    n = m.find(b"needle")
    # Release this mapping explicitly.
    m.close()
```

An access without a present usable translation causes a **page fault**. Prefaulting, fault-around and population options mean not every first page touch necessarily faults separately. The kernel finds or loads the page and installs a mapping; after that, access is a plain memory load.

| | `read()` | `mmap` |
|---|---|---|
| Copy into user buffer | yes | no |
| Access path | syscall per read call, then loads from buffer | ordinary loads once mapped |
| Cost per new page | in syscall | page fault |
| I/O errors | return code | `SIGBUS` |
| Eviction | kernel policy, advisory hints | kernel policy, advisory hints |

`mmap` shines for random access to files that fit comfortably in RAM, for sharing read-only data between processes (shared libraries are mapped this way), and for convenience.

It has real costs at scale:

- **Page faults and TLB shootdowns.** Unmapping or evicting pages across many cores may require translation invalidation and inter-CPU coordination; exact mechanisms and costs vary.
- **Errors arrive as signals.** A disk error or a file truncated by someone else turns a memory access into `SIGBUS`, which is hard to handle.
- **No control over write-back.** A modified page can be written to disk at any moment, so a database must enforce WAL ordering before dirtying shared mapped data or use a design that preserves ordering through another mechanism. This is a design constraint, not proof that every mmap database is incorrect.

The CIDR 2022 paper "Are You Sure You Want to Use MMAP in Your DBMS?" documents these problems in databases that started with `mmap` and later moved away (MongoDB's original storage engine was one example).

## Key takeaways
- Mapped access can avoid a read-buffer copy while exposing fault and truncation risks.
- Shared mapped database writes need explicit crash-recovery ordering.

## Further reading
- [Page cache — Wikipedia](https://en.wikipedia.org/wiki/Page_cache)
- [Documentation for /proc/sys/vm (dirty_* settings) — kernel.org](https://docs.kernel.org/admin-guide/sysctl/vm.html)
- [open(2): O_DIRECT notes — Linux manual page](https://man7.org/linux/man-pages/man2/open.2.html)
- [posix_fadvise(2) — Linux manual page](https://man7.org/linux/man-pages/man2/posix_fadvise.2.html)
- [mmap(2) — Linux manual page](https://man7.org/linux/man-pages/man2/mmap.2.html)
- [sendfile(2) — Linux manual page](https://man7.org/linux/man-pages/man2/sendfile.2.html)
- [Are You Sure You Want to Use MMAP in Your DBMS? — CIDR 2022](https://db.cs.cmu.edu/mmap-cidr2022/)
- [Zero-copy — Wikipedia](https://en.wikipedia.org/wiki/Zero-copy)
