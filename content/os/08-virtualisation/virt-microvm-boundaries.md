---
id: virt-microvm-boundaries
title: MicroVMs and choosing an isolation boundary
level: advanced
minutes: 4
sourceLesson: virt-isolation-security
summary: Firecracker reduces its virtual device model and confines the host VMM with several controls.
---

This unit focuses on microVMs and choosing an isolation boundary. It builds on the earlier virtualisation units in this module.

### Firecracker: microVMs

Firecracker (AWS, written in Rust) is a KVM-based virtual machine monitor stripped down to almost nothing. It offers virtio-net, virtio-block, virtio-vsock, a serial console and a partial keyboard controller (used only to reset the VM). There is no BIOS, no PCI bus by default and no USB or GPU emulation.

Firecracker publishes configuration-specific targets: at most 125 ms from InstanceStart to guest /sbin/init and at most 5 MiB VMM overhead under its documented small-VM, tuned-kernel host conditions. These exclude guest RAM and have workload/configuration caveats; they are not universal end-to-end launch figures or capacity guarantees. The project documents use in AWS Lambda and AWS Fargate. A guest kernel remains behind a virtualisation boundary.

Defence in depth continues outside the VM. For a hardened deployment, the **jailer** sets up host-side restrictions such as chroot, namespaces, cgroups and reduced privileges; Firecracker applies its thread-specific seccomp filters. The jailer limits the VMM's host privileges; the outcome of any escape depends on the vulnerability and deployment. A guest-kernel compromise alone is not the same as executing host VMM code.

**Kata Containers** brings the same model to Kubernetes. Each pod runs in a lightweight VM (QEMU, Cloud Hypervisor or Firecracker), with an agent inside it creating ordinary containers. The trade-offs are higher memory per pod, slower start than runc, and harder device and file-sharing paths.

## Choosing a level

| Option | Boundary | Cost |
|---|---|---|
| runc + defaults | Shared kernel, filtered | Workload dependent |
| + rootless/userns | Scoped host identity | Configuration dependent |
| gVisor | User-space kernel | Syscall overhead |
| Firecracker/Kata | Guest kernel + hardware support | Guest/VMM resources |

Hardened runc can fit trusted workloads when its shared-kernel boundary matches the threat model. Hostile multi-tenant code warrants evaluating a stronger sandbox or microVM boundary, with its compatibility and operational costs.

## Pitfalls

- **`--privileged`**, in ordinary rootful Docker, grants broad capabilities/device access and relaxes normal seccomp and LSM restrictions. Rootless/namespace scope and host configuration still matter. With accessible host devices and suitable kernel support, this can permit mounting host storage and exercising host-root-equivalent authority; a particular disk path is not guaranteed.
- **Adding `SYS_ADMIN` to fix one error** undoes most of the hardening. Find the specific capability or syscall instead.
- **Unconfined seccomp in Kubernetes.** Set `RuntimeDefault` in every pod, or enable the kubelet's `seccompDefault` option.
- **Host mounts.** Sensitive host paths or daemon sockets can undermine isolation by exposing data or authority. They do not literally disable every remaining credential, seccomp or LSM check.
- **Unpatched kernels.** Container hardening reduces exposure, but kernel updates are still the main defence for shared-kernel isolation.

> [!note] Verification limits
> The historical vulnerabilities are source-checked examples, not exploits run during this review. No live gVisor, Firecracker or Kata isolation/performance experiment was performed. Published Firecracker targets are scoped above; no universal sandbox ranking, escape guarantee or launch-rate estimate is supported here.

## Key takeaways

- Firecracker reduces its virtual device model and confines the host VMM with several controls.
- Choose and measure a boundary against the actual workload and threat model; no option proves universal safety.

## Further reading

- [capabilities(7) — Linux manual page](https://man7.org/linux/man-pages/man7/capabilities.7.html)
- [Seccomp BPF — Linux kernel documentation](https://docs.kernel.org/userspace-api/seccomp_filter.html)
- [Seccomp security profiles for Docker — Docker docs](https://docs.docker.com/engine/security/seccomp/)
- [gVisor security model — gVisor docs](https://gvisor.dev/docs/architecture_guide/security/)
- [Firecracker: Lightweight Virtualization for Serverless Applications — NSDI 2020](https://www.usenix.org/conference/nsdi20/presentation/agache)
- [Firecracker design — GitHub](https://github.com/firecracker-microvm/firecracker/blob/main/docs/design.md)
