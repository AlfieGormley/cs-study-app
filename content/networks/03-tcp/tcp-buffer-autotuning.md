---
id: tcp-buffer-autotuning
sourceLesson: tcp-flow-control
title: Socket buffers and receive autotuning
level: intermediate
minutes: 3
summary: Socket buffers and receive autotuning, with worked examples and explicit assumptions.
---

## Buffer autotuning

The advertised window must be supported by the receiver’s capacity and update policy; it is not a direct byte-for-byte reading of allocated socket memory. Linux grows buffers automatically per connection, based on how fast the application reads and the measured RTT. The limits are in `net.ipv4.tcp_rmem` and `tcp_wmem` (min, default, max). Defaults vary with kernel version, available memory and distribution settings. The retrieved kernel documentation lists a 131,072-byte default receive-buffer allocation and a memory-dependent autotuning maximum; inspect the running system rather than assume a universal 6 MB cap.

> [!warning] Setting SO_RCVBUF turns autotuning off
> On Linux, calling `setsockopt(SO_RCVBUF)` sets an explicit receive-buffer limit and disables receive autotuning for that socket. Linux doubles the requested value for accounting and reports that doubled value through `getsockopt`; neither value directly equals the advertised payload window. Code that "helpfully" sets a 64 KB buffer can make long-distance transfers much slower than the default. Compare measured receive windows, buffer settings and application read behaviour before changing limits.

If the **effective advertised window** were 6,000,000 bytes, the modelled ceiling at 100 ms RTT would be 480 Mbit/s. A configured 6 MiB memory limit is a different quantity and unit. At a target 10 Gbit/s payload rate and 100 ms RTT, the model requires 125 MB of usable in-flight capacity, plus implementation-dependent memory overhead:

```formula
X_max = W × 8 / RTT
X_max = 6,000,000 B × 8 / (0.1 s)
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

## Key takeaways

- Linux buffer limits and advertised payload windows are different quantities.
- Explicit SO_RCVBUF sets a receive-memory limit and disables receive autotuning on that socket.
- Size measured usable windows against the target rate and RTT instead of assuming one default fits all paths.

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
