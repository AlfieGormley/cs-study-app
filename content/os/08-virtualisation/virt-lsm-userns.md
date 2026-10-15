---
id: virt-lsm-userns
title: LSM policies and mapped user identities
level: advanced
minutes: 3
sourceLesson: virt-isolation-security
summary: LSM policy adds checks beyond ordinary credentials and permissions.
---

This unit focuses on LSM policies and mapped user identities. It builds on the earlier virtualisation units in this module.

## LSMs: AppArmor and SELinux

Linux Security Modules add **mandatory access control** checks inside the kernel, on objects such as files, sockets and mounts, using path names or labels.

- **AppArmor** (Ubuntu, Debian) uses path-based profiles. Docker loads `docker-default`, which denies writes to most of `/proc/sys`, `/sys` and mounting.
- **SELinux** policies use labels such as container_t and MCS categories to constrain permitted access. Actual domains, shared labels, categories and enforcement depend on runtime/policy configuration; containers do not invariably receive distinct categories.

An enforcing LSM policy can deny file access even when a pathname becomes reachable. DAC permissions and credentials also matter; merely enabling an LSM does not prove a particular file is denied.

## User namespaces: root that isn't

In a user namespace, UID 0 inside the container maps to an unprivileged UID range on the host, say 100000–165535. The kernel stores each range as a start inside, a start outside and a length (the three numbers in `/proc/<pid>/uid_map`) and translates by adding a fixed shift:

```formula
u_host = h_0 + (u_ctr − c_0)
for c_0 ≤ u_ctr < (c_0 + L)
where
u_host: the user ID (UID) the host kernel sees and checks
u_ctr: the UID as seen inside the container
c_0: the first container UID of the mapped range, here 0
h_0: the first host UID of the range, here 100000
L: the length of the range: how many UIDs it maps, here 65536
≤, <: at most, and strictly less than
In words: a container UID is shifted by a fixed amount into the host range; a UID outside every mapped range cannot be used, and appears as the overflow ID (usually 65534).
```

With the example range, container UID 0 becomes host UID 100000, and container UID 1000 becomes host UID 101000. New user namespaces initially grant capabilities scoped to that user namespace, but runtimes may drop them. A mount-visibility escape alone does not grant host-root credentials; a kernel exploit can defeat more than mount isolation.

This is the foundation of **rootless** Podman and Docker. Kubernetes supports it per pod with `hostUsers: false`. The feature is stable as of Kubernetes 1.36.

The trade-off is that user namespaces let unprivileged code reach kernel code that was previously root-only, such as mounting some file systems or creating network devices. Several kernel CVEs have been reachable only this way, which is why some distributions restrict unprivileged user namespace creation.

## Key takeaways

- LSM policy adds checks beyond ordinary credentials and permissions.
- User-namespace root has a mapped host identity and namespace-scoped capabilities, not host-root authority.

## Further reading

- [capabilities(7) — Linux manual page](https://man7.org/linux/man-pages/man7/capabilities.7.html)
- [Seccomp BPF — Linux kernel documentation](https://docs.kernel.org/userspace-api/seccomp_filter.html)
- [Seccomp security profiles for Docker — Docker docs](https://docs.docker.com/engine/security/seccomp/)
- [gVisor security model — gVisor docs](https://gvisor.dev/docs/architecture_guide/security/)
- [Firecracker: Lightweight Virtualization for Serverless Applications — NSDI 2020](https://www.usenix.org/conference/nsdi20/presentation/agache)
- [Firecracker design — GitHub](https://github.com/firecracker-microvm/firecracker/blob/main/docs/design.md)
