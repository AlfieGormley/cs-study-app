---
id: tcp-receive-window-budget
sourceLesson: tcp-flow-control
title: Receive windows and the new-data budget
level: intermediate
minutes: 3
summary: Receive windows and the new-data budget, with worked examples and explicit assumptions.
---

A server on a 10 Gbit/s link can produce data far faster than a phone can process it. Without receiver flow control, sustained arrivals faster than the application drains them can exhaust finite receive buffering and cause drops. Retransmitting does not remove that bottleneck.

**Flow control** prevents this. The receiver tells the sender, through valid window advertisements, which sequence range it is prepared to receive. The sender limits new transmissions accordingly; advertisements are delayed feedback, and window shrinkage or special probes require more detailed rules.

Flow control is about **the receiver**. Congestion control (the congestion-control units) is about **the network**. They are separate mechanisms with separate windows, and the sender obeys whichever is smaller:

```formula
A = max(0, min(rwnd, cwnd) − F)
A = max(0 B, min(65,535 B, 14,600 B)
               − 10,000 B)
A = 14,600 B − 10,000 B = 4,600 B
where
A: how many more bytes of new data the sender may send right now, in bytes (B)
rwnd: the receive window: how much the receiver has said it can accept, in bytes
cwnd: the congestion window: the sender's own estimate of how much the network can take, in bytes (the congestion-control units)
F: the bytes in flight: sent but not yet acknowledged
min: whichever of the values in brackets is smaller
max: whichever is larger; max(0, …) stops the answer going below zero
B: bytes
In words: the sender may fill whichever window is smaller, minus what is already in flight. With a 65,535-byte rwnd, a 14,600-byte cwnd and 10,000 bytes in flight, it may send 4,600 more bytes.
```

This is a simplified new-data budget with both windows expressed in bytes and measured from a consistent ACK point. Actual sending also depends on available data, pacing, recovery state and socket/packetisation rules.

## The receive window

Each TCP segment carries a 16-bit **window** field: the number of bytes, starting at the ACK number, that the receiver has room for. It is a sequence-space advertisement, not an exact measurement of unused socket memory: bookkeeping, buffered out-of-order data, scaling and window-update policy matter.

```
accepted contiguous data | advertised range
-------------------------+-----------------
                         ^ ACK / RCV.NXT
                         <---- rwnd ------>

Accepted data may still await app reads.
Out-of-order data may occupy the range.
```

As the application calls `recv()`, the buffer drains and window-update policy can permit a larger advertised window. If the application stops reading while data continues to arrive, finite receive capacity can be exhausted: the receiver advertises zero and the sender must stop ordinary new-data transmission. This is **backpressure**: a slow consumer automatically slows the producer, at the transport boundary. An application that keeps accumulating work in its own queue can still grow memory unless it propagates backpressure further.

The sender tracks a **sliding window**:

```
 acked   | in flight  | can send | not yet
---------+------------+----------+--------
         ^SND.UNA     ^SND.NXT   ^UNA+wnd
```

An ACK acknowledging new data advances the left edge; duplicate or stale ACKs do not. An accepted window update can change the right edge.

## Key takeaways

- The receive window advertises acceptable sequence space rather than an exact unused-memory reading.
- The simplified new-data budget uses the smaller of receive and congestion windows, minus consistent bytes in flight.
- Application read policy and propagated backpressure determine whether slow consumption is contained.

## Further reading

- [RFC 7323: TCP Extensions for High Performance](https://www.rfc-editor.org/rfc/rfc7323)
- [RFC 896: Congestion Control in IP/TCP Internetworks (Nagle)](https://www.rfc-editor.org/rfc/rfc896)
- [RFC 1122: Requirements for Internet Hosts](https://www.rfc-editor.org/rfc/rfc1122)
- [Nagle's algorithm — Wikipedia](https://en.wikipedia.org/wiki/Nagle%27s_algorithm)
- [Linux ip-sysctl documentation (tcp_rmem, tcp_wmem)](https://docs.kernel.org/networking/ip-sysctl.html)
- [Bandwidth-delay product — Wikipedia](https://en.wikipedia.org/wiki/Bandwidth-delay_product)
- [Linux TCP socket options](https://man7.org/linux/man-pages/man7/tcp.7.html)
- [Linux socket buffer accounting](https://man7.org/linux/man-pages/man7/socket.7.html)
- [Go TCPConn.SetNoDelay](https://pkg.go.dev/net#TCPConn.SetNoDelay)
