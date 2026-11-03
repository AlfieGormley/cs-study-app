---
id: api-short-long-polling
title: Polling delay and request load
level: advanced
minutes: 5
summary: Compare periodic and held-open requests, accounting for timeout and message-driven completions.
sourceLesson: api-real-time
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

- **Latency**: for uniformly distributed arrivals and successful punctual polls, the scheduling delay averages half the interval. A 5 s interval gives ~2.5 s average scheduling delay, up to 5 s before adding network and server processing time.
- **Load**: most responses are empty. 1 million clients polling every 5 s is **200,000 requests/s**, nearly all saying "nothing new".

Both follow from the poll interval:

```formula reference
D_avg = I / 2
R = N / I
where
D_avg: the average wait between an update happening and the next poll seeing it, in seconds (s)
I: the poll interval, the time between one client's polls, in seconds
R: the total request rate the server receives, in requests per second
N: the number of clients polling
s: seconds
In words: an update lands at a random point in the interval, so on average it waits half of it; and every client sends one request per interval, so halving the delay doubles the load.
```

These assume updates arrive at random times and every poll goes out on schedule; network and server time add to this scheduling delay.

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

## Estimating long-poll completions

A held-open request saves empty responses, but does not remove request processing:

Long polls still complete on messages or timeouts. Each completion starts another request, so both message traffic and timeout settings contribute to load.

Shorter timeouts create more empty completions. More frequent messages also complete polls sooner. Batching, network time and reconnect gaps affect measured traffic; size the system with its actual workload.

## Key takeaways
- Short polling trades lower delay for more request traffic.
- Long polls finish on a message or timeout and immediately start another request.
- Buffer messages across re-poll gaps and configure intermediary timeouts.
- Arrival models matter when estimating how often long polls complete.

## Further reading
- [RFC 6202: Known issues and best practices for long polling and streaming](https://www.rfc-editor.org/rfc/rfc6202)
