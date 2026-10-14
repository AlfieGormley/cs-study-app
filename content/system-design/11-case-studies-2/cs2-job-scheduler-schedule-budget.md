---
id: cs2-job-scheduler-schedule-budget
title: Scheduler workload and burst budget
level: advanced
minutes: 4
summary: Separate schedule storage from run history and design for round-time bursts.
sourceLesson: cs2-job-scheduler
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

Assume 100 M (100 million) schedules, mostly recurring, and that on average each one runs about once every 3 hours (10,800 seconds). The average firing rate is the number of schedules divided by how often each fires:

```formula
r = J / p
r = 100,000,000 / 10,800 s ≈ 9,300 runs/s
where
r: average job runs started per second, across all schedules
J: schedules stored; here 100 million
p: average gap between one schedule's runs, in seconds (s); 3 hours = 10,800 s
s: seconds
runs: job executions
≈: approximately equal to
In words: 100 million jobs that each run every three hours start about 9,300 runs a second on average.
```

Averages hide the real load. Cron schedules cluster on round times: the hourly expression `0 * * * *` means "minute 0 of every hour". Say 10 M schedules are hourly and 20% of those fire exactly at the top of the hour (hh:00:00):

```formula
B = H × f
B = 10,000,000 × 0.2 = 2,000,000 runs
m = B / (r × 1 s)
m ≈ 2,000,000 / 9,300 ≈ 215
B / 60 s ≈ 33,000 runs/s
where
B: runs due in the same second at the top of the hour
H: hourly schedules; here 10 million
f: fraction of them that fire exactly at :00; here 20% = 0.2
m: how many times bigger that burst is than one second's average load
r: the average rate, about 9,300 runs per second
60 s: one minute, if the burst may be spread across it
s: seconds
runs: job executions
≈: approximately equal to
In words: 2 million runs land in the same second, more than 200 times an average second; even spread over a minute that is about 33,000 a second.
```

Storage, assuming about 1 KB (kilobyte) per job record and about 500 bytes per run-history row:

```formula
D_jobs = 100,000,000 × 1 KB = 100 GB
D_runs = 500 B × 9,300/s × 86,400 s
D_runs ≈ 400 GB/day
D_30 = 400 GB/day × 30 days = 12 TB
where
D_jobs: storage for all job definitions
D_runs: run history written per day
D_30: run history kept with a 30-day TTL (time to live: rows are deleted after 30 days)
B: bytes
KB: kilobytes, 1,000 bytes
GB: gigabytes, 1,000,000,000 bytes
TB: terabytes, 1,000 GB
s: seconds; a day has 86,400 s
day: one day
days: days
≈: approximately equal to
In words: the job table is about 100 GB, but run history grows by about 400 GB a day, so 30 days of it is about 12 TB.
```

What matters:

- Average throughput is a workload to benchmark, not a guarantee about an arbitrary sharded database. The **top-of-minute and top-of-hour spikes** are the real design load. Two million runs due in the same second can't all fire within the 1–2 s target unless execution/dispatch capacity can absorb the burst. Read-ahead can pre-stage work but does not remove simultaneous execution demand; allowed jitter changes the timing contract.
- Run history dwarfs job definitions. Put it in a store with TTLs, or in time-partitioned tables you can drop.

## Key takeaways
- Average firing rate hides simultaneous cron demand.
- Read-ahead stages work but does not remove execution capacity requirements.
- Run-history retention can dominate job-definition storage.

## Further reading
- [Executing cron scripts reliably at scale (Slack Engineering)](https://slack.engineering/executing-cron-scripts-reliably-at-scale/)
- [Asynchronous task scheduling at Dropbox (Dropbox Tech)](https://dropbox.tech/infrastructure/asynchronous-task-scheduling-at-dropbox)
- [CronJob (Kubernetes docs)](https://kubernetes.io/docs/concepts/workloads/controllers/cron-jobs/)
