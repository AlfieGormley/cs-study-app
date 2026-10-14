---
id: cs2-job-scheduler-due-transactions
title: Transactional due-job polling
level: advanced
minutes: 4
summary: Record each occurrence, advance its schedule and persist dispatch intent together.
sourceLesson: cs2-job-scheduler
---

## API design

This is an illustrative endpoint contract, not a runnable HTTP request. Arrows distinguish responses from submitted fields.

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

This is a schema sketch: PK marks the primary key. It omits executable type declarations and migrations.

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

Follow the arrows as data paths; the drawing is not a deployment specification.

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

The SQL fragment below selects candidate rows and illustrates one bound occurrence. The application computes its next scheduled instant; these bindings are inputs, not SQL variables. Ownership fencing must be checked in the same protected transaction.

```sql
BEGIN;
-- Other pollers skip already claimed rows.
SELECT job_id, next_run_at FROM jobs
WHERE shard_id = :s
  AND next_run_at <= now() + interval '5 s'
  AND state = 'active'
ORDER BY next_run_at
LIMIT 500
FOR UPDATE SKIP LOCKED;

-- Bind one selected job and occurrence.
INSERT INTO runs(job_id, scheduled_at)
VALUES (:j, :scheduled)
ON CONFLICT DO NOTHING;
UPDATE jobs SET next_run_at = :next,
  version = version + 1
  WHERE job_id = :j AND version = :v;
-- Durable intent survives a relay crash.
INSERT INTO outbox(job_id, scheduled_at)
VALUES (:j, :scheduled)
ON CONFLICT DO NOTHING;
-- Roll back on an affected-count conflict.
COMMIT;
```

- The `(shard_id, next_run_at)` index makes the scan cheap.
- `FOR UPDATE SKIP LOCKED` (PostgreSQL, MySQL 8) lets several pollers share a shard safely, because each skips rows another poller has locked.
- Reading **5 s ahead** and dispatching into an in-memory timer absorbs polling jitter, the small variation in exactly when each poll runs. Persist pending dispatch so timers can be rebuilt after failure; no timer guarantees exact execution time.
- Computing `next_run_at` *in the same transaction* as the run insert makes the run creation, next-time update and durable outbox intent atomic under the database durability contract. The relay and worker still require recovery and deduplication.

## Key takeaways
- A unique occurrence key deduplicates durable run creation.
- SKIP LOCKED helps pollers share row work; an index limits the scan.
- Advance schedules with run and outbox records in one transaction.

## Further reading
- [Executing cron scripts reliably at scale (Slack Engineering)](https://slack.engineering/executing-cron-scripts-reliably-at-scale/)
- [Asynchronous task scheduling at Dropbox (Dropbox Tech)](https://dropbox.tech/infrastructure/asynchronous-task-scheduling-at-dropbox)
- [Amazon SQS visibility timeout (AWS docs)](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-visibility-timeout.html)
