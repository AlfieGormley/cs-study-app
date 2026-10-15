---
id: proc-wait-exit-status
sourceLesson: proc-fork-exec-wait
title: "Waiting and interpreting exit status"
level: intermediate
minutes: 3
summary: "Wait macros distinguish a normal exit from signal termination."
---

Wait macros distinguish a normal exit from signal termination. This lesson focuses on waiting and interpreting exit status.

## wait: collecting the result

A parent calls `wait` or `waitpid` to block until a child finishes and to collect its **exit status**.

```c
int status;
pid_t done = waitpid(pid, &status, 0);
if (done < 0) {
    /* Check errno; handle EINTR. */
    perror("waitpid");
/* Decode status only after wait */
/* succeeds. */
} else if (WIFEXITED(status))
    printf("exit %d\n",
           WEXITSTATUS(status));
else if (WIFSIGNALED(status))
    printf("signal %d\n",
           WTERMSIG(status));
```

The exit status is **8 bits**: 0 to 255. The parent sees only the low 8 bits of the value the child passed to `exit`, which is the remainder after dividing by 256:

```formula
s_seen = s mod 256
s_seen = 256 mod 256 = 0
s_seen = 300 mod 256 = 44
where
s: the value the child passed to exit()
s_seen: the status the parent reads with WEXITSTATUS
mod: the remainder after division: 300 = 1 × 256 + 44, so 300 mod 256 = 44
256: the number of different values 8 bits can hold (2 to the power 8)
In words: anything above 255 wraps round, so the parent sees only what is left over after removing whole multiples of 256.
```

So `exit(256)` looks like success (0) to the parent, and `exit(300)` arrives as 44. Convention: 0 means success, anything else failure.

Bash and several other shells use these conventions (other shells may encode signal deaths differently):

| `$?` | Meaning |
|---|---|
| 0 | success |
| 1–125 | program-defined failure |
| 126 | found but not executable |
| 127 | command not found |
| Signal-derived status | Bash encoding explained below |

When a child dies from a signal rather than calling `exit`, Bash builds `$?` from the signal number:

```formula
s_bash = 128 + N
s_bash = 128 + 9 = 137
s_bash = 128 + 15 = 143
where
s_bash: the status Bash reports in its $? variable
N: the number of the signal that killed the child, for example 9 for SIGKILL or 15 for SIGTERM
In words: Bash adds 128 to the signal number, so any status above 128 hints at a signal death.
```

In Bash, signal 9 can produce 137 and signal 15 can produce 143, but explicit `exit(137)` or `exit(143)` produce the same values. Status alone cannot prove a signal or OOM cause; inspect wait status or runtime diagnostics.

> [!tip] `exit` versus `_exit`
> `exit()` runs `atexit` handlers and flushes stdio buffers. `_exit()` goes straight to the kernel. In a forked child that fails to `exec`, use `_exit` so you don't flush a copy of the parent's buffers a second time.

## Key takeaways
- Wait macros distinguish a normal exit from signal termination.
- Only low exit-status bits survive; Bash status values alone can be ambiguous.

## Further reading
- [Interlude: Process API — OSTEP](https://pages.cs.wisc.edu/~remzi/OSTEP/cpu-api.pdf)
- [fork(2) — Linux manual page](https://man7.org/linux/man-pages/man2/fork.2.html)
- [execve(2) — Linux manual page](https://man7.org/linux/man-pages/man2/execve.2.html)
- [wait(2) — Linux manual page](https://man7.org/linux/man-pages/man2/wait.2.html)
- [posix_spawn(3) — Linux manual page](https://man7.org/linux/man-pages/man3/posix_spawn.3.html)
- [Zombie process — Wikipedia](https://en.wikipedia.org/wiki/Zombie_process)
- [Copy-on-write — Wikipedia](https://en.wikipedia.org/wiki/Copy-on-write)
