---
id: tcp-window-throughput-scaling
sourceLesson: tcp-flow-control
title: Window throughput and negotiated scaling
level: intermediate
minutes: 4
summary: Window throughput and negotiated scaling, with worked examples and explicit assumptions.
---

## The window limits throughput

In a steady-state model with fixed usable byte window and a fixed ACK round trip, the window imposes a throughput ceiling. The sender can have at most one window of data unacknowledged, and the first ACK takes one round trip to come back, so at most one window is delivered per RTT (other limits can make the actual rate lower):

```formula
X ≤ W / RTT
where
X: throughput, the sustained rate of delivered data, in bytes per second (B/s)
W: the usable window, in bytes (B)
RTT: round-trip time, in seconds (s)
≤: is at most
B/s: bytes per second
In words: you can deliver at most one window per round trip, so a bigger window or a shorter round trip raises the ceiling.
```

The original 16-bit field caps the window at **65,535 bytes**. On a path with a 100 ms RTT:

```formula
X_max = 65,535 B / (0.1 s) = 655,350 B/s
X_max = 655,350 × 8 bit/s ≈ 5.2 Mbit/s
where
X_max: the throughput ceiling set by the window, in bytes per second (B/s), then in megabits per second (Mbit/s)
B: bytes
s: seconds; 100 ms is 0.1 s
bit: binary digit; multiply bytes by 8 to get bits
Mbit/s: megabits per second, millions of bits per second
≈: approximately equal to
In words: a 64 KB window over a 100 ms round trip can never carry more than about 5.2 Mbit/s, however fast the link is.
```

That's a 5 Mbit/s ceiling on a 1 Gbit/s connection. To fill a pipe, the window must be at least the **bandwidth-delay product** (BDP), the amount of data "in the pipe" during one RTT:

```formula
BDP = C RTT
BDP = 1 Gbit/s × 0.1 s = 100 Mbit
BDP = 100 Mbit / 8 = 12.5 MB
65,535 B / (12,500,000 B) ≈ 0.005
where
BDP: bandwidth-delay product, the data needed in flight to keep the link busy, in megabits (Mbit) or megabytes (MB)
C: the link's capacity (bandwidth), here 1 gigabit per second (Gbit/s)
RTT: round-trip time, in seconds (s); 100 ms is 0.1 s
Gbit/s: gigabits per second, a thousand million bits per second
Mbit: megabit, a million bits
MB: megabyte, a million bytes
B: bytes
s: seconds
≈: approximately equal to
In words: a 1 Gbit/s path with a 100 ms round trip holds 12.5 MB in flight, and a 64 KB window is only about 0.5 % of that.
```

So a 64 KB window is about 0.5% of what this path needs.

## Window scaling

[RFC 7323](https://www.rfc-editor.org/rfc/rfc7323) adds the **window scale** option. Each side sends a shift count (0 to 14) in its SYN, and when scaling is successfully negotiated, each side’s later advertised window uses that side’s shift. Window fields in SYN and SYN+ACK segments themselves are **not scaled**. Each step of the shift count doubles what the window field means:

```formula
W = F × 2^S
W_max = 65,535 × 2^14
W_max = 65,535 × 16,384
W_max = 1,073,725,440 B
where
W: the window the receiver actually means, in bytes (B)
F: the value in the 16-bit window field, 0 to 65,535
S: the shift count agreed in the SYN, 0 to 14
2^S: S twos multiplied together (2^7 = 128); shifting a binary number left by S places multiplies it by this
W_max: the largest possible window, using the biggest field value and the biggest shift (14)
B: bytes
In words: each step of the shift count doubles the window; the maximum, 65,535 shifted by 14, is 1,073,725,440 bytes, just below 1 GiB.
```

For example, shifting a field of 1,000 left by seven bits gives an advertised window of 128,000 bytes.

Two details matter in practice:

- The option is only valid on SYN segments, and **both** sides must send it. If either side doesn't, neither direction scales.
- Because it is negotiated once, a middlebox that strips it from the SYN, or a firewall that tracks windows but ignores scaling, can silently cap a connection at 64 KB, or drop segments it thinks are outside the window. A rate near that modelled bound is a clue; endpoint and on-path captures are needed to establish missing or inconsistent negotiation.

## Key takeaways

- A fixed usable window divided by RTT bounds steady-state payload throughput under the model.
- Filling a path requires enough in-flight capacity for its bandwidth-delay product.
- Window scaling is negotiated on SYNs, which themselves retain unscaled window fields.

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
