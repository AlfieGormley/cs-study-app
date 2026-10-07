---
id: arch-stateless-web-tier
title: Stateless services and scaling the web tier
level: basic
minutes: 12
summary: Why stateless application servers are the foundation of horizontal scaling, where session state goes instead, and how autoscaling, containers and Kubernetes fit together.
---

A common way to scale an application tier is **adding instances behind a load balancer**. Making requests independent of any particular instance simplifies this; stateful systems can also scale through partitioning or replication. That property is called being **stateless**, and most large web architectures are built around it.

## What "stateless" really means

A stateless application tier does not rely on **instance-local client state surviving until a later request**. Rebuildable caches and per-request working memory are compatible with this design. Everything a request needs either arrives with the request or is fetched from a shared store.

```
          +---------------+
 users -->| load balancer |
          +--+----+----+--+
             |    |    |
           [A]  [B]  [C]   app servers
             \    |    /    (no local state)
          +---+---+---+---+
          | Redis  |  DB  |  shared state
          +--------+------+
```

It does **not** mean the system has no state. The state has been pushed down into a tier that's designed to hold it (a database, a cache cluster, object storage), so the app tier becomes disposable.

What you get from that:

- **Horizontal scaling.** More instances can increase capacity when requests distribute well and shared dependencies have headroom; scaling is not automatically linear.
- **Easy failure handling.** If server B dies, the load balancer stops sending it traffic. Durable external state remains available under its own guarantees, but in-flight requests, connections and uncommitted work can be lost.
- **Simple deploys.** Rolling updates replace servers one by one; no user is pinned to an old box.
- **Autoscaling.** Servers can be added and removed automatically because none of them is special.

The Twelve-Factor App calls this "execute the app as one or more stateless processes": anything that must persist goes into a backing service.

## Where session state goes

Users still log in and have shopping baskets. There are three common places for that state.

### 1. Sticky sessions (avoid as the main strategy)

The load balancer pins each user to one server (via a cookie or IP hash), and the session lives in that server's memory.

- Load spreads unevenly: a few heavy users can overload one box.
- When the server dies or is redeployed, its users lose their sessions.
- Scaling in is painful because you have to drain long-lived sessions.

Sticky sessions are sometimes used as a *performance optimisation* (to keep a warm local cache) on top of a design that still works without them.

### 2. A shared session store

The server stores a random session ID in a cookie, and the session data in Redis or Memcached keyed by that ID.

- Any server can serve any request with a lookup whose latency depends on topology, load and the store.
- The session store must itself be highly available (Redis with replicas, or a managed service).
- Deleting the session prevents future authorizations only once all relevant checks observe the deletion; caches, replicas, failover and already-authorized requests affect cut-off.

### 3. Client-side tokens

The state goes into a signed token the client sends with every request, such as a JWT or a signed cookie.

- Verification can be local if the server already has trusted keys and policy. Signature checking must be accompanied by issuer, audience, expiry and application-specific authorization checks.
- Tokens can't easily be revoked before they expire, so keep them short-lived (say 15 minutes) with a refresh token.
- Every request carries the token, so keep it small (a few hundred bytes, not your whole basket).

| Approach | Lookup cost | Revocation | Failure risk |
|---|---|---|---|
| Sticky | none | easy | lose sessions |
| Redis store | Store lookup | Depends on observation/consistency | Store outage or lost state |
| JWT | verify sig | hard | key leak |

> [!tip] Files are state too
> Uploaded files written to `/tmp` on one server are invisible to the others. Send uploads straight to object storage (S3, GCS) instead, ideally via presigned URLs so they don't pass through the app tier at all.

> [!note] Evidence gap
> Fixed session-lookup and VM/container startup timings are omitted: this project has no measured deployment establishing them. Use application readiness measurements and load tests for capacity planning.

## Autoscaling

With stateless servers you can let a controller adjust the count to match load. Typical signals:

- **CPU utilisation**: simple and widely used; choose a target from load testing and required headroom; 50–70% is an illustrative starting range, not a universal optimum.
- **Requests per second per instance**: better when the work is I/O-bound and CPU stays low.
- **Queue depth**: for workers, scale on the number of messages waiting.
- **Schedules**: scale up before a known peak (9 am logins, a 7 pm TV advert).

Autoscaling isn't instant. VM provisioning, image pulls and application warm-up all take time; measure readiness time for the actual workload rather than assuming a VM/container timing range. If traffic can double in 30 seconds, autoscaling alone won't save you. Keep a baseline buffer, use predictive or scheduled scaling, and shed load gracefully.

> [!warning] Scaling the web tier can break the database
> Going from 10 to 100 app servers, each with a pool of 20 database connections, takes you from 200 to 2,000 connections. Whether that exceeds limits or sustainable load depends on database configuration, memory and active query demand. Use a connection pooler (PgBouncer, RDS Proxy) and remember the bottleneck usually moves down a tier.

## Containers

A **container** packages an application and its dependencies into an image for a supported platform; host kernel, architecture, configuration and external services still affect behavior. Unlike a VM, it shares the host's kernel, which can reduce some virtualization overhead. Time to serving readiness still depends on the runtime, image availability, initialization and dependencies.

Containers suit stateless services: an image is immutable, any copy is interchangeable, and you replace them rather than patch them.

## Kubernetes basics

Running hundreds of containers by hand isn't feasible. **Kubernetes** is an orchestrator: you declare the state you want, and its controllers continuously work to make reality match.

The core objects:

- **Pod**: the smallest unit, one or more containers that share a network namespace and are scheduled together.
- **Deployment**: "keep 10 replicas of this pod template running"; it handles rolling updates and rollbacks.
- **Service**: a normal ClusterIP Service provides a stable virtual IP and DNS name for matching endpoints. Headless and ExternalName Services behave differently.
- **Ingress / Gateway**: routes external HTTP traffic to Services.
- **HorizontalPodAutoscaler (HPA)**: adjusts a Deployment's replica count from metrics such as CPU.
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

For a CPU utilization target, percentages are relative to configured CPU requests, not a node's total capacity. The HPA's simplified rule is:

```
desired = ceil(current * metric / target)
e.g. ceil(4 * 90% / 60%) = ceil(6) = 6
```

The HPA also ignores small deviations (a default tolerance of about 10%) and, by default, uses the highest recent recommendation within a default 5-minute scale-down stabilisation window, so a brief dip doesn't remove pods you'll need again a minute later.

When the cluster itself runs out of room, a **cluster autoscaler** (or Karpenter, originally built by AWS) can provision nodes when suitable capacity is available and policy permits. Timing is workload/provider-dependent; quotas, capacity shortages and scheduling constraints can leave pods Pending.

> [!example] A rolling deploy
> A Deployment has 10 replicas with `maxUnavailable: 1` and `maxSurge: 2`. The controller allows up to 2 extra non-terminating pods and can reduce available capacity to 9 during normal rollout; it need not wait for both new pods before removing any old pod. Terminating pods can temporarily make the total higher. This aims to maintain availability, but statelessness and schema compatibility alone do not guarantee invisible updates: APIs, sessions, capacity and draining must also remain compatible.

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
- Stateless app tiers do not depend on durable instance-local client state; replaceable caches are allowed, while backing stores retain the state that must survive.
- Push session state into a shared store (Redis) or a signed client token; use sticky sessions only as an optimisation.
- Autoscale on a signal that reflects your bottleneck, keep headroom, and remember new capacity takes time to arrive.
- Scaling the web tier shifts pressure to databases and caches; plan connection pooling.
- Kubernetes runs stateless services as Deployments of pods behind a stable Service, with HPA for scaling and probes for safe rollouts.
- Graceful shutdown matters: `SIGTERM` and endpoint removal happen in parallel, so keep serving briefly, then drain in-flight requests before exiting.

## Further reading
- [The Twelve-Factor App: Processes](https://12factor.net/processes)
- [Kubernetes: Overview](https://kubernetes.io/docs/concepts/overview/)
- [Kubernetes: Deployments](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)
- [Kubernetes: Horizontal Pod Autoscaling](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/)
- [Kubernetes: Service](https://kubernetes.io/docs/concepts/services-networking/service/)
