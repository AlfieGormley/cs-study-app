---
id: proc-syscalls
title: System calls and CPU modes
level: basic
minutes: 12
summary: User and kernel mode, the difference between traps, exceptions and interrupts, what actually happens on a Linux x86-64 syscall, what one costs, and how the vDSO avoids the cost entirely.
---

Ordinary programs normally access protected devices through the kernel; authorised user-space drivers are an exception. Yet `cat` reads files and `curl` sends packets. The trick is that programs don't do these things; they *ask the kernel to*. The asking mechanism is the **system call**.

The challenge is to let untrusted code ask for privileged work without letting it *become* privileged. The CPU solves this with modes and a small set of fixed entry points.

## User mode and kernel mode

At any moment a CPU core runs in one of (at least) two modes:

- **User mode**: privileged instructions fault. Only pages marked user-accessible can be touched.
- **Kernel mode**: privileged operations are available, but mappings, memory protections, hardware rules and any hypervisor still constrain accesses.

The only ways from user mode into kernel mode are events the hardware routes to **addresses the kernel chose in advance**. User code can't jump into the middle of the kernel. It can only knock on doors whose locations the kernel registered at boot.

This idea is called **limited direct execution**. Run the program directly on the CPU at full speed (direct execution), but limit what it can do, and make sure the kernel regains control when needed.

## Three ways into the kernel

| Event | Cause | Example |
|---|---|---|
| Trap (syscall) | Deliberate | `syscall`, `svc` |
| Exception (fault) | Error in current instruction | Page fault, divide by 0 |
| Interrupt | External hardware | Timer tick, NIC packet |

- **Traps** are *synchronous and intentional*: the program executes a special instruction to request a service.
- In this introductory classification, **faults** are synchronous conditions caused by the current instruction. Architectural terminology also includes deliberate traps among exceptions. Some are fixable (a page fault on a lazily allocated page; the kernel maps it and re-runs the instruction). Some are fatal (a segfault becomes `SIGSEGV`).
- **Interrupts** are *asynchronous*: a device signals the CPU regardless of what's running. The **timer interrupt** is vital, because it is how the kernel takes the CPU back from a program stuck in `while (1);`.

Terminology varies between textbooks and CPU vendors (Intel calls all of these "interrupts and exceptions"), but the distinction of deliberate versus error versus external is what matters.

## Anatomy of a Linux syscall on x86-64

Here is `write(1, "hi\n", 3)` from start to finish.

```
user: write(1, "hi\n", 3)    (glibc)
  rax = 1      syscall number (write)
  rdi = 1      arg 1: fd
  rsi = buf    arg 2: pointer
  rdx = 3      arg 3: count
  syscall      -> switch to ring 0
---------------------------------------
kernel: entry_SYSCALL_64
  preserve user stack pointer
  switch to kernel stack
  save user registers
  dispatch number -> __x64_sys_write
  validate fd, copy from user buffer
  rax = 3      bytes written
  sysret/iret   -> back to ring 3
---------------------------------------
user: glibc checks rax, returns 3
```

Key details:

1. **The syscall number** goes in `rax`. On x86-64, `read` is 0, `write` is 1 and `getpid` is 39. Numbers differ by architecture; ARM64 puts the number in `x8` and uses the `svc #0` instruction.
2. **Arguments** go in `rdi, rsi, rdx, r10, r8, r9`, up to six. (`r10` replaces `rcx`, which the `syscall` instruction overwrites with the return address.)
3. **The `syscall` instruction** switches to ring 0 and jumps to the address the kernel stored in a model-specific register (`MSR_LSTAR`) at boot. User code chooses *which service*, never *where to jump*.
4. **The kernel never trusts user pointers.** It copies data in and out with `copy_from_user` and `copy_to_user`, which check that the address really belongs to user space and handle faults safely.
5. **Errors** come back as a negative value in `rax`, such as `-EBADF`. glibc turns this into a return of `-1` and sets `errno`.

You can bypass the named syscall wrapper using libc's generic `syscall()` function. It still translates errors to `-1` and `errno`; this is not raw inline assembly:

```c
#include <sys/syscall.h>
#include <unistd.h>

int main(void) {
    syscall(SYS_write, 1, "hi\n", 3);
    long pid = syscall(SYS_getpid);
    return pid > 0 ? 0 : 1;
}
```

> [!tip] Watch syscalls happen
> `strace -c ls` runs `ls` and prints a table of every syscall it made, how many times, and the time spent. `strace -f -e trace=openat,read cmd` shows just those calls, following child processes. It's the single most useful tool for "why is this program slow / failing?"

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
> Copying a 100 MB file with 1-byte `read` and `write` calls makes 200 million syscalls. At an explicitly hypothetical 200 ns each, that's 40 seconds of pure overhead. With a 64 KiB buffer it's around 3,200 syscalls: under a millisecond. Same data, tens of thousands of times fewer calls.

How systems reduce the cost:

- **Batching**: buffer in user space (stdio), use `readv`/`writev` to move several buffers in one call, or `sendmmsg` for several UDP packets.
- **Avoid copies**: `sendfile` and `splice` move data between file descriptors inside the kernel.
- **Shared rings**: `io_uring` lets a program queue many I/O requests in memory shared with the kernel and submit them with one call, or even none if a kernel thread polls the ring.
- **Avoid the kernel entirely**: the vDSO, next.

## The vDSO: syscalls without the syscall

Some calls are made constantly but only *read* data the kernel maintains. The classic case is `clock_gettime`: logging libraries, profilers and databases call it millions of times a second.

Linux maps a small shared library called the **vDSO** (virtual dynamic shared object) into every process. It contains user-mode code for a few calls, plus a read-only page of data the kernel keeps updated (the current time base). On x86-64 it provides `clock_gettime`, `gettimeofday`, `time` and `getcpu`.

```
$ cat /proc/self/maps | grep vdso
7ffd8a5f2000-7ffd8a5f4000 r-xp ... [vdso]
```

When glibc's `clock_gettime(CLOCK_MONOTONIC, &ts)` runs, it calls the vDSO function, which reads the kernel's data page and the CPU's timestamp counter in user mode. No mode switch, so it avoids kernel-entry overhead when that clock and clocksource support the fast path.

> [!warning] When the vDSO falls back
> If the system clock source can't be read from user mode (for example some virtual machines using a clock source the vDSO doesn't support), the vDSO quietly falls back to a real syscall. A service that suddenly spends a lot of time in `clock_gettime` after moving to new VMs is a known symptom. Check `/sys/devices/system/clocksource/clocksource0/current_clocksource`.

## Pitfalls

- **Assuming `errno` is always valid.** It's only meaningful when the call reported failure; successful calls may leave junk in it.
- **Ignoring `EINTR`.** A blocking syscall interrupted by a signal handler may return `-1` with `errno == EINTR`. Robust code retries (or uses `SA_RESTART`).
- **Short reads and writes.** `read` can return fewer bytes than asked, for example near EOF or when fewer bytes are currently available on a pipe or socket. Loop until you have what you need.
- **Counting syscalls in hot loops.** A per-request `stat()` or `gettimeofday` (on a system without vDSO support) can dominate a fast server's profile.

## Key takeaways
- The CPU enforces user and kernel modes; user code enters the kernel only at entry points the kernel registered in advance.
- In the simplified terminology here, syscall traps are deliberate, faults are synchronous conditions such as page faults, and device interrupts are asynchronous. CPU manuals use more specific categories.
- On Linux x86-64 the syscall number goes in `rax`, up to six arguments in registers, and the `syscall` instruction switches to ring 0; errors come back negative and glibc converts them to `-1` plus `errno`.
- Syscall overhead depends on the implementation and workload; batching, buffering and `io_uring` can amortise entry overhead.
- The vDSO runs read-only calls like `clock_gettime` in user mode, avoiding the syscall altogether.

## Further reading
- [Mechanism: Limited Direct Execution — OSTEP](https://pages.cs.wisc.edu/~remzi/OSTEP/cpu-mechanisms.pdf)
- [Anatomy of a system call, part 1 — LWN](https://lwn.net/Articles/604287/)
- [Anatomy of a system call, part 2 — LWN](https://lwn.net/Articles/604515/)
- [syscall(2) — Linux manual page](https://man7.org/linux/man-pages/man2/syscall.2.html)
- [vdso(7) — Linux manual page](https://man7.org/linux/man-pages/man7/vdso.7.html)
- [Kernel page-table isolation — Wikipedia](https://en.wikipedia.org/wiki/Kernel_page-table_isolation)
