---
id: tcp-syn-flood-cookies
sourceLesson: tcp-connections
title: SYN floods and cookie trade-offs
level: intermediate
minutes: 4
summary: SYN floods and cookie trade-offs, with worked examples and explicit assumptions.
---

## SYN floods and SYN cookies

When a server receives a SYN, normal stateful Linux processing creates **request-socket** state associated with the listener and sends SYN+ACK. Exact memory use depends on kernel/configuration. It retransmits the SYN+ACK if no ACK comes back: the Linux documentation retrieved here specifies five SYN+ACK retries by default, with a one-second initial timeout that doubles after each try, and a final timeout near 63 seconds:

```formula
T_last = 1 s + 2 s + 4 s + 8 s + 16 s
T_last = 31 s
T_final = T_last + 32 s = 63 s
where
T_last: the time from the first SYN+ACK to its fifth and last retransmission, in seconds (s)
T_final: when the kernel gives up on the half-open attempt: one more doubled wait after the last retry
s: seconds
In words: waits of 1, 2, 4, 8 and 16 seconds put the fifth retry at 31 s; one final 32-second wait means the attempt is abandoned at about 63 s.
```

This is a documented default, not a universal timing guarantee. It also shows why half-open state is costly: each spoofed SYN can hold an entry for about a minute.

A **SYN flood** attempts to exhaust connection-establishment resources with SYN traffic, often using spoofed addresses. The final ACKs never arrive, the SYN queue fills with half-open entries, and real clients' SYNs are dropped. The attacker needs no completed connections and can hide behind random sources.

## SYN cookies

A **SYN cookie** avoids retaining an ordinary per-attempt half-open entry: encode enough information in the server's sequence-number construction to validate a returning ACK and reconstruct connection state. Secret keys and other shared server state still exist, and processing consumes CPU and bandwidth.

A conceptual flow is:

```
SYN + endpoint tuple
        |
        v
secret + time + supported option state
        |
        v
cookie sequence number -> SYN+ACK
        |
client returns ACK acknowledging cookie
        |
validate freshness/authenticator
        |
create established-connection state
```

The exact encoding is implementation-dependent. The client's ACK acknowledges the cookie plus one (a SYN uses one sequence number), so the server first subtracts one (0 minus one becomes the largest 32-bit value):

```formula
S_cookie = (A − 1) mod 2^32
where
S_cookie: the cookie sequence number the server sent in its SYN+ACK
A: the acknowledgement number in the client's returning ACK
mod: modulo, the remainder after dividing by 2^32 = 4,294,967,296; it makes 0 − 1 wrap round to 4,294,967,295 instead of going negative
In words: take the client's acknowledgement number, step back one, and wrap round if needed; that recovers the cookie, which the server then checks.
```

The implementation's validation rules follow. An off-path attacker that cannot observe the SYN+ACK must guess a valid value; finite cookie authenticators do not make guessing mathematically impossible.

Costs:

- Limited cookie space constrains the amount of MSS/option state encoded; the set of supported MSS values depends on the implementation.
- Option support can be reduced; implementations may encode extra state in negotiated timestamp fields. Behaviour varies by version and client options.
- Without per-attempt timer state, there is no autonomous SYN+ACK retransmission timer for that attempt. A retransmitted client SYN can elicit another SYN+ACK.

Linux has its own cookie construction. Its documented default, `net.ipv4.tcp_syncookies = 1`, sends cookies **only when the SYN queue overflows**, when the kernel is built with SYN-cookie support; value 2 requests unconditional generation. Cookies do not remedy every overload or network-capacity problem. Large providers also filter floods upstream, before they reach servers.

## Key takeaways

- Spoofed SYN traffic can consume state, processing and network resources before connections complete.
- SYN cookies validate a returning ACK without retaining an ordinary per-attempt half-open entry.
- Finite option/authenticator space, implementation choices and absent per-attempt timers constrain cookies.

## Further reading

- [RFC 9293: Transmission Control Protocol](https://www.rfc-editor.org/rfc/rfc9293)
- [RFC 4987: TCP SYN Flooding Attacks and Common Mitigations](https://www.rfc-editor.org/rfc/rfc4987)
- [SYN cookies — Wikipedia](https://en.wikipedia.org/wiki/SYN_cookies)
- [Coping with the TCP TIME-WAIT state on busy Linux servers — Vincent Bernat](https://vincent.bernat.ch/en/blog/2014-tcp-time-wait-state-linux)
- [SYN packet handling in the wild — Cloudflare blog](https://blog.cloudflare.com/syn-packet-handling-in-the-wild/)
- [RFC 6528: Defending against Sequence Number Attacks](https://www.rfc-editor.org/rfc/rfc6528)
- [Linux TCP configuration defaults](https://kernel.org/doc/html/latest/networking/ip-sysctl.html)
