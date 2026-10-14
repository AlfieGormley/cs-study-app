---
id: api-websocket-duplex-contract
title: WebSocket upgrades and duplex protocols
level: advanced
minutes: 2
summary: Trace the classic upgrade and choose a full-duplex transport when clients stream too.
sourceLesson: api-real-time
---

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
| Short poll | Half the interval | Pull | Lowest |
| Long poll | Low | Pull-ish | Low |
| SSE | Low | Server→client | Low |
| WebSocket | Low | Both | Higher protocol responsibility |

A practical rule: **SSE for server push, WebSockets when the client also streams, polling when updates are rare.**

## Key takeaways
- Classic HTTP/1.1 WebSocket upgrades with 101, then exchanges text or binary frames.
- WebSocket provides framing; the application owns acknowledgement, reconnect and resume semantics.
- Use SSE for one-way push, WebSockets for frequent two-way streams and polling for rare updates.

## Further reading
- [MDN: The WebSocket API](https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API)
- [RFC 6455: The WebSocket Protocol](https://www.rfc-editor.org/rfc/rfc6455)
