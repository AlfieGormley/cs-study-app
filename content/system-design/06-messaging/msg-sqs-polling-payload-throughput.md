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

Other SQS details worth knowing (quotas as of 2026):

| Setting | Value |
|---|---|
| Max message size | 1 MiB (256 KB before 2025) |
| Retention | 1 min–14 days (default 4) |
| Long poll wait | up to 20 s |
| Batch receive | up to 10 messages |

For anything bigger than the limit (images, large documents), use the **claim check** pattern: store the payload in S3 and send a small message holding its key. AWS's extended client libraries do this for you.

Use **long polling** (`WaitTimeSeconds=20`). Short polling returns immediately even when the queue is empty, which wastes requests (and money, since SQS bills per request) and can miss messages because it samples only a subset of servers.

Standard SQS queues offer nearly unlimited throughput but only **best-effort ordering** and **at-least-once** delivery. **SQS FIFO queues** guarantee order within a *message group* and deduplicate within a 5-minute window, at lower throughput. Without high-throughput mode, a FIFO queue handles 300 API calls per second per action (`SendMessage`, `ReceiveMessage`, `DeleteMessage`). Each call can carry a batch of up to 10 messages, so batching is what lifts the ceiling from 300 to about 3,000 messages per second per action. If a FIFO producer throttles at exactly 300 or 3,000 messages a second, that limit is the first suspect.

**High-throughput mode** spreads message groups across internal partitions and raises the limit to thousands or tens of thousands of calls per second, depending on the region (as of 2026). SQS hashes each message group ID to choose a partition, so the extra capacity only appears if you use many distinct message group IDs. Every message in one group still lands on one partition, because the group's order must be kept.

## Key takeaways

- Long polling reduces empty receive traffic; batches move up to ten messages per SQS API call.
- Use a claim check for large files: store the object and send its reference.
- FIFO orders each message group; high throughput also requires enough distinct groups to distribute load.

## Further reading

- [Amazon SQS message quotas (AWS docs)](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/quotas-messages.html)
