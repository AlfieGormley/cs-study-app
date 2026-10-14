---
id: cs1-chat-session-epochs-reconnect
title: Route devices with session epochs and safe reconnects
level: advanced
minutes: 3
summary: A gateway owns live sockets, so balance and drain connections deliberately.
sourceLesson: cs1-chat-system
---

The chat path uses a session registry to find each device’s current gateway. That mapping is a hint to a live route, while the durable inbox remains the recovery path if a socket or registry entry is stale.

## Deep dive 1: Connections and routing

### Gateways are stateful

Each gateway holds hundreds of thousands of long-lived sockets. They do little computation: TLS termination, heartbeats, framing. Languages and runtimes built for huge numbers of lightweight concurrent processes shine here: WhatsApp’s historical connection report used Erlang, and Discord’s published scaling account describes Elixir (on the same BEAM virtual machine) for its live messaging layer.

Load balancers distribute *new* connections; once connected, a device stays on its gateway until the socket drops. Use least-connections balancing for new sockets, since round-robin ignores how many long-lived connections each gateway already holds.

### Finding a user's gateway

The **session registry** maps `device_id → gateway_id`. Gateways register a connection epoch on connect; refresh and deletion compare that epoch so an old gateway cannot delete or extend a newer session. To deliver, the chat service reads the registry and sends the message to that gateway over an internal RPC or a per-gateway queue.

Registry entries can be stale. A phone that loses signal and reconnects to a different gateway may briefly have two entries, or an old one that hasn't expired. Store a **connection ID** (or epoch) with each entry, overwrite on reconnect, and have a gateway reply "not here" for a device it no longer holds, so the chat service re-reads the registry or leaves the message in the inbox for the next sync. The inbox makes a misrouted push harmless: nothing is deleted until the device acks.

An alternative is **pub/sub**: each gateway subscribes to channels for its connected users (Redis pub/sub, or a message bus), and the chat service publishes to `user:{id}`. This is simpler to reason about, but pub/sub systems such as Redis's are fire-and-forget, so you still need the inbox and acks for reliability.

### Reconnect storms

If a gateway with 250,000 connections crashes, all its clients reconnect at once. Clients must reconnect with **exponential backoff and jitter**, and gateways should be subject to **connection draining** gradually during deploys (stop accepting new connections, ask clients to move in batches). Otherwise a routine deploy becomes a self-inflicted DDoS.

## Key takeaways

- A gateway owns live sockets, so balance and drain connections deliberately.
- Guard registry refreshes and deletes with connection epochs.
- Recover from stale routing through inbox retention and retry, rather than dropping work.

## Further reading

- [Slack: live messaging architecture](https://slack.engineering/real-time-messaging/)
- [AWS: exponential backoff and jitter](https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/)
