---
id: tcp-graceful-close-time-wait
sourceLesson: tcp-connections
title: Graceful close, half-close and TIME_WAIT
level: intermediate
minutes: 3
summary: Graceful close, half-close and TIME_WAIT, with worked examples and explicit assumptions.
---

## Closing: the four-way exchange

TCP connections are **full duplex**, so each direction is closed separately. Either side sends FIN to say "I have no more data". The other side acknowledges it, may keep sending, and later sends its own FIN.

```
A (active close)        B (passive)
ESTABLISHED             ESTABLISHED
  | FIN seq=8000          |
  |---------------------->| CLOSE_WAIT
FIN_WAIT_1                |
  |          ACK ack=8001 |
  |<----------------------|
FIN_WAIT_2                |
  |   (B may send more)   |
  |          FIN seq=9000 |
  |<----------------------| LAST_ACK
TIME_WAIT                 |
  | ACK ack=9001          |
  |---------------------->| CLOSED
(wait 2 x MSL)
CLOSED
```

B often combines its ACK and FIN into one segment, giving three segments in total. A **half-close** (`shutdown(SHUT_WR)` on A) sends a FIN but keeps receiving; that is how a client can say "that's my whole request" and still read the response.

## TIME_WAIT and 2×MSL

In the ordinary sequential graceful close above, the active closer ends in **TIME_WAIT**, and stays there for twice the **maximum segment lifetime** (MSL), the longest a segment is assumed to survive in the network:

```formula
T_TW = 2 × MSL
T_TW = 2 × 120 s = 240 s = 4 min
where
T_TW: how long the active closer stays in TIME_WAIT, in seconds (s)
MSL: maximum segment lifetime, the longest a segment is assumed to survive in the network; RFC 793 suggested 2 minutes (120 s)
s: seconds
min: minutes
In words: with RFC 793's suggested two-minute MSL, TIME_WAIT lasts four minutes; real stacks often use a shorter fixed value (Linux: 60 s).
```

Simultaneous close can put both endpoints in TIME_WAIT; aborts and special reuse cases follow different rules. Two purposes of TIME_WAIT are:

1. **A retransmitted FIN may need another ACK.** Keeping connection state lets the endpoint acknowledge a repeated FIN if the peer missed the final ACK. The TIME_WAIT timer can restart when the FIN is received again. MSL is a segment-lifetime assumption, not the peer's retransmission timeout, so adding two presumed network delays is not a proof of the retransmission schedule.
2. **Old duplicates must expire.** Retaining the connection incarnation for the specified interval reduces confusion if the same endpoint tuple is reused. The guarantee relies on the MSL/sequence-number assumptions; TCP also specifies constrained early-reuse cases.

RFC 793 suggested an MSL of 2 minutes, which is where the 4 minutes above comes from. Linux v6.12 defines its ordinary TIME_WAIT interval as **60 seconds**; reuse, retransmitted segments and resource handling can affect an observed entry’s lifetime.

## Key takeaways

- TCP closes its two sending directions independently; half-close preserves the receiving direction.
- In an ordinary sequential close, the active closer enters TIME_WAIT.
- TIME_WAIT supports repeated-FIN acknowledgement and separation from old duplicates; implementation intervals differ from the historical MSL example.

## Further reading

- [RFC 9293: Transmission Control Protocol](https://www.rfc-editor.org/rfc/rfc9293)
- [RFC 4987: TCP SYN Flooding Attacks and Common Mitigations](https://www.rfc-editor.org/rfc/rfc4987)
- [SYN cookies — Wikipedia](https://en.wikipedia.org/wiki/SYN_cookies)
- [Coping with the TCP TIME-WAIT state on busy Linux servers — Vincent Bernat](https://vincent.bernat.ch/en/blog/2014-tcp-time-wait-state-linux)
- [SYN packet handling in the wild — Cloudflare blog](https://blog.cloudflare.com/syn-packet-handling-in-the-wild/)
- [RFC 6528: Defending against Sequence Number Attacks](https://www.rfc-editor.org/rfc/rfc6528)
- [Linux TCP configuration defaults](https://kernel.org/doc/html/latest/networking/ip-sysctl.html)
