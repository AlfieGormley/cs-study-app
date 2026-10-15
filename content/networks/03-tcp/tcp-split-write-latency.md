---
id: tcp-split-write-latency
sourceLesson: tcp-flow-control
title: Diagnosing split-write latency
level: intermediate
minutes: 3
summary: Diagnosing split-write latency, with worked examples and explicit assumptions.
---

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

- A held short body and a delayed ACK can create a measurable split-request dependency.
- Batch complete messages or use TCP_NODELAY where appropriate after confirming the mechanism.
- TCP_NODELAY, CORK and QUICKACK affect different decisions and do not guarantee packet boundaries or immediate delivery.

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

> [!note] Content omitted after review
> Universal Linux/Windows delayed-ACK times, a universal 6 MB autotuning limit and one-write/one-packet guarantees are omitted because they are not supported across versions and configurations. Timing scenarios are explicit examples, not benchmarks.
