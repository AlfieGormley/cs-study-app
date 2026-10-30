---
id: tcp-socket-short-io
sourceLesson: tcp-sockets
title: Short I/O, EOF and operation deadlines
level: intermediate
minutes: 3
summary: Short reads, partial writes, end of stream and timeouts: the rules for using socket calls correctly.
---

## Partial reads, partial writes and EOF

Three rules for using the calls correctly:

1. For a positive `n`, ordinary blocking **`recv(n)` returns at most n bytes**. Short reads are allowed. Flags, low-water settings, timeouts and errors can change when it returns; loop for a specified length.
2. **`send()` may send only part of the buffer**, returning the count it accepted, for example because of limited buffer capacity. Python's `sendall()` handles partial writes on blocking sockets, but may raise; success means local acceptance, not peer processing.
3. With a positive read size and no local receive shutdown, **`recv()` returning `b""` indicates end of stream** after received bytes have been consumed: the peer closed its sending direction. It is not an error and not "no data yet". If you don't treat it as the end, you'll spin forever on a closed connection.

Error conditions show up as exceptions:

| Python exception | Usual meaning |
|---|---|
| `ConnectionRefusedError` | RST in reply to SYN |
| `ConnectionResetError` | Peer sent RST mid-connection |
| `BrokenPipeError` | Writing to a stream no longer usable for sending; peer half-close alone need not cause it |
| `TimeoutError` / `socket.timeout` | An operation exceeded its applicable timeout; `sendall()` has an overall timeout |

Choose operation timeouts and application deadlines. A silent peer can otherwise leave a blocking read waiting indefinitely. Linux’s documented default keepalive idle interval is 7,200 seconds when keepalive is enabled, but applications and configuration can change it. Keepalive is not a substitute for a request deadline.

## Key takeaways

- Positive-length reads may be short and sends may accept only part of a buffer.
- Empty bytes indicate stream EOF under the stated socket conditions, not temporary lack of data.
- Operation timeouts, total request deadlines and application acknowledgements solve different problems.

## Further reading

- [Python socket module documentation](https://docs.python.org/3/library/socket.html)
- [Socket Programming HOWTO — Python docs](https://docs.python.org/3/howto/sockets.html)
