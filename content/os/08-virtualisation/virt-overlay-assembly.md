---
id: virt-overlay-assembly
title: Overlay layers and assembling a native container
level: intermediate
minutes: 3
sourceLesson: virt-container-primitives
summary: Copy-up creates an upper version of a modified lower file; physical costs depend on backing storage.
---

This unit focuses on overlay layers and assembling a native container. It builds on the earlier virtualisation units in this module.

## Overlay file systems: cheap roots

As a decimal-unit illustration, fifty full 200 MB copies require 10 GB before metadata. Layer sharing can avoid that duplication. One common Linux implementation is **overlayfs**; storage backends vary.

```sh
# Leftmost lowerdir wins on name conflicts.
mount -t overlay overlay -o \
 lowerdir=/l/app:/l/python:/l/debian,\
upperdir=/c1/upper,workdir=/c1/work \
 /c1/merged
```

- **lowerdir**: one or more read-only layers, listed top layer first. Can be shared by containers using the same unpacked layers.
- **upperdir**: this container's private writable layer.
- **workdir**: initially empty scratch directory on the same filesystem as upperdir; backing filesystem support and non-overlapping paths must meet overlayfs requirements.
- **merged view**: the unified view that becomes the container's root.

Lookups search from the top down. Writes follow three rules:

1. **Create** a new file: it goes in upperdir.
2. **Modify** a file that exists only in a lower layer: **copy-up**. A file-level upper copy is created before data modification. Metadata-only copy-up, sparse extents and backing-filesystem cloning can alter the actual I/O and physical allocation.
3. **Delete** a lower file: overlayfs creates a **whiteout** in upperdir (for example, a 0/0 character device or a supported zero-size file with a whiteout xattr) that hides it. A deleted directory that is recreated is marked **opaque directory** with an extended attribute.

> [!warning] Copy-up pitfalls
> Copy-up is file-level, so a small change to a large lower file can be expensive; physical copying/allocation depends on sparse-file and reflink support. Write-heavy data often belongs on suitable persistent storage outside the image overlay. Docker-managed volumes and bind mounts are distinct storage choices, not synonyms. Also, deleting a file in a later layer does not reclaim space: the bytes still live in the lower layer.

## Putting it together

A conceptual native-container setup (real runtimes synchronise steps and may delegate storage/network setup):

1. `clone()` a child with `CLONE_NEWPID | CLONE_NEWNS | CLONE_NEWNET | CLONE_NEWUTS | CLONE_NEWIPC` (and `CLONE_NEWUSER` for rootless).
2. Parent: keep the child blocked while configuring UID/GID maps when needed, cgroup membership/limits and the selected networking.
3. Child/runtime: configure the prepared rootfs and mounts, switch root, mount suitable procfs and set the hostname. Rootfs preparation need not use overlayfs or be done by runc.
4. Child: drop capabilities, install a seccomp filter, then `execve()` the application.

That is essentially what `runc` does, given a JSON description of these settings.

> [!note] Execution limits
> This pass ran PID/UTS namespace creation, cgroup writes, overlay copy-up/whiteouts and pivot_root with old-root detach in disposable Linux containers. The overlay upper/work directories needed a supported tmpfs backing mount; nested overlay storage was rejected. No application security boundary is proved by these small mechanics checks.

## Key takeaways

- Copy-up creates an upper version of a modified lower file; physical costs depend on backing storage.
- Whiteouts hide lower files without reclaiming their stored bytes.

## Further reading

- [namespaces(7) — Linux manual page](https://man7.org/linux/man-pages/man7/namespaces.7.html)
- [Control Group v2 — Linux kernel documentation](https://docs.kernel.org/admin-guide/cgroup-v2.html)
- [pivot_root(2) — Linux manual page](https://man7.org/linux/man-pages/man2/pivot_root.2.html)
- [Overlay Filesystem — Linux kernel documentation](https://docs.kernel.org/filesystems/overlayfs.html)
- [pid_namespaces(7) — Linux manual page](https://man7.org/linux/man-pages/man7/pid_namespaces.7.html)
