---
id: tcp-buffer-autotuning
sourceLesson: tcp-flow-control
title: Socket buffers and receive autotuning
level: intermediate
minutes: 3
summary: How Linux sizes socket buffers automatically, and how setting SO_RCVBUF by hand can cap a long-distance transfer.
---

## Buffer autotuning

The advertised window must be supported by the receiver’s capacity and update policy; it is not a direct byte-for-byte reading of allocated socket memory. Linux grows buffers automatically per connection, based on how fast the application reads and the measured RTT. The limits are in `net.ipv4.tcp_rmem` and `tcp_wmem` (min, default, max). Defaults vary with kernel version, available memory and distribution settings. The retrieved kernel documentation lists a 131,072-byte default receive-buffer allocation and a memory-dependent autotuning maximum; inspect the running system rather than assume a universal 6 MB cap.

> [!warning] Setting SO_RCVBUF turns autotuning off
> On Linux, calling `setsockopt(SO_RCVBUF)` sets an explicit receive-buffer limit and disables receive autotuning for that socket. Linux doubles the requested value for accounting and reports that doubled value through `getsockopt`; neither value directly equals the advertised payload window. Code that "helpfully" sets a 64 KB buffer can make long-distance transfers much slower than the default. Compare measured receive windows, buffer settings and application read behaviour before changing limits.

Size the window you need from the path, not from a habit. If the **effective advertised window** were 6,000,000 bytes, the window/RTT ceiling at 100 ms RTT would be about 480 Mbit/s. Reaching 10 Gbit/s on the same path would need about 125 MB of usable window, plus implementation-dependent memory overhead. A configured 6 MiB memory limit is a different quantity from either window.

When a long-distance transfer plateaus, compare three things side by side: the advertised receive window seen in captures (or `ss -ti`), the round-trip time, and the rate. If the rate is close to one window per round trip and the window is not growing, look for an explicit `SO_RCVBUF`, a low `tcp_rmem` maximum, or a window-scale shift that is too small.

## Key takeaways

- Linux buffer limits and advertised payload windows are different quantities.
- Explicit SO_RCVBUF sets a receive-memory limit and disables receive autotuning on that socket.
- Size measured usable windows against the target rate and RTT instead of assuming one default fits all paths.

## Further reading

- [Linux ip-sysctl documentation (tcp_rmem, tcp_wmem)](https://docs.kernel.org/networking/ip-sysctl.html)
- [Linux socket buffer accounting](https://man7.org/linux/man-pages/man7/socket.7.html)
- [Linux TCP socket options](https://man7.org/linux/man-pages/man7/tcp.7.html)
