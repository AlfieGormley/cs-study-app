---
id: mem-page-faults
title: Page faults, copy-on-write, mmap and swap
level: intermediate
minutes: 14
summary: What happens when a page table entry says "not here", how Linux uses that one exception to build demand paging, copy-on-write fork, memory-mapped files and swap, and what each kind of fault costs.
---

The last two lessons treated a not-present page table entry as an error. In practice it is the opposite. The **page fault** is the most useful exception the hardware has, and Linux leans on it for almost everything clever about memory.

The idea is simple. The OS deliberately leaves PTEs not-present, or present but read-only, and waits. When the program touches the page, the CPU traps into the kernel, which decides what the page *should* be, fixes the PTE and lets the instruction run again. On successful resolution the instruction resumes; the program can still observe latency and fault counters, and some faults fail.

That one trick gives you:

- **Demand paging**: memory is allocated only when first touched.
- **Copy-on-write**: `fork` shares pages until one side writes.
- **Memory-mapped files**: file contents appear in memory and load lazily.
- **Swap**: pages can live on disk and come back on demand.

## What the hardware does

On x86-64, when the MMU cannot complete a translation (a not-present entry at any level) or the access breaks a permission bit, it raises exception 14, the **page fault (#PF)**. Before jumping to the kernel's handler it:

1. Puts the faulting virtual address in the **CR2** register.
2. Pushes an **error code** describing the access.
3. Saves the instruction pointer of the faulting instruction, not the next one, so the instruction can be **restarted**.

| Error bit | Set means |
|---|---|
| P (0) | Page present: a protection violation |
| W (1) | The access was a write |
| U (2) | It came from user mode |
| I (4) | It was an instruction fetch |

So the kernel learns exactly what happened: "user-mode write to 0x7f3a1000, page not present".

## What Linux does with it

The handler (`exc_page_fault`, then `handle_mm_fault`) asks one question first: **is this address inside a VMA?**

A **VMA** (virtual memory area) is the kernel's record of one mapped region: start, end, permissions and what backs it (a file, or nothing for anonymous memory). You can see them in `/proc/<pid>/maps`.

```
fault at addr, access type
        |
  addr in a VMA? -- no --> SIGSEGV
        | yes
  access allowed --- no --> SIGSEGV
  by VMA perms?
        | yes
  what is the page?
   - never touched -> allocate frame
   - in page cache -> map it
   - in swap       -> read it back
   - COW-shared    -> copy it
        |
  fix PTE, return, retry instruction
```

The crucial distinction is between the **page table** (what the hardware sees right now) and the **VMA** (what the process is allowed to have). Missing or incompatible VMAs are common SIGSEGV causes, but the VMA check is not the whole story. File faults can deliver SIGBUS; allocation can fail; architecture-specific protection and special mappings have additional rules.

## Minor and major faults

- A **minor fault** is accounted as resolved without the page-in I/O required by a major fault, for example demand-zero allocation or mapping resident backing. Its handler may still incur allocation, reclaim or contention work.
- A **major fault** is accounted as requiring page-in I/O, for example missing file or swap backing. Latency depends on caching, device, queueing and kernel behavior.

Fault type is useful evidence, but it does not alone determine duration.

> [!note] Content gap
> Fixed minor/major fault latencies are omitted because no reproducible benchmark configuration is provided. Times in the arithmetic exercise below are hypothetical inputs.

```
$ /usr/bin/time -v ./prog
  Major (requiring I/O) page
    faults: 3
  Minor (reclaiming a frame) page
    faults: 16450
```

`ps -o min_flt,maj_flt -p <pid>` and `perf stat -e page-faults,major-faults` report the same counters.

### The cost in numbers

Treat the page fault rate `p` like a TLB miss rate:

```
EAT = (1 - p) * mem + p * fault
```

> [!example] One fault per thousand accesses
> Memory access 100 ns, major fault 8 ms (8,000,000 ns), p = 0.001.
>
> EAT = 0.999 × 100 + 0.001 × 8,000,000 = 99.9 + 8,000 ≈ **8,100 ns**. Memory is now about 80 times slower.
>
> To keep the slowdown under 10% (EAT < 110 ns) you need p × 7,999,900 < 10, so p < 1.25 × 10^-6: fewer than **one major fault per 800,000 accesses**.

This is why a machine that is swapping heavily feels frozen rather than merely slow.

## Demand paging in action

A large glibc allocation may use anonymous mmap, depending on allocator state and tunables. An ordinary new anonymous mapping without prefaulting can initially reserve a virtual region with backing populated lazily. Under a base-page model, first writes allocate zero-filled backing; page size, THP and prior population affect the fault count.

This C program counts those faults:

```c
#include <stdio.h>
#include <sys/mman.h>
#include <sys/resource.h>
#include <unistd.h>

static long minflt(void) {
    struct rusage u;
    getrusage(RUSAGE_SELF, &u);
    return u.ru_minflt;
}

int main(void) {
    size_t len = 64UL << 20; /* 64 MiB */
    char *p = mmap(NULL, len,
        PROT_READ | PROT_WRITE,
        MAP_PRIVATE | MAP_ANONYMOUS,
        -1, 0);
    if (p == MAP_FAILED) {
        perror("mmap");
        return 1;
    }
    long step = sysconf(_SC_PAGESIZE);
    if (step <= 0) return 1;
    long before = minflt();
    for (size_t i = 0; i < len; i += step)
        ((volatile char *)p)[i] = 1;
    printf("%ld faults\n",
           minflt() - before);
    munmap(p, len);
}
```

64 MiB / 4 KiB = 16,384 pages, so with 4 KiB pages it prints a number close to **16,384**. With transparent huge pages set to `always`, each fault can map a whole 2 MiB page and the count drops to a few dozen.

Two refinements:

- On common Linux configurations, reads of untouched anonymous mappings can use read-only shared zero backing. Architecture, THP and mapping flags affect this; page tables and metadata still cost memory, and calloc may have allocator-specific behavior.
- `MAP_POPULATE` requests prefaulting but does not guarantee full population or future residency. Successful ordinary `mlock` keeps the range resident, whereas `mlock2(MLOCK_ONFAULT)` is lazy. Neither removes every later COW/protection fault, especially across fork.

## Copy-on-write and fork

`fork` must give the child a copy of the parent's whole address space. Copying gigabytes would make `fork` unusably slow, especially since most children immediately call `exec` and throw the copy away.

Instead Linux:

1. Creates the child's memory context and mappings, respecting exceptions such as DONTFORK/WIPEONFORK.
2. Shares eligible private backing under COW and write-protects the required mappings; some page-table work can be deferred.
3. Leaves shared mappings shared. Certain pinned/private pages may need special copying rather than ordinary COW.

When either process writes, the read-only PTE causes a protection fault. The kernel sees the VMA is writable, so this is a **COW fault**: it allocates a new frame, copies the 4 KiB, points the writer's PTE at the copy with write permission, and drops the reference on the original. If the writer turns out to be the only remaining user, it simply makes the page writable again with no copy.

```
after fork         after child writes
parent  child      parent      child
  \      /            |           |
 [frame 7 RO]    [frame 7]   [frame 9 RW]
                              (copy of 7)
```

Real systems depend on this:

- **Redis** `BGSAVE` forks, and the child writes a snapshot of the frozen dataset while the parent keeps serving. COW can add backing for modified pages, alongside child buffers, new parent allocations and page tables. A write-heavy workload can substantially increase total physical memory use, which is why Redis warns about memory headroom.
- **Pre-fork servers** (Gunicorn, PHP-FPM, Android's Zygote) load code once and fork workers that share it.

> [!warning] COW is not free
> `fork` still copies page tables, so forking a process with 100 GiB mapped takes noticeable time even before any page is copied. Later writes may copy backing or reuse it when exclusive. Suitable posix_spawn implementations can avoid copying the parent's address space for exec; vfork has strict child-side restrictions and is not a drop-in fork replacement.

## Memory-mapped files

`mmap` on a file descriptor makes the file's bytes appear in the address space. For ordinary mappings without prefaulting, population is lazy; MAP_POPULATE, existing page-cache state and other flags can change when work occurs.

```c
int fd = open("data.bin", O_RDONLY);
char *d = mmap(NULL, size, PROT_READ,
               MAP_PRIVATE, fd, 0);
/* first touch of d[i] faults the
   page in from the page cache */
```

The page frames are the kernel's **page cache** pages for that file. Resident, up-to-date cached backing can avoid page-in I/O. Readahead, eviction and fault-around mean neither process history nor one page implies a fixed count/type of faults.

| Flag | Writes go to |
|---|---|
| `MAP_SHARED` | The page cache, later the file; other mappers see them |
| `MAP_PRIVATE` | A private COW copy; the file is unchanged |
| `MAP_ANONYMOUS` | No file; zero-filled memory |

The program loader maps executables and shared libraries `MAP_PRIVATE`. That is how a hundred processes share one copy of libc's code in RAM.

Pitfalls of file mapping:

- **SIGBUS, not EIO.** If the file is truncated, or a disk read fails, touching the page delivers `SIGBUS`. There is no return value to check.
- **Durability needs explicit synchronization.** Check successful msync(MS_SYNC) or the applicable fsync protocol for file data; file creation/rename may also need directory synchronization. Hardware and filesystem guarantees still apply.
- **Hidden stalls.** Any pointer dereference can block for a disk read. LMDB embraces mmap; many database designers avoid it for exactly this reason.

## Swap

When RAM runs short, the kernel must free frames (lesson 5 covers how it chooses). What it does depends on the page:

| Page kind | To reclaim it |
|---|---|
| Clean file page | Just drop it; reread later |
| Dirty file page | Write it back to the file |
| Anonymous page | Write it to **swap** |

Preserving live anonymous data during reclaim normally requires swap backing. This is different from freeing or explicitly discarding unneeded anonymous pages, which can happen without swap. With swap, it writes the page out and stores a **swap entry** (which swap device, which slot) in the now not-present PTE. The OS is allowed to use those bits because the hardware ignores a PTE whose present bit is clear. A later access resolves the swap entry. It can use resident swap-cache or compressed backing; a storage read is not inevitable.

`vm.swappiness` (default 60, range 0 to 200) tells the kernel how willing it is to swap anonymous pages compared with dropping page cache.

Modern variants compress instead of writing to disk:

- **zswap**: a compressed RAM cache in front of a swap device.
- **zram**: a compressed RAM block device used as swap. Several operating-system distributions use it; exact defaults depend on version and configuration. Optional zram writeback can use a backing device.

Compression trades CPU and metadata for saved backing capacity; cost and compression ratio depend on data and configuration.

## Other uses of the fault path

- **Stack growth**: eligible grow-down stack mappings may expand within limits; an arbitrary below-stack fault does not guarantee expansion.
- **Guard pages**: deliberately unmapped pages below thread stacks turn overflows into immediate `SIGSEGV`.
- **userfaultfd**: lets a user-space program handle faults on a region. QEMU uses it for post-copy live migration, fetching guest pages over the network on demand.
- **Garbage collectors and databases** use `mprotect` to trap writes and track dirty pages.

## Key takeaways
- A page fault is a restartable exception: CR2 holds the address, the error code says why, and the kernel fixes the PTE and retries.
- Linux consults VMAs and backing state. Invalid accesses often deliver SIGSEGV; file failures may deliver SIGBUS, and other resource/protection failures are possible.
- Minor/major counters distinguish page-in work, not fixed latency. An expensive fault can dominate a hypothetical average even at a low rate.
- Demand paging allocates frames on first touch; reads of untouched anonymous memory map the shared zero page.
- fork marks private pages read-only and copies them only on write; page tables are still copied.
- mmap maps page-cache pages lazily; MAP_SHARED writes reach the file, MAP_PRIVATE writes are COW copies; I/O errors arrive as SIGBUS.
- Preserving anonymous contents during reclaim normally needs swap backing; discard/free are different. Swap entries identify backing that may be cached or compressed.

## Further reading
- [OSTEP: Beyond Physical Memory: Mechanisms (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/vm-beyondphys.pdf)
- [OSTEP: Complete Virtual Memory Systems (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/vm-complete.pdf)
- [Concepts overview — Linux kernel memory management docs](https://www.kernel.org/doc/html/latest/admin-guide/mm/concepts.html)
- [mmap(2) — Linux manual page](https://man7.org/linux/man-pages/man2/mmap.2.html)
- [fork(2) — Linux manual page](https://man7.org/linux/man-pages/man2/fork.2.html)
- [zswap — Linux kernel docs](https://www.kernel.org/doc/html/latest/admin-guide/mm/zswap.html)
- [Page fault — Wikipedia](https://en.wikipedia.org/wiki/Page_fault)
