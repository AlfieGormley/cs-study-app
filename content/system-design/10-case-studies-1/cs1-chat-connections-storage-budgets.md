---
id: cs1-chat-connections-storage-budgets
title: Budget chat connections, heartbeats and storage
level: advanced
minutes: 5
summary: Use explicit traffic and per-gateway assumptions.
sourceLesson: cs1-chat-system
---

Chat separates several requirements that a single messages-per-second estimate hides: live connections, durable acceptance, ordering, device recovery and retained history.

## State the contract

For this hypothetical design, support direct and group messages, device delivery acknowledgements, offline recovery, presence and end-to-end encryption. An illustrative group limit is 1,000 members; it is not a current provider limit.

Define latency for online recipients separately from offline delivery. Define which failures acknowledged messages must survive, how long undelivered work is retained and what happens when a device never returns. No deployment can promise unconditional delivery or durability against every failure.

## Size distinct resources

- **Connections:** each gateway owns open sockets, TLS state and buffers. Connection count alone does not establish message throughput.
- **Heartbeats:** more connected devices and shorter intervals create more background traffic even when nobody sends a message. Include responses, registry refreshes, mobile battery and failure-detection delay.
- **Messages:** group and multi-device delivery amplify the work beyond sender message count. Measure payload sizes and the required acknowledgements.
- **Recovery:** a gateway failure creates reconnects, authentication and catch-up work. Reserve capacity and use bounded backoff with jitter; random delays do not guarantee evenly spaced arrivals.

Historical connection experiments do not prove the capacity of this TLS and message workload. Benchmark the selected runtime, hardware, buffers and protocol at the promised latency and failure load.

## Retention and media

Keeping only undelivered server-side messages and retaining searchable history are different product choices. Either can coexist with encrypted storage, subject to the key and device-recovery design. Budget history, replicas, indexes and backups separately from transient socket state.

Media can dominate bytes even when only a small share of messages contains it. Use a separate upload and retrieval path, with the chat envelope carrying an authorised reference. A gateway must never be the only durable copy of accepted work: reconnects recover from the inbox or retained history.

## Key takeaways

- Budget connections, heartbeats, messages and reconnect work separately.
- State durability, retention and offline recovery limits explicitly.
- Measure history and media costs rather than inferring them from text-message traffic.

## Further reading

- [Discord: partitioned message storage](https://discord.com/blog/how-discord-stores-trillions-of-messages)
- [Slack: live messaging architecture](https://slack.engineering/real-time-messaging/)
- [Meta: WhatsApp multi-device design](https://engineering.fb.com/2021/07/14/security/whatsapp-multi-device/)
