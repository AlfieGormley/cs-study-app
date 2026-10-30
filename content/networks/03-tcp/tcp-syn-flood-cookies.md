---
id: tcp-syn-flood-cookies
sourceLesson: tcp-connections
title: SYN floods and cookie trade-offs
level: intermediate
minutes: 4
summary: How a SYN flood exhausts half-open state, and what SYN cookies trade away to resist it.
---

## SYN floods and SYN cookies

When a server receives a SYN, normal stateful Linux processing creates **request-socket** state associated with the listener and sends SYN+ACK. Exact memory use depends on kernel/configuration. It retransmits the SYN+ACK if no ACK comes back. The Linux documentation retrieved here specifies five SYN+ACK retries by default with a one-second initial timeout that doubles each time: waits of 1, 2, 4, 8 and 16 seconds put the last retry at 31 seconds, and one more doubled wait means the attempt is abandoned after about 63 seconds. This is a documented default, not a universal timing guarantee. It shows why half-open state is costly: each spoofed SYN can hold an entry for about a minute.

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

The exact encoding is implementation-dependent. The client's ACK acknowledges the cookie plus one (a SYN uses one sequence number), so the server subtracts one, wrapping round at the 32-bit limit, to recover the cookie and then applies its validation rules. An off-path attacker that cannot observe the SYN+ACK must guess a valid value; finite cookie authenticators do not make guessing mathematically impossible.

> [!analogy] Real-world analogy: A stamped ticket instead of a reservation book
> A busy venue stops writing everyone who turns up into a reservation book. Instead the door staff hand each person a ticket stamped with a secret mark and the time, with their party size written on it, and keep nothing themselves. When someone comes back with a ticket, staff check the mark and the time, read the party size off the ticket and seat them.
>
> **How it maps:** The reservation book is the SYN queue of half-open entries. The stamped ticket is the cookie carried in the server's initial sequence number, including the little option state (such as the MSS) it can encode. Coming back with the ticket is the client's ACK, which the server validates with its secret and a freshness check before creating the connection.
>
> **Where it stops:** A ticket has room for only a little information, just as a cookie can encode only limited MSS and option state. A forger who guesses the mark could still get in, and an attacker can still waste the staff's time and the doorway's capacity even without a book to fill.

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

- [RFC 4987: TCP SYN Flooding Attacks and Common Mitigations](https://www.rfc-editor.org/rfc/rfc4987)
- [SYN cookies — Wikipedia](https://en.wikipedia.org/wiki/SYN_cookies)
- [SYN packet handling in the wild — Cloudflare blog](https://blog.cloudflare.com/syn-packet-handling-in-the-wild/)
- [Linux TCP configuration defaults](https://kernel.org/doc/html/latest/networking/ip-sysctl.html)
