---
id: mem-file-mapping
sourceLesson: mem-page-faults
title: File mappings, private writes and SIGBUS
level: intermediate
minutes: 2
summary: Ordinary file mappings use page-cache backing and can fault lazily.
---

## Memory-mapped files

`mmap` on a file descriptor makes the file's bytes appear in the address space. For ordinary mappings without prefaulting, population is lazy; MAP_POPULATE, existing page-cache state and other flags can change when work occurs.

```c
int fd = open("data.bin", O_RDONLY);
char *d = mmap(NULL, size, PROT_READ,
               MAP_PRIVATE, fd, 0);
/* Partial fragment: check open/mmap
   errors and supply file size first.
   An uncached translation can fault;
   resident page-cache data avoids I/O. */
```

The page frames are the kernel's **page cache** pages for that file. Resident, up-to-date cached backing can avoid page-in I/O. Readahead, eviction and fault-around mean neither process history nor one page implies a fixed count/type of faults.

| Flag | Writes go to |
|---|---|
| `MAP_SHARED` | The page cache, later the file; other mappers see them |
| `MAP_PRIVATE` | A private COW copy; the file is unchanged |
| `MAP_ANONYMOUS` | No file; zero-filled memory |

The program loader maps executables and shared libraries `MAP_PRIVATE`. That is how a hundred processes share one copy of libc's code in RAM.

Pitfalls of file mapping:

- **Mapped-access failures can deliver SIGBUS.** Accessing a whole page beyond a truncated file’s end, or an unresolvable backing-object error, can deliver `SIGBUS`. A load has no ordinary read-style error return. A partial final page and particular failure paths have additional rules.
- **Durability needs explicit synchronization.** Check successful msync(MS_SYNC) or the applicable fsync protocol for file data; file creation/rename may also need directory synchronization. Hardware and filesystem guarantees still apply.
- **Hidden stalls.** Any pointer dereference can block for a disk read. LMDB embraces mmap; many database designers avoid it for exactly this reason.

## Key takeaways
- Ordinary file mappings use page-cache backing and can fault lazily.
- Private writes leave the file unchanged; shared writes need an appropriate durability protocol.
- Truncation can turn a later mapped access into SIGBUS.

## Further reading
- [OSTEP: Beyond Physical Memory: Mechanisms (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/vm-beyondphys.pdf)
- [OSTEP: Complete Virtual Memory Systems (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/vm-complete.pdf)
- [Concepts overview — Linux kernel memory management docs](https://www.kernel.org/doc/html/latest/admin-guide/mm/concepts.html)
- [mmap(2) — Linux manual page](https://man7.org/linux/man-pages/man2/mmap.2.html)
- [fork(2) — Linux manual page](https://man7.org/linux/man-pages/man2/fork.2.html)
- [zswap — Linux kernel docs](https://www.kernel.org/doc/html/latest/admin-guide/mm/zswap.html)
- [Page fault — Wikipedia](https://en.wikipedia.org/wiki/Page_fault)
