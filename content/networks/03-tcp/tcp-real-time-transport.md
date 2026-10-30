---
id: tcp-real-time-transport
sourceLesson: tcp-udp-ports
title: Real-time updates and transport over UDP
level: basic
minutes: 3
summary: Why games, calls and QUIC use UDP: fresh data matters more than waiting for old data.
---

## Live games and voice: old data is useless

Consider a game sending independent full-state position snapshots 60 times a second: one every 16.7 ms or so. A 100 ms stall therefore spans about six snapshots, and by the time a lost one could be resent, several newer ones already describe the world better.

A new snapshot can supersede a lost one; delta updates and important game events can have different reliability requirements. TCP would **hold back** every later update until the lost one was retransmitted, delaying delivery of later bytes until the gap is repaired. The delay depends on detection, retransmission and buffering; the whole game loop need not freeze. That is **head-of-line blocking**, and independent deadline-sensitive updates can prefer skipping out-of-date data to waiting for that gap.

> [!analogy] Real-world analogy: A live scoreboard by text message
> A friend texts you the score of a match every minute. If one text goes missing, you do not want them to resend "2–1 at 63 minutes" when you already have "3–1 at 64 minutes"; and you certainly would not want your phone to hide the newer texts until the old one turned up.
>
> **How it maps:** Each text is an independent snapshot of the whole game state sent in a UDP datagram, which the game can simply skip when it is superseded. TCP behaves like a phone that refuses to show later texts until the missing one is redelivered: that is head-of-line blocking.
>
> **Where it stops:** Some game messages are not superseded, such as "player picked up the key", and need their own reliability. Real-time media also has hard playback deadlines, so late audio may be concealed rather than simply skipped.

Voice and video calls (RTP over UDP) work the same way: a late frame may be concealed or discarded, but timely retransmission and forward error correction can also help. RFC 4588 specifies RTP retransmission; media deadlines determine its usefulness.

## QUIC: build your own transport

QUIC ([RFC 9000](https://www.rfc-editor.org/rfc/rfc9000)), the transport under HTTP/3, uses UDP; HTTP/3 commonly uses **port 443**, but QUIC is not restricted to that port. QUIC provides its own loss recovery, stream reliability, congestion control and protected transport, and can be implemented in user space. UDP is used not because QUIC wants unreliability, but because using existing UDP socket support can ease endpoint and middlebox deployment. UDP is neither the only permitted non-TCP transport nor guaranteed to pass every path. The transport-performance units cover why.

## Others

Examples using UDP include DHCPv4 initial discovery, conventional NTP/SNMP exchanges, UDP syslog, multicast media and WireGuard. Several of these application families also define other transports; “syslog” alone does not imply UDP.

## Key takeaways

- Independent state updates can supersede old data, while important events may need separate reliability.
- TCP delivery gaps can delay later stream bytes; this need not freeze an entire game loop.
- QUIC builds protected, congestion-controlled transport services above UDP rather than relying on base UDP for reliability.

## Further reading

- [RFC 4588: RTP retransmission](https://www.rfc-editor.org/rfc/rfc4588)
- [RFC 8085: UDP Usage Guidelines](https://www.rfc-editor.org/rfc/rfc8085)
- [User Datagram Protocol — Wikipedia](https://en.wikipedia.org/wiki/User_Datagram_Protocol)
