---
id: msg-sqs-polling-payload-throughput
title: SQS polling, payloads and FIFO throughput
level: basic
minutes: 2
summary: Reduce empty receives, keep large payloads outside the queue and size FIFO traffic by message groups.
sourceLesson: msg-message-queues
---

Once acknowledgement timing is correct, the remaining SQS design choices are how to fetch efficiently, what belongs in the payload, and how ordered traffic is distributed.

## SQS limits, polling and FIFO throughput

Other SQS details worth knowing:

| Setting | Value |
|---|---|
| Max message size | 1 MiB (256 KB before 2025) |
| Retention | 1 min–14 days (default 4) |
| Long poll wait | up to 20 s |
| Batch receive | up to 10 messages |

For anything bigger than the limit (images, large documents), use the **claim check** pattern: store the payload in S3 and send a small message holding its key. AWS's extended client libraries do this for you.

Use **long polling** (`WaitTimeSeconds=20`). Short polling returns immediately even when the queue is empty, which wastes requests (and money, since SQS bills per request) and can miss messages because it samples only a subset of servers.

Standard SQS queues offer nearly unlimited throughput but only **best-effort ordering** and **at-least-once** delivery. **SQS FIFO queues** guarantee order within a *message group* and deduplicate within a 5-minute window, at lower throughput. Without high-throughput mode, a FIFO queue handles 300 API calls per second per action (`SendMessage`, `ReceiveMessage`, `DeleteMessage`). Each call can carry a batch of up to 10 messages, which sets the ceiling:

```formula
R_max = C × b
R_max = 300/s × 10 = 3000 msg/s
where
R_max: the most messages per second one action (for example SendMessage) can move
C: API calls per second allowed per action: 300 for a FIFO queue without high-throughput mode
b: messages per call (the batch size), at most 10 in SQS
msg: messages
s: seconds; "/s" means per second
In words: 300 calls a second, each carrying up to 10 messages, is at most 3,000 messages a second per action; unbatched it is only 300.
```

**High-throughput mode** spreads groups across internal partitions and raises this to thousands or tens of thousands of calls per second, depending on the region, provided you use many distinct message group IDs.

## Key takeaways

- Long polling reduces empty receive traffic; batches move up to ten messages per SQS API call.
- Use a claim check for large files: store the object and send its reference.
- FIFO orders each message group; high throughput also requires enough distinct groups to distribute load.

## Further reading

- [Amazon SQS message quotas (AWS docs)](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/quotas-messages.html)
