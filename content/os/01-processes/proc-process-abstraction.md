---
id: proc-process-abstraction
title: The process abstraction
level: basic
minutes: 12
summary: What a process is, how its virtual address space is laid out (text, data, BSS, heap, mmap, stack), what the kernel keeps in the process control block, and the states a process moves through.
---

A **program** is a file: instructions and data sitting on disk. A **process** is a program *running*: the instructions plus everything needed to execute them right now. Run `python3` in three terminals and you have one program and three processes.

The process is the OS's central abstraction. It gives each running program the illusion of its own CPU and its own private memory, even though dozens of processes share a few cores and one pool of RAM.

## What makes up a process

A process is roughly:

- **An address space**: the memory it can see, from its code to its stack.
- **Execution state**: the CPU registers, including the program counter (which instruction is next) and stack pointer.
- **OS resources**: open file descriptors, current directory, signal handlers, user and group IDs, resource limits.
- **Identity**: a process ID (PID), a parent PID, and accounting information like CPU time used.

One process can contain several **threads**. Threads share the address space and resources but each has its own registers and stack. Threads are the next module's subject; for now picture one thread per process.

## The address space

Each process sees a **virtual address space**: a range of addresses that the MMU translates to physical RAM using per-process page tables. Two processes can both use address `0x400000` and see completely different data.

The following is a schematic of a conventional Linux x86-64 layout (low addresses at the bottom), not an exact map. With four-level paging the low user range spans 128 TiB; a large non-canonical gap separates it from high kernel addresses. Five-level paging supports a larger range.

Where does 128 TiB come from? Four-level paging translates 48-bit virtual addresses, and Linux gives the lower half of that range to user space and the upper half to the kernel:

```formula
S_user = 2^{n − 1} B
S_user = 2^{48 − 1} B = 2^47 B
S_user = 140,737,488,355,328 B
S_user = 128 TiB
where
S_user: the size of the user part of each process's virtual address space, in bytes (B)
n: the number of virtual-address bits the page tables translate: 48 with four-level paging, 57 with five-level paging
B: byte, 8 bits
TiB: tebibyte, 2 to the power 40 bytes (1,099,511,627,776 B), so 2^47 B is 2^7 = 128 TiB
In words: 48 address bits can name 2^48 bytes; half of those, 128 TiB, belong to user space.
```

A process only uses a tiny part of that range; the rest is simply unmapped. With five-level paging (57 bits) the same halving gives 64 PiB of user space, though Linux only hands out addresses above 128 TiB to programs that ask for them.

```
 0xffff...  +--------------------+
            | kernel (no access) |
 ~128 TiB   +--------------------+
            | stack  (grows down)|
            |        v           |
            |                    |
            | mmap region:       |
            | shared libs, big   |
            | mallocs, mapped    |
            | files              |
            |        ^           |
            | heap   (grows up)  |
            +--------------------+
            | BSS  (zeroed data) |
            | data (init'd data) |
            | rodata (constants) |
            | text (code)        |
 0x0        +--------------------+
            (page 0 unmapped)
```

| Region | Holds | Permissions |
|---|---|---|
| text | machine code | read + execute |
| rodata | string literals, `const` globals | read |
| data | initialised globals and statics | read + write |
| BSS | zero or uninitialised globals | read + write |
| heap | `malloc` memory | read + write |
| mmap | shared libs, large allocations | varies |
| stack | locals, return addresses | read + write |

Some details that matter:

- **Text is read-only and shared.** Processes using the same executable can share file-backed code pages. An ordinary write to a read-only mapping faults; mappings and permissions can differ.
- **BSS costs nothing on disk.** The executable records only its size; the kernel maps zero-filled pages at load time. A 100 MB `static char buf[100000000];` doesn't make your binary 100 MB.
- **The heap** grows with the `brk` syscall. glibc may use separate `mmap` allocations for requests not served by its free lists above a threshold initially 128 KiB and normally adjusted dynamically. Arenas and tunables also affect placement.
- **The stack** grows downwards as functions are called. Its limit is environment-dependent; an illustrative 8 MiB limit appears as 8192 KiB in `ulimit -s`. Deep recursion past the limit hits an unmapped guard region and the process gets `SIGSEGV`.
- **Page zero is normally unmapped** on ordinary Linux deployments. Null dereference is undefined in C, so the language itself does not guarantee a particular signal.
- **ASLR** (address space layout randomisation) shifts the stack, heap, libraries and (for position-independent executables) the text to random offsets on every run, making exploits harder.
- **Kernel mappings** are inaccessible to ordinary user-mode code. With KPTI, the user page tables contain only minimal kernel-entry mappings; the full kernel map is selected on entry.

### Seeing it for yourself

```c
#include <stdio.h>
#include <stdlib.h>

int g_init = 42;      /* data   */
int g_zero;           /* BSS    */
const char *s = "hi"; /* pointer: data */

int main(void) {
    int local = 1;               /* stack */
    int *h = malloc(16);         /* heap  */
    printf("text  %p\n", (void *)main);
    printf("data  %p\n", (void *)&g_init);
    printf("bss   %p\n", (void *)&g_zero);
    printf("heap  %p\n", (void *)h);
    printf("stack %p\n", (void *)&local);
    free(h);
    return 0;
}
```

This illustrates one conventional executable layout; exact ordering and locations depend on the ABI, linker, allocator and ASLR settings. ASLR does not promise a different value on every run. `cat /proc/<pid>/maps` lists every region of a live process with its permissions and backing file.

> [!note] `s` versus `*s`
> In the example, the pointer variable `s` is an initialised global, so it lives in **data**. The string `"hi"` it points to lives in **rodata**. Writing through this `const char *` is rejected without a cast; modifying the literal through a writable-typed pointer is undefined behaviour and commonly faults. Reassigning `s = "yo"` is valid.

## The process control block

The kernel needs a record of every process. Textbooks call it the **process control block (PCB)**. In Linux it's `struct task_struct`, a structure with hundreds of fields. The important ones:

| Field | Why |
|---|---|
| PID, parent, children | identity and family tree |
| State | running, sleeping, zombie... |
| Saved registers | to resume it later |
| Memory map (`mm`) | page tables, regions |
| Open files table | fd to file mapping |
| Credentials | UID, GID, capabilities |
| Scheduling info | priority, CPU time used |
| Signal state | handlers, pending, blocked |

When a process isn't running, its PCB holds everything needed to continue it later, exactly where it left off. This is what makes a **context switch** possible (lesson 5).

In Linux, every thread has its own `task_struct`. Threads of one process share the same `mm` (address space) and file table by pointing to the same structures. "Process" and "thread" are really just different sharing settings, a theme we'll return to.

Much of `task_struct` is visible in `/proc/<pid>/status`:

```
$ grep -E 'State|PPid|Threads|VmRSS' \
    /proc/self/status
State:  R (running)
PPid:   2817
Threads:        1
VmRSS:      1024 kB
```

## Process states

A process moves between a few states. The classic textbook model:

```
        admit        dispatch
 new -------> ready ---------> running
               ^ ^              |  |
               | +--preempted---+  |
    event done |                   | wait
               |                   | (I/O,
               +---- blocked <-----+  lock)

 running ---exit---> terminated
```

- **Ready**: could run, waiting for a CPU.
- **Running**: on a CPU right now. At most one executing thread per logical CPU at an instant; an SMT core can execute several hardware threads.
- **Blocked** (waiting, sleeping): can't run until something happens, such as disk I/O completing, a packet arriving, a lock being released or a timer expiring.
- **Terminated**: finished, but not yet cleaned up.

Two transitions are important. **Running to ready** happens when the scheduler **preempts** a process (usually because the timer interrupt shows its time slice is used up). **Running to blocked** happens when the process asks for something that isn't available yet; it gives up the CPU voluntarily. A blocked process uses no CPU.

### Linux's states

`ps` and `top` show Linux's own letters:

| Letter | Meaning |
|---|---|
| R | running or runnable (ready) |
| S | interruptible sleep |
| D | uninterruptible sleep (usually I/O) |
| T | stopped (e.g. Ctrl-Z, `SIGSTOP`) |
| Z | zombie: exited, not yet reaped |
| I | idle kernel thread |

Linux doesn't distinguish ready from running: both are `R`. Sleeping is split in two. `S` sleeps can be woken by a signal. `D` sleeps can't, because the kernel is in the middle of something that must finish (often waiting on a disk or NFS server). A task in a truly uninterruptible wait cannot act on `SIGKILL` until the wait ends. The displayed `D` state can also cover killable waits that do respond to fatal signals; it is not a complete description of the wait primitive.

> [!warning] Load average counts `D`
> Linux's load average counts tasks in `R` *and* `D`. A load of 40 on an 8-core box doesn't necessarily mean CPU saturation; it might be 35 processes stuck on a hung NFS mount. Check `top` for many `D` processes and low CPU use.

How is the number itself made? About every 5 seconds the kernel counts the tasks in `R` or `D` and folds that count into three moving averages, one for each of the 1, 5 and 15-minute figures that `uptime` and `top` print:

```formula
n = N_R + N_D
α = e^{−Δt / τ}
L_new = α × L_old + (1 − α) × n
where
n: the number of tasks counted at this sample
N_R: tasks running or runnable (state R)
N_D: tasks in uninterruptible sleep (state D)
α: alpha, the weight kept from the old average, between 0 and 1
e: Euler's number, about 2.718; e^{x} is the exponential function
Δt: the time between samples, about 5 seconds
τ: tau, the averaging period: 60 s, 300 s or 900 s for the 1, 5 and 15-minute figures
L_old: the load average before this sample
L_new: the load average after this sample
In words: each sample nudges the average a small step towards the current count of R and D tasks; the longer the period, the smaller the step.
```

Worked example: an idle machine (load 0) suddenly has 40 tasks stuck in `R` or `D`. After one minute, which is 12 samples, the 1-minute figure is:

```formula
α = e^{−5 s / 60 s} ≈ 0.920
L_k = n × (1 − α^k)
L_12 = 40 × (1 − 0.920^12)
L_12 ≈ 40 × 0.63 ≈ 25
where
α: alpha, the weight each sample keeps from the old average, for the 1-minute figure
e: Euler's number, about 2.718
s: second
L_k: the 1-minute load average after k samples, starting from 0
n: the steady count of R and D tasks, here 40
k: the number of 5-second samples taken so far; 12 samples is one minute
L_12: the load average after 12 samples, that is, after one minute
≈: approximately equal to (rounded)
In words: each sample keeps 92 % of the old average and adds 8 % of the current count, so after one minute the figure has covered only about 63 % of the way from 0 to 40.
```

The figure only approaches 40 after several minutes. That lag is why a load spike shows up first in the 1-minute figure and only later in the 15-minute one. The kernel actually does this arithmetic in fixed-point integers, so its constants differ slightly in the last digits.

## Key takeaways
- A process is a running program: an address space, execution state (registers), OS resources and an identity.
- The virtual address space has text, rodata, data, BSS, heap, an mmap region and a stack; each has its own permissions, and the kernel half is inaccessible from user mode.
- The kernel tracks each process (in Linux, each thread) with a PCB, `task_struct`, holding everything needed to pause and resume it.
- The textbook states are new, ready, running, blocked and terminated; preemption moves running to ready, waiting for something moves running to blocked.
- Linux shows `R`, `S`, `D`, `T` and `Z`; `D` is uninterruptible and counts towards load average.

## Further reading
- [The Abstraction: The Process — OSTEP](https://pages.cs.wisc.edu/~remzi/OSTEP/cpu-intro.pdf)
- [The Abstraction: Address Spaces — OSTEP](https://pages.cs.wisc.edu/~remzi/OSTEP/vm-intro.pdf)
- [proc(5) — Linux manual page](https://man7.org/linux/man-pages/man5/proc.5.html)
- [Process control block — Wikipedia](https://en.wikipedia.org/wiki/Process_control_block)
- [Process state — Wikipedia](https://en.wikipedia.org/wiki/Process_state)
- [Address space layout randomization — Wikipedia](https://en.wikipedia.org/wiki/Address_space_layout_randomization)
