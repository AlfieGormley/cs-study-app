---
id: tcp-stream-message-framing
sourceLesson: tcp-sockets
title: Byte streams and message framing
level: intermediate
minutes: 3
summary: Byte streams and message framing, with worked examples and explicit assumptions.
---

## A stream has no message boundaries

TCP delivers a **byte stream**. It does not preserve the boundaries of your `send()` calls:

```
client: send(b"hello")
client: send(b"world")

server recv(1024) may return:
  b"helloworld"         (coalesced)
  b"hel", then b"loworld" (split)
  b"hello", then b"world"
```

All three are correct TCP behaviour. Nagle, segmentation, retransmission and the timing of `recv()` calls all affect where the cuts fall. A one-read-per-message assumption can fail even on localhost; a passing local test does not establish framing correctness.

Protocols that distinguish messages need **framing**. A single stream-to-EOF transfer can use EOF as its boundary:

- **Length prefix**: send a fixed-size length, then that many bytes. For example, gRPC has its own message-length prefix inside HTTP/2 DATA frames; the HTTP/2 frame header is a separate framing layer.
- **Delimiter**: end each message with a marker, such as `\r\n` in SMTP and in HTTP/1.1 headers. The receiver buffers until it finds one.
- **Protocol-defined body rules**: HTTP/1.1 uses status/method rules, `Content-Length`, chunked encoding, or connection closure as applicable; not every response has a body.

## Key takeaways

- TCP preserves byte order rather than application write boundaries.
- A receiver may observe a send split across reads or several sends combined.
- Length prefixes, delimiters and protocol-defined EOF/body rules supply message framing.

## Further reading

- [Python socket module documentation](https://docs.python.org/3/library/socket.html)
- [Socket Programming HOWTO — Python docs](https://docs.python.org/3/howto/sockets.html)
- [Python selectors module documentation](https://docs.python.org/3/library/selectors.html)
- [Beej's Guide to Network Programming](https://beej.us/guide/bgnet/)
- [The C10K problem — Dan Kegel](http://www.kegel.com/c10k.html)
- [SYN packet handling in the wild — Cloudflare blog](https://blog.cloudflare.com/syn-packet-handling-in-the-wild/)
