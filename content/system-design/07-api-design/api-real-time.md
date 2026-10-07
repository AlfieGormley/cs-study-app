---
id: api-real-time
title: Real-time communication
level: advanced
minutes: 14
summary: Short polling, long polling, Server-Sent Events and WebSockets compared, and how to scale millions of persistent connections.
---

HTTP was designed for request/response: the client asks, the server answers. But chat messages, live scores, ride locations, stock prices and collaborative cursors all need the **server** to push data to the client the moment it changes.

There are four main techniques, with different directionality, framing and reconnect behavior.

## Short polling

The client asks repeatedly on a timer.

```
Client              Server
  |--GET /msgs?since=t->|
  |<-- 200 [] ----------|
  .. 5 s ..
  |--GET /msgs?since=t->|
  |<-- 200 [] ----------|
  .. 5 s ..
  |--GET /msgs?since=t->|
  |<-- 200 [msg] -------|
```

It's trivially simple and uses ordinary HTTP infrastructure. But it's wasteful and slow:

- **Latency**: for uniformly distributed arrivals and successful punctual polls, the scheduling delay averages half the interval. A 5 s interval gives ~2.5 s average scheduling delay, up to 5 s before adding network and processing time.
- **Load**: most responses are empty. 1 million clients polling every 5 s is **200,000 requests/s**, nearly all saying "nothing new".

Short polling is fine for dashboards that refresh every 30–60 s, or job-status checks. It's the right default when updates are rare and a delay is acceptable.

## Long polling

The client asks, and the server **holds the request open** until there's data (or a timeout, typically 20–60 s). As soon as the client gets a response, it immediately asks again.

```
Client              Server
  |--GET /msgs?since=t->|
  |      (held open)    |
  |                     | msg arrives
  |<-- 200 [msg] -------|
  |--GET /msgs?since=t2>|  re-poll
  |      (held open)    |
  |       ...30 s...    |
  |<-- 204 (timeout) ---|
  |--GET /msgs?since=t2>|
```

Updates arrive almost immediately, and there are far fewer empty responses. It uses plain HTTP, but intermediaries still need suitable timeout settings. AWS SQS's `ReceiveMessage` with `WaitTimeSeconds` is long polling.

Drawbacks:

- Each waiting client holds a connection, so large deployments benefit from event-driven I/O or lightweight tasks rather than a dedicated heavyweight OS thread for each idle request.
- There's a small gap between a response and the next request where messages must be buffered server-side, which is why the `since=` cursor matters.
- Each completed poll needs a new request; a response can batch several messages, and HTTP/2 can compress repeated headers.

## Server-Sent Events (SSE)

SSE is a standard for the server to **stream** events over one long-lived HTTP response. The browser's `EventSource` API handles it natively.

```
GET /scores/stream HTTP/1.1
Accept: text/event-stream
```

```
HTTP/1.1 200 OK
Content-Type: text/event-stream
Cache-Control: no-cache

id: 101
event: goal
data: {"team":"ARS","min":63}

id: 102
event: goal
data: {"team":"CHE","min":71}
```

Each event is a few text lines followed by a blank line. Features that make SSE pleasant:

- **Automatic reconnection.** If the connection drops, the browser reconnects by itself.
- **Resumption.** On reconnect the browser sends `Last-Event-ID: 102`, so the server can replay anything missed. That only works if the server keeps a short replay buffer (or can query events after id 102); the header just tells it where to start.
- **`retry:` field** lets the server set the reconnect delay.
- It uses HTTP, including HTTP/2 multiplexing. Configure intermediary buffering and timeouts. Native EventSource supports cookies but does not expose arbitrary request headers such as Authorization.

Limitations:

- **One-way**: server to client only. The client sends data with ordinary `POST` requests.
- **Text only** (UTF-8). Binary needs a text encoding such as base64.
- Over HTTP/1.1, browsers allow only ~6 connections per domain, so many tabs with SSE can exhaust them. HTTP/2 multiplexes streams, subject to negotiated stream limits.

SSE is underused. Live feeds, notifications, progress bars and streaming LLM responses (OpenAI's and Anthropic's APIs both stream tokens over SSE) are a perfect fit.

## WebSockets

A WebSocket (RFC 6455) is a **full-duplex**, persistent connection. It starts as an HTTP request and then upgrades:

```
GET /chat HTTP/1.1
Host: example.com
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==
Sec-WebSocket-Version: 13
```

```
HTTP/1.1 101 Switching Protocols
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Accept: <accept value>
```

For the shown key, `<accept value>` is `s3pPLMBiTxaQ9kYGzzhZRbK+xOo=` (the RFC 6455 example).

After the `101`, the TCP connection carries WebSocket **frames** in both directions. Base frame headers occupy 2–14 bytes, excluding extensions and TCP/TLS overhead; fragmented messages use multiple frames. HTTP header sizes depend on the request and protocol version. Text and binary are both supported.

Classic WebSockets take over a whole TCP connection. RFC 8441 defines how to run them as one stream inside an HTTP/2 connection instead, which some browsers and servers support.

Use WebSockets when the client sends frequently too: chat, multiplayer games, collaborative editing (Figma, Google Docs), trading terminals.

Costs:

- **You build the protocol.** WebSocket gives you a pipe of messages, not semantics. You design message types, acknowledgements, reconnection and resume yourself (or use Socket.IO, Phoenix Channels and similar).
- **No automatic reconnect** in the browser API.
- **Stateful connections** are harder to load-balance and deploy (see below).
- Some corporate proxies still break the upgrade; use `wss://` (TLS) which mostly avoids this.

## Comparison

| | Latency | Direction | Complexity |
|---|---|---|---|
| Short poll | Interval/2 | Pull | Lowest |
| Long poll | Low | Pull-ish | Low |
| SSE | Low | Server→client | Low |
| WebSocket | Low | Both | Higher protocol responsibility |

A practical rule: **SSE for server push, WebSockets when the client also streams, polling when updates are rare.**

## Scaling persistent connections

Request/response servers are easy to scale because any server can handle any request. Persistent connections break that: each client is attached to *one* server for minutes or hours.

### Connection capacity

An idle connection consumes a socket, buffers, TLS state and application state. Measure memory and active traffic costs for the actual stack; idle capacity does not establish throughput under load.

> [!note] Content gap: connection capacity measurements
> No reproducible benchmark accompanies the generic per-connection memory and per-server capacity estimates previously presented here. Those estimates are omitted; the quiz supplies explicit hypothetical sizing inputs.

Limits to tune: file descriptors (`ulimit -n`), ephemeral ports on proxies, kernel socket buffers and TLS memory.

### The fan-out problem

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

### Load balancing

- The load balancer must support the `Upgrade` and long-lived connections. L7 balancers such as NGINX, Envoy and AWS ALB do. Set idle timeouts generously (AWS ALB's default is 60 s) and send **heartbeats** (ping/pong) every ~30 s, so that idle connections aren't culled by the balancer or by NAT devices along the way.
- Heartbeats also detect *dead* connections. A phone that loses signal doesn't send a TCP close, so without pings the server can hold a "connected" socket for a client that vanished minutes ago.
- Balancing happens at **connect** time only. If you add servers, existing connections stay where they are, so new servers initially receive only new or reconnected clients. Use least-connections balancing, and consider a maximum connection age (say, a few hours, with jitter) so the fleet rebalances itself gradually.

### Deploys and reconnect storms

Restarting a gateway drops every connection on it at once. If 200,000 clients all reconnect immediately, they hammer the auth service and the remaining gateways.

- **Drain gracefully**: stop accepting new connections, then close existing ones gradually over minutes.
- **Clients reconnect with exponential backoff and jitter**.
- **Resume, don't replay everything**: the client sends its last-seen message id or sequence number, and the server sends only what was missed.

### Managed options

If you don't want to run this yourself: AWS API Gateway WebSocket APIs, Azure Web PubSub, Ably, Pusher. They hold the connections and give your backend a simple "send to connection id" API.

## Key takeaways
- **Short polling**: simple but wasteful; average latency is half the interval.
- **Long polling**: the server holds the request until data arrives. Near-instant over plain HTTP, but a new request after each response (which may batch messages).
- **SSE**: one-way server push over HTTP with built-in reconnect and `Last-Event-ID` resume. Ideal for feeds, notifications and streamed LLM output.
- **WebSockets**: full-duplex, low-overhead frames after an HTTP `101` upgrade. Best when clients send often too, but you own the protocol.
- Persistent connections need a **gateway tier that manages connection state**, a **pub/sub or registry** for cross-server fan-out, **heartbeats**, and careful handling of **reconnect storms**.

## Further reading
- [MDN: Using server-sent events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events)
- [MDN: The WebSocket API](https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API)
- [RFC 6455: The WebSocket Protocol](https://www.rfc-editor.org/rfc/rfc6455)
- [RFC 6202: Known issues and best practices for long polling and streaming](https://www.rfc-editor.org/rfc/rfc6202)
- [Slack engineering: Real-time messaging](https://slack.engineering/real-time-messaging/)
- [Discord: How Discord scaled Elixir to 5,000,000 concurrent users](https://discord.com/blog/how-discord-scaled-elixir-to-5-000-000-concurrent-users)
- [Socket.IO: Redis adapter](https://socket.io/docs/v4/redis-adapter/)
