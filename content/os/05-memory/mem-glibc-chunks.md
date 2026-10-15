---
id: mem-glibc-chunks
sourceLesson: mem-allocators
title: Checking glibc chunk size and usable bytes
level: advanced
minutes: 3
summary: The stated glibc 2.39 x86-64 arena model rounds requests with header and minimum-size rules.
---

## glibc malloc (ptmalloc2)

The following concrete model is **glibc 2.39 on ordinary x86-64 Linux**, with default alignment and no replacement/debug allocator. Its lineage includes dlmalloc and ptmalloc2, but glibc has substantially changed it. Other versions and tunables differ; inspect the deployed version rather than treating these defaults as permanent.

### Chunks

An ordinary arena allocation is an **arena chunk** with an 8-byte size/status word immediately before the returned pointer. The layout also has a preceding previous-size field; for an in-use arena chunk, usable space can borrow the next chunk's previous-size word. Separately mmapped chunks have different overhead. On x86-64 chunks are multiples of 16 bytes with a minimum of 32. A request needs its own bytes plus the 8-byte header, rounded up to a multiple of 16:

```formula
C = max(32, 16⌈(n + 8) / 16⌉)
U = C − 8
where
C: the chunk size in bytes
n: the number of bytes requested from malloc
⌈ ⌉: ceiling: round up to a whole number, so 16⌈x / 16⌉ is x rounded up to a multiple of 16
max: the larger of its two arguments; 32 is the minimum chunk size
U: the usable bytes in the chunk, which is what malloc_usable_size reports
In words: add the 8-byte header, round up to the next multiple of 16 (at least 32), and everything except the header is usable.
```

For example, malloc(100) needs 108 bytes, which rounds up to a 112-byte chunk with 104 usable. This model holds for ordinary arena chunks in the stated glibc release; separately mmapped chunks follow different rules.

```
malloc(1)   -> 32-byte chunk, 24 usable
malloc(24)  -> 32-byte chunk, 24 usable
malloc(25)  -> 48-byte chunk, 40 usable
malloc(100) -> 112-byte chunk, 104 usable
```

You can check it:

```c
#include <malloc.h>
#include <stdio.h>
#include <stdlib.h>

int main(void) {
    size_t n[] = {1, 24, 25, 100};
    for (int i = 0; i < 4; i++) {
        void *p = malloc(n[i]);
        if (!p) return 1;
        /* Usable capacity is diagnostic;
           keep accesses within n[i]. */
        printf("%zu -> %zu\n", n[i],
               malloc_usable_size(p));
        free(p);
    }
}
/* 1 -> 24, 24 -> 24,
   25 -> 40, 100 -> 104 */
```

`malloc_usable_size` is a diagnostic, rather than permission to write beyond the requested allocation.

The header is also why a heap buffer overflow is so dangerous: an overflow can damage adjacent payload or allocator metadata, potentially enabling exploitation despite integrity checks. Not every out-of-bounds byte reaches a size field.

## Key takeaways
- The stated glibc 2.39 x86-64 arena model rounds requests with header and minimum-size rules.
- Usable-size reporting is allocator-specific and does not justify writing beyond a requested allocation.

## Further reading
- [MallocInternals — glibc wiki](https://sourceware.org/glibc/wiki/MallocInternals)
- [mallopt(3) — Linux manual page](https://man7.org/linux/man-pages/man3/mallopt.3.html)
- [OSTEP: Free-Space Management (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/vm-freespace.pdf)
- [jemalloc](https://jemalloc.net/)
- [TCMalloc design](https://google.github.io/tcmalloc/design.html)
- [mimalloc on GitHub](https://github.com/microsoft/mimalloc)
- [Buddy memory allocation — Wikipedia](https://en.wikipedia.org/wiki/Buddy_memory_allocation)
- [Slab allocation — Wikipedia](https://en.wikipedia.org/wiki/Slab_allocation)
- [Physical Page Allocation, from Understanding the Linux Virtual Memory Manager](https://www.kernel.org/doc/gorman/html/understand/understand009.html)
