---
id: virt-namespace-views
title: Namespaces, PID 1 and entering a container
level: intermediate
minutes: 5
sourceLesson: virt-container-primitives
summary: Namespaces provide scoped resource views, not a complete security policy.
---

A virtual machine fakes an entire computer, and runs its own kernel on it. A **container** does something much lighter: it is an ordinary Linux process that the kernel shows a restricted, customised view of the system.

There is no `container` object in the Linux kernel. A container is a combination of independent features:

- **Namespaces** control what a process can **see**.
- **cgroups** control how much it can **use**.
- A **root file system** switch (`pivot_root`) controls which files it starts from.
- A **layered file system** (usually overlayfs) makes that root cheap to create.
- Security filters (capabilities, seccomp, LSMs) control what it may **do**. The later container-security units explain these controls.

These are common primitives for native Linux process containers. Kubernetes orchestrates containers through runtimes; VM-backed and userspace-kernel sandboxes can implement a different boundary.

## Namespaces: private views of global resources

A **namespace** wraps a global resource so that processes inside it see their own isolated copy. Linux has eight:

| Namespace | Isolates | Since |
|---|---|---|
| mnt | Mount table | 2.4.19 (2002) |
| uts | Hostname | 2.6.19 |
| ipc | SysV IPC, POSIX queues | 2.6.19 |
| pid | Process IDs | 2.6.24 |
| net | Interfaces, routes, ports | 2.6.29 |
| user | UIDs, GIDs, capabilities | 2.6.23; completed in 3.8 |
| cgroup | cgroup root view | 4.6 |
| time | Boot/monotonic clocks | 5.6 |

Core namespace-management interfaces include:

- `clone(flags)` creates a process in new namespaces, with flags such as `CLONE_NEWPID | CLONE_NEWNET`.
- `unshare(flags)` creates requested namespaces; PID and time namespaces apply to subsequently created children rather than changing the caller's current membership.
- `setns(fd, nstype)` can join an existing namespace through a namespace descriptor. PID membership is different: it selects the namespace for future children, so a helper must also fork. Runtime exec also sets up root, credentials and resource/security controls.

You can try it without Docker. The `unshare` command wraps the system call:

```
$ sudo unshare --uts --pid --fork \
    --mount-proc bash
# hostname box1
# hostname
box1
# ps -e
  PID TTY      TIME CMD
    1 pts/0    0:00 bash
    4 pts/0    0:00 ps
```

The displayed session is illustrative: the new shell has its own hostname and is **PID 1**. The exact PID of `ps`, terminal name and timing depend on the shell and helper processes. On the host, the same bash has an ordinary PID like 48213. Both views are true: a process has a PID in each PID namespace it is visible in.

### What each namespace gives you

- **pid**: the first process becomes PID 1, the container's init. If it exits, the kernel kills every other process in the namespace. Namespace init has special signal protection: an ordinary SIGTERM needs an installed handler; an ancestor namespace can force SIGKILL/SIGSTOP. Docker's stop signal and grace period are configurable (the documented Linux default timeout is 10 seconds). Init helpers also forward signals and reap children.
- **net**: a fresh, empty network stack with only a loopback interface that is down. A common bridge configuration creates a **veth pair**, places one end inside and optionally uses host NAT. Host networking, routed networking and other plugins differ. Two containers can both listen on port 80 because each has its own port space.
- **mnt**: a private copy of the mount table. Mounts inside do not appear on the host (subject to mount propagation settings).
- **uts**: hostname and NIS domain name.
- **ipc**: System V shared memory, semaphores and message queues, plus POSIX message queues.
- **user**: maps UIDs inside to different UIDs outside. UID 0 inside can be UID 100000 on the host, so it does not gain initial-user-namespace root privileges merely by being UID 0 inside. It can still access resources allowed to the mapped host identity. This is the basis of rootless containers.
- **cgroup**: hides the host's cgroup paths so the container sees its own cgroup as `/`.
- **time**: lets a container see a different monotonic and boot-time clock, mainly for checkpoint/restore.

> [!note] Namespaces are not security boundaries on their own
> Namespaces enforce resource isolation, but the overall boundary depends on credentials, capabilities and other controls. Loading host kernel modules requires privileges in the initial user namespace; root in a child user namespace does not acquire that power. Native Linux process containers share a kernel attack surface.

## Key takeaways

- Namespaces provide scoped resource views, not a complete security policy.
- PID namespace entry affects future children; namespace init has special signal and lifetime rules.

## Further reading

- [namespaces(7) — Linux manual page](https://man7.org/linux/man-pages/man7/namespaces.7.html)
- [Control Group v2 — Linux kernel documentation](https://docs.kernel.org/admin-guide/cgroup-v2.html)
- [pivot_root(2) — Linux manual page](https://man7.org/linux/man-pages/man2/pivot_root.2.html)
- [Overlay Filesystem — Linux kernel documentation](https://docs.kernel.org/filesystems/overlayfs.html)
- [pid_namespaces(7) — Linux manual page](https://man7.org/linux/man-pages/man7/pid_namespaces.7.html)
