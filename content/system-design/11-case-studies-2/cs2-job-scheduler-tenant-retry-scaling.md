---
id: cs2-job-scheduler-tenant-retry-scaling
title: Scheduler fairness and retry capacity
level: advanced
minutes: 3
summary: Protect other tenants from bursts and prevent failed endpoints receiving synchronized retries.
sourceLesson: cs2-job-scheduler
---

## Multi-tenancy and fairness

- Give each tenant quotas on schedules, firings per second and concurrent runs.
- Use weighted fair queuing on the work queue (a queue per tenant, or per priority class) so a tenant scheduling 1 M jobs at midnight doesn't delay everyone else's.
- Isolate worker pools for heavy tenants or job types.

## Bottlenecks and trade-offs

- **Polling interval vs load**: polling every 100 ms per shard is accurate but costs database QPS. Read-ahead plus in-memory timers gives accuracy *and* cheap polling.
- **More shards** mean finer rebalancing and more parallelism, but more leases to manage. 1,024 shards over 50 nodes is about 20 each.
- **At-least-once vs at-most-once**: some jobs (sending a bill) prefer at-most-once, risking a missed run rather than a duplicate. Expose it as a per-job choice, with idempotency keys as the default answer.
- **Database as queue**: benchmark SKIP LOCKED with the actual row size, indexes, contention and durability settings. When the measured dispatch load exceeds the chosen database budget, hand off to Kafka or SQS for dispatch, and keep the database for state.

## Evolving at 10x

- **1 B schedules, about 100 k firings/s**: more shards, timing wheels per shard holding the next few minutes, and dispatch straight into partitioned Kafka topics.
- **Workflows**: jobs with dependencies (DAGs) and long-running steps lead to durable-execution engines (Temporal, Airflow for batch), which durably track workflow/task progress. Temporal replays workflow history while activities need retry-safe effects; Airflow schedules and retries tasks rather than replaying arbitrary code with the same semantics.
- **Multi-region**: assign each shard a home region, replicate the job store, and make sure fencing works across regions (a single global coordination service, or per-region shard ownership).

## Recovery load belongs in the capacity plan

A failed endpoint creates pending attempts in addition to ordinary scheduled work. Retrying every failed run at exactly the same thirty-second boundary merely moves the original burst into repeated waves. Exponential backoff widens the interval after repeated failures; a cap bounds that interval, and independently chosen jitter spreads the recovery work within the permitted window. A retry budget limits how much of the system can be spent recovering one dependency.

Fairness applies at both dispatch and execution. Per-tenant queues alone do not stop one tenant occupying every worker with long jobs. Pair service weights with concurrent-run quotas and use separate pools where heavy work needs isolation. Observe scheduled-to-start delay, active workers, retry backlog and terminal outcomes by tenant. A healthy fleet-wide average can hide a small tenant waiting twenty minutes behind another tenant's midnight burst.

These are control policies to test with the actual workloads. Neither timing wheels nor a larger work queue creates unlimited endpoint throughput, and a region failover needs a tested ownership and replication-loss policy.

> **Content gap:** no measured scheduler fleet or timing SLA validation is supplied. All capacity and timing targets are illustrative. Provider side effects require their own retry/idempotency contracts; a local run row alone cannot guarantee exactly-once effects.

## Key takeaways
- Apply per-tenant firing, concurrency and schedule quotas together with fair service.
- Use capped backoff and random jitter for retries against struggling targets.
- Scaling workflow orchestration still requires retry-safe external effects and fenced ownership.

## Further reading
- [Executing cron scripts reliably at scale (Slack Engineering)](https://slack.engineering/executing-cron-scripts-reliably-at-scale/)
- [Asynchronous task scheduling at Dropbox (Dropbox Tech)](https://dropbox.tech/infrastructure/asynchronous-task-scheduling-at-dropbox)
- [CronJob (Kubernetes docs)](https://kubernetes.io/docs/concepts/workloads/controllers/cron-jobs/)
- [Amazon SQS visibility timeout (AWS docs)](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-visibility-timeout.html)
