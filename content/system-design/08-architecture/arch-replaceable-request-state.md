---
id: arch-replaceable-request-state
title: Making application instances replaceable
level: basic
minutes: 3
summary: Decide which state must survive outside an application instance and which working state can be rebuilt.
sourceLesson: arch-stateless-web-tier
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

### Check the replacement boundary

Ask whether another instance could reconstruct everything needed for the next request. A configuration cache fetched again from its source passes that test. A basket or avatar held only in one instance does not. A WebSocket connection necessarily has live connection state, but reconnecting clients need a way to restore room membership and resume useful work on a different instance. Moving state elsewhere also transfers responsibility: persistence, availability and access control belong to the backing service's design.

## Key takeaways
- Statelessness removes dependence on durable instance-local client state between requests.
- Shared stores retain durable state; caches and per-request memory can remain local when rebuildable.
- Instance replacement can still lose in-flight work, and shared dependencies still bound scaling.

## Further reading
- [The Twelve-Factor App: Processes](https://12factor.net/processes)
