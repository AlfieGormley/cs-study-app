---
id: arch-pod-readiness-rollout-draining
title: Keeping traffic safe during pod replacement
level: basic
minutes: 3
summary: Connect Kubernetes routing, probes, rollout limits and graceful shutdown to instance replacement.
sourceLesson: arch-stateless-web-tier
---

The earlier units made instances disposable and identified capacity limits. Kubernetes must now replace those instances while routing traffic and finishing work safely.

## Kubernetes basics

Running hundreds of containers by hand isn't feasible. **Kubernetes** is an orchestrator: you declare the state you want, and its controllers continuously work to make reality match.

The core objects:

- **Pod**: the smallest unit, one or more containers that share a network namespace and are scheduled together.
- **Kubernetes Deployment**: "keep 10 replicas of this pod template running"; it handles rolling updates and rollbacks.
- **Service**: a normal ClusterIP Service provides a stable virtual IP and DNS name for matching endpoints. Headless and ExternalName Services behave differently.
- **Ingress / Gateway**: routes external HTTP traffic to Services.
- **HorizontalPodAutoscaler (HPA)**: adjusts a Kubernetes Deployment's replica count from metrics such as CPU.
- **Probes**: readiness contributes to endpoint eligibility for normal Service traffic; a liveness failure reaching its threshold can restart the failing container under its restart policy.

```
 Ingress
    |
 Service "web"  (stable DNS)
    |
 +--+-----+------+
 |        |      |
Pod      Pod    Pod   <- Deployment
                         replicas: 3
                       <- HPA: 3..20
```

> [!example] A rolling deploy
> A Kubernetes Deployment has 10 replicas with `maxUnavailable: 1` and `maxSurge: 2`. The controller allows up to 2 extra non-terminating pods and can reduce available capacity to 9 during normal rollout; it need not wait for both new pods before removing any old pod. Terminating pods can temporarily make the total higher. This aims to maintain availability, but statelessness and schema compatibility alone do not guarantee invisible updates: APIs, sessions, capacity and draining must also remain compatible.

## Graceful shutdown

Stateless doesn't mean you can kill a pod mid-request. When Kubernetes terminates a pod, two paths proceed **in parallel**: the kubelet runs any `preStop` hook and then sends the stop signal (normally `SIGTERM`), while the control plane marks the terminating endpoint not ready for normal Service traffic. Load balancers and every node's kube-proxy take a moment to notice that removal, so new requests can keep arriving during the propagation delay, including after SIGTERM; there is no universal one- or two-second bound.

A well-behaved server therefore:

1. Keeps serving while termination begins and endpoint readiness changes propagate. A `preStop` hook may provide a short delay **before** `SIGTERM`; the hook and subsequent draining share the termination grace period.
2. Stops accepting new connections and fails its readiness probe.
3. Finishes in-flight requests, within the grace period (`terminationGracePeriodSeconds`, 30 s by default, after which it gets `SIGKILL`).
4. Exits.

A server that exits the instant it receives `SIGTERM` drops the requests that were still on their way to it, which shows up as a handful of connection resets on every deploy.

Long-lived connections (WebSockets, streaming) need extra care: clients must be able to reconnect to another instance and resume.

## Key takeaways
- A normal Service routes to eligible endpoints while a Kubernetes Deployment replaces pod replicas.
- Readiness controls normal traffic eligibility; a liveness failure can restart the container.
- Rolling-update limits allow surplus and unavailable capacity within configured bounds.
- Endpoint changes and shutdown proceed concurrently: allow propagation and drain in-flight work within the grace period.

## Further reading
- [Kubernetes: Overview](https://kubernetes.io/docs/concepts/overview/)
- [Kubernetes: Deployments](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)
- [Kubernetes: Service](https://kubernetes.io/docs/concepts/services-networking/service/)
