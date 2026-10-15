---
id: proc-fork-copy-on-write
sourceLesson: proc-fork-exec-wait
title: "Copy-on-write and snapshot costs"
level: intermediate
minutes: 2
summary: "Private pages can remain physically shared until a write requires separation."
---

Private pages can remain physically shared until a write requires separation. This lesson focuses on copy-on-write and snapshot costs.

## Copy-on-write: why fork is cheap

Copying gigabytes of memory on every `fork`, only to throw it away at `exec`, would be absurd. Modern kernels use **copy-on-write (COW)**:

1. `fork` copies the parent's *page tables*, not its pages. Parent and child now map the same physical frames.
2. Private writable mappings are protected for COW; mappings intentionally shared with `MAP_SHARED` retain shared semantics.
3. When either process writes to a page, the CPU faults. For a shared private page with a 4 KiB base-page mapping, the kernel normally copies that page, gives the writer its own private copy, marks it writable and restarts the instruction.

```
after fork:
 parent PT --\
              >-- frame 7 (read-only)
 child PT ---/

child writes:
 parent PT ----- frame 7  (exclusive)
 child PT  ----- frame 9  (copy)
```

So `fork` costs roughly the time to copy page tables, which is proportional to the parent's *mapped* memory, not to its total contents being copied. Actual cost depends on populated page tables, page sizes, allocator state, hardware and kernel. The calling thread cannot continue past fork until it returns; other threads are not universally frozen for that entire period.

> [!example] Redis snapshots
> Redis saves snapshots by forking. The child writes the dataset to disk from its frozen COW view while the parent keeps serving writes. Every page the parent modifies during the save gets copied, so a write-heavy Redis can retain nearly twice the private dataset's physical pages during `BGSAVE`, plus page-table, buffer and other overhead. Redis latency documentation warns that transparent huge pages can worsen COW latency and memory usage. Copying versus splitting and page sizes depend on the kernel; not every small write necessarily copies 2 MiB.

## Key takeaways
- Private pages can remain physically shared until a write requires separation.
- Copy-on-write reduces initial copying but can increase memory use during concurrent writes.

## Further reading
- [Interlude: Process API — OSTEP](https://pages.cs.wisc.edu/~remzi/OSTEP/cpu-api.pdf)
- [fork(2) — Linux manual page](https://man7.org/linux/man-pages/man2/fork.2.html)
- [execve(2) — Linux manual page](https://man7.org/linux/man-pages/man2/execve.2.html)
- [wait(2) — Linux manual page](https://man7.org/linux/man-pages/man2/wait.2.html)
- [posix_spawn(3) — Linux manual page](https://man7.org/linux/man-pages/man3/posix_spawn.3.html)
- [Zombie process — Wikipedia](https://en.wikipedia.org/wiki/Zombie_process)
- [Copy-on-write — Wikipedia](https://en.wikipedia.org/wiki/Copy-on-write)
