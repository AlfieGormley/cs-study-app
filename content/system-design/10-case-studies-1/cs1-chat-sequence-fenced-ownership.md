---
id: cs1-chat-sequence-fenced-ownership
title: Order conversations with fenced sequence ownership
level: advanced
minutes: 3
summary: Order by committed server sequences rather than phone clocks.
sourceLesson: cs1-chat-system
---

Delivery can be retried and devices can reconnect in any order. A conversation nevertheless needs one committed display order. This unit combines server sequence allocation with fencing so a paused former owner cannot keep writing.

## Deep dive 3: Ordering

Client clocks can't be trusted: phones drift, and users change their clocks. Two messages sent a millisecond apart from different phones might carry timestamps in the wrong order.

Instead, give each conversation a **server-assigned, monotonically increasing sequence number**:

- Route all writes for a conversation to one owner (partition the chat service by `conv_id`, e.g. with consistent hashing), which increments a counter per conversation. A single owner can be adequate for the assumed group rate; benchmark high-volume channels and bound their queues.
- Alternatively, store the counter in the database and use an atomic increment or conditional write (a lightweight transaction in Cassandra), which is slower but needs no single owner.
- Guard against **two owners** after a failover: an old owner that was only paused (a long GC pause, a network blip) may wake up and keep assigning numbers. Give each ownership a lease with an epoch number (a fencing token), and make the message write conditional on the current epoch, so a stale owner's writes are rejected.
- Clients display messages in `seq` order. If sequences are committed contiguously, seeing 41 then 43 signals a gap. If failed allocations, deletions or filtering create intentional gaps, the protocol must distinguish those so clients do not wait forever.

This gives **total order per conversation**: everyone sees the same order, even if two people "talked over each other". There's no global order across conversations, and none is needed.

What about messages typed while offline? The client shows them optimistically in a "pending" state; they get their real `seq` when the server accepts them and may slot in after messages that arrived in the meantime. The product should document this pending-to-committed ordering behavior.

## Recover the committed boundary

A new owner must recover the durable sequence state before allocating further messages. Sequence allocation, message persistence and ownership validation need a coherent atomic contract: a separate increment followed by a failed write may create an intentional gap, whereas reusing an increment after failover may duplicate order positions. The client protocol must explain both cases.

A lease expiration alone does not stop an old process. It may be paused and unaware that its lease expired. Store a monotonically increasing ownership epoch and make every write validate it at the resource that accepts the message. An expired owner’s delayed request then fails even if its local process believes it is still active. This is separate from the session epoch used to protect gateway routing.

## Key takeaways

- Order by committed server sequences rather than phone clocks.
- Reject writes from stale ownership epochs at storage.
- Distinguish missing required messages from intentional sequence gaps.

## Further reading

- [Slack: live messaging architecture](https://slack.engineering/real-time-messaging/)
- [Cassandra: lightweight transactions](https://cassandra.apache.org/doc/latest/cassandra/developing/cql/dml.html)
