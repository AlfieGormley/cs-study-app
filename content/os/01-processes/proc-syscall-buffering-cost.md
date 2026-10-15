---
id: proc-syscall-buffering-cost
sourceLesson: proc-syscalls
title: "Buffering and syscall overhead"
level: basic
minutes: 5
summary: "Batching reduces the number of kernel entries for a fixed payload."
---

Batching reduces the number of kernel entries for a fixed payload. This lesson focuses on buffering and syscall overhead.

## Library calls versus system calls

Not every libc function is a syscall:

| Function | Syscall? |
|---|---|
| `strlen`, `memcpy` | Never |
| `printf` | Sometimes (`write` when buffer flushes) |
| `malloc` | Sometimes (`brk` or `mmap` for more memory) |
| `read`, `open` | Always (thin wrapper) |

`printf` writes into a user-space buffer. When stdout is a terminal it's **line-buffered** and flushes on each newline. When stdout is a file or pipe it's **fully buffered** (typically 4 KiB or more), so a thousand `printf` calls may become a handful of `write` syscalls. This buffering exists precisely because syscalls are expensive.

## What a syscall costs

System calls add work beyond an ordinary function call; the size of that overhead depends on the operation and machine:

- The mode switch itself and saving and restoring registers.
- Security work on entry and exit: on CPUs affected by Meltdown, **kernel page-table isolation (KPTI)** switches page tables on every entry and exit. Spectre mitigations add further barriers.
- **Indirect cost**: the kernel's code and data displace your program's lines in the L1 cache and entries in the TLB and branch predictors. Your code runs slower for a while after returning.

> [!note] Content gap: syscall latency
> No reproducible benchmark is supplied for the original nanosecond figures. Universal function-call, syscall and vDSO timing numbers are omitted; measure the chosen CPU, kernel, mitigations and workload.

> [!example] Cost adds up
> Copying a 100 MB file with 1-byte `read` and `write` calls makes 200 million syscalls. With a 64 KiB buffer it makes about 3,050. Same data, tens of thousands of times fewer calls. The working is below.

To estimate the pure syscall overhead of a copy loop, count the calls and multiply by a per-call cost. Each chunk of the file needs one `read` and one `write`, and the last chunk may be partly empty, so the chunk count is rounded up:

```formula
N = 2⌈S / b⌉
T = N t_call
N_1 = 2 × 100,000,000 = 200,000,000
T_1 = 200,000,000 × 200 ns = 40 s
N_64 = 2 × ⌈100,000,000 B / 65,536 B⌉
N_64 = 2 × 1,526 = 3,052
T_64 = 3,052 × 200 ns ≈ 0.61 ms
where
N: the number of syscalls the copy makes: one read plus one write per chunk
S: the file size, in bytes (B); here 100 MB = 100,000,000 B
b: the buffer size, the number of bytes each read or write call moves, in bytes (B)
⌈ ⌉: the ceiling: round up to the next whole number, because a part-filled last chunk still costs a call (⌈1,525.9⌉ = 1,526)
T: the total time spent on per-call overhead alone, not on moving the data
t_call: the overhead of one syscall, in nanoseconds (ns); 200 ns is an explicitly hypothetical figure, not a measurement
N_1, T_1: the call count and overhead with a 1-byte buffer (b = 1 B)
N_64, T_64: the call count and overhead with a 64 KiB buffer (b = 65,536 B)
B: byte, 8 bits
MB: megabyte, 1,000,000 bytes
KiB: kibibyte, 1,024 bytes, so 64 KiB = 65,536 B
ns: nanosecond, one billionth of a second
ms: millisecond, one thousandth of a second (1 ms = 1,000,000 ns)
s: second
≈: approximately equal to (the result is rounded)
In words: overhead is paid per call, not per byte, so making each call move 65,536 times more data cuts the call count, and the overhead, by roughly that factor: from 40 seconds to well under a millisecond.
```

The model ignores the final `read` that returns 0 at end of file, short reads, and the time spent actually copying bytes, which does not shrink with a bigger buffer. Real per-call costs vary with CPU, kernel and mitigations, so measure them before trusting the exact figures.

How systems reduce the cost:

- **Batching**: buffer in user space (stdio), use `readv`/`writev` to move several buffers in one call, or `sendmmsg` for several UDP packets.
- **Avoid copies**: `sendfile` and `splice` move data between file descriptors inside the kernel.
- **Shared rings**: `io_uring` lets a program queue many I/O requests in memory shared with the kernel and submit them with one call, or even none if a kernel thread polls the ring.
- **Avoid the kernel entirely**: the vDSO, next.

## Key takeaways
- Batching reduces the number of kernel entries for a fixed payload.
- A per-call overhead model needs measured inputs and does not predict total copy time.

## Further reading
- [Mechanism: Limited Direct Execution — OSTEP](https://pages.cs.wisc.edu/~remzi/OSTEP/cpu-mechanisms.pdf)
- [Anatomy of a system call, part 1 — LWN](https://lwn.net/Articles/604287/)
- [Anatomy of a system call, part 2 — LWN](https://lwn.net/Articles/604515/)
- [syscall(2) — Linux manual page](https://man7.org/linux/man-pages/man2/syscall.2.html)
- [vdso(7) — Linux manual page](https://man7.org/linux/man-pages/man7/vdso.7.html)
- [Kernel page-table isolation — Wikipedia](https://en.wikipedia.org/wiki/Kernel_page-table_isolation)
