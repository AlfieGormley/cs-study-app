---
id: virt-seccomp-abi
title: Seccomp filters, pointer limits and syscall ABIs
level: advanced
minutes: 3
sourceLesson: virt-isolation-security
summary: Classic seccomp filters inspect numeric arguments and ABI identifiers, not pointed-to path strings.
---

This unit focuses on seccomp filters, pointer limits and syscall ABIs. It builds on the earlier virtualisation units in this module.

## seccomp: filtering system calls

Capabilities gate *privileged* operations. **seccomp** goes further and decides which system calls a process may make at all, and with which arguments.

In filter mode (seccomp-bpf), the process installs a small classic-BPF program. The kernel runs it on **every system call entry**. The program sees the syscall number, the architecture and the six raw argument registers, and it returns an action:

| Action | Effect |
|---|---|
| `ALLOW` | Run the syscall |
| `ERRNO` | Fail it with e.g. `EPERM` |
| `KILL_PROCESS` | Kill with `SIGSYS` |
| `TRAP` | Send `SIGSYS` to a handler |
| `USER_NOTIF` | Ask a supervisor process |
| `LOG` | Allow, but log it |

A libseccomp C fragment (supply errno/seccomp headers, link libseccomp and a fail helper that exits; successful load applies to the calling thread unless synchronisation is requested):

```c
/* Deny two calls; allow all others. */
scmp_filter_ctx ctx =
  seccomp_init(SCMP_ACT_ALLOW);
if (!ctx) fail("seccomp_init");
if (seccomp_rule_add(ctx,
      SCMP_ACT_ERRNO(EPERM),
      SCMP_SYS(keyctl), 0) < 0)
  fail("keyctl rule");
if (seccomp_rule_add(ctx,
      SCMP_ACT_ERRNO(EPERM),
      SCMP_SYS(kexec_load), 0) < 0)
  fail("kexec rule");
/* Installation persists after release. */
if (seccomp_load(ctx) < 0)
  fail("seccomp_load");
seccomp_release(ctx); /* filter remains */
```

That is a *denylist*: allow everything except the named calls. Docker's default profile is the opposite, an **allowlist** with a default action of `ERRNO`. The exact rules depend on runtime version, architecture and capabilities. The retrieved Moby profile restricts calls such as keyctl and namespace operations, with conditional allowances for some privileged operations. Inspect the deployed profile rather than assuming a fixed count or universal deny list.

Filters stack. A process can add more filters but never remove one, and every filter runs, with action precedence deciding the result (and defined rules for equal-precedence data). A filter applies per thread unless explicitly synchronised to other threads.

> [!warning] What seccomp cannot see
> Classic BPF filters see only register values. They cannot follow pointers, so they cannot inspect a path passed to `open()`. Even if they could, another thread could change the memory after the check (a TOCTOU race). Path-based policy belongs to an LSM. Filters must identify the syscall ABI. Checking arch distinguishes the i386 ABI from x86-64, but x32 uses AUDIT_ARCH_X86_64 too and marks syscall numbers with __X32_SYSCALL_BIT; arch alone is insufficient for that case.

Why bother, if the default profile allows most calls? Because many kernel exploits need a rarely used syscall. CVE-2022-0185 affected filesystem-context handling on vulnerable kernels. An unprivileged attacker could reach the required namespaced CAP_SYS_ADMIN through user namespaces where permitted; already-privileged callers did not need that exact route. A profile blocking the necessary calls can close this path. Kubernetes seccomp defaults and policy must be checked on the actual cluster.

## Key takeaways

- Classic seccomp filters inspect numeric arguments and ABI identifiers, not pointed-to path strings.
- Filter stacking can only restrict further; deployed allowlists and architecture rules must be checked.

## Further reading

- [capabilities(7) — Linux manual page](https://man7.org/linux/man-pages/man7/capabilities.7.html)
- [Seccomp BPF — Linux kernel documentation](https://docs.kernel.org/userspace-api/seccomp_filter.html)
- [Seccomp security profiles for Docker — Docker docs](https://docs.docker.com/engine/security/seccomp/)
- [gVisor security model — gVisor docs](https://gvisor.dev/docs/architecture_guide/security/)
- [Firecracker: Lightweight Virtualization for Serverless Applications — NSDI 2020](https://www.usenix.org/conference/nsdi20/presentation/agache)
- [Firecracker design — GitHub](https://github.com/firecracker-microvm/firecracker/blob/main/docs/design.md)
