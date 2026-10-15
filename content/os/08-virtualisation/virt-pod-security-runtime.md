---
id: virt-pod-security-runtime
title: Security contexts, admission and RuntimeClass
level: advanced
minutes: 3
sourceLesson: virt-k8s-os-view
summary: SecurityContext configures several kernel controls; admission checks the selected policy version.
---

This unit focuses on security contexts, admission and RuntimeClass. It builds on the earlier virtualisation units in this module.

## Security contexts and admission

This is a container-level securityContext fragment; hostUsers belongs at pod spec level, while some fields can also be inherited from pod-level securityContext.

```yaml
# Independent controls reinforce each other.
securityContext:
  runAsNonRoot: true
  runAsUser: 10001
  allowPrivilegeEscalation: false
  readOnlyRootFilesystem: true
  capabilities: {drop: ["ALL"]}
  seccompProfile: {type: RuntimeDefault}
```

| Field | Kernel mechanism |
|---|---|
| `runAsUser` | `setuid()` before exec |
| `allowPrivilegeEscalation: false` | `no_new_privs` |
| `capabilities.drop` | runtime capability-set configuration |
| `seccompProfile` | seccomp-bpf filter |
| `readOnlyRootFilesystem` | root mounted read-only |
| `privileged: true` | broad runtime privilege relaxation |
| pod `spec.hostUsers: false` | user namespace |

Writing this into every pod is error-prone, so Kubernetes has **Pod Security Admission**. You label a Kubernetes namespace with `pod-security.kubernetes.io/enforce=restricted`, and the API server rejects pods that do not meet the **Restricted Pod Security Standard**. For ordinary Linux host-user-namespace pods, the selected Restricted policy version requires running as non-root, dropping ALL capabilities (only `NET_BIND_SERVICE` may be added back), `allowPrivilegeEscalation: false` and a RuntimeDefault or Localhost seccomp profile. The **baseline standard** blocks the worst options, such as privileged containers, host namespaces and `hostPath`.

## RuntimeClass: choosing the boundary per pod

Sometimes the shared kernel is not enough. A **RuntimeClass** maps a name to a CRI runtime handler configured in containerd. The first YAML document below defines the class; the second is only the relevant pod-spec fragment, not a complete Pod object:

```yaml
# The node must already have this handler.
apiVersion: node.k8s.io/v1
kind: RuntimeClass
metadata: {name: gvisor}
handler: runsc
---
spec:
  runtimeClassName: gvisor
```

With the handler installed, configured and supported on the selected node, the pod can use a gVisor sandbox (`runsc`) or a Kata microVM (`kata`) instead of runc. The pod model survives, because in Kata the "pod sandbox" *is* the VM and the containers run inside it. RuntimeClass can also declare `overhead`, so the scheduler accounts for the VM's extra memory and CPU.

## Pitfalls

- **CPU limits on latency-sensitive services** cause throttling at low average utilisation. Watch `nr_throttled`.
- **No container memory limit** can allow growth until other constraints apply. Pod/ancestor limits, admission defaults and node policy may still constrain it; inspect the effective configuration rather than predicting a guaranteed failure.
- **Mismatched cgroup drivers** (kubelet on systemd, runtime on cgroupfs) give two managers of one tree and unstable nodes.
- **Thinking `localhost` is private.** Every container in a pod shares one network namespace, so any of them can reach the others' ports.
- **`hostPath`, `hostNetwork` and `hostPID`** expose selected host resources or share specific namespaces; they do not remove every namespace or security control. Reserve them for node agents.

> [!note] Deployment gaps
> This lesson was source-checked and its arithmetic model executed, but no Kubernetes cluster was created. Runtime-specific namespace layouts, admission exceptions, QoS feature gates and cgroup files must be checked on the deployed version. Exact latency and OOM outcomes are not guaranteed by the examples.

## Key takeaways

- SecurityContext configures several kernel controls; admission checks the selected policy version.
- RuntimeClass selects a preconfigured supported handler and may declare sandbox overhead.

## Further reading

- [Pods — Kubernetes docs](https://kubernetes.io/docs/concepts/workloads/pods/)
- [Resource management for pods and containers — Kubernetes docs](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/)
- [About cgroup v2 — Kubernetes docs](https://kubernetes.io/docs/concepts/architecture/cgroups/)
- [Pod Quality of Service classes — Kubernetes docs](https://kubernetes.io/docs/concepts/workloads/pods/pod-qos/)
- [Node-pressure eviction — Kubernetes docs](https://kubernetes.io/docs/concepts/scheduling-eviction/node-pressure-eviction/)
- [Pod Security Standards — Kubernetes docs](https://kubernetes.io/docs/concepts/security/pod-security-standards/)
- [Runtime Class — Kubernetes docs](https://kubernetes.io/docs/concepts/containers/runtime-class/)
