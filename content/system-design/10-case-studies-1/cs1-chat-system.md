---
id: cs1-chat-system
title: Design a chat system like WhatsApp
level: advanced
minutes: 23
summary: Design 1:1 and group messaging for hundreds of millions of users, covering WebSocket gateways, message routing, delivery and read receipts, offline delivery, per-conversation ordering and presence.
---

Chat looks like the news feed's cousin, but its constraints are different. Messages must arrive in **well under a second**, must **never be lost**, must appear **in the same order** for everyone in a conversation, and the system has to know, for hundreds of millions of devices, which server each one is connected to *right now*.

It's also the problem where the server stops being stateless. Each connected client is pinned to a gateway holding its open socket, and much of the design is about living with that.

## Step 1: Requirements

**Functional**

- 1:1 messaging and group messaging (assume a product limit of about 1,000 members; this is not a claim about a current provider limit).
- Text plus media (images, video, voice notes).
- **Receipts**: sent (server has it), delivered (recipient's device has it), read.
- **Offline delivery**: messages to an offline user are delivered when they reconnect, and a push notification wakes their phone.
- **Presence**: online / last seen; optionally typing indicators.
- **Multi-device**: a phone plus a desktop or web client.

**Non-functional**

- **Low latency**: end-to-end delivery under ~500 ms when both users are online (typically far less).
- **Durability**: once the sender sees "sent", the message must not be lost.
- **Ordering**: messages in a conversation appear in the same order for every participant.
- **High availability**, with graceful reconnects.
- **End-to-end encryption**: the server routes ciphertext it can't read.

Out of scope: voice/video calls, stories, payments.

## Step 2: Estimates

Assume **500 million DAU**, each sending **40 messages/day**. These are hypothetical design inputs, not current WhatsApp usage figures.

```
Messages: 500M x 40 = 20B/day
Average:  20B / 10^5 s ≈ 200,000/s
Peak (x3)              ≈ 600,000/s
```

Concurrent connections: if ~half of DAU are connected at peak, that's **250 million open sockets**. How many per server? In January 2012 WhatsApp reported pushing a single FreeBSD/Erlang server (24 cores, about 100 GB of RAM) past **2 million** TCP connections, with CPU still around 40% idle. That historical report does not establish this design's production TLS/message throughput. For the arithmetic below, explicitly assume 250,000 connections per gateway; validate that with the actual workload.

```
250M / 250k per gateway ≈ 1,000 gateways
Heartbeats: 250M / 30 s ≈ 8M pings/s
            plus corresponding pongs
```

Those heartbeats are tiny and handled by the gateways locally, but both connection memory and heartbeat/message processing must be included when sizing gateways.

Storage depends on the product model:

- **WhatsApp-style** (store until delivered, history lives on devices): the server holds only undelivered messages, a small, fast-churning dataset.
- **Messenger/Slack/Discord-style** (server keeps history):

```
20B x ~200 B (ciphertext + metadata)
  ≈ 4 TB/day
  ≈ 1.5 PB/year (before replication)
```

Media goes to object storage via a CDN, and messages carry only a reference. At, say, 5% of messages carrying 200 KB of media: `20B × 0.05 × 200 KB = 200 TB/day`, which is why media gets its own path.

## Step 3: API

Clients hold a persistent **WebSocket** connection (over TLS) for real-time traffic. HTTP polling would mean either high latency or a flood of empty requests; WebSockets give a full-duplex channel with tiny per-message overhead. Long polling or server-sent events are fallbacks for restrictive networks.

Frames over the socket:

```
-> send   {clientMsgId, convId, body}
<- ack    {clientMsgId, msgId, seq}
<- msg    {msgId, convId, seq, from, body}
-> recv   {convId, upToSeq}      delivered
-> read   {convId, upToSeq}      read
<- receipt{convId, userId, upToSeq, type}
-> ping / <- pong                heartbeat
```

REST endpoints for everything that isn't real-time:

```
GET  /v1/conversations/{id}/messages
     ?beforeSeq=...&limit=50
POST /v1/media   -> upload URL
POST /v1/groups  {name, members}
```

`clientMsgId` is a UUID generated on the device. If the client retries a send after a dropped connection, the server sees the same ID and doesn't create a duplicate.

## Step 4: Data model

```
messages   (Cassandra/ScyllaDB)
  PK: (conv_id, bucket)  cluster: seq
  msg_id, sender_id, body, created_at

conversations / members
  conv_id, type (1:1|group), members[]

inbox      (per device, undelivered)
  device_id -> [msg refs], until acked

cursors
  (conv_id, device_id) -> delivered_seq,
                        read_seq

sessions   (Redis, TTL'd)
  device_id -> gateway_id, connected_at
```

The dominant query is "the latest N messages in conversation X, older than Y": a range scan within one partition, ordered by sequence. That's exactly what a wide-column store does well. Discord stores trillions of messages this way, partitioned by channel plus a **time bucket** (a static time window) so a busy channel's partition doesn't grow without bound.

> [!example] Discord's Cassandra to ScyllaDB migration
> By 2022 Discord's messages cluster had grown from 12 Cassandra nodes (2017) to 177, and it suffered from **hot partitions**: a huge server announcing something sends thousands of users to read the same channel bucket at once, overloading the few replicas that hold it. Latency spikes then spread through the cluster, and JVM garbage-collection pauses made it worse.
>
> Discord's fix had two parts. It put **data services written in Rust** between the API and the database, routed by channel with consistent hashing, which perform **request coalescing**: if many users ask for the same rows at the same moment, the database is queried once. Then it migrated to **ScyllaDB** (a C++ reimplementation of Cassandra without a JVM), copying data at up to about 3.2 million messages/s with an initial estimate of nine days; the article reports completion after several days and a final tombstone cleanup. The new cluster of **72 nodes** brought p99 history reads from 40–125 ms down to about 15 ms, and p99 inserts from 5–70 ms to a steady 5 ms.
>
> The lesson for interviews: partitioning by `(channel, time bucket)` solves unbounded partitions, but not *hot* ones. Coalescing and caching in front of the store handle those.

## Step 5: High-level design

```
 Client A            Client B
    | WebSocket         ^
    v                   |
 Gateway 12         Gateway 87
    |                   ^
    v                   |
 Chat service ----------+
  |      |       |
  v      v       v
 Msg   Session  Push svc
 store registry (APNs/FCM)
```

Walk through Alice sending "hi" to Bob:

1. Alice's app sends `{clientMsgId, convId, "hi"}` over her socket to **Gateway 12**.
2. The gateway forwards it to the **chat service** responsible for that conversation.
3. The chat service atomically enforces deduplication on `(sender_id, clientMsgId)` and message persistence, assigns the next **sequence number** for the conversation, and **persists** the message (to the message store or Bob's inbox).
4. Only after the required durable write and recoverable fan-out intent succeed does it **ack** Alice. The tick mapping here is this design's UI contract, not a claim about WhatsApp server internals.
5. It looks up Bob's devices in the **session registry**: Bob's phone is on Gateway 87.
6. It forwards the message to Gateway 87, which pushes it down Bob's socket.
7. Bob's phone acks receipt; the chat service updates Bob's delivered cursor and sends Alice a **delivered** receipt: two ticks.
8. When Bob opens the chat, his app sends `read upToSeq`, which becomes Alice's **read** receipt.

If Bob is offline at step 5, the message waits in his inbox and the **push service** attempts an APNs/FCM wake-up notification. Push delivery and background execution are not guaranteed, so reconnect/history sync must recover messages independently.

## Deep dive 1: Connections and routing

### Gateways are stateful

Each gateway holds hundreds of thousands of long-lived sockets. They do little computation: TLS termination, heartbeats, framing. Languages and runtimes built for huge numbers of lightweight concurrent processes shine here: WhatsApp is built on Erlang, and Discord uses Elixir (on the same BEAM virtual machine) for its real-time layer.

Load balancers distribute *new* connections; once connected, a device stays on its gateway until the socket drops. Use least-connections balancing for new sockets, since round-robin ignores how many long-lived connections each gateway already holds.

### Finding a user's gateway

The **session registry** maps `device_id → gateway_id`. Gateways register a connection epoch on connect; refresh and deletion compare that epoch so an old gateway cannot delete or extend a newer session. To deliver, the chat service reads the registry and sends the message to that gateway over an internal RPC or a per-gateway queue.

Registry entries can be stale. A phone that loses signal and reconnects to a different gateway may briefly have two entries, or an old one that hasn't expired. Store a **connection ID** (or epoch) with each entry, overwrite on reconnect, and have a gateway reply "not here" for a device it no longer holds, so the chat service re-reads the registry or leaves the message in the inbox for the next sync. The inbox makes a misrouted push harmless: nothing is deleted until the device acks.

An alternative is **pub/sub**: each gateway subscribes to channels for its connected users (Redis pub/sub, or a message bus), and the chat service publishes to `user:{id}`. This is simpler to reason about, but pub/sub systems such as Redis's are fire-and-forget, so you still need the inbox and acks for reliability.

### Reconnect storms

If a gateway with 250,000 connections crashes, all its clients reconnect at once. Clients must reconnect with **exponential backoff and jitter**, and gateways should be **drained** gradually during deploys (stop accepting new connections, ask clients to move in batches). Otherwise a routine deploy becomes a self-inflicted DDoS.

## Deep dive 2: Delivery guarantees and receipts

The goal: **at-least-once delivery, with deduplication**, so users experience exactly-once.

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

## Deep dive 3: Ordering

Client clocks can't be trusted: phones drift, and users change their clocks. Two messages sent a millisecond apart from different phones might carry timestamps in the wrong order.

Instead, give each conversation a **server-assigned, monotonically increasing sequence number**:

- Route all writes for a conversation to one owner (partition the chat service by `conv_id`, e.g. with consistent hashing), which increments a counter per conversation. A single owner can be adequate for the assumed group rate; benchmark high-volume channels and bound their queues.
- Alternatively, store the counter in the database and use an atomic increment or conditional write (a lightweight transaction in Cassandra), which is slower but needs no single owner.
- Guard against **two owners** after a failover: an old owner that was only paused (a long GC pause, a network blip) may wake up and keep assigning numbers. Give each ownership a lease with an epoch number (a fencing token), and make the message write conditional on the current epoch, so a stale owner's writes are rejected.
- Clients display messages in `seq` order. If sequences are committed contiguously, seeing 41 then 43 signals a gap. If failed allocations, deletions or filtering create intentional gaps, the protocol must distinguish those so clients do not wait forever.

This gives **total order per conversation**: everyone sees the same order, even if two people "talked over each other". There's no global order across conversations, and none is needed.

What about messages typed while offline? The client shows them optimistically in a "pending" state; they get their real `seq` when the server accepts them and may slot in after messages that arrived in the meantime. The product should document this pending-to-committed ordering behavior.

## Deep dive 4: Group messaging

### Small groups (up to ~1,000): fan-out on write

When a message is sent to a 200-member group, the chat service writes it once and enqueues a reference into each member device's inbox, then routes it to whichever devices are online. 200 deliveries per message is fine at these group sizes.

With **end-to-end encryption**, fan-out also involves the client. Encrypting separately for each member device would make a 1,000-device group cost 1,000 encryptions per message, so the Signal Protocol's **sender keys** scheme (used by WhatsApp for groups) has each sender distribute sender-key material securely to members, updating it when required by membership/security changes, then encrypt each message a single time. The server fans out one ciphertext.

### Large channels (10k–1M members): fan-out on read

For Slack- or Discord-style channels with huge membership, writing to every member's inbox is wasteful because most members aren't looking. Instead:

- Store the message once in the channel's partition.
- Push it only to **currently connected** members who have that channel open or subscribed (pub/sub per channel).
- Everyone else fetches it from the channel history when they open the app, using their per-channel read cursor to show unread counts.

This is the feed's push vs pull trade-off again, decided by group size.

## Deep dive 5: Presence

Presence ("online", "last seen 10:42") is deceptively expensive because every change potentially interests many people.

- **Heartbeats**: the client pings every ~30 s; the gateway updates `presence:{user}` in Redis with a TTL of ~60–90 s. No heartbeat, key expires, user is offline. This handles phones that vanish without a clean disconnect (a tunnel, a dead battery).
- **Debounce flapping**: mobile connections drop and reconnect constantly. Wait a few seconds before announcing "offline", or you'll broadcast storms of online/offline transitions.
- **Fan-out only to interested viewers**: if a user with 500 contacts goes online, don't push to all 500. Push presence only to users who currently have a chat with them open (who have subscribed), and let everyone else fetch presence lazily when they open the chat.
- **Typing indicators** are ephemeral: send them over the socket, never persist them, and drop them freely under load.

Without these optimisations, presence traffic can easily exceed message traffic.

## Deep dive 6: Multi-device and offline sync

Each device has its own inbox and its own delivered cursor. When a desktop client comes online after a week, it asks "for each conversation, give me everything after my last seq", fetched from history in pages. With end-to-end encryption, each device has its own keys, so senders encrypt for each of the recipient's devices (WhatsApp's multi-device design works this way). A message to a friend with a phone and two laptops, sent from your phone while your own laptop is linked, becomes about four encrypted copies: one per recipient device plus one per other device of yours.

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
| WebSockets | Real-time, stateful servers |
| Persist before ack | Durable, adds a write to latency |
| Per-conv sequence | Total order, single owner per conv |
| Push for small groups | Fast, write amplification |
| Pull for big channels | Cheap writes, cursor complexity |

Failure modes to cover:

- **Gateway crash**: clients reconnect with jitter; unacked messages are still in inboxes and are redelivered.
- **Chat service owner failure**: another instance takes over the conversation's partition; it must recover the last `seq` from the store before assigning new ones, or it will issue duplicates, and an epoch-fenced lease stops the old owner writing if it comes back.
- **Region failure**: users reconnect to another region; inboxes and history must be replicated there, according to the promised recovery point. Asynchronous replication can lose acknowledged messages if the source region is permanently lost before replication.

## At 10x scale

At 5 billion users' worth of traffic (~6M messages/s at peak, billions of connections):

- **Regional gateways and chat services**, with users homed to a region and cross-region routing only for conversations that span regions.
- **Tiered storage**: recent messages on fast SSD clusters, older history compacted onto cheaper storage.
- **More aggressive presence economy**: coarser "last seen", presence only for open chats.
- **Media** handled entirely through pre-signed uploads to object storage and CDN delivery, keeping the message path tiny.
- **Connection efficiency** becomes the main cost driver: invest in the gateway runtime (Erlang/Elixir, or carefully tuned event loops), and compress plaintext only under an appropriate security design before encryption (ciphertext itself generally does not compress), and tune heartbeats to keep mobile battery and bandwidth costs down.

## Key takeaways

- Real-time delivery uses persistent WebSocket connections to stateful gateways, plus a session registry mapping each device to its gateway.
- Persist before acking the sender; use client message IDs and device acks for at-least-once delivery with deduplication.
- Receipts are cumulative cursors (`upToSeq`), aggregated for groups.
- Order messages with a server-assigned sequence per conversation, never with client clocks.
- Small groups fan out on write; very large channels store once and push only to online subscribers.
- Presence needs heartbeats with TTLs, debouncing and lazy fan-out, or it outgrows message traffic.
- Partitioning history by `(channel, time bucket)` bounds partition size; hot partitions need request coalescing and caching in front of the store, as Discord found.
- End-to-end encryption moves search, history and notification rendering onto the client.
- Offline users get an inbox plus a push notification; reconnects need jittered backoff to avoid storms.

## Further reading

- [WhatsApp blog: 1 million is so 2011](https://blog.whatsapp.com/1-million-is-so-2011)
- [Discord: how Discord stores trillions of messages](https://discord.com/blog/how-discord-stores-trillions-of-messages)
- [Meta engineering: how WhatsApp enables multi-device capability](https://engineering.fb.com/2021/07/14/security/whatsapp-multi-device/)
- [Discord: how Discord scaled Elixir to 5,000,000 concurrent users](https://discord.com/blog/how-discord-scaled-elixir-to-5-000-000-concurrent-users)
- [Slack engineering: real-time messaging](https://slack.engineering/real-time-messaging/)
- [Meta engineering: building mobile-first infrastructure for Messenger](https://engineering.fb.com/2014/10/09/production-engineering/building-mobile-first-infrastructure-for-messenger/)
- [MDN: the WebSocket API](https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API)
- [ByteByteGo: how Slack supports billions of daily messages](https://blog.bytebytego.com/p/how-slack-supports-billions-of-daily)
- [Signal Protocol (Wikipedia)](https://en.wikipedia.org/wiki/Signal_Protocol)
