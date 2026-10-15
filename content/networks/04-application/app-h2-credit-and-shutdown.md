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

This lets a proxy stop one slow download from filling its buffers without stalling the other streams. It also caps speed: the sender can have at most one window of data in flight before the receiver returns credit, and fresh credit takes a round trip to come back. In an ideal feedback model with prompt credit return, negligible transmission time and no other bottleneck:

```formula
T_max ≈ W / RTT
T_max ≈ 65,535 B / 0.1 s = 655,350 B/s
T_max ≈ 655,350 × 8 bit/s ≈ 5.24 Mbit/s
where
T_max: the highest sustained rate the window allows, in bytes per second (B/s) or megabits per second (Mbit/s)
W: the flow-control window, in bytes (B); 65,535 B before SETTINGS changes it
RTT: the round-trip time for data to reach the receiver and its WINDOW_UPDATE credit to come back, in seconds (s); here 100 ms = 0.1 s
≈: approximately equal to; this is an upper bound under ideal assumptions
B: bytes
s: seconds
bit: one binary digit; 8 bits make a byte
Mbit: megabit, one million bits
In words: a 64 KiB window over a 100 ms round trip limits one stream to about 5 megabits per second, however fast the link is.
```

Doubling the window or halving the RTT doubles this ceiling. Delayed credit and other bottlenecks lower it. The receiver can advertise more stream credit; connection credit must also suffice.

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
