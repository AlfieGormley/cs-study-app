---
id: cs2-job-scheduler
title: Distributed job scheduler (cron at scale)
level: advanced
minutes: 15
summary: Design a multi-tenant scheduler that fires millions of one-off and cron jobs on time, covering delayed queues, leader election with fencing, sharding, at-least-once execution and the cron edge cases that bite.
---

"Run this at 09:00 every weekday" is easy on one box with `crontab`. It's hard when there are 100 M schedules, the box can die, two boxes might both think they're in charge, and half the world's jobs are scheduled for exactly midnight.

A distributed scheduler is really three systems. A **durable store of what should run when**. A **trigger** that notices when things are due. An **execution layer** that attempts them with recoverable retries and records success, failure or an explicit skipped/dead-lettered outcome.

## Requirements

### Functional
- Create one-off jobs ("run at T") and recurring jobs (cron expression plus a time zone).
- Each job has a payload or target (an HTTP endpoint, a queue message, a container), a retry policy and a timeout.
- Pause, resume, delete, trigger now.
- Query run history and status.

### Non-functional
- **On time**: fire within about 1–2 s of the scheduled time (p99).
- **Recoverable execution** with duplicate attempts possible. Eventual execution requires recovery and continued retry; configured deadlines and retry limits may terminate a run. Record every skipped or dead-lettered run explicitly.
- **Highly available**: no single scheduler node is a single point of failure.
- **Scalable**: to hundreds of millions of schedules and tens of thousands of firings a second.
- **Multi-tenant**: one noisy tenant can't starve others.

## Back-of-the-envelope

```
Schedules: 100 M (mostly recurring)
Avg frequency: ~1 run / 3 h
  100e6 / 10,800 s = ~9,300 runs/s avg

Top-of-hour spike ("0 * * * *"):
  say 10 M schedules are hourly
  and 20% of them fire at :00
  -> 2 M runs due at hh:00:00
  -> ~200x the per-second average
  spread over 60 s: ~33,000/s

Job record ~1 KB  -> 100 GB
Run history ~500 B x 9,300/s x 86,400
  = ~400 GB/day (TTL to 30 days = 12 TB)
```

What matters:

- Average throughput is a workload to benchmark, not a guarantee about an arbitrary sharded database. The **top-of-minute and top-of-hour spikes** are the real design load. Two million runs due in the same second can't all fire within the 1–2 s target unless execution/dispatch capacity can absorb the burst. Read-ahead can pre-stage work but does not remove simultaneous execution demand; allowed jitter changes the timing contract.
- Run history dwarfs job definitions. Put it in a store with TTLs, or in time-partitioned tables you can drop.

## API design

```
POST /v1/jobs
  { name, schedule: "0 9 * * MON-FRI",
    timezone: "Europe/London",
    target: {type:"http", url, method},
    payload, timeout_s: 300,
    retry: {max: 5, backoff: "exp"},
    concurrency: "forbid" }
  Idempotency-Key: <uuid>
  -> { job_id, next_run_at }

POST   /v1/jobs/{id}:pause | :resume | :run
DELETE /v1/jobs/{id}
GET    /v1/jobs/{id}/runs?limit=50
```

Workers receive a stable **run id** based on job ID and scheduled UTC occurrence, suitable for an enforced idempotency contract. Manual triggers need their own operation ID; decide how schedule-version changes affect identity.

> **Content gap:** no measured scheduler fleet or timing SLA validation is supplied. All capacity and timing targets are illustrative. Provider side effects require their own retry/idempotency contracts; a local run row alone cannot guarantee exactly-once effects.

## Data model

```
jobs(job_id PK, tenant_id, schedule,
     timezone, next_run_at, payload,
     retry_policy, state, version,
     shard_id)
  INDEX (shard_id, next_run_at)

runs(job_id, scheduled_at,   PK both
     attempt, status, worker_id,
     lease_expires_at, started_at,
     finished_at, error)
```

The **composite primary key** `(job_id, scheduled_at)` on `runs` is the crucial piece. Even if two scheduler instances both decide to fire the 09:00 run, only one `INSERT` succeeds. The database's uniqueness check is the dedup.

## High-level architecture

```
 Clients
    |
    v
+--------+     +-----------------+
| Job API|---->|  Job store      |
+--------+     | (sharded, by    |
               |  shard_id)      |
               +-----------------+
                  ^          |
       claim due  |          | due jobs
                  |          v
+-------------------------------+
| Scheduler nodes               |
| (each owns shards via lease)  |
+-------------------------------+
                  |
                  v
          +--------------+
          | Work queue   |
          | (Kafka/SQS)  |
          +--------------+
                  |
                  v
          +--------------+
          | Worker pools |---> targets
          +--------------+
                  |
                  v
           run status / acks
```

## Deep dive 1: finding due jobs

### Option A: poll an index
Each scheduler node, for each shard it owns, loops:

```
BEGIN;
SELECT job_id, next_run_at FROM jobs
WHERE shard_id = :s
  AND next_run_at <= now() + interval '5 s'
  AND state = 'active'
ORDER BY next_run_at
LIMIT 500
FOR UPDATE SKIP LOCKED;

-- for each job:
INSERT INTO runs(job_id, scheduled_at, ...)
  ON CONFLICT DO NOTHING;
UPDATE jobs SET next_run_at = :next,
  version = version + 1
  WHERE job_id = :j AND version = :v;
-- plus an outbox row to enqueue
COMMIT;
```

- The `(shard_id, next_run_at)` index makes the scan cheap.
- `FOR UPDATE SKIP LOCKED` (PostgreSQL, MySQL 8) lets several pollers share a shard safely, because each skips rows another poller has locked.
- Reading **5 s ahead** and dispatching into an in-memory timer absorbs polling jitter, which can reduce polling jitter. Persist pending dispatch so timers can be rebuilt after failure; no timer guarantees exact execution time.
- Computing `next_run_at` *in the same transaction* as the run insert makes the run creation, next-time update and durable outbox intent atomic under the database durability contract. The relay and worker still require recovery and deduplication.

### Option B: time-bucketed tables
Write jobs into buckets keyed by minute: `due(bucket = '2026-10-01T09:00', shard, job_id)`. The scheduler reads due buckets, including missed buckets after downtime; reschedules and cancellation need version checks and bucket cleanup. This works well on Cassandra or DynamoDB, which support secondary indexing but still benefit from deliberately partitioned time buckets rather than one hot global due-time access path.

### Option C: in-memory timing wheel
Load the next N minutes of due jobs into a **hierarchical timing wheel**: an array of slots, one per second, with overflow wheels for minutes and hours. Insertion can be O(1) for a fixed number of wheel levels; expiring a bucket costs at least O(k) for its k due timers. Kafka uses timing wheels internally for delayed operations. The database stays the source of truth, and the wheel is a cache of the near future, rebuilt from the store on failover.

### Option D: delayed-message queues
For one-off delays, a queue with native delay does the waiting for you. SQS delay queues and per-message timers support delays of up to 15 minutes (FIFO queues only support the queue-level delay). For anything longer, AWS points you at EventBridge Scheduler. A Redis sorted set scored by timestamp, polled with `ZRANGEBYSCORE` and moved atomically into recoverable in-flight state with a Lua script, is a popular DIY version. Long delays go in the database, and are moved into the short-delay queue when they're close.

## Deep dive 2: who is in charge? Leader election and sharding

A **single leader** scheduler is simple, but it's a throughput ceiling and its failover is a visible outage. Slack's write-up is a useful real example: it replaced a single cron host with a scheduler service that runs several pods with leader election, hands the work to its distributed job queue, and records runs in a database table for deduplication and monitoring. Instead, split jobs into many **shards** (say 1,024, using `shard_id = hash(job_id) % 1024`) and give each shard exactly one owner at a time.

- Owners take **leases** in a coordination service (etcd, ZooKeeper, Consul). Each lease has a TTL (say 10 s) and is renewed every few seconds.
- If a node dies, its leases expire, and other nodes claim the orphaned shards.
- Rebalance as nodes join, aiming for about 1,024/N shards each.

### Split brain and fencing
Leases expire by **time**, and a paused process (a 15 s GC pause, a frozen VM) doesn't know its lease ran out. When it wakes, it may still act as owner while the new owner also acts. Defences:

1. **Fencing tokens**: every lease grant comes with a monotonically increasing number (an etcd revision or ZooKeeper zxid). The protected resource must atomically install/check the current epoch and reject stale writes. A newly granted coordinator lease does not automatically teach an unrelated database its new token.
2. **Idempotent firing**: the `runs` primary key makes double-firing harmless at the database level, whoever the owner is.

Use both. This is the standard argument (from Martin Kleppmann's critique of Redlock) that **lock-based mutual exclusion needs fencing to be safe**.

## Deep dive 3: at-least-once execution

```
QUEUED -> LEASED(worker, until)
  -> SUCCEEDED
  -> FAILED -> retry (backoff) -> QUEUED
  -> lease expired -> QUEUED (redeliver)
```

- A worker **leases** a run (like an SQS visibility timeout) and **heartbeats** to extend the lease for long jobs.
- It **acks only after** the work completes. If it crashes, the lease expires and the run is redelivered.
- Therefore a run may execute **more than once**: a worker can finish the work and then die before acking. Exactly-once *execution* is impossible in general (it's the Two Generals problem in disguise). What you can achieve is **effectively-once effects** when the side-effect destination enforces deduplication or the effect and run record share one atomic transaction. A local pre-send flag can lose work, and a post-send flag leaves ambiguity.
- Retries use exponential backoff with **jitter**, and go to a dead-letter queue after max attempts, with an alert to the owner.

## Deep dive 4: cron semantics that bite

- **Time zones and DST**: "01:30 Europe/London" doesn't exist on the last Sunday in March (clocks jump from 01:00 GMT to 02:00 BST), and occurs *twice* on the last Sunday in October. Choose and document a policy (for example, skip non-existent times, and fire once on the first occurrence). Always store the zone, not a UTC offset.
- **Missed runs**: if the scheduler was down from 08:55 to 09:10, does the 09:00 run fire late, or get skipped? Kubernetes CronJob exposes this as `startingDeadlineSeconds`: a run that can't start within that many seconds of its scheduled time is counted as missed and skipped. Offer per-job policy, and limit catch-up to stop a flood of backlogged runs after an outage.
- **Overlap**: a job scheduled every minute that takes 3 minutes. Policies are **Allow** (run concurrently), **Forbid** (do not start concurrently; missed occurrences may still start later within the starting deadline) and **Replace** (replace the running Job). These are Kubernetes' `concurrencyPolicy` values.
- **Thundering herd**: add deterministic **jitter** within a window the tenant allows ("hourly, any time in the first 5 minutes"). Hash `job_id` to an offset so each job is stable from run to run but the jobs spread out.

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

## Key takeaways
- Separate the durable schedule store, the trigger and the executors. The store is the source of truth, and every in-memory structure (timing wheels, read-ahead buffers) is a rebuildable cache.
- Find due jobs with an indexed `next_run_at` scan using `FOR UPDATE SKIP LOCKED` and read-ahead, advancing `next_run_at` in the same transaction as recording the run.
- Shard schedules and give each shard one owner via leases. Leases alone aren't safe, so add fencing tokens and an idempotent `(job_id, scheduled_at)` run key.
- Recovery uses leases, heartbeats and acknowledgments after work; attempts may repeat, while deadlines/retry limits can stop eventual execution. Make side effects idempotent with the run id, and use backoff with jitter plus a dead-letter queue.
- Handle cron edge cases explicitly: DST gaps and overlaps, missed-run policy, concurrency policy, and top-of-hour spikes (add jitter).

## Further reading
- [Executing cron scripts reliably at scale (Slack Engineering)](https://slack.engineering/executing-cron-scripts-reliably-at-scale/)
- [Asynchronous task scheduling at Dropbox (Dropbox Tech)](https://dropbox.tech/infrastructure/asynchronous-task-scheduling-at-dropbox)
- [CronJob (Kubernetes docs)](https://kubernetes.io/docs/concepts/workloads/controllers/cron-jobs/)
- [How to do distributed locking (Martin Kleppmann)](https://martin.kleppmann.com/2016/02/08/how-to-do-distributed-locking.html)
- [Amazon SQS visibility timeout (AWS docs)](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-visibility-timeout.html)
- [ZooKeeper recipes: leader election and locks](https://zookeeper.apache.org/doc/current/recipes.html)
- [Leader election (Wikipedia)](https://en.wikipedia.org/wiki/Leader_election)
