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

The key tuning rule: **set the visibility timeout comfortably longer than your worst-case processing time.** Too short, and slow jobs reappear and are done twice. Too long, and a message whose worker really did crash sits hidden for the whole timeout before anyone retries it.

When SQS triggers AWS Lambda, AWS recommends a visibility timeout of at least **six times the function's timeout**, plus any batching window (`MaximumBatchingWindowInSeconds`). A function with a 2-minute timeout therefore wants at least 12 minutes. The margin exists because Lambda may need to retry a batch if the function is throttled, and all of that must happen before the messages reappear. Lambda refuses outright to connect a function whose timeout exceeds the queue's visibility timeout.

If jobs genuinely vary (a 10-second job sometimes takes 10 minutes), the worker can call `ChangeMessageVisibility` periodically as a heartbeat to extend its lease. That keeps a short timeout, so crashed work is retried quickly, without timing out healthy slow jobs. Extensions cannot take one receive beyond the 12-hour maximum: extending does not reset that limit.

> [!analogy] Real-world analogy: a meeting room booked in 30-minute slots
> You book a meeting room for 30 minutes. If you overrun without extending the booking, the next person is allowed to walk in, and now two meetings are happening in one room. If you finish early, you release the room so someone else can use it straight away.
>
> **How it maps:** Receiving a message is taking the booking; the visibility timeout is the slot length. Overrunning is a job that takes longer than the timeout, so a second worker receives it. Extending the booking is `ChangeMessageVisibility`, and releasing the room is `DeleteMessage`.
>
> **Where it stops:** A booking system normally never double-books an active slot, but an SQS standard queue can occasionally deliver a duplicate even inside the visibility window, so the lease is not an exclusive lock. And SQS never checks whether you are still "in the room": only a delete, an extension or the timeout changes anything.

## Key takeaways

- Visibility temporarily hides a delivery; SQS standard queues can still deliver a duplicate.
- Delete with the latest receipt handle after successful processing, and extend visibility when long jobs need it.
- For SQS-triggered Lambda, AWS recommends at least six times the function timeout plus the batching window.

## Further reading

- [Amazon SQS visibility timeout (AWS docs)](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-visibility-timeout.html)
- [SQS event source configuration (AWS Lambda)](https://docs.aws.amazon.com/lambda/latest/dg/services-sqs-configure.html)
