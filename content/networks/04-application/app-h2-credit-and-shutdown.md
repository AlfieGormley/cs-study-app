---
id: app-h2-credit-and-shutdown
title: "HTTP/2 credit, shutdown and reset abuse"
level: intermediate
minutes: 3
sourceLesson: app-http2-quic
summary: "Stream and connection windows both limit DATA; credit feedback can constrain throughput."
---

### Flow control

**HTTP/2 flow control** applies **per stream and per connection**, on top of TCP's receive credit. Before settings, each has a **65,535-byte** window. SETTINGS_INITIAL_WINDOW_SIZE adjusts stream windows; the connection window is enlarged with WINDOW_UPDATE. Sending DATA uses up window; the receiver returns credit with WINDOW_UPDATE. Only DATA payloads count, including their pad-length and padding bytes, but excluding the 9-byte frame header.

This lets a proxy stop one slow download from filling its buffers without stalling the other streams. It also caps speed. The sender can have at most one window of unacknowledged DATA outstanding, and fresh credit takes a round trip to come back, so in an ideal model with prompt credit return and no other bottleneck:

```formula essential
T_max ≈ W / RTT
where
T_max: the highest sustained rate the window allows, in bytes per second (B/s)
W: the flow-control window, in bytes (B); 65,535 B unless SETTINGS or WINDOW_UPDATE changes it
RTT: the round-trip time for DATA to reach the receiver and its WINDOW_UPDATE credit to come back, in seconds (s)
≈: approximately equal to; this is an upper bound under ideal assumptions
B: bytes
s: seconds
In words: at most one window of data can be delivered per round trip, so the ceiling grows with a bigger window and shrinks with a longer round trip, regardless of link speed.
```

With the default 64 KiB window and a 100 ms round trip, one stream tops out near 5 Mbit/s even on a gigabit link. Doubling the window or halving the RTT doubles the ceiling; delayed credit and other bottlenecks lower it. Because both windows apply, a receiver that wants faster transfers must raise the stream window (SETTINGS_INITIAL_WINDOW_SIZE or WINDOW_UPDATE on the stream) **and** give enough connection credit (WINDOW_UPDATE on stream 0). Opening more streams does not help when the shared connection window is the limit.

### GOAWAY, RST_STREAM and Rapid Reset

GOAWAY reports the highest peer-initiated stream ID on which the sender might have acted or might still act. Higher-numbered requests were not processed and may be retried; lower-numbered unfinished requests may have ambiguous outcomes. That makes graceful restarts possible.

`RST_STREAM` cancels one stream cheaply. In 2023 attackers abused this in the **Rapid Reset** attack (CVE-2023-44487): open a stream with HEADERS, immediately reset it, repeat. The stream never counts against `SETTINGS_MAX_CONCURRENT_STREAMS` for long, but the server still starts work on each request. Google reported a peak of about 398 million requests per second. Mitigations can limit abusive creation/reset work or terminate offending connections; deployed protection depends on implementation and configuration.

### Priorities and push

RFC 9113 deprecated the original tree-based priority scheme. Its replacement ([RFC 9218](https://www.rfc-editor.org/rfc/rfc9218)) is a simple `priority` header, such as `u=1, i` (urgency 0 to 7, default 3; `i` means incremental). Chrome’s published removal rationale included limited performance benefit and cache-related waste; it disabled HTTP/2 server push by default starting with Chrome 106 in 2022. Other clients and non-browser use differ.

## Key takeaways
- Stream and connection windows both limit DATA; credit feedback can constrain throughput.
- GOAWAY distinguishes unprocessed higher stream IDs from potentially acted-on lower IDs.

## Further reading
- [RFC 9113](https://www.rfc-editor.org/rfc/rfc9113)
- [RFC 9218](https://www.rfc-editor.org/rfc/rfc9218)
- [Google: Rapid Reset research](https://cloud.google.com/blog/products/identity-security/how-it-works-the-novel-http2-rapid-reset-ddos-attack)
- [Chrome server-push removal](https://developer.chrome.com/blog/removing-push/)
