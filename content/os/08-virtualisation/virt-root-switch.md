---
id: virt-root-switch
title: Changing roots without keeping host references
level: intermediate
minutes: 2
sourceLesson: virt-container-primitives
summary: chroot changes pathname lookup but leaves working directories and descriptors intact.
---

This unit focuses on changing roots without keeping host references. It builds on the earlier virtualisation units in this module.

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

## Key takeaways

- chroot changes pathname lookup but leaves working directories and descriptors intact.
- A correct pivot_root setup detaches the old visible root, while credentials and leaked references still matter.

## Further reading

- [namespaces(7) — Linux manual page](https://man7.org/linux/man-pages/man7/namespaces.7.html)
- [Control Group v2 — Linux kernel documentation](https://docs.kernel.org/admin-guide/cgroup-v2.html)
- [pivot_root(2) — Linux manual page](https://man7.org/linux/man-pages/man2/pivot_root.2.html)
- [Overlay Filesystem — Linux kernel documentation](https://docs.kernel.org/filesystems/overlayfs.html)
- [pid_namespaces(7) — Linux manual page](https://man7.org/linux/man-pages/man7/pid_namespaces.7.html)
