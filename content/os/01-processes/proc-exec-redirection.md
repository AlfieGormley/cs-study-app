---
id: proc-exec-redirection
sourceLesson: proc-fork-exec-wait
title: "Replacing a program and redirecting output"
level: intermediate
minutes: 3
summary: "Exec replaces the program while preserving process identity and selected resources."
---

Exec replaces the program while preserving process identity and selected resources. This lesson focuses on replacing a program and redirecting output.

## exec: replace the program

`exec` loads a new program into the *current* process. The code, data, heap and stack are thrown away and replaced; execution starts at the new program's entry point. If `exec` succeeds, it never returns.

```c
char *argv[] = {"ls", "-l", NULL};
/* Success replaces this program image. */
execvp("ls", argv);
perror("execvp");   /* only on failure */
_exit(127);
```

What survives `exec`:

- The **PID** and parent: it's the same process, running a different program.
- **Open file descriptors**, unless marked close-on-exec (`O_CLOEXEC` / `FD_CLOEXEC`).
- Current directory, user IDs (unless setuid), resource limits.
- Signals set to *ignore* stay ignored; signals with handlers reset to default (the handler code is gone).

The family is `execl`, `execv`, `execle`, `execve`, `execvp` and `execlp`. They differ in how arguments are passed (as separate arguments, `l`, or as one `argv` array, `v`), whether `PATH` is searched (`p`) and whether you pass an environment (`e`). On Linux, these classic pathname-based interfaces ultimately use **`execve`** (related interfaces such as `fexecve` can instead use `execveat`).

## Why split fork and exec?

Between `fork` and `exec`, the child runs *your* code in its own process. It can rearrange its environment before the new program starts. This is how a shell does `ls > out.txt`:

```c
pid_t pid = fork();
if (pid == 0) {
    int fd = open("out.txt",
        O_WRONLY | O_CREAT | O_TRUNC, 0644);
    if (fd < 0) _exit(126);
    /* Redirect stdout before exec keeps */
    /* fd 1. */
    if (dup2(fd, 1) < 0) _exit(126);
    /* Keep stdout open if open returned */
    /* 1. */
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
- **`clone`**: Linux's general primitive. related process/thread creation interfaces, including `clone3`, select which resources and namespaces to share. `fork` wrappers and runtimes can use these mechanisms differently.

## Key takeaways
- Exec replaces the program while preserving process identity and selected resources.
- The fork/exec gap enables redirection but needs care in multithreaded programs.

## Further reading
- [Interlude: Process API — OSTEP](https://pages.cs.wisc.edu/~remzi/OSTEP/cpu-api.pdf)
- [fork(2) — Linux manual page](https://man7.org/linux/man-pages/man2/fork.2.html)
- [execve(2) — Linux manual page](https://man7.org/linux/man-pages/man2/execve.2.html)
- [wait(2) — Linux manual page](https://man7.org/linux/man-pages/man2/wait.2.html)
- [posix_spawn(3) — Linux manual page](https://man7.org/linux/man-pages/man3/posix_spawn.3.html)
- [Zombie process — Wikipedia](https://en.wikipedia.org/wiki/Zombie_process)
- [Copy-on-write — Wikipedia](https://en.wikipedia.org/wiki/Copy-on-write)
