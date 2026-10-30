---
id: tcp-stream-message-framing
sourceLesson: tcp-sockets
title: Byte streams and message framing
level: intermediate
minutes: 3
summary: Why TCP does not keep your send() boundaries, and the framing rules applications use instead.
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

> [!analogy] Real-world analogy: Dictating over a crackly phone without punctuation
> You read two sentences down the phone to someone writing them down. They hear every word in order, but if you never say "full stop", they cannot tell where one sentence ends and the next begins, and they may have written half a sentence when you pause.
>
> **How it maps:** The words arriving in order are TCP's ordered byte stream; your pauses are `send()` calls, which the listener cannot see; each `recv()` is them writing down whatever they have heard so far. Saying "full stop" is a delimiter, and announcing "the next sentence has twelve words" is a length prefix.
>
> **Where it stops:** A person can guess sentence breaks from meaning, but a program cannot: without an explicit rule it will read exactly what arrived, which might be one and a half messages.

Protocols that distinguish messages need **framing**. A single stream-to-EOF transfer can use EOF as its boundary:

- **Length prefix**: send a fixed-size length, then that many bytes. For example, gRPC has its own message-length prefix inside HTTP/2 DATA frames; the HTTP/2 frame header is a separate framing layer.
- **Delimiter**: end each message with a marker, such as `\r\n` in SMTP and in HTTP/1.1 headers. The receiver buffers until it finds one.
- **Protocol-defined body rules**: HTTP/1.1 uses status/method rules, `Content-Length`, chunked encoding, or connection closure as applicable; not every response has a body.

## Key takeaways

- TCP preserves byte order rather than application write boundaries.
- A receiver may observe a send split across reads or several sends combined.
- Length prefixes, delimiters and protocol-defined EOF/body rules supply message framing.

## Further reading

- [Socket Programming HOWTO — Python docs](https://docs.python.org/3/howto/sockets.html)
- [Python socket module documentation](https://docs.python.org/3/library/socket.html)
