---
id: tcp-handshake-reachability
sourceLesson: tcp-connections
title: Stale handshakes and unpredictable ISNs
level: intermediate
minutes: 3
summary: Stale handshakes and unpredictable ISNs, with worked examples and explicit assumptions.
---

## Why three messages, not two?

Each side must learn that the **other** side received its ISN. The client's SYN is acknowledged by the server's SYN+ACK; the server's SYN is acknowledged by the client's final ACK. Two messages would leave the server not knowing whether its ISN arrived.

There is also the **old duplicate** problem. A SYN delayed in the network from a long-dead attempt could arrive at the server. With three messages, the server's SYN+ACK reaches a client that is not expecting it, and the client replies with RST. If that response arrives, the server abandons the stale attempt. With no reply, it can retain half-open state until timeout; the handshake is not a defence against every spoof or replay scenario.

## Why random ISNs?

If ISNs were predictable (say, always 0), two problems arise:

- **Stale segments**: a delayed segment from a previous connection with the same 5-tuple could fall inside the new connection's sequence space and be accepted as data.
- **Spoofing**: an off-path attacker who can guess the server's ISN can forge the final ACK and inject data while pretending to be another IP. Predictable sequence numbers have historically enabled off-path spoofing; reachability and other validation assumptions also matter.

[RFC 6528](https://www.rfc-editor.org/rfc/rfc6528), incorporated into RFC 9293, describes a clock component plus a keyed function of endpoint addresses/ports. RFC 9293 discusses an approximately 4 µs clock; actual implementations can differ. The construction aims to make new ISNs hard for an off-path attacker to predict while separating connection incarnations.

## Key takeaways

- The third handshake message acknowledges the server SYN and helps reject old connection attempts.
- Unpredictable ISNs resist off-path guessing, while connection-incarnation rules also guard against stale segments.
- Bidirectional reachability and cryptographic peer identity are different properties.

## Further reading

- [RFC 9293: Transmission Control Protocol](https://www.rfc-editor.org/rfc/rfc9293)
- [RFC 4987: TCP SYN Flooding Attacks and Common Mitigations](https://www.rfc-editor.org/rfc/rfc4987)
- [SYN cookies — Wikipedia](https://en.wikipedia.org/wiki/SYN_cookies)
- [Coping with the TCP TIME-WAIT state on busy Linux servers — Vincent Bernat](https://vincent.bernat.ch/en/blog/2014-tcp-time-wait-state-linux)
- [SYN packet handling in the wild — Cloudflare blog](https://blog.cloudflare.com/syn-packet-handling-in-the-wild/)
- [RFC 6528: Defending against Sequence Number Attacks](https://www.rfc-editor.org/rfc/rfc6528)
- [Linux TCP configuration defaults](https://kernel.org/doc/html/latest/networking/ip-sysctl.html)
