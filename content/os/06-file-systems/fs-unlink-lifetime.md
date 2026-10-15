---
id: fs-unlink-lifetime
title: Unlinking names and retaining open files
level: basic
minutes: 2
summary: Unlink removes a name, while open descriptions or mappings can keep file storage alive.
sourceLesson: fs-file-abstraction
---

This unit focuses on unlinking names and retaining open files. The preceding units provide the file and storage concepts used here.

### Closing, and files with no name

`close` drops the descriptor. The open file description can be freed when its final reference is released. Mappings, queued descriptor passing or in-flight operations can retain references after the last numeric descriptor closes.

`unlink(path)` removes a *name*. Ordinary unlinked file storage becomes reclaimable once no links and no remaining open/mapping references retain it. Snapshots or filesystem-specific features can retain underlying blocks further. So you can delete a 50 GB log file that a process is still writing, and `df` shows no space freed while its open reference remains; mappings or other references may retain it longer. `lsof +L1` lists such deleted-but-open files. The same trick is used deliberately for temporary files: open, unlink immediately, and the file vanishes automatically when the process dies.

Descriptors are a limited resource. `ulimit -n` shows the per-process limit (the actual soft/hard limits depend on shell, service and system settings). A server that leaks a descriptor per request eventually fails with `EMFILE: Too many open files`.

## Key takeaways
- Unlink removes a name, while open descriptions or mappings can keep file storage alive.
- Rotation by rename does not redirect an already-open descriptor to a newly created file.

## Further reading
- [OSTEP: Interlude: Files and Directories (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/file-intro.pdf)
- [Overview of the Linux Virtual File System — kernel.org](https://www.kernel.org/doc/html/latest/filesystems/vfs.html)
- [open(2) — Linux manual page](https://man7.org/linux/man-pages/man2/open.2.html)
- [dup(2) — Linux manual page](https://man7.org/linux/man-pages/man2/dup.2.html)
- [File descriptor — Wikipedia](https://en.wikipedia.org/wiki/File_descriptor)
- [Everything is a file — Wikipedia](https://en.wikipedia.org/wiki/Everything_is_a_file)
