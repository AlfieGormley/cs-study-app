---
id: tcp-zero-window-syndrome
sourceLesson: tcp-flow-control
title: Zero windows, persist probes and tiny windows
level: intermediate
minutes: 3
summary: Zero windows, persist probes and tiny windows, with worked examples and explicit assumptions.
---

## Zero windows and the persist timer

When the receiver's buffer fills, it advertises a **zero window**: a window field of 0. The sender stops.

Later the application reads, and the receiver sends a **window update**. But that update is a pure ACK carrying no data, and TCP doesn't retransmit pure ACKs. If it is lost, the sender waits for a window to open and the receiver waits for data: **deadlock**.

The fix is the **persist timer**. With data awaiting transmission against a zero window, the sender uses **zero-window probes** to solicit the current window. Probe segment construction depends on the implementation; it should not be confused with permission for unrestricted out-of-window data. The receiver must reply with an ACK carrying its current window, so a delivered probe/reply exchange can reveal the reopened window. Continued loss or endpoint failure can still prevent progress. Probes back off exponentially, like retransmissions.

In `ss -ti` or a packet capture, repeated zero windows show a receiver-side flow-control restriction. Check application reads, memory pressure, socket policy and reassembly state; the capture alone does not uniquely identify a slow application or exclude concurrent network problems.

## Silly window syndrome

If a receiver advertises a window as soon as a few bytes free up, and a sender fills it immediately, the connection degenerates into tiny segments: 40 bytes of headers carrying 10 bytes of data. Only a fifth of what crosses the wire is useful:

```formula
E = D / (D + H)
E = 10 B / (10 B + 40 B) = 0.2 = 20 %
where
E: efficiency, the fraction of each packet that is application data
D: data bytes per segment, here 10 bytes (B)
H: header bytes per segment; 20 for IPv4 plus 20 for TCP = 40 bytes
B: bytes
In words: with 10-byte segments, 80 % of the bytes sent are headers.
```

That is **silly window syndrome**, and there are fixes on both sides:

- **Receiver** (Clark's algorithm): don't advertise a larger window until it can grow by at least one MSS or half the buffer, whichever is smaller (see the formula below).
- **Sender**: don't send tiny segments when you could wait and send a full one. That leads to Nagle.

Clark's receiver rule as a formula:

```formula
G_min = min(MSS, M / 2)
G_min = min(1,460 B, 65,536 B / 2) = 1,460 B
where
G_min: the smallest increase in free space worth advertising, in bytes (B)
MSS: maximum segment size, the most data one segment carries; 1,460 bytes is typical on Ethernet
M: the receive buffer size; here 64 KiB = 65,536 bytes
min: whichever of the values in brackets is smaller
B: bytes
In words: wait until a full segment's worth of space (or half the buffer, if that is smaller) has freed up before opening the window again.
```

## Key takeaways

- A zero window stops ordinary new-data sending; persist probes can recover a lost window update when replies get through.
- Repeated zero windows identify a receive-side restriction without uniquely proving its cause.
- Receiver window-update thresholds and sender batching avoid wasteful tiny-segment patterns.

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
