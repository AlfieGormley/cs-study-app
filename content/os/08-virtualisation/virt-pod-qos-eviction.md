---
id: virt-pod-qos-eviction
title: QoS scores and node-pressure eviction
level: advanced
minutes: 3
sourceLesson: virt-k8s-os-view
summary: Ordinary QoS rules bias kernel OOM selection, but do not impose a universal victim order.
---

This unit focuses on QoS scores and node-pressure eviction. It builds on the earlier virtualisation units in this module.

## QoS classes and who dies first

For ordinary Linux pods using container-level CPU/memory resources, the following summary applies. Pod-level resource specifications and critical-pod exceptions require additional rules:

| Class | Rule | `oom_score_adj` |
|---|---|---|
| Guaranteed | requests equal limits, CPU and memory, every container | −997 |
| Burstable | anything in between | 3 to 999 |
| BestEffort | no CPU/memory requests or limits | 1000 |

For a non-critical Burstable container without pod-level resource adjustments, the kubelet sets the adjustment from the share of node memory the container requests. The more memory it reserves, the lower (safer) its score:

```formula
A = 1000 − floor((1000 M_req) / M_node)
A_set = min(max(3, A), 999)
where
A: the raw oom_score_adj before clamping (no unit); the kernel's range is −1000 to 1000
M_req: the container's memory request, in bytes (or any unit, as long as both use the same one)
M_node: the node's memory capacity, in the same unit
A_set: the value actually written, clamped to 3–999; the kubelet computes the floor as 1000 + (−997) = 3
max: the larger of its inputs
min: the smaller of its inputs
floor: round down to the nearest integer
In words: subtract the requested fraction of node memory, scaled to 1000, from 1000, then keep the result between 3 and 999 so this adjustment lies between the ordinary Guaranteed and BestEffort adjustments. Actual OOM ranking also depends on memory use and eligibility.
```

A container requesting a quarter of node memory capacity gets an adjustment of 750, and one requesting one per cent gets 990. The kubelet rounds the scaled requested share down before subtracting. The retrieved kubelet source (`pkg/kubelet/qos/policy.go`) clamps this ordinary Burstable case to at least 3. Read the deployed source when checking documentation examples or special pod cases.

Two separate mechanisms use these values:

1. **Node-pressure eviction** (kubelet). When `memory.available` drops below the hard threshold (100Mi by default on Linux), the kubelet terminates pods to reclaim memory. It ranks them first by whether their usage exceeds their requests, then by Pod priority, then by how far usage exceeds requests. Hard-pressure eviction uses no termination grace period. A controller may create a replacement pod; the original pod is not moved or rescheduled as the same object. Soft-threshold grace settings differ.
2. **Kernel OOM killer** (node-wide). If memory runs out before the kubelet reacts, the kernel picks a victim by usage plus `oom_score_adj`. These adjustments bias victim selection; actual memory use, eligible scope and other factors matter. QoS class alone is not a strict universal kill ordering or a promise that a Guaranteed workload survives.

## Key takeaways

- Ordinary QoS rules bias kernel OOM selection, but do not impose a universal victim order.
- Kubelet pressure eviction is a separate mechanism with its own ranking and grace rules.

## Further reading

- [Pods — Kubernetes docs](https://kubernetes.io/docs/concepts/workloads/pods/)
- [Resource management for pods and containers — Kubernetes docs](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/)
- [About cgroup v2 — Kubernetes docs](https://kubernetes.io/docs/concepts/architecture/cgroups/)
- [Pod Quality of Service classes — Kubernetes docs](https://kubernetes.io/docs/concepts/workloads/pods/pod-qos/)
- [Node-pressure eviction — Kubernetes docs](https://kubernetes.io/docs/concepts/scheduling-eviction/node-pressure-eviction/)
- [Pod Security Standards — Kubernetes docs](https://kubernetes.io/docs/concepts/security/pod-security-standards/)
- [Runtime Class — Kubernetes docs](https://kubernetes.io/docs/concepts/containers/runtime-class/)
