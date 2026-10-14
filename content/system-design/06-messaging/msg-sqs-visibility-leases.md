---
id: msg-sqs-visibility-leases
title: SQS visibility timeouts and processing leases
level: basic
minutes: 2
summary: Tune visibility for job duration and understand why receipt handles and timeouts do not guarantee exclusive work.
sourceLesson: msg-message-queues
---

SQS treats a received message as temporarily leased work. A worker must finish and delete it before that lease expires, or extend the lease while it continues.

## How SQS does it: visibility timeouts

Amazon SQS has no persistent connection between broker and consumer, so it cannot notice that a consumer died. Instead it uses a **visibility timeout**.

1. A consumer calls `ReceiveMessage`. SQS returns the message plus a **receipt handle**, and normally hides it from other consumers. Standard queues can still deliver duplicates during the visibility window, so visibility is not an exclusive-processing lock.
2. The message stays invisible for the visibility timeout (default **30 seconds**, maximum **12 hours**).
3. The consumer uses the most recent receipt handle with DeleteMessage after processing. Standard queues can occasionally redeliver even after deletion, and an obsolete receipt handle does not guarantee deletion.
4. If not, the message becomes visible again and another consumer can receive it.

```
0 s     receive m1 (invisible)
0–30 s  worker processing...
30 s    timeout: m1 visible again
31 s    worker B receives m1 (dup!)
```

(Times are seconds after the first receive.)

The key tuning rule: **set the visibility timeout comfortably longer than your worst-case processing time.** When SQS triggers AWS Lambda, AWS gives a recommended minimum, because Lambda may need to retry a throttled batch before the messages reappear:

```formula
V ≥ 6 × T_fn + T_batch
V ≥ 6 × 2 min + 0 min = 12 min
where
V: the queue's visibility timeout
≥: is at least
T_fn: the Lambda function's timeout, for example 2 minutes
T_batch: the batching window (MaximumBatchingWindowInSeconds) if you set one; 0 in this example
min: minutes
In words: give the queue at least six times the function's timeout, plus any batching window; a 2-minute function needs a visibility timeout of at least 12 minutes.
```

If jobs genuinely vary (a 10-second job sometimes takes 10 minutes), the worker can call `ChangeMessageVisibility` periodically as a heartbeat to extend its lease.

## Key takeaways

- Visibility temporarily hides a delivery; SQS standard queues can still deliver a duplicate.
- Delete with the latest receipt handle after successful processing, and extend visibility when long jobs need it.
- For SQS-triggered Lambda, AWS recommends at least six times the function timeout plus the batching window.

## Further reading

- [Amazon SQS visibility timeout (AWS docs)](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-visibility-timeout.html)
- [SQS event source configuration (AWS Lambda)](https://docs.aws.amazon.com/lambda/latest/dg/services-sqs-configure.html)
