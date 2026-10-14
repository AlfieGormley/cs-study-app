---
id: cs2-job-scheduler-execution-cron
title: Repeatable attempts and cron policy
level: advanced
minutes: 4
summary: Document DST, overlap and missed-run behaviour while making effects retry-safe.
sourceLesson: cs2-job-scheduler
---

## Deep dive 3: at-least-once execution

```
QUEUED -> LEASED(worker, until)
  -> SUCCEEDED
  -> FAILED -> retry (backoff) -> QUEUED
  -> lease expired -> QUEUED (redeliver)
```

- A worker **leases** a run (like an SQS visibility timeout) and **heartbeats** to extend the lease for long jobs.
- It **acks only after** the work completes. If it crashes, the lease expires and the run is redelivered.
- Therefore a run may execute **more than once**: a worker can finish the work and then die before acking. Exactly-once *execution* is impossible in general under arbitrary crashes and ambiguous external responses. What you can achieve is **effectively-once effects** when the side-effect destination enforces deduplication or the effect and run record share one atomic transaction. A local pre-send flag can lose work, and a post-send flag leaves ambiguity.
- Retries use exponential backoff with **random jitter** (a random extra delay), and go to a dead-letter queue after max attempts, with an alert to the owner.

## Deep dive 4: cron semantics that bite

- **Time zones and DST**: "01:30 Europe/London" doesn't exist on the last Sunday in March (clocks jump from 01:00 GMT, Greenwich Mean Time, to 02:00 BST, British Summer Time), and occurs *twice* on the last Sunday in October. Choose and document a policy (for example, skip non-existent times, and fire once on the first occurrence). Always store the zone, not a UTC offset.
- **Missed runs**: if the scheduler was down from 08:55 to 09:10, does the 09:00 run fire late, or get skipped? Kubernetes CronJob exposes this as `startingDeadlineSeconds`: a run that can't start within that many seconds of its scheduled time is counted as missed and skipped. Offer per-job policy, and limit catch-up to stop a flood of backlogged runs after an outage.
- **Overlap**: a job scheduled every minute that takes 3 minutes. Policies are **Allow** (run concurrently), **Forbid** (do not start concurrently; missed occurrences may still start later within the starting deadline) and **Replace** (replace the running Job). These are Kubernetes' `concurrencyPolicy` values.
- **Thundering herd**: add **deterministic jitter** within a window the tenant allows ("hourly, any time in the first 5 minutes"). Hash `job_id` to an offset so each job is stable from run to run but the jobs spread out.

## A repeatable permitted offset

This Python example chooses an offset only for jobs whose contract permits the first five minutes. Use a stable algorithm across processes; Python’s built-in string hash can vary between processes.

```python
from hashlib import sha256

# Keep the slot stable across processes.
job_id = "report-42"
h = int.from_bytes(
    sha256(job_id.encode()).digest(), "big"
)
# Allow a slot in the first five minutes.
offset_s = h % 300

# 273 seconds after the nominal start.
print(offset_s)
```

## Read attempts separately from occurrences

An occurrence is the logical scheduled job identified by its job and scheduled UTC time. Attempts are the deliveries that try to carry out that occurrence. Keep the logical identifier stable through worker retries; changing it after a network error defeats destination-side deduplication. Manual runs and schedule-version changes require an explicit identity policy.

The state diagram above is a recovery contract, not a claim of exactly-once network delivery. Acknowledgements and leases identify what the scheduler knows. Only the side-effect destination can confirm whether an external action happened, unless the action and run record share one atomic transaction. A deadline or retry cap ends the retry obligation and needs a visible terminal outcome.

## Key takeaways
- A completed effect followed by a lost acknowledgement can produce a duplicate attempt.
- Specify DST gaps, repeated local times and catch-up policy explicitly.
- Deterministic permitted jitter spreads schedules; random retry jitter addresses correlated failures.

## Further reading
- [CronJob (Kubernetes docs)](https://kubernetes.io/docs/concepts/workloads/controllers/cron-jobs/)
- [Amazon SQS visibility timeout (AWS docs)](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-visibility-timeout.html)
- [Executing cron scripts reliably at scale (Slack Engineering)](https://slack.engineering/executing-cron-scripts-reliably-at-scale/)
