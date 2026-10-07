---
id: rel-safe-deployments
title: Safe deployments and zero-downtime migrations
level: advanced
minutes: 13
summary: Compare rolling, blue-green and canary releases, decouple deploy from release with feature flags, and change database schemas without downtime using expand and contract.
---

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
  rollback = flip back to blue
```

- **Pros**: fast routing cutover and rollback when the router, connections and shared state permit; you can test green with production config before switching.
- **Cons**: double the capacity during deploys; all users switch at once, so a bug not caught in testing hits 100% of traffic immediately. Shared state (the database) isn't duplicated, so schema changes still need care.
- Watch out for long-lived connections (WebSockets) and in-flight requests at switch time; drain them.

## Canary releases

Send a small fraction of real traffic to the new version, compare its metrics with the old version's, and widen gradually.

```
1%  ──▶ v2   compare errors, latency
5%  ──▶ v2   still good?
25% ──▶ v2
100%──▶ v2
any stage bad → route 0% to v2
```

The key is **comparison**: the canary's error rate and latency are judged against a control group (the baseline running v1 at the same time, ideally on the same number of hosts), not against a fixed threshold. Tools like Spinnaker's Kayenta and Argo Rollouts run automated canary analysis.

Considerations from the SRE workbook:

- The canary must get enough traffic to be statistically meaningful. 1% of a 100 req/s service is one request a second; a 0.1% error-rate increase would take a long time to detect.
- Bake time must cover slow-to-appear problems: memory leaks, cache expiry, daily batch jobs.
- Canary populations can be hosts, a percentage of requests, or specific users (internal staff first).

### Staged rollouts at scale

AWS describes deploying in **waves**: first a single box ("one-box"), then one AZ, then one region, then progressively larger groups of regions, with automated monitoring and rollback at each stage and bake time between them. A full global deploy may take days, deliberately. Combined with cell-based architecture, a bad change is usually caught while it affects a tiny fraction of customers.

| Strategy | Extra capacity | Rollback | Exposure |
|---|---|---|---|
| Rolling | ~0 | slow | grows by batch |
| Blue-green | ~1× extra (~2× total) | routing-dependent | broad cutover |
| Canary | small | fast | 1% → 100% |

## Feature flags: separating deploy from release

A **feature flag** (feature toggle) wraps new behaviour in a runtime condition:

```
if flags.enabled("new_checkout",
                 user=ctx.user):
    return new_checkout(cart)
return old_checkout(cart)
```

This splits two things that used to be one:

- **Deploy**: ship the code to production (dark, off).
- **Release**: turn the behaviour on, for 1% of users, then staff, then everyone.

Benefits: potentially fast behavior rollback by flipping a flag (subject to propagation and already-started effects), trunk-based development with unfinished features merged behind flags, and A/B experiments.

Pete Hodgson's article on martinfowler.com classifies flags by longevity and dynamism: **release toggles** (short-lived), **experiment toggles**, **ops toggles** (kill switches for expensive features under load) and **permission toggles**.

> [!warning] Flags are debt and config is code
> Independent binary flags permit up to `2^n` configurations, although not every combination is reachable or a distinct execution path. Remove release flags once rolled out. And remember a flag change is a production change: stage it, audit it and monitor it like a deploy. Several major outages have come from a config or flag pushed globally at once.

## Rollback safety

Rolling back only works if the old version can run against whatever the new version did. AWS's guidance is that **every change must be backwards and forwards compatible** with the version on either side of it.

The classic trap: v2 writes data in a new format. You roll back to v1, which can't read it, and now the rollback is causing the outage. AWS's solution is a **two-phase deployment**:

1. Deploy a version that can *read* the new format but still *writes* the old one. Let it reach 100%.
2. Deploy a version that *writes* the new format.

Now rolling back from step 2 to step 1 is safe, because step 1 can read both.

## Zero-downtime schema changes: expand and contract

You can't upgrade the database and every application server in the same instant. For some period, old and new code run against the same schema. So schema changes must be split into compatible steps. Martin Fowler calls this **parallel change**, or **expand and contract**.

Example: rename column `fullname` to `display_name` on a large `users` table.

```
1 EXPAND   add display_name (nullable)
2 DUAL     app writes both columns
3 BACKFILL copy fullname → display_name
4 MIGRATE  app reads display_name
5 CONTRACT stop writing fullname,
           later drop the column
```

Before switching reads, all active writers must synchronize both columns atomically (for example in one UPDATE), or use a carefully designed compatibility trigger. Complete and verify the backfill only after old single-column writers have retired; otherwise they can leave the new column stale after it was copied. During rollback, preserve that synchronization.

The expansion and migration stages should support both old and new code. Contraction deliberately removes compatibility: drop the old column only after old binaries and the rollback window have retired. A destructive drop is not automatically reversible.

### Practical details

- **Avoid locking DDL** on large tables. In PostgreSQL, adding a nullable column is a metadata-only change, and since version 11 so is adding one with a constant (non-volatile) default. Many type changes rewrite the table under an exclusive lock; binary-compatible changes can avoid a rewrite. Where applicable, `CREATE INDEX CONCURRENTLY` avoids blocking ordinary writes, but can wait on transactions and leave an invalid index after failure; it cannot run inside a transaction block. For MySQL, tools like gh-ost and pt-online-schema-change copy the table in the background.
- **Beware lock queues.** Even an instant `ALTER TABLE` needs a brief exclusive lock. If a long-running query holds a conflicting lock, the `ALTER` waits, and every new query on the table queues behind it. Set a short `lock_timeout` (e.g. a few seconds) and retry, rather than stalling the whole table.
- **Backfill in batches** (say 10,000 rows at a time, throttled on replica lag), not one giant `UPDATE` that holds locks and floods replication.
- **Never drop in the same release** that stops using a column; wait until no running version references it, and keep a backup.
- Run migrations as a separate, observable step, not on application start-up from every instance at once.

```
-- batched backfill
UPDATE users
SET display_name = fullname
WHERE id BETWEEN :lo AND :hi
  AND display_name IS NULL;
-- sleep if replica lag > 1s
```

## Automating the guardrails

A mature pipeline does all of this without humans watching graphs:

1. Build once; promote the same artefact through stages.
2. Deploy to one box / canary; run automated analysis against baseline.
3. Bake; check SLO burn rates, errors and latency.
4. Proceed in waves, or **automatically roll back** on regression.
5. Block deploys when the error budget is exhausted (see the SLO lesson) or outside safe hours.

## Key takeaways

- Changes can trigger outages; staged deployment is an important reliability control.
- Rolling deploys are cheap but slow to roll back; blue-green enables fast routing rollback at roughly 2× application capacity when state remains compatible; canaries limit exposure and compare against a baseline.
- Feature flags decouple deploy from release and provide fast kill switches subject to propagation and state compatibility, but they are config changes that need staging and clean-up.
- Every change must be compatible with the version before and after it; use two-phase deploys for data format changes.
- Change schemas with expand and contract: add, dual-write, backfill in batches, switch reads, then remove.

## Further reading

- [Canarying releases (Google SRE workbook)](https://sre.google/workbook/canarying-releases/)
- [Automating safe, hands-off deployments (AWS Builders' Library)](https://aws.amazon.com/builders-library/automating-safe-hands-off-deployments/)
- [Ensuring rollback safety during deployments (AWS Builders' Library)](https://aws.amazon.com/builders-library/ensuring-rollback-safety-during-deployments/)
- [Blue-green deployment (Martin Fowler)](https://martinfowler.com/bliki/BlueGreenDeployment.html)
- [Canary release (Martin Fowler)](https://martinfowler.com/bliki/CanaryRelease.html)
- [Feature toggles (Pete Hodgson, martinfowler.com)](https://martinfowler.com/articles/feature-toggles.html)
- [Parallel change (Martin Fowler)](https://martinfowler.com/bliki/ParallelChange.html)
- [Release engineering (Google SRE book)](https://sre.google/sre-book/release-engineering/)
