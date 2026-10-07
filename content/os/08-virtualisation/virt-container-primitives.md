---
id: virt-container-primitives
title: Containers from first principles
level: intermediate
minutes: 14
summary: There is no 'container' in the Linux kernel. Here is what there is instead, namespaces, cgroups v2, pivot_root and overlay file systems, and how they combine into one.
---

A virtual machine fakes an entire computer, and runs its own kernel on it. A **container** does something much lighter: it is an ordinary Linux process that the kernel shows a restricted, customised view of the system.

There is no `container` object in the Linux kernel. A container is a combination of independent features:

- **Namespaces** control what a process can **see**.
- **cgroups** control how much it can **use**.
- A **root file system** switch (`pivot_root`) controls which files it starts from.
- A **layered file system** (usually overlayfs) makes that root cheap to create.
- Security filters (capabilities, seccomp, LSMs) control what it may **do**. They get the next lesson but one.

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

The new shell has its own hostname and believes it is **PID 1**. (`ps` is PID 4 because the two `hostname` runs took PIDs 2 and 3.) On the host, the same bash has an ordinary PID like 48213. Both views are true: a process has a PID in each PID namespace it is visible in.

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

## cgroups v2: limiting and accounting

**Control groups** organise processes into a tree and attach resource controllers to each node. Cgroups v2 uses a unified hierarchy, commonly mounted at `/sys/fs/cgroup`. Inspect the actual host: available/enabled controllers and boot configuration vary.

A simplified administrator example on a disposable, correctly delegated cgroup v2 hierarchy follows. It assumes the controllers are available, permissions allow these writes, and a service manager is not managing the same subtree. Commands must succeed before continuing; do not treat this as a universal host setup script.

```
$ cd /sys/fs/cgroup
$ echo +cpu +memory +pids \
    > cgroup.subtree_control
$ mkdir demo
$ echo "50000 100000" > demo/cpu.max
$ echo 256M > demo/memory.max
$ echo 100 > demo/pids.max
$ echo $$ > demo/cgroup.procs
```

After successful writes, the shell and later children share a fair-scheduler CPU quota averaging half a CPU, a 256 MiB accounted-memory limit and a 100-task limit (threads count). Ancestor limits also apply; pre-existing children are not automatically moved with the shell.

| File | Meaning |
|---|---|
| `cpu.max` | Quota and period in µs; `max 100000` means no limit |
| `cpu.weight` | Relative share under contention, 1–10000, default 100 |
| `memory.max` | Accounted-memory limit; reclaim/OOM handling |
| `memory.high` | Throttling/reclaim threshold; may be exceeded |
| `pids.max` | Maximum tasks; stops fork bombs |
| `io.max` | Per-device bandwidth or IOPS limits |

A few mechanics are worth knowing precisely:

- **CPU quota is enforced per period.** `50000 100000` means 50 ms of CPU time per 100 ms window, *across all threads*. In an idealised case with four threads running continuously on four available CPUs, no burst credit and no tighter ancestor limit, 50 ms of budget lasts 12.5 ms of wall time. Scheduler accounting and runtime slices make actual traces less exact. Lesson 6 shows why this hurts latency.
- **`cpu.weight` only matters under contention.** A sufficiently parallel group may use otherwise-idle allowed CPUs, subject to quota, affinity, cpuset and ancestor restrictions.
- **Memory limits count page cache too.** A process that reads large files fills its cgroup's page cache; reclaimable cache can reduce pressure, but pinned/dirty data and other charges matter. memory.max can be exceeded temporarily, and some allocation failures do not invoke the OOM killer. A container can look "full" when much usage is reclaimable cache. `memory.stat` shows the breakdown, and `memory.events` counts `oom_kill`s.
- **The "no internal processes" rule.** For domain resource distribution, a non-root cgroup must have no internal processes before enabling domain controllers for children. The root and threaded-controller subtrees have exceptions; "processes only in leaves" is not a universal rule.

cgroups v1, still found on older hosts, had a separate tree per controller (`/sys/fs/cgroup/memory/...`, `/sys/fs/cgroup/cpu/...`), which made consistent limits awkward. Its CPU knob was `cpu.shares` (default 1024) rather than `cpu.weight`.

## Changing root: chroot vs pivot_root

A container needs its own file system: the image's `/bin`, `/lib` and `/etc` instead of the host's.

The old tool is **`chroot(path)`**, which changes the directory a single process treats as `/`. It is **not** an isolation boundary:

- It changes only the process's root, not the mount table. Existing mounts remain, and inherited descriptors or a working directory outside the new root can still provide access.
- A root process can escape: create a subdirectory, `chroot` into it while keeping its working directory *outside* the new root, then `chdir("..")` repeatedly back to the real `/`, and `chroot(".")`.

A common native-runtime setup uses **`pivot_root(new_root, put_old)`** inside a mount namespace, with suitable private mount propagation and no leaked external references:

1. Make `new_root` a mount point (bind-mount the container's root onto itself).
2. `pivot_root` makes it the root mount and moves the old root to `put_old` underneath it.
3. Unmount `put_old` with `MNT_DETACH`.

This removes the old root from the visible mount tree when setup is correct. It is not a complete security proof: open descriptors, other bind mounts, propagation and retained privileges must also be controlled. Lazy unmount can leave referenced mounts alive.

```
before            after pivot + umount
/ (host)          / (container rootfs)
|- bin            |- bin  (image's)
|- var            |- etc  (image's)
|- containers/    |- proc (new procfs)
   |- c1/rootfs   (host root: gone)
```

## Overlay file systems: cheap roots

As a decimal-unit illustration, fifty full 200 MB copies require 10 GB before metadata. Layer sharing can avoid that duplication. One common Linux implementation is **overlayfs**; storage backends vary.

```
mount -t overlay overlay -o \
 lowerdir=/l/app:/l/python:/l/debian,\
upperdir=/c1/upper,workdir=/c1/work \
 /c1/merged
```

- **lowerdir**: one or more read-only layers, the leftmost on top. Can be shared by containers using the same unpacked layers.
- **upperdir**: this container's private writable layer.
- **workdir**: initially empty scratch directory on the same filesystem as upperdir; backing filesystem support and non-overlapping paths must meet overlayfs requirements.
- **merged**: the unified view that becomes the container's root.

Lookups search from the top down. Writes follow three rules:

1. **Create** a new file: it goes in upperdir.
2. **Modify** a file that exists only in a lower layer: **copy-up**. A file-level upper copy is created before data modification. Metadata-only copy-up, sparse extents and backing-filesystem cloning can alter the actual I/O and physical allocation.
3. **Delete** a lower file: overlayfs creates a **whiteout** in upperdir (for example, a 0/0 character device or a supported zero-size file with a whiteout xattr) that hides it. A deleted directory that is recreated is marked **opaque** with an extended attribute.

> [!warning] Copy-up pitfalls
> Copy-up is file-level, so a small change to a large lower file can be expensive; physical copying/allocation depends on sparse and clone support. Write-heavy data often belongs on suitable persistent storage outside the image overlay. Docker-managed volumes and bind mounts are distinct storage choices, not synonyms. Also, deleting a file in a later layer does not reclaim space: the bytes still live in the lower layer.

## Putting it together

A conceptual native-container setup (real runtimes synchronise steps and may delegate storage/network setup):

1. `clone()` a child with `CLONE_NEWPID | CLONE_NEWNS | CLONE_NEWNET | CLONE_NEWUTS | CLONE_NEWIPC` (and `CLONE_NEWUSER` for rootless).
2. Parent: keep the child blocked while configuring UID/GID maps when needed, cgroup membership/limits and the selected networking.
3. Child/runtime: configure the prepared rootfs and mounts, switch root, mount suitable procfs and set the hostname. Rootfs preparation need not use overlayfs or be done by runc.
4. Child: drop capabilities, install a seccomp filter, then `execve()` the application.

That is essentially what `runc` does, given a JSON description of these settings.

## Key takeaways

- A container is a normal process plus namespaces (what it sees), cgroups (what it uses) and a new root file system.
- The eight namespaces are mnt, uts, ipc, pid, net, user, cgroup and time; `clone`, `unshare` and `setns` manage them.
- cgroups v2 is one tree of files under `/sys/fs/cgroup`; `cpu.max` sets a quota per period, `memory.max` an accounted-memory limit with reclaim and allocation/OOM handling.
- `chroot` alone is not a security boundary. A root-mount switch plus correct mount, descriptor and privilege isolation is a common stronger setup.
- overlayfs stacks shared read-only layers under a per-container upper layer, with file-level copy-up and whiteouts for deletes; actual storage/I/O costs depend on backing support.

> [!note] Execution limits
> The namespace and cgroup views were inspected in an isolated Linux container, and resource-limit values were checked. The nested unshare probe was denied by the outer security policy. No privileged pivot_root or overlay mount was performed; those shell fragments remain source-reviewed examples with stated setup requirements.

## Further reading

- [namespaces(7) — Linux manual page](https://man7.org/linux/man-pages/man7/namespaces.7.html)
- [Control Group v2 — Linux kernel documentation](https://docs.kernel.org/admin-guide/cgroup-v2.html)
- [pivot_root(2) — Linux manual page](https://man7.org/linux/man-pages/man2/pivot_root.2.html)
- [Overlay Filesystem — Linux kernel documentation](https://docs.kernel.org/filesystems/overlayfs.html)
- [pid_namespaces(7) — Linux manual page](https://man7.org/linux/man-pages/man7/pid_namespaces.7.html)
