---
id: proc-fork-exec-wait
title: "Creating processes: fork, exec and wait"
level: intermediate
minutes: 14
summary: How Unix creates processes with fork and exec, how copy-on-write makes fork cheap, how parents collect exit codes with wait, and what zombies, orphans and PID 1 are really about.
---

Every process on a Linux system, except the very first, was created by another process. Your shell starts `ls`; `systemd` started your shell's login session; the kernel started `systemd`. The whole system is a family tree, and you can see it with `pstree -p`.

Unix builds this tree from three calls with an unusual design: **`fork`** copies the current process, **`exec`** replaces the copy's program with a new one, and **`wait`** lets the parent collect the result. Splitting creation into separate steps looks odd at first, but it's what makes shells, redirection and pipelines so simple.

## fork: one call, two returns

`fork()` creates a new **child** process that is an almost exact copy of the **parent**: same code, same memory contents, same open files, same current position in the program. Both continue from the instruction after `fork`.

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
        x += 5;
        printf("child %d\n", x);
        return 0;
    }
    wait(NULL);              /* parent */
    printf("parent %d\n", x);
    return 0;
}
```

Assuming successful calls and no interruption of the wait, this prints `child 15` then `parent 10`. The child changed *its own copy* of `x`. After `fork` the two processes have separate address spaces; private-memory changes are separate; explicitly shared mappings and external resources remain shared.

> [!example] Counting processes
> `for (i = 0; i < 3; i++) fork();` followed by `printf("x\n")` prints `x` **8** times. Each `fork` doubles the number of processes: 1, 2, 4, 8. Assuming every fork succeeds and every process executes the remaining calls, n successive forks give 2ⁿ processes.

### What the child inherits

- **Copied**: memory (stack, heap, data), registers, signal handlers, current directory, environment, resource limits.
- **Shared**: open files. The child's file descriptor table is a copy, but each entry points to the *same* open file description, so they share the file offset. If both write to the same fd, their output interleaves rather than overwriting.
- **Not inherited**: the PID, pending signals, process-associated record locks held with `fcntl` (open-file-description locks are inherited), timers, and all threads but the one that called `fork`.

> [!warning] stdio buffers get copied too
> `printf("a"); fork(); printf("b\n");` prints `ab` **twice**. The `a` was still sitting in the stdio buffer in user memory when `fork` copied it. Call `fflush(stdout)` before `fork` if there's buffered output.

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
> Redis saves snapshots by forking. The child writes the dataset to disk from its frozen COW view while the parent keeps serving writes. Every page the parent modifies during the save gets copied, so a write-heavy Redis can need up to twice its memory during `BGSAVE`. Redis latency documentation warns that transparent huge pages can worsen COW latency and memory usage. Copying versus splitting and page sizes depend on the kernel; not every small write necessarily copies 2 MiB.

## exec: replace the program

`exec` loads a new program into the *current* process. The code, data, heap and stack are thrown away and replaced; execution starts at the new program's entry point. If `exec` succeeds, it never returns.

```c
char *argv[] = {"ls", "-l", NULL};
execvp("ls", argv);
perror("execvp");   /* only on failure */
_exit(127);
```

What survives `exec`:

- The **PID** and parent: it's the same process, running a different program.
- **Open file descriptors**, unless marked close-on-exec (`O_CLOEXEC` / `FD_CLOEXEC`).
- Current directory, user IDs (unless setuid), resource limits.
- Signals set to *ignore* stay ignored; signals with handlers reset to default (the handler code is gone).

The family is `execl`, `execv`, `execle`, `execve`, `execvp` and `execlp`. They differ in how arguments are passed (list or vector), whether `PATH` is searched (`p`) and whether you pass an environment (`e`). All are wrappers around the one syscall, **`execve`**.

## Why split fork and exec?

Between `fork` and `exec`, the child runs *your* code in its own process. It can rearrange its environment before the new program starts. This is how a shell does `ls > out.txt`:

```c
pid_t pid = fork();
if (pid == 0) {
    int fd = open("out.txt",
        O_WRONLY | O_CREAT | O_TRUNC, 0644);
    if (fd < 0) _exit(126);
    if (dup2(fd, 1) < 0) _exit(126);
    if (fd != 1) close(fd);
    execlp("ls", "ls", NULL);
    _exit(127);
}
waitpid(pid, NULL, 0);
```

`ls` has no idea it's writing to a file; it writes to fd 1 as always. The same trick with `pipe` gives pipelines, and `setpgid`, `chdir` or dropping privileges all slot into the same gap.

The downside: forking a huge process just to `exec` wastes page-table copying, and forking a multithreaded process is risky (only the calling thread survives, and a lock another thread held stays locked forever). Alternatives exist:

- **`posix_spawn`**: create and exec in one call; glibc implements it with a fast `clone` variant. Used by modern runtimes and recommended for large processes.
- **`vfork`**: the child borrows the parent's memory and the parent is suspended until the child calls `exec` or `_exit`. Fast but easy to misuse.
- **`clone`**: Linux's general primitive. `fork`, threads and containers are all `clone` with different flags for what to share.

## wait: collecting the result

A parent calls `wait` or `waitpid` to block until a child finishes and to collect its **exit status**.

```c
int status;
pid_t done = waitpid(pid, &status, 0);
if (done < 0) {
    /* Check errno; handle EINTR. */
    perror("waitpid");
} else if (WIFEXITED(status))
    printf("exit %d\n",
           WEXITSTATUS(status));
else if (WIFSIGNALED(status))
    printf("signal %d\n",
           WTERMSIG(status));
```

The exit status is **8 bits**: 0 to 255. `exit(256)` looks like success (0) to the parent, and `exit(300)` arrives as 44 (300 mod 256). Convention: 0 means success, anything else failure.

Bash and several other shells use these conventions (other shells may encode signal deaths differently):

| `$?` | Meaning |
|---|---|
| 0 | success |
| 1–125 | program-defined failure |
| 126 | found but not executable |
| 127 | command not found |
| 128 + N | killed by signal N |

In Bash, signal 9 can produce 137 and signal 15 can produce 143, but explicit `exit(137)` or `exit(143)` produce the same values. Status alone cannot prove a signal or OOM cause; inspect wait status or runtime diagnostics.

> [!tip] `exit` versus `_exit`
> `exit()` runs `atexit` handlers and flushes stdio buffers. `_exit()` goes straight to the kernel. In a forked child that fails to `exec`, use `_exit` so you don't flush a copy of the parent's buffers a second time.

## Zombies and orphans

When a process exits, the kernel frees its memory and closes its files, but keeps a small record, its PID and exit status, so the parent can collect it. Until the parent calls `wait`, the child is a **zombie** (`Z` in `ps`, often shown as `<defunct>`).

- A zombie has no executing user code or normal address space, but retains kernel bookkeeping memory and a PID.
- It can't be killed: it's already dead. `kill -9` does nothing.
- Leaking zombies is a parent bug. Enough of them can exhaust available PIDs or other process limits and `fork` starts failing with `EAGAIN`.

Fixes: call `waitpid` (often in a `SIGCHLD` handler, looping with `WNOHANG` because signals don't queue), or set `SIGCHLD` to `SIG_IGN`, which tells Linux to reap children automatically.

If the **parent** dies first, its children become **orphans**. The kernel re-parents them to PID 1, or to the nearest ancestor that marked itself a **subreaper** with `prctl(PR_SET_CHILD_SUBREAPER)` (systemd's per-user manager does this). The new parent's job includes reaping them when they exit.

## PID 1: init and systemd

PID 1 is the first user-space process, started by the kernel at boot. On most Linux distributions it is **systemd**. It has special duties and rules:

- It is the ultimate parent, and must reap any orphaned zombies.
- If initial-namespace init exits, Linux panics. If a nested PID namespace's init exits, the kernel kills the remaining processes in that namespace instead.
- Init has special signal handling: ordinary terminating signals with default dispositions are generally ignored. Namespace and sender matter; ancestor PID namespaces can forcibly deliver SIGKILL/SIGSTOP to a nested namespace init.

> [!warning] The container PID 1 problem
> In a container, your application is often PID 1 in its PID namespace. It inherits those duties without knowing it. A Node or Python app that spawns subprocesses may never reap orphaned grandchildren, and it may ignore `SIGTERM` because it installed no handler, so Docker waits for its configured timeout (10 seconds by default for Linux containers) and then sends SIGKILL. The configured stop signal can differ from SIGTERM. The fix is a tiny init: `docker run --init` (which uses `tini`) or `tini`/`dumb-init` as the entrypoint.

> [!note] Content gap: fork performance
> No reproducible fork benchmark is supplied for this machine. Universal milliseconds-per-GB figures are omitted. Short snippets assume successful process creation and suitable headers unless they explicitly handle errors; production code must check failures and interrupted waits.

## Key takeaways
- `fork` returns twice: the child's PID in the parent, 0 in the child. The child has a copy of memory and shares the parent's open files.
- Copy-on-write makes `fork` cost roughly the page tables, not the memory; pages are copied only when written.
- `exec` replaces the program in the same process (same PID, inherited fds); the gap between `fork` and `exec` is where shells set up redirection and pipes.
- `wait` distinguishes normal exit from signal death. Bash commonly displays 128 + signal number, but a displayed 137 alone is ambiguous.
- An unreaped dead child is a zombie; a child whose parent died is an orphan, adopted by PID 1 or a subreaper. In containers, run a proper init as PID 1.

## Further reading
- [Interlude: Process API — OSTEP](https://pages.cs.wisc.edu/~remzi/OSTEP/cpu-api.pdf)
- [fork(2) — Linux manual page](https://man7.org/linux/man-pages/man2/fork.2.html)
- [execve(2) — Linux manual page](https://man7.org/linux/man-pages/man2/execve.2.html)
- [wait(2) — Linux manual page](https://man7.org/linux/man-pages/man2/wait.2.html)
- [posix_spawn(3) — Linux manual page](https://man7.org/linux/man-pages/man3/posix_spawn.3.html)
- [Zombie process — Wikipedia](https://en.wikipedia.org/wiki/Zombie_process)
- [Copy-on-write — Wikipedia](https://en.wikipedia.org/wiki/Copy-on-write)
