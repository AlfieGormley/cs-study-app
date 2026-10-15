---
id: tcp-stream-blocking-ossification
sourceLesson: tcp-performance
title: Stream delivery gaps and ossification
level: advanced
minutes: 3
summary: Stream delivery gaps and ossification, with worked examples and explicit assumptions.
---

## Head-of-line blocking

TCP delivers one ordered byte stream. If one segment is lost, later stream bytes cannot be delivered in order until the gap is filled (or the connection fails), even if those bytes belong to an unrelated request.

That matters for **HTTP/2**, which multiplexes many streams over a single TCP connection:

```
TCP stream:  [css][js][img1][img2]
loss in js:        ^
css: delivered
later bytes wait for gap recovery
```

Multiple HTTP/1.1 connections have separate TCP delivery ordering; HTTP/2 multiplexes streams on a connection. A TCP gap blocks later bytes on that connection, not resources already delivered or other connections. Recovery has no fixed one-RTT duration. Which HTTP version is faster depends on the workload, implementation and path.

## Ossification: why TCP is hard to change

TCP commonly runs in OS kernels, although user-space implementations exist. Devices along a path may inspect or rewrite it:

- **NATs and firewalls** track TCP state, rewrite ports and sometimes sequence numbers.
- **Middleboxes** strip unknown options, normalise headers, or drop packets that look unusual. Compatibility therefore needs testing and fallback. Multipath TCP includes fallback to ordinary TCP when its negotiation does not succeed.
- **Deployment dependencies** can include OS updates and peer support, depending on the extension. Sender-only congestion-control changes need not update both endpoints.

These constraints contribute to **ossification**: deployed equipment’s assumptions can restrict protocol evolution. This does not mean every TCP change takes a decade or that extensions have stopped.

## Key takeaways

- A missing TCP range holds up later bytes on that connection, including multiplexed HTTP/2 streams.
- Other connections and already delivered bytes do not acquire that same delivery dependency.
- Deployed middlebox assumptions can obstruct extensions, making negotiation and fallback important.

## Further reading

- [The Macroscopic Behavior of the TCP Congestion Avoidance Algorithm — Mathis et al.](https://www.cs.utexas.edu/~lam/395t/papers/Mathis1998.pdf)
- [Introduction to bufferbloat — bufferbloat.net](https://www.bufferbloat.net/projects/bloat/wiki/Introduction/)
- [RFC 8289: Controlled Delay Active Queue Management](https://www.rfc-editor.org/rfc/rfc8289)
- [RFC 9000: QUIC](https://www.rfc-editor.org/rfc/rfc9000)
- [The QUIC Transport Protocol: Design and Internet-Scale Deployment — Google (SIGCOMM 2017)](https://research.google/pubs/the-quic-transport-protocol-design-and-internet-scale-deployment/)
- [RFC 7413: TCP Fast Open](https://www.rfc-editor.org/rfc/rfc7413)
- [RFC 9001: Using TLS to Secure QUIC](https://www.rfc-editor.org/rfc/rfc9001)
- [RFC 9002: QUIC Loss Detection and Congestion Control](https://www.rfc-editor.org/rfc/rfc9002)
- [Mathis and Mahdavi: Deprecating the TCP Macroscopic Model (2019 editorial)](https://ccronline.sigcomm.org/wp-content/uploads/2019/10/acmdl19-323.pdf)
