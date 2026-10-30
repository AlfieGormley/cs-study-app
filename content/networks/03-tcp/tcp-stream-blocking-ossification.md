---
id: tcp-stream-blocking-ossification
sourceLesson: tcp-performance
title: Stream delivery gaps and ossification
level: advanced
minutes: 3
summary: Why one lost segment stalls every HTTP/2 stream on a TCP connection, and why TCP is hard to change.
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

> [!analogy] Real-world analogy: One checkout queue for several shoppers' items
> Several shoppers put their items on one conveyor belt at a single till, separated by dividers. If the cashier must re-check the price of one item, everything behind it on the belt waits, including the next shoppers' items, even though their purchases have nothing to do with it.
>
> **How it maps:** The belt is the single TCP byte stream; each shopper's items are an HTTP/2 stream; the price check is a lost segment being retransmitted. Because TCP must hand over bytes strictly in order, data for unrelated streams waits behind the gap.
>
> **Where it stops:** A cashier could set the problem item aside and carry on; TCP cannot, because it knows nothing about streams. QUIC behaves like separate belts sharing one cashier: a gap holds up only its own stream, although all streams still share congestion and flow control.

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

- [RFC 9000: QUIC](https://www.rfc-editor.org/rfc/rfc9000)
- [The QUIC Transport Protocol: Design and Internet-Scale Deployment — Google (SIGCOMM 2017)](https://research.google/pubs/the-quic-transport-protocol-design-and-internet-scale-deployment/)
