---
id: tcp-flow-control
title: Flow control, window scaling, Nagle and delayed ACK
level: intermediate
minutes: 14
summary: How the receive window stops a fast sender drowning a slow receiver, why a 64 KB window caps throughput on long paths, window scaling and buffer autotuning, zero windows, and how Nagle and delayed ACKs can interact to delay small messages.
---

A server on a 10 Gbit/s link can produce data far faster than a phone can process it. Without receiver flow control, sustained arrivals faster than the application drains them can exhaust finite receive buffering and cause drops. Retransmitting does not remove that bottleneck.

**Flow control** prevents this. The receiver tells the sender, through valid window advertisements, which sequence range it is prepared to receive. The sender limits new transmissions accordingly; advertisements are delayed feedback, and window shrinkage or special probes require more detailed rules.

Flow control is about **the receiver**. Congestion control (lesson 5) is about **the network**. They are separate mechanisms with separate windows, and the sender obeys whichever is smaller:

```formula
A = max(0, min(rwnd, cwnd) − F)
A = max(0, min(65,535, 14,600) − 10,000)
A = 14,600 B − 10,000 B = 4,600 B
where
A: how many more bytes of new data the sender may send right now, in bytes (B)
rwnd: the receive window: how much the receiver has said it can accept, in bytes
cwnd: the congestion window: the sender's own estimate of how much the network can take, in bytes (lesson 5)
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
X_max = 65,535 B / 0.1 s = 655,350 B/s
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
BDP = C × RTT
BDP = 1 Gbit/s × 0.1 s = 100 Mbit
BDP = 100 Mbit / 8 = 12.5 MB
65,535 B / 12,500,000 B ≈ 0.005
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

### Window scaling

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

For example, a field of 1,000 with shift 7 means 1,000 × 128 = 128,000 bytes.

Two details matter in practice:

- The option is only valid on SYN segments, and **both** sides must send it. If either side doesn't, neither direction scales.
- Because it is negotiated once, a middlebox that strips it from the SYN, or a firewall that tracks windows but ignores scaling, can silently cap a connection at 64 KB, or drop segments it thinks are outside the window. A rate near that modelled bound is a clue; endpoint and on-path captures are needed to establish missing or inconsistent negotiation.

### Buffer autotuning

The advertised window must be supported by the receiver’s capacity and update policy; it is not a direct byte-for-byte reading of allocated socket memory. Linux grows buffers automatically per connection, based on how fast the application reads and the measured RTT. The limits are in `net.ipv4.tcp_rmem` and `tcp_wmem` (min, default, max). Defaults vary with kernel version, available memory and distribution settings. The retrieved kernel documentation lists a 131,072-byte default receive-buffer allocation and a memory-dependent autotuning maximum; inspect the running system rather than assume a universal 6 MB cap.

> [!warning] Setting SO_RCVBUF turns autotuning off
> On Linux, calling `setsockopt(SO_RCVBUF)` sets an explicit receive-buffer limit and disables receive autotuning for that socket. Linux doubles the requested value for accounting and reports that doubled value through `getsockopt`; neither value directly equals the advertised payload window. Code that "helpfully" sets a 64 KB buffer can make long-distance transfers much slower than the default. Compare measured receive windows, buffer settings and application read behaviour before changing limits.

If the **effective advertised window** were 6,000,000 bytes, the modelled ceiling at 100 ms RTT would be 480 Mbit/s. A configured 6 MiB memory limit is a different quantity and unit. At a target 10 Gbit/s payload rate and 100 ms RTT, the model requires 125 MB of usable in-flight capacity, plus implementation-dependent memory overhead:

```formula
X_max = W × 8 / RTT
X_max = 6,000,000 B × 8 / 0.1 s
X_max = 480,000,000 bit/s = 480 Mbit/s
W_need = X × RTT / 8
W_need = 10^10 bit/s × 0.1 s / 8
W_need = 125,000,000 B = 125 MB
where
X_max: the throughput ceiling, in bits per second (bit/s)
W: the effective advertised window, in bytes (B)
RTT: round-trip time, in seconds (s); 100 ms is 0.1 s
W_need: the window needed to reach a target rate
X: the target payload rate; 10 Gbit/s is 10^10 bit/s
bit: binary digit; × 8 turns bytes into bits and / 8 turns bits into bytes
Mbit/s: megabits per second
MB: megabytes, millions of bytes
B: bytes
s: seconds
In words: a 6 MB window at 100 ms caps a flow at 480 Mbit/s; to reach 10 Gbit/s on the same path you need a 125 MB window.
```

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

## Nagle's algorithm

John Nagle's 1984 rule ([RFC 896](https://www.rfc-editor.org/rfc/rfc896)) addresses, among other cases, interactive terminal traffic where a one-byte keystroke could occupy a 41-byte IPv4/TCP packet with minimal headers:

```formula
P = H_IP + H_TCP + D
P = 20 B + 20 B + 1 B = 41 B
where
P: the size of the whole packet, in bytes (B)
H_IP: the minimal IPv4 header, 20 bytes
H_TCP: the minimal TCP header, 20 bytes
D: the data, one keystroke, 1 byte
B: bytes
In words: sending each keystroke on its own wastes 40 bytes of headers to carry 1 byte, so only about 2.4 % of the packet is data.
```

The rule:

> If there is unacknowledged data in flight, buffer small writes until either the outstanding data is ACKed or you have a full MSS to send.

In the simplified classic rule, further short new-data sends wait while data is outstanding unless enough data forms a full segment. Retransmissions, FIN handling and implementation variants require additional rules. On a slow link, keystrokes typed during one RTT are batched into one packet. Full-sized ready segments are not delayed by Nagle’s small-segment condition; partially filled tails or incremental application writes can still be affected.

## Delayed ACK

The receiver has its own optimisation. Instead of ACKing every segment at once, it waits briefly in the hope of **piggybacking** the ACK on response data, or covering two segments with one ACK. RFC 9293 requires delayed ACKs to be delayed by **less than 500 ms** and says an ACK **SHOULD** be generated for at least every second full-sized segment or every 2 × RMSS bytes of new data:

```formula
N_ack = 2 × RMSS
N_ack = 2 × 1,460 B = 2,920 B
where
N_ack: the most new data that should arrive before the receiver sends an ACK, in bytes (B)
RMSS: the receiver's maximum segment size, the largest segment it expects; 1,460 bytes is typical on Ethernet
B: bytes
In words: on a typical Ethernet path, the receiver should ACK at least every 2,920 bytes of new data, that is every second full segment.
```

Other conditions can call for prompt ACKs.

Actual ACK scheduling depends on stack version, mode, connection state and configuration. The example below assumes a measured 40 ms delayed-ACK timer; that is not a universal Linux or Windows default.

## When Nagle meets delayed ACK

Each optimisation is sensible. Together they create one of networking's best-known performance bugs. Consider a trace where a small header has already been sent, a separate short body is held by Nagle, and the receiver delays its ACK while waiting for the complete request:

```
Client                     Server
write(header) -- seg 1 --> (waits for
                            body; delays
                            its ACK)
write(body)   held by Nagle:
              seg 1 unACKed
   ... measured delay (example: 40 ms) ...
              <---- ACK -- delayed ACK
                           timer fires
              -- seg 2 -->
              <-- response
```

The client won't send the body until the header is ACKed (Nagle). The server won't ACK the header until its timer fires, because it has no response to piggyback the ACK on until it has the whole request (delayed ACK). That particular exchange incurs the delayed-ACK wait. Not every pair of writes reproduces it: coalescing, ACK modes, message sizes and timing vary. A 40 ms extra wait can dominate a 1 ms path, but does not by itself prove an exact 40× total-response slowdown.

The pattern to watch for is **write, write, read**. Possible fixes after confirming this interaction:

1. **Write the whole message at once.** Build the buffer in user space, or use `writev()`/`sendmsg()` with several pieces. This supplies the data together and can avoid the split-message dependency, but one API call does not guarantee one packet, full `sendmsg` completion or no other stall. Handle partial writes where required.
2. **Disable Nagle** with `TCP_NODELAY` for latency-sensitive request/response protocols. Go’s `net.TCPConn` documentation specifies NoDelay enabled by default. Other libraries require their own documentation/configuration checks.
3. On Linux, `TCP_CORK` (or the `MSG_MORE` flag) does the opposite: delay partial-segment output while assembling data; full segments can still be sent and Linux documents a timeout ceiling, for when you want full segments assembled from several writes, as web servers do when sending headers plus a file.

```python
import socket

def send_request(s, header, body):
    # Caller owns a connected TCP socket.
    # header/body are bytes; set a timeout
    # suitable for the application first.
    s.setsockopt(socket.IPPROTO_TCP,
                 socket.TCP_NODELAY, 1)
    s.sendall(header + body)
```

> [!tip] TCP_NODELAY doesn't make TCP "unbuffered"
> It only stops TCP waiting for ACKs before sending small segments. Other buffering, pacing, congestion/flow control and packetisation still apply. Ten writes need not become ten packets; batching can nevertheless reduce overhead.

`TCP_QUICKACK` on Linux attacks the problem from the receiving side by sending ACKs immediately, but the setting is not permanent; the kernel can drop back into delayed-ACK mode, so one call is not a permanent “never delay ACKs” policy. Whether repeated requests help requires measurement; it is not a portable solution.

## Key takeaways
- The receive window advertises acceptable sequence space and reflects buffer/update policy; ordinary new-data sending is constrained by both rwnd and cwnd; shrinkage, recovery and probes need additional rules.
- In the steady-state model with a fixed window, throughput is capped at window / RTT. Filling a path needs a window of at least the bandwidth-delay product.
- The 16-bit window maxes out at 64 KB; window scaling (negotiated on SYNs only) raises it to about 1 GiB.
- Linux autotunes buffers up to `tcp_rmem`/`tcp_wmem` maxima; setting `SO_RCVBUF` disables autotuning for that socket.
- A zero window stops ordinary new-data transmission; successfully delivered persist probes and replies can recover from a lost window update.
- Nagle (sender) and delayed ACK (receiver) can stall a split write-write-read exchange until the delayed-ACK timer expires. Write whole messages at once, or set `TCP_NODELAY`.

## Further reading
- [RFC 7323: TCP Extensions for High Performance](https://www.rfc-editor.org/rfc/rfc7323)
- [RFC 896: Congestion Control in IP/TCP Internetworks (Nagle)](https://www.rfc-editor.org/rfc/rfc896)
- [RFC 1122: Requirements for Internet Hosts](https://www.rfc-editor.org/rfc/rfc1122)
- [Nagle's algorithm — Wikipedia](https://en.wikipedia.org/wiki/Nagle%27s_algorithm)
- [Linux ip-sysctl documentation (tcp_rmem, tcp_wmem)](https://docs.kernel.org/networking/ip-sysctl.html)
- [Bandwidth-delay product — Wikipedia](https://en.wikipedia.org/wiki/Bandwidth-delay_product)

> [!note] Content omitted after review
> Universal Linux/Windows delayed-ACK times, a universal 6 MB autotuning limit and one-write/one-packet guarantees are omitted because they are not supported across versions and configurations. Timing scenarios are explicit examples, not benchmarks.

- [Linux TCP socket options](https://man7.org/linux/man-pages/man7/tcp.7.html)
- [Linux socket buffer accounting](https://man7.org/linux/man-pages/man7/socket.7.html)
- [Go TCPConn.SetNoDelay](https://pkg.go.dev/net#TCPConn.SetNoDelay)
