---
id: virt-isolation-security
title: Isolating containers
level: advanced
minutes: 14
summary: How capabilities, seccomp, LSMs and user namespaces shrink what a container can do to a shared kernel, and when to reach for gVisor or a Firecracker microVM instead.
---

Namespaces control what a container can **see**. Cgroups control how much it can **use**. These mechanisms provide real restrictions, but are not the whole security policy. Powerful actions depend on capability scope, namespaces and other checks; UID 0 in a child user namespace cannot simply load host modules or reboot the host.

Native Linux process containers share a host kernel. Its attack surface depends on kernel version, architecture and enabled interfaces. A reachable vulnerability can compromise that boundary; VM-backed runtimes use a different boundary. Container security is about shrinking that attack surface in layers. When the layers aren't enough, you put a second kernel in the way.

```
  possible defence layers
  |  plain process
  |  + namespaces, cgroups
  |  + caps, seccomp, LSM
  |  + user namespace
  |  gVisor (user-space kernel)
  |  microVM (Firecracker, Kata)
  v  assess threat model and workload
```

## Capabilities: splitting root

Traditional Unix has two kinds of process: UID 0 can do anything, and everyone else is checked. Linux splits root's power into about 40 **capabilities**. The kernel checks the relevant capability, not the UID, before a privileged action.

| Capability | Grants |
|---|---|
| `CAP_NET_BIND_SERVICE` | Bind below configured privileged-port threshold |
| `CAP_NET_ADMIN` | Routes, iptables, interfaces |
| `CAP_SYS_PTRACE` | Trace other processes |
| `CAP_SYS_MODULE` | Load kernel modules |
| `CAP_SYS_ADMIN` | Mounts, namespaces, much more |

`CAP_SYS_ADMIN` is often called "the new root". It covers so many operations that granting it gives away most of what capabilities were meant to protect.

Each thread has several capability sets. **Effective** is what the kernel checks right now. **Permitted** is the most the thread can raise effective to. **Bounding** limits file-permitted capability gains on exec and additions to the inheritable set; it is not an absolute mask on all current or inheritable capability paths. Runtimes must configure permitted, effective, inheritable, ambient and bounding sets consistently. New user namespaces also have their own capability scope.

The Moby default list retrieved for this review contains 14 capabilities, including `CHOWN`, `DAC_OVERRIDE`, `SETUID`, `SETGID`, `NET_BIND_SERVICE`, `NET_RAW`, `KILL` and `SYS_CHROOT`. It drops everything else, including `SYS_ADMIN`, `SYS_MODULE`, `NET_ADMIN` and `SYS_PTRACE`. You can see the result in `/proc/self/status`:

```
CapEff: 00000000a80425fb
```

That is a bitmask, with bit *n* standing for capability number *n*. This Python decodes it:

```
NAMES = {0: "CHOWN", 1: "DAC_OVERRIDE",
         3: "FOWNER", 4: "FSETID",
         5: "KILL", 6: "SETGID",
         7: "SETUID", 8: "SETPCAP",
         10: "NET_BIND_SERVICE",
         13: "NET_RAW", 18: "SYS_CHROOT",
         21: "SYS_ADMIN", 27: "MKNOD",
         29: "AUDIT_WRITE", 31: "SETFCAP"}

def decode(hexmask):
    m = int(hexmask, 16)
    return [NAMES.get(b, f"cap{b}")
            for b in range(64)
            if m >> b & 1]

print(len(decode("a80425fb")))   # 14
print("SYS_ADMIN" in
      decode("a80425fb"))        # False
```

The best practice is `--cap-drop=ALL`, then add back only what the app needs. Most web services need nothing. Binding port 80 needs NET_BIND_SERVICE only when that port is below the network namespace's ip_unprivileged_port_start threshold. Some runtimes lower the threshold; check it before adding a capability.

### no_new_privs

A setuid-root binary such as `sudo` normally gains privileges when executed. `prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0)` prevents exec from granting new privileges for a process and all its descendants, permanently. Docker's `--security-opt no-new-privileges` and Kubernetes' `allowPrivilegeEscalation: false` set it. It also lets an unprivileged process install a seccomp filter, since it can no longer use a setuid binary to trick a filtered program.

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

```
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
if (seccomp_load(ctx) < 0)
  fail("seccomp_load");
seccomp_release(ctx); /* filter remains */
```

That is a *denylist*: allow everything except the named calls. Docker's default profile is the opposite, an **allowlist** with a default action of `ERRNO`. The exact rules depend on runtime version, architecture and capabilities. The retrieved Moby profile restricts calls such as keyctl and namespace operations, with conditional allowances for some privileged operations. Inspect the deployed profile rather than assuming a fixed count or universal deny list.

Filters stack. A process can add more filters but never remove one, and every filter runs, with action precedence deciding the result (and defined rules for equal-precedence data). A filter applies per thread unless explicitly synchronised to other threads.

> [!warning] What seccomp cannot see
> BPF filters see only register values. They cannot follow pointers, so they cannot inspect a path passed to `open()`. Even if they could, another thread could change the memory after the check (a TOCTOU race). Path-based policy belongs to an LSM. Filters must identify the syscall ABI. Checking arch distinguishes i386 from x86-64, but x32 uses AUDIT_ARCH_X86_64 too and marks syscall numbers with __X32_SYSCALL_BIT; arch alone is insufficient for that case.

Why bother, if the default profile allows most calls? Because many kernel exploits need a rarely used syscall. CVE-2022-0185 affected filesystem-context handling on vulnerable kernels. An unprivileged attacker could reach the required namespaced CAP_SYS_ADMIN through user namespaces where permitted; already-privileged callers did not need that exact route. A profile blocking the necessary calls can close this path. Kubernetes seccomp defaults and policy must be checked on the actual cluster.

## LSMs: AppArmor and SELinux

Linux Security Modules add **mandatory access control** checks inside the kernel, on objects such as files, sockets and mounts, using path names or labels.

- **AppArmor** (Ubuntu, Debian) uses path-based profiles. Docker loads `docker-default`, which denies writes to most of `/proc/sys`, `/sys` and mounting.
- **SELinux** policies use labels such as container_t and MCS categories to constrain permitted access. Actual domains, shared labels, categories and enforcement depend on runtime/policy configuration; containers do not invariably receive distinct categories.

An enforcing LSM policy can deny file access even when a pathname becomes reachable. DAC permissions and credentials also matter; merely enabling an LSM does not prove a particular file is denied.

## User namespaces: root that isn't

In a user namespace, UID 0 inside the container maps to an unprivileged UID range on the host, say 100000–165535. New user namespaces initially grant capabilities scoped to that user namespace, but runtimes may drop them. Container UID 0 in this example maps to host UID 100000. A mount-visibility escape alone does not grant host-root credentials; a kernel exploit can defeat more than mount isolation.

This is the foundation of **rootless** Podman and Docker. Kubernetes supports it per pod with `hostUsers: false`. The feature is stable as of Kubernetes 1.36.

The trade-off is that user namespaces let unprivileged code reach kernel code that was previously root-only, such as mounting some file systems or creating network devices. Several kernel CVEs have been reachable only this way, which is why some distributions restrict unprivileged user namespace creation.

## When the shared kernel is the problem

All of the above filters requests to the **host kernel**. A reachable kernel flaw can bypass important protections. Dirty Pipe (CVE-2022-0847) enabled constrained modification of readable file-backed page-cache data on vulnerable kernels, including read-only files; exploitability depended on reachable files and calls. No profile is required to allow splice, and the flaw did not mean every process could overwrite arbitrary host files.

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

### Firecracker: microVMs

Firecracker (AWS, written in Rust) is a KVM-based virtual machine monitor stripped down to almost nothing. It offers virtio-net, virtio-block, virtio-vsock, a serial console and a partial keyboard controller (used only to reset the VM). There is no BIOS, no PCI bus by default and no USB or GPU emulation.

Firecracker publishes configuration-specific targets: at most 125 ms from InstanceStart to guest /sbin/init and at most 5 MiB VMM overhead under its documented small-VM, tuned-kernel host conditions. These exclude guest RAM and have workload/configuration caveats; they are not universal end-to-end launch figures or capacity guarantees. The project documents use in Lambda and Fargate. A guest kernel remains behind a virtualisation boundary.

Defence in depth continues outside the VM. For a hardened deployment, the **jailer** sets up host-side restrictions such as chroot, namespaces, cgroups and reduced privileges; Firecracker applies its thread-specific seccomp filters. The jailer limits the VMM's host privileges; the outcome of any escape depends on the vulnerability and deployment. A guest-kernel compromise alone is not the same as executing host VMM code.

**Kata Containers** brings the same model to Kubernetes. Each pod runs in a lightweight VM (QEMU, Cloud Hypervisor or Firecracker), with an agent inside it creating ordinary containers. The trade-offs are higher memory per pod, slower start than runc, and harder device and file-sharing paths.

## Choosing a level

| Option | Boundary | Cost |
|---|---|---|
| runc + defaults | Shared kernel, filtered | Workload dependent |
| + rootless/userns | Scoped host identity | Configuration dependent |
| gVisor | User-space kernel | Syscall overhead |
| Firecracker/Kata | Guest kernel + hardware support | Guest/VMM resources |

Your own trusted services in a single-tenant cluster are well served by hardened runc. Anything that runs code you did not write, for tenants who may be hostile, deserves a sandbox or a microVM.

## Pitfalls

- **`--privileged`**, in ordinary rootful Docker, grants broad capabilities/device access and relaxes normal seccomp and LSM restrictions. Rootless/namespace scope and host configuration still matter. A privileged container can mount the host disk and is effectively root on the host.
- **Adding `SYS_ADMIN` to fix one error** undoes most of the hardening. Find the specific capability or syscall instead.
- **Unconfined seccomp in Kubernetes.** Set `RuntimeDefault` in every pod, or enable the kubelet's `seccompDefault` option.
- **Host mounts.** Sensitive host paths or daemon sockets can undermine isolation by exposing data or authority. They do not literally disable every remaining credential, seccomp or LSM check.
- **Unpatched kernels.** Container hardening reduces exposure, but kernel updates are still the main defence for shared-kernel isolation.

## Key takeaways

- Containers share one kernel; isolation means shrinking the kernel surface a container can reach.
- Capabilities split root; the retrieved Moby default list has 14 capabilities; drop ALL and add back the minimum, and never hand out `SYS_ADMIN` lightly.
- seccomp-bpf filters syscalls by number and raw arguments, cannot inspect pointers, and must check the architecture; deployed allowlist contents vary with version and capabilities.
- LSMs (AppArmor, SELinux) enforce path and label policy; user namespaces make container root an unprivileged host user.
- Kernel and runtime bugs defeat filters, so hostile multi-tenant code needs a second kernel: gVisor's user-space Sentry or a Firecracker/Kata microVM.

> [!note] Verification limits
> The historical vulnerabilities are source-checked examples, not exploits run during this review. No live gVisor, Firecracker or Kata isolation/performance experiment was performed. Published Firecracker targets are scoped above; no universal sandbox ranking, escape guarantee or launch-rate estimate is supported here.

## Further reading

- [capabilities(7) — Linux manual page](https://man7.org/linux/man-pages/man7/capabilities.7.html)
- [Seccomp BPF — Linux kernel documentation](https://docs.kernel.org/userspace-api/seccomp_filter.html)
- [Seccomp security profiles for Docker — Docker docs](https://docs.docker.com/engine/security/seccomp/)
- [gVisor security model — gVisor docs](https://gvisor.dev/docs/architecture_guide/security/)
- [Firecracker: Lightweight Virtualization for Serverless Applications — NSDI 2020](https://www.usenix.org/conference/nsdi20/presentation/agache)
- [Firecracker design — GitHub](https://github.com/firecracker-microvm/firecracker/blob/main/docs/design.md)
