---
id: cs1-chat-contract-partitions-path
title: Connect socket frames to partitioned message storage
level: advanced
minutes: 4
summary: Use persistent sockets for bidirectional live delivery.
sourceLesson: cs1-chat-system
---

## Step 3: API

Clients hold a persistent **WebSocket** connection (over TLS) for live message traffic. HTTP polling would mean either high latency or a flood of empty requests; WebSockets give a full-duplex channel with tiny per-message overhead. Long polling or server-sent events are fallbacks for restrictive networks.

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

REST endpoints for everything that isn't live socket traffic:

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

The dominant query is "the latest 50 messages in this conversation, older than the one I'm looking at": a range scan within one partition, ordered by sequence. That's exactly what a wide-column store does well. Discord stores trillions of messages this way, partitioned by channel plus a **time bucket** (a fixed time interval) so retained history is split across partitions. Bytes within an interval still depend on message rate and size.

> [!example] Discord's Cassandra to ScyllaDB migration
> By 2022 Discord's messages cluster had grown from 12 Cassandra nodes (2017) to 177, and it suffered from **hot partitions**: a huge server announcing something sends thousands of users to read the same channel bucket at once, overloading the few replicas that hold it. Latency spikes then spread through the cluster, and JVM garbage-collection pauses made it worse.
>
> Discord's fix had two parts. It put **data services written in Rust** between the API and the database, routed by channel with consistent hashing, which perform **request coalescing**: if many users ask for the same rows at the same moment, the database is queried once. Then it migrated to **ScyllaDB** (a C++ reimplementation of Cassandra without a JVM), copying data at up to about 3.2 million messages/s with an initial estimate of nine days; the article reports completion after several days and a final tombstone cleanup. The new cluster of **72 nodes** brought p99 history reads from 40–125 ms down to about 15 ms, and p99 inserts from 5–70 ms to a steady 5 ms.
>
> The lesson for interviews: partitioning by `(channel, time bucket)` bounds the covered time span, but neither byte size nor concurrent demand. Coalescing and caching in front of the store handle those.

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

## Key takeaways

- Use persistent sockets for bidirectional live delivery.
- Partition history by conversation and time bucket, while protecting hot reads.
- Persist message and recoverable fan-out before the sender acknowledgement.

## Further reading

- [Discord: how Discord stores trillions of messages](https://discord.com/blog/how-discord-stores-trillions-of-messages)
- [RFC 6455: WebSocket protocol](https://www.rfc-editor.org/rfc/rfc6455.html)
