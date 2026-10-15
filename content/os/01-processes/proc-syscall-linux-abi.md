---
id: proc-syscall-linux-abi
sourceLesson: proc-syscalls
title: "Following a Linux syscall"
level: basic
minutes: 3
summary: "The x86-64 Linux syscall ABI uses numbered services and specific argument registers."
---

The x86-64 Linux syscall ABI uses numbered services and specific argument registers. This lesson focuses on following a linux syscall.

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
    /* Request stdout output: three */
    /* bytes. */
    syscall(SYS_write, 1, "hi\n", 3);
    /* This libc entry still handles */
    /* errno. */
    long pid = syscall(SYS_getpid);
    return pid > 0 ? 0 : 1;
}
```

> [!tip] Watch syscalls happen
> `strace -c ls` runs `ls` and prints a table of every syscall it made, how many times, and the time spent. `strace -f -e trace=openat,read cmd` shows just those calls, following child processes. It's the single most useful tool for "why is this program slow / failing?"

## Key takeaways
- The x86-64 Linux syscall ABI uses numbered services and specific argument registers.
- libc translates raw negative error returns into failure results and errno.

## Further reading
- [Mechanism: Limited Direct Execution — OSTEP](https://pages.cs.wisc.edu/~remzi/OSTEP/cpu-mechanisms.pdf)
- [Anatomy of a system call, part 1 — LWN](https://lwn.net/Articles/604287/)
- [Anatomy of a system call, part 2 — LWN](https://lwn.net/Articles/604515/)
- [syscall(2) — Linux manual page](https://man7.org/linux/man-pages/man2/syscall.2.html)
- [vdso(7) — Linux manual page](https://man7.org/linux/man-pages/man7/vdso.7.html)
- [Kernel page-table isolation — Wikipedia](https://en.wikipedia.org/wiki/Kernel_page-table_isolation)
