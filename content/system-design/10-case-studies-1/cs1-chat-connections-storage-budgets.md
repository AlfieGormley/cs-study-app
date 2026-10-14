---
id: cs1-chat-connections-storage-budgets
title: Budget chat connections, heartbeats and storage
level: advanced
minutes: 5
summary: Use explicit traffic and per-gateway assumptions.
sourceLesson: cs1-chat-system
---

Chat looks like the news feed's cousin, but its constraints are different. Messages must arrive in **well under a second**, must **never be lost**, must appear **in the same order** for everyone in a conversation, and the system has to know, for hundreds of millions of devices, which server each one is connected to *right now*.

It's also the problem where the server stops being stateless. Each connected client is pinned to a gateway holding its open socket, and much of the design is about living with that.

## Step 1: Requirements

**Functional**

- 1:1 messaging and group messaging (assume a product limit of about 1,000 members; this is not a claim about a current provider limit).
- Text plus media (images, video, voice notes).
- **Read receipts**: sent (server has it), delivered (recipient's device has it), read.
- **Offline delivery**: messages to an offline user are recovered when they reconnect, and a push notification attempts to wake their phone.
- **Presence indicators**: online / last seen; optionally typing indicators.
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

```formula
daily = 500M × 40 = 20B/day
avg = 20B / (10^5 s) ≈ 200,000/s
peak = 200,000/s × 3 = 600,000/s
where
daily: messages sent per day
avg: average messages per second
peak: messages per second at the busiest time, using an assumed peak factor of 3
M: million (10^6)
B: billion (10^9)
day: one day; /day means per day
10^5: 100,000, the seconds in a day (86,400) rounded up
s: seconds; /s means per second
≈: approximately equal to (rounded)
In words: 500 million users sending 40 messages a day is 20 billion a day, about 200,000 a second, and about 600,000 a second at peak.
```

Concurrent connections: if ~half of DAU are connected at peak, that's **250 million open sockets**. How many per server? In January 2012 WhatsApp reported pushing a single FreeBSD/Erlang server (24 logical CPUs, about 96 GB of RAM) past **2 million** TCP connections, with CPU still around 40% idle. That historical report does not establish this design's production TLS/message throughput. For the arithmetic below, explicitly assume 250,000 connections per gateway; validate that with the actual workload.

```formula
gateways = conns / cap
gateways = 250M / (250k) = 1,000
pings = conns / interval
pings = 250M / (30 s) ≈ 8M/s
where
gateways: gateway servers needed
conns: open connections at peak, 250 million
cap: connections one gateway holds, an assumed 250,000 (250k)
pings: heartbeat messages per second arriving across the fleet (each answered by a pong)
interval: time between heartbeats from one client, 30 seconds
M: million
k: thousand
s: seconds; /s means per second
≈: approximately equal to (8.3 million rounded)
In words: 250 million sockets at 250,000 per server needs about 1,000 gateways, and a heartbeat every 30 seconds from each is about 8 million pings a second, plus as many pongs.
```

Those heartbeats are tiny and handled by the gateways locally, but both connection memory and heartbeat/message processing must be included when sizing gateways. A gateway owns sockets, not the only durable message copy. The design retains unacknowledged messages in a server-side device inbox, so a failed gateway causes reconnects with jitter and redelivery rather than deleting the messages.

Storage depends on the product model:

- **WhatsApp-style** (store until delivered, history lives on devices): the server holds only undelivered messages, a small, fast-churning dataset.
- **Messenger/Slack/Discord-style** (server keeps history):

```formula
daily = 20 bn × 200 B = 4 TB
yearly = 4 TB × 365 ≈ 1.5 PB
where
daily: new message data per day, before replication
yearly: the same for a year
bn: billion (10^9) messages per day
B: bytes; about 200 per message (ciphertext plus metadata)
TB: terabyte, 10^12 bytes
PB: petabyte, 10^15 bytes (1,000 TB)
≈: approximately equal to (1.46 PB rounded)
In words: 20 billion 200-byte messages a day is 4 TB a day, about 1.5 PB a year before replication.
```

Media goes to object storage via a CDN, and messages carry only a reference. At, say, 5% of messages carrying 200 KB of media:

```formula
media = 20 bn × 0.05 × 200 KB = 200 TB
where
media: new media stored per day
bn: billion (10^9) messages per day
0.05: the share of messages carrying media (5%)
KB: kilobyte, 1,000 bytes
TB: terabyte, 10^12 bytes
In words: one message in twenty carrying a 200 KB photo adds 200 TB a day, fifty times the text, which is why media gets its own path.
```

## Key takeaways

- Use explicit traffic and per-gateway assumptions.
- Heartbeats create substantial work beyond message throughput.
- History retention and media dominate different storage paths.

## Further reading

- [WhatsApp: historical connection experiment](https://blog.whatsapp.com/1-million-is-so-2011)
- [Discord: partitioned message storage](https://discord.com/blog/how-discord-stores-trillions-of-messages)
