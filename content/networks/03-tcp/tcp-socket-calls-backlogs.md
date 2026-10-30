---
id: tcp-socket-calls-backlogs
sourceLesson: tcp-sockets
title: Socket lifecycle and pending queues
level: intermediate
minutes: 3
summary: What each socket call does in TCP, and how the SYN and accept queues behave under load.
---

Python's **socket API** wraps the operating system's networking calls. Similar concepts appear in other languages, but high-level runtimes, platforms and socket modes differ in their errors, buffering and lifetime rules.

This lesson follows a TCP connection through the socket calls on each side, then looks at the two kernel queues that hold connections before the application accepts them. Framing, short reads and complete servers follow in the next lessons.

## The calls and what they do in TCP

```
Server                 Client
socket()               socket()
bind(port)
listen(backlog)        connect(addr)
   SYN queue  <-- SYN ----
              --- SYN+ACK -->
   accept q   <-- ACK ----  (returns)
accept()  (returns a new socket)
recv()/send()  <------>  send()/recv()
close()        <-FIN/ACK->  close()
```

| Call | What happens in the kernel |
|---|---|
| `socket()` | Creates an endpoint; state CLOSED |
| `bind()` | Associates a local address/port, subject to reuse rules |
| `listen(n)` | State LISTEN; creates the queues |
| `connect()` | Ordinary blocking TCP: initiates setup, then succeeds or fails; non-blocking mode differs |
| `accept()` | Returns a new connected socket from pending connections |
| `close()` | Releases this socket reference; final closure can initiate FIN or an abort, depending on state/options |

Two points surprise people:

- **`accept()` does not perform the handshake.** The kernel completes handshakes on its own, whether or not the application is calling `accept()`. In ordinary TCP it dequeues a completed connection and returns a **new** socket; the peer may already have sent FIN before acceptance. Fast Open can allow acceptance before the normal handshake finishes. The listener remains available.
- **Ordinary blocking `connect()` success means the client-side handshake progressed successfully**, not that the server application accepted you or processed data. Queue overflow can leave the server still waiting to complete its side.

## The backlog and the two queues

A useful Linux model distinguishes two kinds of pending state (SYN cookies can avoid allocating an entry per SYN):

1. The **SYN queue**: half-open connections waiting for the final ACK.
2. The **accept queue**: completed connections waiting for `accept()`.

The `backlog` argument to `listen()` sets the size of the **accept queue**, capped by `net.core.somaxconn` (4,096 by default since Linux 5.4; 128 before).

If the application is too slow to accept and that queue fills, one Linux path with `tcp_abort_on_overflow = 0` can **ignore** the client's final ACK; other overload paths can drop SYNs. The client thinks it's connected and may send its request; the server retransmits SYN+ACK and the connection completes later, or not. The symptom is clients seeing occasional multi-second delays on connect or first request. `nstat` shows `TcpExtListenOverflows` climbing.

> [!tip] Investigate queue overload
> Arrival bursts, slow acceptance, resource limits and backlog configuration can all contribute. Inspect application scheduling and queue/counter measurements. A growing overflow counter does not by itself identify a single cause or prove one packet-level sequence.

## Key takeaways

- The kernel can progress an ordinary TCP handshake before the application accepts it.
- Acceptance returns a separate connected socket while the listener remains available.
- Linux pending queues, caps and overflow paths need version/configuration-aware diagnosis.

## Further reading

- [Python socket module documentation](https://docs.python.org/3/library/socket.html)
- [SYN packet handling in the wild — Cloudflare blog](https://blog.cloudflare.com/syn-packet-handling-in-the-wild/)
- [Beej's Guide to Network Programming](https://beej.us/guide/bgnet/)
