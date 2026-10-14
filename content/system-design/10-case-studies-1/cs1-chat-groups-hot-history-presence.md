---
id: cs1-chat-groups-hot-history-presence
title: Scale group delivery and interested-viewer presence
level: advanced
minutes: 3
summary: Push references for small groups and pull history for very large channels.
sourceLesson: cs1-chat-system
---

Conversation history is partitioned by conversation and a time bucket, and every device has a cursor. Group size determines how much delivery is precomputed; presence uses a different, ephemeral path.

## Deep dive 4: Group messaging

### Small groups (up to ~1,000): fan-out on write

When a message is sent to a 200-member group, the chat service writes it once and enqueues a reference into each member device's inbox, then routes it to whichever devices are online. The delivery amplification is 200 members in this one-device-per-member example; benchmark the resulting rate and account for multiple devices.

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

## Size the busiest bucket

At an assumed 50 messages a second and 200 bytes each, a busy channel adds 10 kilobytes a second. A 100-megabyte raw partition target lasts about 10,000 seconds, or 2.8 hours, before replication and database overhead. Choose a shorter bucket or an additional split when observed rates exceed this assumption. A popular announcement can overload readers of the current bucket even when the bucket is small; request coalescing reduces duplicate reads of those same rows.

## Key takeaways

- Push references for small groups and pull history for very large channels.
- Protect hot channel buckets with caching and request coalescing.
- A fixed time span does not guarantee a byte bound during a burst.
- Debounce presence changes and notify only interested viewers.

## Further reading

- [Discord: partitioned message storage](https://discord.com/blog/how-discord-stores-trillions-of-messages)
- [Meta: WhatsApp multi-device design](https://engineering.fb.com/2021/07/14/security/whatsapp-multi-device/)
- [Discord: scaling Elixir](https://discord.com/blog/how-discord-scaled-elixir-to-5-000-000-concurrent-users)
