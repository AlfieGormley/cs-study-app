---
id: cs1-chat-device-acks-offline-sync
title: Use device acknowledgements and cursors for recovery
level: advanced
minutes: 3
summary: Keep sender outboxes and recipient inboxes until durable acknowledgement.
sourceLesson: cs1-chat-system
---

Assume the storage and fan-out intent from the previous path are durable under a declared failure model. Now define what the UI acknowledgements mean and how each device catches up after a lost connection.

## Deep dive 2: Delivery guarantees and receipts

The goal: **at-least-once delivery, with deduplication**, to avoid duplicate presentation within the declared retention and recovery model. This is not an unconditional end-to-end exactly-once guarantee.

- **Sender → server**: the client keeps a message in its local outbox until it receives the ack. On reconnect, it resends unacked messages; the server dedups on `clientMsgId`.
- **Server → recipient**: the message stays in the device's inbox until the device acks it. If the gateway pushes it and the connection drops before the ack, the message is redelivered on reconnect. The client dedups on `msgId`.
- **Persist before ack**: the server acks the sender only after a durable write (e.g. sufficient replicas plus commit-log synchronization and a declared failure model in Cassandra; quorum acknowledgement alone does not mean fsync completed). Acking first and persisting later risks losing a message the sender believes was sent.

Receipts map directly onto these acks:

| Tick | Meaning | Triggered by |
|---|---|---|
| 1 grey | Server has it | Durable write |
| 2 grey | Device has it | Recipient ack |
| 2 blue | Read | Chat opened |

Receipts are **cumulative cursors** (`upToSeq`), not one event per message. A device must persist every required message through that cursor before acknowledging it; advance cursors monotonically and never acknowledge across a missing message. Retention and permanent device loss bound the delivery guarantee. Reading 50 messages sends one receipt, not 50. In a group of 500, receipts are aggregated server-side ("read by 312") rather than sending 500 receipts to every member.

## Deep dive 6: Multi-device and offline sync

Each device has its own inbox and its own delivered cursor. When a desktop client comes online after a week, it asks "for each conversation, give me everything after my last seq", fetched from history in pages. With end-to-end encryption, each device has its own keys, so senders encrypt for each of the recipient's devices (WhatsApp's multi-device design works this way). A message to a friend with a phone and two laptops, sent from your phone while your own laptop is linked, becomes about four encrypted copies: one per recipient device plus one per other device of yours.

## Key takeaways

- Keep sender outboxes and recipient inboxes until durable acknowledgement.
- Redelivery requires stable message IDs and device deduplication.
- Advance cumulative cursors only across all required persisted messages.
- Separate each device’s history cursor and encryption session.

## Further reading

- [Meta: WhatsApp multi-device design](https://engineering.fb.com/2021/07/14/security/whatsapp-multi-device/)
- [Slack: live messaging architecture](https://slack.engineering/real-time-messaging/)
