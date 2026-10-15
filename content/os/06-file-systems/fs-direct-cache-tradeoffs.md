---
id: fs-direct-cache-tradeoffs
title: Direct I/O and double buffering
level: intermediate
minutes: 2
summary: Direct I/O can bypass ordinary page caching but has alignment and support constraints.
sourceLesson: fs-page-cache
---

This unit focuses on direct I/O and double buffering. The preceding units provide the file and storage concepts used here.

## Bypassing the cache: O_DIRECT

Opening a file with `O_DIRECT` asks the kernel to move data **directly between your buffer and the device**, skipping the page cache.

Who wants that? Databases with their own cache. MySQL's InnoDB has a buffer pool, Oracle and ScyllaDB manage their own memory, and caching the same page again in the kernel would waste RAM (**double buffering**) and add a copy. InnoDB on Linux is commonly configured with `innodb_flush_method=O_DIRECT`.

PostgreSQL normally uses buffered I/O alongside its own `shared_buffers`. Its documentation suggests about a quarter of RAM as a starting point on a dedicated server, then measurement. The developer-only `debug_io_direct` setting can request cache bypass on supported systems; it is not a general production recommendation or evidence that every PostgreSQL I/O path is buffered.

The rules and caveats of `O_DIRECT`:

- Buffer address, file offset and length can have alignment requirements that are not universally identical to the device's logical block size. Requirements vary by filesystem/kernel/file and can be queried via STATX_DIOALIGN where supported. Misalignment can fail with EINVAL or fall back to buffered I/O.
- Direct I/O avoids ordinary page-cache hits and read-ahead. Application caching/batching, block-layer merging, device behavior and workload determine performance; it is not universally slower.
- It is **not** a durability guarantee. The data may still sit in the device's volatile cache, and file metadata (size, block allocation) isn't flushed. You still need `fsync` or `O_DSYNC`.

For these version-dependent settings, see the [PostgreSQL developer I/O documentation](https://www.postgresql.org/docs/current/runtime-config-developer.html) and [memory configuration guidance](https://www.postgresql.org/docs/current/runtime-config-resource.html).

## Key takeaways
- Direct I/O can bypass ordinary page caching but has alignment and support constraints.
- Cache bypass does not provide durability; database and kernel cache sizing must be considered together.

## Further reading
- [Page cache — Wikipedia](https://en.wikipedia.org/wiki/Page_cache)
- [Documentation for /proc/sys/vm (dirty_* settings) — kernel.org](https://docs.kernel.org/admin-guide/sysctl/vm.html)
- [open(2): O_DIRECT notes — Linux manual page](https://man7.org/linux/man-pages/man2/open.2.html)
- [posix_fadvise(2) — Linux manual page](https://man7.org/linux/man-pages/man2/posix_fadvise.2.html)
- [mmap(2) — Linux manual page](https://man7.org/linux/man-pages/man2/mmap.2.html)
- [sendfile(2) — Linux manual page](https://man7.org/linux/man-pages/man2/sendfile.2.html)
- [Are You Sure You Want to Use MMAP in Your DBMS? — CIDR 2022](https://db.cs.cmu.edu/mmap-cidr2022/)
- [Zero-copy — Wikipedia](https://en.wikipedia.org/wiki/Zero-copy)
