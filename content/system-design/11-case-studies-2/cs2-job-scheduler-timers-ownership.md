---
id: cs2-job-scheduler-timers-ownership
title: Long delays and fenced shard ownership
level: advanced
minutes: 4
summary: Choose a rebuildable timer structure and reject stale scheduler owners.
sourceLesson: cs2-job-scheduler
---

### Option B: time-bucketed tables
Write jobs into buckets keyed by minute: a minute bucket, a shard identifier and a job identifier. The scheduler reads due buckets, including missed buckets after downtime; reschedules and cancellation need version checks and bucket cleanup. This works well on Cassandra or DynamoDB, which support secondary indexing but still benefit from deliberately partitioned time buckets rather than one hot global due-time access path.

### Option C: in-memory timing wheel
Load the next N minutes of due jobs into a **hierarchical timing wheel**: an array of slots, one per second, with overflow wheels for minutes and hours. Insertion can be O(1), meaning constant time however many timers exist, for a fixed number of wheel levels; expiring a bucket costs at least O(k), time proportional to k, for its k due timers. Kafka uses timing wheels internally for delayed operations. The database stays the source of truth, and the wheel is a cache of the near future, rebuilt from the store on failover.

### Option D: delayed-message queues
For one-off delays, a queue with native delay does the waiting for you. SQS delay queues and per-message timers support delays of up to 15 minutes (FIFO queues only support the queue-level delay). For anything longer, AWS points you at EventBridge Scheduler. A Redis sorted set scored by timestamp, polled with `ZRANGEBYSCORE` and moved atomically into recoverable in-flight state with a Lua script, is a popular DIY version. Long delays go in the database, and are moved into the short-delay queue when they're close.

## Deep dive 2: who is in charge? Leader election and sharding

A **single leader** scheduler is simple, but it's a throughput ceiling and its failover is a visible outage. Slack's write-up is a useful real example: it replaced a single cron host with a scheduler service that runs several pods with leader election, hands the work to its distributed job queue, and records runs in a database table for deduplication and monitoring. Instead, split jobs into many **shards** (say 1,024, using a stable integer hash of the job ID and taking its remainder after division by 1,024, so every job lands in a shard numbered 0 to 1,023) and give each shard exactly one owner at a time.

- Owners take **leases** in a coordination service (etcd, ZooKeeper, Consul). Each lease has a TTL (say 10 s) and is renewed every few seconds.
- If a node dies, its leases expire, and other nodes claim the orphaned shards.
- Rebalance as nodes join, aiming for approximately equal shares, with fractional allocations rounded between nodes.

### Split brain and fencing
Leases expire by **time**, and a paused process (a 15 s GC pause, a frozen VM) doesn't know its lease ran out. When it wakes, it may still act as owner while the new owner also acts. Defences:

1. **Fencing tokens**: every lease grant comes with a monotonically increasing number (an etcd revision or ZooKeeper zxid). The protected resource must atomically install/check the current epoch and reject stale writes. A newly granted coordinator lease does not automatically teach an unrelated database its new token.
2. **Idempotent firing**: the `runs` primary key makes double-firing harmless at the database level, whoever the owner is.

Use both. This is the standard argument (from Martin Kleppmann's critique of Redlock) that **lock-based mutual exclusion needs fencing to be safe**.

## Key takeaways
- Long delays belong in durable scheduling state rather than an out-of-range queue timer.
- Timing wheels accelerate near-future work while the database remains authoritative.
- Install ownership epochs at the protected store; a lease alone cannot reject a paused old process.

## Further reading
- [How to do distributed locking (Martin Kleppmann)](https://martin.kleppmann.com/2016/02/08/how-to-do-distributed-locking.html)
- [Amazon SQS visibility timeout (AWS docs)](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-visibility-timeout.html)
- [ZooKeeper recipes: leader election and locks](https://zookeeper.apache.org/doc/current/recipes.html)
- [Leader election (Wikipedia)](https://en.wikipedia.org/wiki/Leader_election)
- [SQS delay queue limit](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-delay-queues.html)
