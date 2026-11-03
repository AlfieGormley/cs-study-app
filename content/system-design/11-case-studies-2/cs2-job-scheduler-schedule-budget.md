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

## The schedule distribution is the workload

An illustrative fleet has 100 million schedules, each running once every three hours on average. That averages roughly 9,300 occurrences per second. The same average can describe evenly staggered jobs or millions due at exactly the same instant; those require very different dispatch capacity.

Cron expressions often align work at minute or hour boundaries. Inspect the actual next-run distribution rather than multiplying an average by an arbitrary safety factor. A target to start jobs within two seconds requires enough dispatch and execution capacity for the allowed burst, including recovered work after an outage.

## Read-ahead and jitter solve different problems

Read-ahead prepares due work before its start time, reducing polling jitter. It cannot make millions of simultaneous side effects cheap. Buffering the burst delays some jobs; that delay needs an explicit lateness policy.

Tenant-approved jitter changes the permitted start times. A job that allows any time in the first five minutes can receive a stable offset within that window. A job that explicitly requires midnight cannot silently be shifted five minutes to make the graph look smoother.

## History grows independently of definitions

The schedule table stores what should run. Run history records repeated occurrences, attempts and outcomes. A small recurring definition may produce thousands of history rows, so history retention can dominate definition storage.

Choose retention, time partitioning and archival retrieval deliberately. Keep pending and unresolved runs discoverable even if ordinary completed history expires. Track scheduled-to-start delay, retry backlog and missed/dead-lettered outcomes alongside storage growth. Neither a modest definition table nor a low average rate proves that the midnight burst is safe.

## Key takeaways
- Average firing rate hides simultaneous cron demand.
- Read-ahead stages work but does not remove execution capacity requirements.
- Run-history retention can dominate job-definition storage.

## Further reading
- [Executing cron scripts reliably at scale (Slack Engineering)](https://slack.engineering/executing-cron-scripts-reliably-at-scale/)
- [Asynchronous task scheduling at Dropbox (Dropbox Tech)](https://dropbox.tech/infrastructure/asynchronous-task-scheduling-at-dropbox)
- [CronJob (Kubernetes docs)](https://kubernetes.io/docs/concepts/workloads/controllers/cron-jobs/)
