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

```formula
D_avg = I / 2
D_avg = 5 s / 2 = 2.5 s
R = N / I
R = 1,000,000 / 5 s = 200,000 per s
where
D_avg: the average wait between an update happening and the next poll seeing it, in seconds (s)
I: the poll interval, the time between one client's polls, in seconds
R: the total request rate the server receives
N: the number of clients polling
s: seconds
In words: an update lands at a random point in the interval, so on average it waits half of it; and every client sends one request per interval, so halving the delay doubles the load.
```

These assume updates arrive at random times and every poll goes out on schedule; network time comes on top of D_avg.

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

For independent Poisson message arrivals, the gap is exponentially distributed. A poll ends at the first arrival or its timeout. With two million clients, a 30-second timeout and a mean gap of 120 seconds:

```formula
D = M × (1 − e^{−T / M})
D = 120 s × (1 − e^{−0.25}) ≈ 26.5 s
R_B = N / D
R_B = 2,000,000 / 26.5 s ≈ 75,000/s
where
D: the average length of one poll, ending at a message or the timeout, whichever comes first
M: the average gap between messages, 120 s
T: the timeout, 30 s
e: Euler's number, about 2.718; e^{−T / M} is the chance that no message arrives before the timeout
N: the number of clients
R_B: the request rate under long polling
≈: approximately equal to
s: seconds; /s means per second
In words: a poll lasts about 26.5 s on average, so each client sends one request every 26.5 s: about **75,000 requests per second**.
```

This ideal model ignores network time, immediate restart cost and batching. A simpler upper bound counts at most one timeout per timeout interval plus the average message rate; it slightly overcounts polls ended early by a message.

## Key takeaways
- Short polling trades lower delay for more request traffic.
- Long polls finish on a message or timeout and immediately start another request.
- Buffer messages across re-poll gaps and configure intermediary timeouts.
- Arrival models matter when estimating how often long polls complete.

## Further reading
- [RFC 6202: Known issues and best practices for long polling and streaming](https://www.rfc-editor.org/rfc/rfc6202)
