---
id: api-sse-reconnect-resume
title: Server-Sent Events and replay
level: advanced
minutes: 2
summary: Stream one-way text events with automatic reconnection and a server-backed Last-Event-ID replay path.
sourceLesson: api-real-time
---

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
- **Replay of missed events.** On reconnect the browser sends `Last-Event-ID: 102`, so the server can replay anything missed. That only works if the server keeps a short replay buffer (or can query events after id 102); the header just tells it where to start.
- **`retry:` field** lets the server set the reconnect delay.
- It uses HTTP, including HTTP/2 multiplexing. Configure intermediary buffering and timeouts. Native EventSource supports cookies but does not expose arbitrary request headers such as Authorization.

Limitations:

- **One-way**: server to client only. The client sends data with ordinary `POST` requests.
- **Text only** (UTF-8). Binary needs a text encoding such as base64.
- Over HTTP/1.1, browsers allow only ~6 connections per domain, so many tabs with SSE can exhaust them. HTTP/2 multiplexes streams, subject to negotiated stream limits.

SSE is underused. Live feeds, notifications, progress bars and streaming LLM responses (OpenAI's and Anthropic's APIs both stream tokens over SSE) are a perfect fit.

## Key takeaways
- EventSource reads UTF-8 events from a long-lived HTTP response.
- Automatic reconnect does not recover events unless the server retains or can query them.
- Configure buffering, timeouts and connection limits; native EventSource does not expose arbitrary request headers.

## Further reading
- [MDN: Using server-sent events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events)
