---
id: virt-capability-sets
title: Capability sets and permanent no-new-privileges
level: advanced
minutes: 5
sourceLesson: virt-isolation-security
summary: Capabilities are scoped powers with several interacting per-thread sets.
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

Traditional Unix gives UID 0 broad discretionary privileges. Additional policies can still restrict it. Linux splits many of those powers into about 40 **capabilities** (41 on kernels since 5.9, numbered 0 to 40). The kernel checks the relevant capability, not the UID, before a privileged action.

| Capability | Grants |
|---|---|
| `CAP_NET_BIND_SERVICE` | Bind below configured privileged-port threshold |
| `CAP_NET_ADMIN` | Routes, iptables, interfaces |
| `CAP_SYS_PTRACE` | Trace other processes |
| `CAP_SYS_MODULE` | Load kernel modules |
| `CAP_SYS_ADMIN` | Mounts, namespaces, much more |

`CAP_SYS_ADMIN` is often called "the new root". It covers so many operations that granting it gives away most of what capabilities were meant to protect.

Each thread has several capability sets. **effective capability set** is what the kernel checks right now. **permitted capability set** is the most the thread can raise effective to. **bounding capability set** limits file-permitted capability gains on exec and additions to the inheritable set; it is not an absolute mask on all current or inheritable capability paths. Runtimes must configure permitted, effective, inheritable, ambient and bounding sets consistently. New user namespaces also have their own capability scope.

The Moby default list retrieved for this review contains 14 capabilities, including `CHOWN`, `DAC_OVERRIDE`, `SETUID`, `SETGID`, `NET_BIND_SERVICE`, `NET_RAW`, `KILL` and `SYS_CHROOT`. It drops everything else, including `SYS_ADMIN`, `SYS_MODULE`, `NET_ADMIN` and `SYS_PTRACE`. You can see the result in `/proc/self/status`:

```
CapEff: 00000000a80425fb
```

That is a bit mask written in hexadecimal. Every capability has a fixed number (CHOWN is 0, SYS_ADMIN is 21), and each capability number selects the correspondingly numbered bit:

```formula
M = Σ 2^c   for all c in C
where
M: the capability mask the kernel prints after CapEff, a 64-bit number shown in hexadecimal (base 16)
C: the set of capability numbers the thread currently holds in its effective set
c: one capability number, from 0 (CHOWN) up to 40 (CHECKPOINT_RESTORE) on kernels since 5.9
Σ: sigma, the summation sign: add up the term after it once for every c in C
2^c: 2 raised to the power c, the value of bit c on its own; for example 2^21 = 2,097,152 = 0x200000
In words: each capability is one bit; the mask is the sum of those bits' values, so bit c is 1 exactly when capability c is held.
```

For example, the Docker default above has bits 0, 1, 3–8, 10, 13, 18, 27, 29 and 31 set: 14 bits, so 14 capabilities. Bit 21 (SYS_ADMIN, worth 0x200000) is not set. This Python decodes any mask the same way:

```python
# Names for the bits used in this example.
NAMES = {0: "CHOWN", 1: "DAC_OVERRIDE",
         3: "FOWNER", 4: "FSETID",
         5: "KILL", 6: "SETGID",
         7: "SETUID", 8: "SETPCAP",
         10: "NET_BIND_SERVICE",
         13: "NET_RAW", 18: "SYS_CHROOT",
         21: "SYS_ADMIN", 27: "MKNOD",
         29: "AUDIT_WRITE", 31: "SETFCAP"}

def decode(hexmask):
    # Decode the kernel hexadecimal string.
    m = int(hexmask, 16)
    # Keep only names whose bit is set.
    return [NAMES.get(b, f"cap{b}")
            for b in range(64)
            if m >> b & 1]


# Count effective powers and test bit 21.
print(len(decode("a80425fb")))   # 14
print("SYS_ADMIN" in
      decode("a80425fb"))        # False
```

The best practice is `--cap-drop=ALL`, then add back only what the app needs. Most web services need nothing. Binding port 80 needs NET_BIND_SERVICE only when that port is below the network namespace's ip_unprivileged_port_start threshold. Some runtimes lower the threshold; check it before adding a capability.

### no_new_privs

A setuid-root binary such as `sudo` normally gains privileges when executed. `prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0)` prevents exec from granting new privileges for a process and all its descendants, permanently. Docker's `--security-opt no-new-privileges` and Kubernetes' `allowPrivilegeEscalation: false` set it. It also lets an unprivileged process install a seccomp filter, since it can no longer use a setuid binary to trick a filtered program.

## Key takeaways

- Capabilities are scoped powers with several interacting per-thread sets.
- no_new_privs prevents exec-based privilege gains and is inherited permanently.

## Further reading

- [capabilities(7) — Linux manual page](https://man7.org/linux/man-pages/man7/capabilities.7.html)
- [Seccomp BPF — Linux kernel documentation](https://docs.kernel.org/userspace-api/seccomp_filter.html)
- [Seccomp security profiles for Docker — Docker docs](https://docs.docker.com/engine/security/seccomp/)
- [gVisor security model — gVisor docs](https://gvisor.dev/docs/architecture_guide/security/)
- [Firecracker: Lightweight Virtualization for Serverless Applications — NSDI 2020](https://www.usenix.org/conference/nsdi20/presentation/agache)
- [Firecracker design — GitHub](https://github.com/firecracker-microvm/firecracker/blob/main/docs/design.md)
