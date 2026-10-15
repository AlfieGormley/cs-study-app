---
id: proc-fork-returns
sourceLesson: proc-fork-exec-wait
title: "Fork returns and inherited state"
level: intermediate
minutes: 4
summary: "Successful fork creates independent private-memory state but shared open file descriptions."
---

Ordinary user-space processes on Linux are created by existing tasks; the kernel starts the initial user-space init process during boot. Your shell starts `ls`; `systemd` started your shell's login session; the kernel started `systemd`. The whole system is a family tree, and you can see it with `pstree -p`.

Unix builds this tree from three calls with an unusual design: **`fork`** copies the current process, **`exec`** replaces the copy's program with a new one, and **`wait`** lets the parent collect the result. Splitting creation into separate steps looks odd at first, but it's what makes shells, redirection and pipelines so simple.

## fork: one call, two returns

`fork()` creates a new **child process** that is an almost exact copy of the **parent process**: same code, same memory contents, same open files, same current position in the program. Both continue from the instruction after `fork`.

The return value directly identifies which branch to take (PIDs and other attributes also differ):

| Return value | Meaning |
|---|---|
| `> 0` | you're the parent; value is the child's PID |
| `0` | you're the child |
| `-1` | fork failed (no child created) |

```c
#include <stdio.h>
#include <sys/wait.h>
#include <unistd.h>

int main(void) {
    int x = 10;
    pid_t pid = fork();
    if (pid == 0) {          /* child  */
        /* Only the child changes its */
        /* copy. */
        x += 5;
        printf("child %d\n", x);
        return 0;
    }
    /* Wait orders the two output lines. */
    wait(NULL);              /* parent */
    printf("parent %d\n", x);
    return 0;
}
```

Assuming successful calls and no interruption of the wait, this prints `child 15` then `parent 10`. The child changed *its own copy* of `x`. After `fork` the two processes have separate address spaces; private-memory changes are separate; explicitly shared mappings and external resources remain shared.

> [!example] Counting processes
> `for (i = 0; i < 3; i++) fork();` followed by `printf("x\n")` prints `x` **8** times. Each `fork` doubles the number of processes: 1, 2, 4, 8.

The general rule: every process alive at a `fork` runs it, so each fork in a straight line doubles the count.

```formula
P = 2^n
P = 2^3 = 2 × 2 × 2 = 8
where
P: the number of processes after the forks, including the original
n: the number of fork calls every process executes one after another, here 3
2^n: n copies of 2 multiplied together
In words: n forks in a row turn one process into 2 to the power n processes.
```

The rule assumes every fork succeeds and every process goes on to execute all the remaining forks. It breaks when a fork sits inside a condition: `if (fork() && fork())` makes 3 processes, not 4, because the first child skips the second fork.

### What the child inherits

- **Copied**: memory (stack, heap, data), registers, signal handlers, current directory, environment, resource limits.
- **Shared**: open files. The child's file descriptor table is a copy, but each entry points to the *same* open file description, so they share the file offset. If both write to the same fd, they share the current offset; scheduling determines write order, and record atomicity depends on the object and operation.
- **Not inherited**: the PID, pending signals, process-associated record locks held with `fcntl` (open-file-description locks are inherited), timers, and all threads but the one that called `fork`.

> [!warning] stdio buffers get copied too
> `printf("a"); fork(); printf("b\n");` prints `ab` **twice**. The `a` was still sitting in the stdio buffer in user memory when `fork` copied it. Call `fflush(stdout)` before `fork` if there's buffered output.

## Key takeaways
- Successful fork creates independent private-memory state but shared open file descriptions.
- Process counting must follow control flow and account for copied stdio buffers.

## Further reading
- [Interlude: Process API — OSTEP](https://pages.cs.wisc.edu/~remzi/OSTEP/cpu-api.pdf)
- [fork(2) — Linux manual page](https://man7.org/linux/man-pages/man2/fork.2.html)
- [execve(2) — Linux manual page](https://man7.org/linux/man-pages/man2/execve.2.html)
- [wait(2) — Linux manual page](https://man7.org/linux/man-pages/man2/wait.2.html)
- [posix_spawn(3) — Linux manual page](https://man7.org/linux/man-pages/man3/posix_spawn.3.html)
- [Zombie process — Wikipedia](https://en.wikipedia.org/wiki/Zombie_process)
- [Copy-on-write — Wikipedia](https://en.wikipedia.org/wiki/Copy-on-write)
