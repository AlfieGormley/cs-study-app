---
id: virt-runtime-stack
title: Containerd, shims and low-level runtimes
level: intermediate
minutes: 3
sourceLesson: virt-runtimes-images
summary: The shim supervises tasks after ordinary runc create/start commands return.
---

This unit focuses on containerd, shims and low-level runtimes. It builds on the earlier virtualisation units in this module.

## The runtime stack

"Docker" is really several cooperating programs. Kubernetes uses the lower part of the same stack.

```
docker CLI       kubelet
    |  REST         |  CRI (gRPC)
 dockerd            |
    |  gRPC         |
    +---> containerd <-+
            | images, snapshots
            |
     containerd-shim-runc-v2
            | (may group containers)
           runc
            | clone, pivot_root,
            | cgroups, exec
        your process
```

| Layer | Job |
|---|---|
| CLI / kubelet | User or orchestrator request |
| dockerd | Docker API, builds, networks, volumes |
| containerd | Pull, store, snapshots, lifecycle |
| shim | Supervises task(s), I/O and exit reporting |
| runc | OCI lifecycle CLI used by the shim |

### runc: the low-level runtime

**runc** is the OCI runtime spec's reference implementation. It takes a **bundle**, a directory containing `rootfs/` and `config.json`, and makes the system calls from the last lesson: clone with namespaces, set up cgroups, pivot_root, drop capabilities, install seccomp, exec.

In the shim-managed create/start workflow, **runc lifecycle commands return** and the shim supervises the running process. An attached runc run invocation can remain until the workload exits. Alternatives such as crun, gVisor runsc and Kata provide different implementations or isolation models; compatibility and runtime integration must be checked before switching.

### containerd and the shim

**containerd** is the long-running daemon that manages images and containers on a host. It pulls and verifies blobs, unpacks layers through a **snapshotter** (overlayfs by default) and prepares bundles.

A **shim** supervises tasks and separates their lifetime from the containerd daemon. The runc-v2 shim can group multiple containers, for example a Kubernetes pod, and manages I/O and exit reporting.

The shim design allows tasks to survive a containerd daemon restart if shims/tasks are preserved and reconnection remains compatible. Service-manager stop behavior and upgrade compatibility still matter. Docker daemon shutdown normally stops containers unless supported **live restore** is enabled; live restore also has documented limitations.

### dockerd and Kubernetes

**dockerd** adds the developer-facing layer: the `docker` API on `/var/run/docker.sock`, image builds, networks and volumes. It delegates running containers to containerd.

Kubernetes talks to runtimes through the **Container Runtime Interface (CRI)**. containerd has a built-in CRI plugin; **CRI-O** is an alternative built only for Kubernetes. Kubernetes used to talk to Docker through an adapter called dockershim, removed in version 1.24 (2022). Images built with Docker still run unchanged, because supported Docker/OCI image formats remain compatible.

## Key takeaways

- The shim supervises tasks after ordinary runc create/start commands return.
- CRI compatibility is separate from Docker daemon tooling and service shutdown behaviour.

## Further reading

- [OCI Image Format Specification — GitHub](https://github.com/opencontainers/image-spec/blob/main/spec.md)
- [OCI Runtime Specification — GitHub](https://github.com/opencontainers/runtime-spec/blob/main/spec.md)
- [Docker build cache — Docker docs](https://docs.docker.com/build/cache/)
- [Building best practices — Docker docs](https://docs.docker.com/build/building/best-practices/)
- [Container Runtime Interface — Kubernetes docs](https://kubernetes.io/docs/concepts/architecture/cri/)
