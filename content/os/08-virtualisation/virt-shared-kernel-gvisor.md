---
id: virt-shared-kernel-gvisor
title: Shared-kernel risks and the gVisor boundary
level: advanced
minutes: 3
sourceLesson: virt-isolation-security
summary: Reachable kernel and runtime flaws can compromise native-container isolation.
---

This unit focuses on shared-kernel risks and the gVisor boundary. It builds on the earlier virtualisation units in this module.

## When the shared kernel is the problem

All of the above filters requests to the **host kernel**. A reachable kernel flaw can bypass important protections. Dirty Pipe (CVE-2022-0847) enabled constrained modification of readable file-backed page-cache data on vulnerable kernels, including read-only files; exploitability depended on reachable files and calls. No profile is required to allow the splice() call, and the flaw did not mean every process could overwrite arbitrary host files.

Runtime bugs matter too. In CVE-2019-5736, a malicious container could overwrite the host's `runc` binary through `/proc/self/exe` while `docker exec` was running, leading to host code execution under the vulnerable runtime's privileges. This is a historical vulnerability, not a claim about patched current releases.

For untrusted, multi-tenant code, such as customer functions, CI jobs from strangers or browser-submitted code, the answer is to put **another kernel** between the workload and the host.

### gVisor: a kernel in user space

gVisor (Google, written in Go) implements the Linux system call interface in a user-space process called the **Sentry**. The application's syscalls are intercepted (by the default **systrap** platform, using seccomp traps, or by a KVM platform) and handled by the Sentry, which has its own memory management, VFS and TCP/IP stack (netstack).

```
 app
  | syscall
  v
 Sentry (Go, user space)
  | small allowlisted set
  | of host syscalls
  v
 host kernel
```

The Sentry itself runs under a strict seccomp filter that allows only a small set of host syscalls. File access goes through a separate **Gofer** process or a restricted direct mode. This design reduces direct host-kernel exposure and adds a sandbox boundary; it is not a proof that every possible escape needs the same two-step exploit chain.

The costs are compatibility (not every syscall or `/proc` file is implemented) and performance on syscall-heavy and I/O-heavy workloads, because each call is handled by Go code rather than the native kernel path. CPU-bound application instructions execute natively, so workloads with few system interactions may have lower overhead; measure the actual workload and platform. It ships as the OCI runtime `runsc` and powers GKE Sandbox and parts of Google's serverless platforms.

## Key takeaways

- Reachable kernel and runtime flaws can compromise native-container isolation.
- gVisor implements application system calls in a sandboxed userspace kernel, with compatibility and workload costs.

## Further reading

- [capabilities(7) — Linux manual page](https://man7.org/linux/man-pages/man7/capabilities.7.html)
- [Seccomp BPF — Linux kernel documentation](https://docs.kernel.org/userspace-api/seccomp_filter.html)
- [Seccomp security profiles for Docker — Docker docs](https://docs.docker.com/engine/security/seccomp/)
- [gVisor security model — gVisor docs](https://gvisor.dev/docs/architecture_guide/security/)
- [Firecracker: Lightweight Virtualization for Serverless Applications — NSDI 2020](https://www.usenix.org/conference/nsdi20/presentation/agache)
- [Firecracker design — GitHub](https://github.com/firecracker-microvm/firecracker/blob/main/docs/design.md)
