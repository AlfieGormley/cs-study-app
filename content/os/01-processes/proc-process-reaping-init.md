---
id: proc-process-reaping-init
sourceLesson: proc-fork-exec-wait
title: "Zombies, orphans and container init"
level: intermediate
minutes: 3
summary: "A zombie retains exit bookkeeping until reaped; it cannot execute or be killed again."
---

A zombie retains exit bookkeeping until reaped; it cannot execute or be killed again. This lesson focuses on zombies, orphans and container init.

## Zombies and orphans

When a process exits, the kernel frees its memory and closes its files, but keeps a small record, its PID and exit status, so the parent can collect it. Until the parent calls `wait`, the child is a **zombie** (`Z` in `ps`, often shown as `<defunct>`).

- A zombie has no executing user code or normal address space, but retains kernel bookkeeping memory and a PID.
- It can't be killed: it's already dead. `kill -9` does nothing.
- Leaking zombies is a parent bug. Enough of them can exhaust available PIDs or other process limits and `fork` starts failing with `EAGAIN`.

Fixes: call `waitpid` (often in a `SIGCHLD` handler, looping with `WNOHANG` because standard-signal coalescing can combine notifications), or set `SIGCHLD` to `SIG_IGN`, which tells Linux to reap children automatically.

If the **parent process** dies first, its children become **orphans**. The kernel re-parents them to PID 1, or to the nearest ancestor that marked itself a **subreaper** with `prctl(PR_SET_CHILD_SUBREAPER)` (systemd's per-user manager does this). The new parent's job includes reaping them when they exit.

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
- A zombie retains exit bookkeeping until reaped; it cannot execute or be killed again.
- PID namespace init and subreapers affect adoption, reaping and signal handling.

## Further reading
- [Interlude: Process API — OSTEP](https://pages.cs.wisc.edu/~remzi/OSTEP/cpu-api.pdf)
- [fork(2) — Linux manual page](https://man7.org/linux/man-pages/man2/fork.2.html)
- [execve(2) — Linux manual page](https://man7.org/linux/man-pages/man2/execve.2.html)
- [wait(2) — Linux manual page](https://man7.org/linux/man-pages/man2/wait.2.html)
- [posix_spawn(3) — Linux manual page](https://man7.org/linux/man-pages/man3/posix_spawn.3.html)
- [Zombie process — Wikipedia](https://en.wikipedia.org/wiki/Zombie_process)
- [Copy-on-write — Wikipedia](https://en.wikipedia.org/wiki/Copy-on-write)
- [PID namespaces and init](https://man7.org/linux/man-pages/man7/pid_namespaces.7.html)
- [Docker stop signal and timeout](https://docs.docker.com/reference/cli/docker/container/stop/)
