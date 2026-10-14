---
id: cs1-chat-encryption-regional-growth
title: Account for encrypted clients and regional recovery
level: advanced
minutes: 3
summary: The selected E2EE design performs search and message rendering on devices.
sourceLesson: cs1-chat-system
---

Earlier units defined durable acknowledgements, ordered conversations and device recovery. End-to-end encryption changes where content operations can run, while regional scale adds a new failure boundary.

## Deep dive 7: What end-to-end encryption changes

With the Signal Protocol the server routes ciphertext and never sees content. That removes several things a staff interviewer may probe:

- **No server-side search or indexing.** Search runs on the device over its local history.
- **New devices need a secure history/key-transfer protocol.** E2EE can coexist with server-stored encrypted history or encrypted backups; a trusted existing device can also transfer history and keys. Retaining only undelivered messages is a product/storage choice, not a requirement of encryption.
- **Push notifications can't contain the text.** Send a generic or encrypted payload, and let the app decrypt and show the message locally.
- **Abuse handling** relies on metadata and user reports (which include the reported messages), not content scanning.
- **Key changes** (a reinstalled app, a new device) must be distributed to contacts, and clients warn when a contact's key changes.

The server's job shrinks to routing, storage of opaque blobs, and key distribution, which makes it simpler but moves work and trust to the clients.

## Bottlenecks and trade-offs

| Decision | Trade-off |
|---|---|
| WebSockets | Live delivery, stateful servers |
| Persist before ack | Durable, adds a write to latency |
| Per-conv sequence | Total order, single owner per conv |
| Push for small groups | Fast, write amplification |
| Pull for big channels | Cheap writes, cursor complexity |

Failure modes to cover:

- **Gateway crash**: clients reconnect with jitter; unacked messages are still in inboxes and are redelivered.
- **Chat service owner failure**: another instance takes over the conversation's partition; it must recover the last `seq` from the store before assigning new ones, or it will issue duplicates, and an epoch-fenced lease stops the old owner writing if it comes back.
- **Region failure**: users reconnect to another region; inboxes and history must be replicated there, according to the promised recovery point. Asynchronous replication can lose acknowledged messages if the source region is permanently lost before replication.

## At 10x scale

At five billion users’ worth of assumed traffic, ten times the preceding scenario means about six million messages a second at peak and billions of connections:

- **Regional gateways and chat services**, with users homed to a region and cross-region routing only for conversations that span regions.
- **Tiered storage**: recent messages on fast SSD clusters, older history compacted onto cheaper storage.
- **More aggressive presence economy**: coarser "last seen", presence only for open chats.
- **Media** handled entirely through pre-signed uploads to object storage and CDN delivery, keeping the message path tiny.
- **Connection efficiency** can become a major cost driver; compare it with measured media, storage and egress costs: invest in the gateway runtime (Erlang/Elixir, or carefully tuned event loops), and compress plaintext only under an appropriate security design before encryption (ciphertext itself generally does not compress), and tune heartbeats to keep mobile battery and bandwidth costs down.

## Key takeaways

- The selected E2EE design performs search and message rendering on devices.
- Encrypted history retention and backups remain product choices.
- Asynchronous regional replication needs a declared recovery point.
- Scale sockets, presence, media and history as separate costs.

## Further reading

- [Meta: WhatsApp multi-device design](https://engineering.fb.com/2021/07/14/security/whatsapp-multi-device/)
- [Signal: Double Ratchet specification](https://signal.org/docs/specifications/doubleratchet/)
- [Slack: live messaging architecture](https://slack.engineering/real-time-messaging/)
