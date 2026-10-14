---
id: api-persistent-gateway-fanout
title: Connection capacity and cross-gateway fan-out
level: advanced
minutes: 3
summary: Separate durable business state from live connection state and route messages across gateway owners.
sourceLesson: api-real-time
---

## Scaling persistent connections

Request/response servers are easy to scale because any server can handle any request. Persistent connections break that: each client is attached to *one* server for minutes or hours.

## Connection capacity

An idle connection consumes a socket, buffers, TLS state and application state. Measure memory and active traffic costs for the actual stack; idle capacity does not establish throughput under load.

> [!note] Content gap: connection capacity measurements
> No reproducible benchmark accompanies the generic per-connection memory and per-server capacity estimates previously presented here. Those estimates are omitted; the quiz supplies explicit hypothetical sizing inputs.

Limits to tune: file descriptors (`ulimit -n`), ephemeral ports on proxies, kernel socket buffers and TLS memory.

## The fan-out problem

Alice is connected to gateway A. Bob is on gateway C. Alice sends Bob a message. How does gateway A get it to C?

```
Alice        Bob
  |           |
+---+ +---+ +---+
| A | | B | | C |  WS gateways
+-+-+ +---+ +-+-+
  |  pub   sub|
  v           |
+---------------+
| pub/sub layer |
| Redis / Kafka |
+---------------+
```

The usual architecture:

1. **Gateway tier** that owns connection state while durable business state lives in services or storage. Keeping business logic separate can simplify scaling.
1. A **connection registry** mapping `user → gateway` (in Redis), or a **pub/sub** channel per user, room or topic.
1. Business logic in ordinary services, which publish messages; the gateway subscribed for that user or channel delivers them.

Slack's real-time architecture works like this: channel servers hold state for channels, gateway servers hold the WebSocket connections, and messages are routed between them. Socket.IO's Redis adapter does the same at small scale, using Redis pub/sub to broadcast across nodes.

For memory sizing, first reserve the OS/runtime allocation, divide the remaining memory by measured memory per connection, apply the target utilisation headroom, then divide the required client count by that per-server allowance and round the server count upwards. CPU, file descriptors and reconnect handshakes may constrain the deployment earlier.

## Key takeaways
- Measure per-connection costs and allow capacity headroom; idle capacity does not establish active throughput.
- A registry or pub/sub layer reaches clients attached to other gateways.
- Keep durable business state in services or storage while gateways own connection state.

## Further reading
- [Slack engineering: Real-time messaging](https://slack.engineering/real-time-messaging/)
- [Discord: How Discord scaled Elixir to 5,000,000 concurrent users](https://discord.com/blog/how-discord-scaled-elixir-to-5-000-000-concurrent-users)
- [Socket.IO: Redis adapter](https://socket.io/docs/v4/redis-adapter/)
