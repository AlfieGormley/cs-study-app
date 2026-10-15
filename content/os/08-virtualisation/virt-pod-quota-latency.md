---
id: virt-pod-quota-latency
title: CPU limits and burst-driven latency
level: advanced
minutes: 4
sourceLesson: virt-k8s-os-view
summary: CPU quota adds up execution across all runnable threads.
---

This unit focuses on CPU limits and burst-driven latency. It builds on the earlier virtualisation units in this module.

## CPU limit → quota and throttling

A CPU limit becomes CFS bandwidth control. The `cpu.max` value `50000 100000` means 50 ms of CPU time per 100 ms period, summed across **all threads** in the cgroup. Runnable fair-class tasks are throttled when the applicable budget is exhausted. Periods, runtime slices, burst configuration and ancestor quotas affect observed timing.

One possible latency cause is quota exhaustion. In an idealised case with four continuously running threads on four available CPUs, no burst credit and no tighter ancestor limit:

```formula
t_wall = Q / N
t_wall = 50 ms / 4 = 12.5 ms
t_thr = P − t_wall
t_thr = 100 ms − 12.5 ms = 87.5 ms
where
t_wall: wall-clock time from the start of a period until the quota is used up, in milliseconds (ms)
Q: the quota: CPU time the cgroup may use per period, here 50 ms (a 500m limit)
N: threads busy at the same time, each on its own CPU, here 4
t_thr: how long the whole cgroup is then throttled, in ms
P: the quota period, here 100 ms
ms: millisecond, one thousandth of a second
In words: four threads burn a 50 ms budget in 12.5 ms of real time, then every thread in the cgroup waits 87.5 ms for the next period.
```

A request arriving just after the quota runs out waits up to 87.5 ms, even when its average over a longer, partly idle measurement interval is below the limit. `cpu.stat` exposes this as `nr_throttled` and `throttled_usec`. The usual fixes are to raise or remove CPU limits (keeping requests), or to size thread pools to the limit. Runtime parallelism settings and container-aware resource detection can help avoid excessive runnable work; their purpose and behavior extend beyond quota throttling.

The quota itself comes from the limit in the same way the shares come from the request. Kubernetes writes a minimum quota of 1 ms:

```formula
Q = max(1000, floor((L_m P) / 1000))
Q = floor(500 × 100000 / 1000) µs
Q = 50000 µs
where
Q: the quota written as the first number of cpu.max, in microseconds (µs)
L_m: the CPU limit in millicores (m); 500m is half a CPU
P: the quota period, here 100000 µs (100 ms)
max: the larger of its two inputs; here it enforces a 1000 µs (1 ms) minimum
floor: round down to a whole number
µs: microsecond, one millionth of a second
In words: the quota is the limit's fraction of a CPU times the period, so a 500m limit allows 50 ms of CPU time in every 100 ms period.
```

A simplified model of the ordinary quota/share conversion as code (integer millicores; excludes feature flags, pod budgets and special policies):

```python
# All returned cpu.max times are in µs.
PERIOD = 100_000  # microseconds

def cpu_max(limit_m):
    if limit_m is None:
        return f"max {PERIOD}"
    if limit_m <= 0:
        raise ValueError("positive limit")
    # Scale and enforce the minimum.
    quota = max(1000,
                limit_m * PERIOD // 1000)
    return f"{quota} {PERIOD}"

def shares(request_m):
    if request_m < 0:
        raise ValueError("negative request")
    # Clamp shares to the supported range.
    return min(262144,
        max(2, request_m * 1024 // 1000))


# Half/two CPUs and no hard CPU quota.
print(cpu_max(500))    # 50000 100000
print(cpu_max(2000))   # 200000 100000
print(cpu_max(None))   # max 100000
print(shares(250))     # 256
```

A 2-CPU limit (2000m) gives a quota of 200,000 µs (200 ms), larger than the 100 ms period. That's allowed, because the quota is summed across CPUs.

## Key takeaways

- CPU quota adds up execution across all runnable threads.
- Low long-term average CPU use does not rule out short periods of quota exhaustion.

## Further reading

- [Pods — Kubernetes docs](https://kubernetes.io/docs/concepts/workloads/pods/)
- [Resource management for pods and containers — Kubernetes docs](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/)
- [About cgroup v2 — Kubernetes docs](https://kubernetes.io/docs/concepts/architecture/cgroups/)
- [Pod Quality of Service classes — Kubernetes docs](https://kubernetes.io/docs/concepts/workloads/pods/pod-qos/)
- [Node-pressure eviction — Kubernetes docs](https://kubernetes.io/docs/concepts/scheduling-eviction/node-pressure-eviction/)
- [Pod Security Standards — Kubernetes docs](https://kubernetes.io/docs/concepts/security/pod-security-standards/)
- [Runtime Class — Kubernetes docs](https://kubernetes.io/docs/concepts/containers/runtime-class/)
