---
id: rel-rolling-blue-green-cutover
title: Rolling and blue-green cutovers
level: advanced
minutes: 3
summary: Compare capacity, exposure and rollback behaviour of two deployment shapes.
sourceLesson: rel-safe-deployments
---

The SLO units explained when release policy permits change. Safe deployments control the exposure of that change. All strategies still need correct state compatibility and meaningful evidence of user outcomes.

Deployments, configuration changes and migrations can trigger outages. Safe change processes reduce that risk. A universal outage percentage is absent here because a reliably applicable population and measurement were not established.

Safe deployment rests on three ideas:

1. **Limit exposure**: a bad change should reach as few users as possible before it's caught.
2. **Detect fast**: compare the new version with the old automatically.
3. **Roll back fast and safely**: undoing a change should be quicker and less risky than fixing forward.

## Rolling deployments

Replace instances in batches: take a few out of the load balancer, upgrade them, health-check them, put them back, repeat.

```
v1 v1 v1 v1 v1 v1
v2 v2 v1 v1 v1 v1   batch 1
v2 v2 v2 v2 v1 v1   batch 2
v2 v2 v2 v2 v2 v2   done
```

- **Pros**: can use spare capacity in the existing fleet or a small surge; ensure remaining instances handle traffic while others are unavailable; it's the Kubernetes Deployment default, where `maxSurge` and `maxUnavailable` (both 25% by default) control the batch size.
- **Cons**: v1 and v2 serve traffic *at the same time*, so they must be compatible with each other and with the data. Rollback is another rolling deploy, so it's slow.
- Health checks only prove the process started, not that it's correct. A bad version can roll out to 100% if it passes shallow checks.

## Blue-green deployments

Run two full environments. **Blue** serves production; deploy v2 to **green**, test it, then switch the router (load balancer, DNS or service mesh) all at once.

```
          ┌──▶ [Blue  v1]  (idle)
[Router]──┤
          └──▶ [Green v2]  (live)
  rollback: route back to blue
```

- **Pros**: fast routing cutover and rollback when the router, connections and shared state permit; you can test green with production config before switching.
- **Cons**: double the capacity during deploys; all users switch at once, so a bug not caught in testing hits 100% of traffic immediately. When both environments share a database, schema changes affect both and still need compatibility. Separate databases require their own synchronisation and cutover design.
- Watch out for long-lived connections (WebSockets) and in-flight requests at switch time; drain them.

## Key takeaways

- Rolling deployments mix versions and need capacity while instances are unavailable.
- Blue-green can switch routing quickly when connections and shared state permit; it needs a second environment.
- A process health check does not establish correct user-visible behaviour.

## Further reading

- [Canarying releases (Google SRE workbook)](https://sre.google/workbook/canarying-releases/)
- [Blue-green deployment (Martin Fowler)](https://martinfowler.com/bliki/BlueGreenDeployment.html)
- [Release engineering (Google SRE book)](https://sre.google/sre-book/release-engineering/)
