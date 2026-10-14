---
id: arch-hpa-metric-stabilisation
title: Calculating and stabilising HPA capacity
level: basic
minutes: 3
summary: Trace the HPA replica formula and explain why readiness, tolerance and stabilisation affect its result.
sourceLesson: arch-stateless-web-tier
---

A Kubernetes Deployment sets a desired replica count. Its HorizontalPodAutoscaler adjusts that count from observed metrics; this unit works through the recommendation, rather than assuming scaling is instantaneous.

## HPA replica recommendations

For a CPU utilization target, percentages are relative to configured CPU requests, not a node's total capacity. The HPA's job is to pick a pod count that would bring the average metric back to the target. If 4 pods average 90% CPU and you want 60%, the same total work spread over more pods brings each one down. The simplified rule from the Kubernetes documentation is:

```formula
R_new = ⌈R × M / T⌉
where
R_new: the number of pod replicas the HPA will ask for
R: the number of pod replicas running now
M: the current average value of the metric across the pods, e.g. CPU at 90 % of each pod's CPU request
T: the target value you configured for that metric, e.g. 60 %
⌈ ⌉: ceiling: round up to the next whole number, because you can't run part of a pod
%: per cent of each pod's requested CPU
In words: scale the pod count by how far the metric is above or below target, then round up.
```

For this example, assume equal CPU requests and valid metrics for every pod. Missing metrics and not-yet-ready pods can alter the controller's recommendation.

For example, 4 pods averaging 90% CPU against a 60% target:

```formula
R_new = ⌈4 × 90 % / 60 %⌉
R_new = ⌈360 % / 60 %⌉ = ⌈6⌉
R_new = 6
where
R_new: the replica count (number of pods) the HPA asks for
⌈ ⌉: ceiling: round up to a whole number
%: per cent of each pod's CPU request
In words: 4 pods at 90 % carry 360 % of one pod's CPU request in total; spread over 6 pods that is 60 % each, exactly on target.
```

The rule assumes the load divides evenly across pods and stays the same while new pods start. In practice it is recalculated every few seconds (15 s by default), so the count converges over several steps.

The HPA also ignores small deviations (a default tolerance of about 10%) and, by default, uses the highest recent recommendation within a default 5-minute scale-down stabilisation window, so a brief dip doesn't remove pods you'll need again a minute later.

When the cluster itself runs out of room, a **cluster autoscaler** (or Karpenter, originally built by AWS) can provision nodes when suitable capacity is available and policy permits. Timing is workload/provider-dependent; quotas, capacity shortages and scheduling constraints can leave pods Pending.

## Key takeaways
- CPU utilisation targets use pod CPU requests as the denominator.
- The simplified HPA calculation scales the current count by current metric over target, then rounds up.
- Tolerance and scale-down stabilisation avoid reacting to small or short-lived changes.
- A recommendation is not ready capacity: node availability, quotas and scheduling can delay new pods.

## Further reading
- [Kubernetes: Horizontal Pod Autoscaling](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/)
