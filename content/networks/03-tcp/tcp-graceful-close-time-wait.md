---
id: tcp-graceful-close-time-wait
sourceLesson: tcp-connections
title: Graceful close, half-close and TIME_WAIT
level: intermediate
minutes: 3
summary: How each direction of a connection closes separately, and why the side that closes first waits in TIME_WAIT.
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

In the ordinary sequential graceful close above, the active closer ends in **TIME_WAIT**, and stays there for twice the **maximum segment lifetime** (MSL), the longest a segment is assumed to survive in the network. RFC 793 suggested an MSL of two minutes, which makes TIME_WAIT four minutes; real stacks often use a shorter fixed value.

Simultaneous close can put both endpoints in TIME_WAIT; aborts and special reuse cases follow different rules. Two purposes of TIME_WAIT are:

1. **A retransmitted FIN may need another ACK.** Keeping connection state lets the endpoint acknowledge a repeated FIN if the peer missed the final ACK. The TIME_WAIT timer can restart when the FIN is received again. MSL is a segment-lifetime assumption, not the peer's retransmission timeout, so adding two presumed network delays is not a proof of the retransmission schedule.
2. **Old duplicates must expire.** Retaining the connection incarnation for the specified interval reduces confusion if the same endpoint tuple is reused. The guarantee relies on the MSL/sequence-number assumptions; TCP also specifies constrained early-reuse cases.

Linux v6.12 defines its ordinary TIME_WAIT interval as **60 seconds**; reuse, retransmitted segments and resource handling can affect an observed entry’s lifetime.

> [!analogy] Real-world analogy: Staying on the line after goodbye
> At the end of a phone call you say "Bye", they say "Bye", and you say "Bye then" one last time. You stay on the line a moment in case they did not hear your last word and say "Hello?" again, so you can answer.
>
> **How it maps:** The two goodbyes are the two FINs; your final "Bye then" is the last ACK. Lingering on the line is TIME_WAIT: the side that said goodbye first keeps the connection's state so it can acknowledge a repeated FIN, and so that stray old segments are not mistaken for a new call on the same tuple.
>
> **Where it stops:** On a phone you linger for a second; TCP waits a set interval (60 seconds on Linux) even when nothing arrives, and a repeated FIN can restart it. And a phone line carries no delayed words from an earlier call, whereas old TCP segments really can turn up late.

## Key takeaways

- TCP closes its two sending directions independently; half-close preserves the receiving direction.
- In an ordinary sequential close, the active closer enters TIME_WAIT.
- TIME_WAIT supports repeated-FIN acknowledgement and separation from old duplicates; implementation intervals differ from the historical MSL example.

## Further reading

- [RFC 9293: Transmission Control Protocol](https://www.rfc-editor.org/rfc/rfc9293)
- [Coping with the TCP TIME-WAIT state on busy Linux servers — Vincent Bernat](https://vincent.bernat.ch/en/blog/2014-tcp-time-wait-state-linux)
