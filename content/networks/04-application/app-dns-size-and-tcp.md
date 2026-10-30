---
id: app-dns-size-and-tcp
title: "DNS truncation, EDNS and TCP fallback"
level: intermediate
minutes: 3
sourceLesson: app-dns-wire
summary: "Without EDNS the ordinary UDP DNS message limit is 512 bytes; required data can force TCP fallback."
---

## Size limits, EDNS and TCP

Classic DNS over UDP limits messages to **512 bytes**. If required response data does not fit, the server sets the **TC bit** and a resolver can retry over **TCP** (port 53, with each message prefixed by a 2-byte length).

**EDNS(0)** ([RFC 6891](https://www.rfc-editor.org/rfc/rfc6891)) extends DNS without changing the header. The client adds an **OPT** pseudo-record to the additional section that advertises a larger UDP buffer size and carries flags such as **DO** ("DNSSEC OK", please include signatures) and options such as cookies and client subnet.

UDP datagrams exceeding path capacity can be fragmented, dropped or trigger an error, depending on IP version, flags and path. Fragment handling can create reliability and spoofing risks. The 2020 **DNS Flag Day** recommended an EDNS buffer of **1,232 bytes**. The figure comes from IPv6: every IPv6 link must carry 1,280-byte packets, and removing the 40-byte IPv6 header and 8-byte UDP header leaves 1,232 bytes for the DNS message, so the whole packet fits without fragmentation.

This reduces fragmentation risk with those assumptions; extension headers, tunnels and IPv4 paths can require different budgets. Larger required answers can fall back to TCP.

## Key takeaways
- Without EDNS the ordinary UDP DNS message limit is 512 bytes; required data can force TCP fallback.
- The 1,232-byte EDNS budget assumes a basic IPv6 header and UDP without additional overhead.

## Further reading
- [RFC 6891](https://www.rfc-editor.org/rfc/rfc6891)
- [RFC 7766](https://www.rfc-editor.org/rfc/rfc7766)
- [DNS Flag Day 2020](https://www.dnsflagday.net/2020/)
