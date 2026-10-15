---
id: virt-pod-request-weights
title: CPU requests, shares and runtime weight mappings
level: advanced
minutes: 5
sourceLesson: virt-k8s-os-view
summary: Requests guide placement and become relative contention weights in the conventional native runtime path.
---

This unit focuses on CPU requests, shares and runtime weight mappings. It builds on the earlier virtualisation units in this module.

## Requests and limits become cgroup files

In the conventional kubelet-managed native Linux layout, a pod has a parent cgroup with container cgroups underneath. With the systemd cgroup driver (the recommended setting, and it must match between kubelet and runtime), the tree looks like this:

```
/sys/fs/cgroup/kubepods.slice/
  kubepods-pod<uid>.slice/   (Guaranteed)
  kubepods-burstable.slice/
    kubepods-burstable-pod<uid>.slice/
      cri-containerd-<id>.scope
  kubepods-besteffort.slice/
```

For the following container-level example, assume cgroup v2, CPU quota enforcement, a 100 ms quota period and no pod-level resource override:

```yaml
# Requests place work; limits bound usage.
resources:
  requests: {cpu: 250m, memory: 256Mi}
  limits:   {cpu: 500m, memory: 512Mi}
```

| Spec | cgroup v2 file | Value |
|---|---|---|
| cpu limit 500m | `cpu.max` | `50000 100000` |
| cpu request 250m | `cpu.weight` | relative share |
| memory limit | `memory.max` | `536870912` |
| memory request | scheduling/priority; optional protection | configuration dependent |

The memory value is just the limit in bytes. Kubernetes' `Mi` suffix is a power-of-two unit:

```formula
M_max = 512 Mi
M_max = 512 × 1024 × 1024 B
M_max = 536870912 B
where
M_max: the memory limit as written into memory.max
Mi: mebibyte (MiB), 1024 × 1024 = 1,048,576 bytes; Kubernetes writes it Mi
B: byte, eight bits
In words: 512Mi is 512 binary megabytes, which is 536,870,912 bytes.
```

### CPU request → weight

A CPU request is first converted to cgroup v1–style **CPU shares**, where 1024 shares meant one whole CPU:

```formula
S_raw = floor((1024 R_m) / 1000)
S = min(max(2, S_raw), 262144)
S = min(max(2, 256), 262144) = 256
where
S_raw: the request scaled into shares before the runtime bounds are applied (no unit)
S: the CPU shares value, clamped to the range 2–262,144 (no unit)
min: the smaller of its two inputs
max: the larger of its two inputs
R_m: the CPU request in millicores (m); 1000m = 1 CPU, so 250m is a quarter of a CPU
floor: round down to a whole number
In words: shares are the request scaled so that one full CPU is worth 1024; a 250m request gives 256 shares.
```

The shares are then converted to `cpu.weight` (range 1–10,000, default 100). Weights matter only under **CPU contention**. A sufficiently parallel container may exceed its request when allowed by limits, affinity and ancestors. Eligible competing sibling cgroups receive relative weight-based service; this is not a flat global split of every container on the node.

The shares-to-weight formula has changed over time. Older runc used a linear mapping that stretches the shares range 2–262,144 onto the weight range 1–10,000:

```formula
W_old = 1 + floor((9999(S − 2)) / 262142)
W_old = 1 + floor(1022 × 9999 / 262142)
W_old = 1 + 38 = 39
where
W_old: the cpu.weight the older linear mapping writes (no unit)
S: the CPU shares value, here 1024 (one CPU)
floor: round down to a whole number
In words: the linear mapping turns one CPU's worth of shares into weight 39, well below the default weight of 100.
```

The current upstream opencontainers/cgroups implementation uses a curve instead, chosen so that the minimum, default and maximum line up:

```formula
x = log_2(S)
y = (x^2 + 125x) / 612 − 7 / 34
W_new = ⌈10^y⌉
where
x: the base-2 logarithm of the shares value
S: the CPU shares value (2 to 262,144)
log_2: logarithm base 2: the power you raise 2 to in order to get the number; log_2(1024) = 10
y: an intermediate exponent (no unit)
W_new: the cpu.weight the curve writes (no unit)
⌈ ⌉: ceiling: round up to the next whole number
In words: the curve maps 2 shares to weight 1, 1024 shares (one CPU) to the default weight 100, and 262,144 shares to the maximum 10,000.
```

For one CPU (1024 shares):

```formula
x = log_2(1024) = 10
y = (100 + 1250) / 612 − 7 / 34 = 2
W_new = ⌈10^2⌉ = 100
where
x: the base-2 logarithm of 1024 shares
log_2: logarithm base 2; 2^10 = 1024
y: the exponent, here exactly 2
W_new: the resulting cpu.weight
⌈ ⌉: ceiling: round up to a whole number
In words: one CPU's worth of shares lands exactly on the default weight of 100 under the curve.
```

The deployed runc/library version determines whether that mapping is used. The curve preserves selected endpoints/defaults, not every ratio: actual weights and CPU-contention shares can change across implementations. Inspect cpu.weight on the deployed runtime instead of assuming a 2:1 request always becomes exactly a 2:1 weight.

## Key takeaways

- Requests guide placement and become relative contention weights in the conventional native runtime path.
- Weight mappings differ across library/runtime versions; inspect the effective cgroup files.

## Further reading

- [Pods — Kubernetes docs](https://kubernetes.io/docs/concepts/workloads/pods/)
- [Resource management for pods and containers — Kubernetes docs](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/)
- [About cgroup v2 — Kubernetes docs](https://kubernetes.io/docs/concepts/architecture/cgroups/)
- [Pod Quality of Service classes — Kubernetes docs](https://kubernetes.io/docs/concepts/workloads/pods/pod-qos/)
- [Node-pressure eviction — Kubernetes docs](https://kubernetes.io/docs/concepts/scheduling-eviction/node-pressure-eviction/)
- [Pod Security Standards — Kubernetes docs](https://kubernetes.io/docs/concepts/security/pod-security-standards/)
- [Runtime Class — Kubernetes docs](https://kubernetes.io/docs/concepts/containers/runtime-class/)
