---
id: tcp-window-throughput-scaling
sourceLesson: tcp-flow-control
title: Window throughput and negotiated scaling
level: intermediate
minutes: 4
summary: Why at most one window can be delivered per round trip, and how window scaling lets long fast paths fill up.
---

## The window limits throughput

In a steady-state model with a fixed usable byte window and a fixed ACK round trip, the window imposes a throughput ceiling. The sender can have at most one window of data unacknowledged, and the first ACK takes one round trip to come back, so at most one window is delivered per RTT (other limits can make the actual rate lower):

```formula essential
X ≤ W / RTT
where
X: throughput, the sustained rate of delivered data, in bytes per second (B/s)
W: the usable window, in bytes (B)
RTT: round-trip time, in seconds (s)
≤: is at most
B/s: bytes per second
In words: you can deliver at most one window per round trip, so a bigger window or a shorter round trip raises the ceiling.
```

Notice what is missing: the link speed. Once the window is the limit, a faster link changes nothing, while a longer round trip lowers the ceiling in direct proportion.

The original 16-bit field caps the window at **65,535 bytes**. Over a 100 ms round trip that is a ceiling of about 5.2 Mbit/s, even on a 1 Gbit/s link; on a 10 ms path the same window allows about 52 Mbit/s.

To fill a pipe, the window must be at least the **bandwidth-delay product** (BDP): the amount of data "in the pipe" during one round trip. It is the same relationship turned around:

```formula reference
BDP = C RTT
where
BDP: bandwidth-delay product, the data that must be in flight to keep the link busy, in bits (convert to bytes by dividing by 8)
C: the link's capacity (bandwidth), in bits per second (bit/s)
RTT: round-trip time, in seconds (s)
bit/s: bits per second
s: seconds
In words: the window needed to keep a path busy is its bandwidth multiplied by its round-trip time, so long, fast paths need very large windows.
```

A 1 Gbit/s path with a 100 ms round trip holds 12.5 MB in flight, so a 64 KB window covers only about 0.5% of it. Such high-bandwidth, long-delay paths are nicknamed **long fat pipes** (or long fat networks).

> [!analogy] Real-world analogy: A conveyor belt you can only load ahead
> A factory may load only a fixed number of boxes onto a long conveyor before the far end confirms what it has received, and each confirmation takes a full trip back. With a short belt, a small allowance keeps it busy. With a very long belt, the same allowance leaves most of it empty, however fast the belt runs.
>
> **How it maps:** The allowance is the window; the trip there and back is the RTT; the belt's capacity is the bandwidth-delay product. Delivered boxes per second can never exceed the allowance per round trip.
>
> **Where it stops:** A real belt carries physical items at a constant speed; on a network the RTT includes queueing that changes with load, and the sender's allowance is the smaller of two windows that themselves change during the connection.

## Window scaling

[RFC 7323](https://www.rfc-editor.org/rfc/rfc7323) adds the **window scale** option. Each side sends a shift count (0 to 14) in its SYN, and when scaling is successfully negotiated, each side’s later advertised window uses that side’s shift. Window fields in SYN and SYN+ACK segments themselves are **not scaled**. Each step of the shift count doubles what the window field means:

```formula reference
W = F × 2^S
where
W: the window the receiver actually means, in bytes (B)
F: the value in the 16-bit window field, 0 to 65,535
S: the shift count agreed in the SYN, 0 to 14
2^S: S twos multiplied together (2^7 = 128); shifting a binary number left by S places multiplies it by this
B: bytes
In words: each step of the shift count doubles the meaning of the window field; the largest shift, 14, allows a window of just under 1 GiB.
```

For example, shifting a field of 1,000 left by seven bits gives an advertised window of 128,000 bytes.

Two details matter in practice:

- The option is only valid on SYN segments, and **both** sides must send it. If either side doesn't, neither direction scales. The shift is therefore fixed in each direction for the life of the connection: a receiver must choose, at the handshake, a shift big enough for the largest window it might later want to advertise.
- Because it is negotiated once, a middlebox that strips it from the SYN, or a firewall that tracks windows but ignores scaling, can silently cap a connection at 64 KB, or drop segments it thinks are outside the window. A rate near that modelled bound is a clue; endpoint and on-path captures are needed to establish missing or inconsistent negotiation.

## Key takeaways

- A fixed usable window divided by RTT bounds steady-state payload throughput under the model.
- Filling a path requires enough in-flight capacity for its bandwidth-delay product.
- Window scaling is negotiated on SYNs, which themselves retain unscaled window fields.

## Further reading

- [RFC 7323: TCP Extensions for High Performance](https://www.rfc-editor.org/rfc/rfc7323)
- [Bandwidth-delay product — Wikipedia](https://en.wikipedia.org/wiki/Bandwidth-delay_product)
