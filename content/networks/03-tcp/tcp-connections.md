---
id: tcp-connections
title: TCP connection management
level: intermediate
minutes: 14
summary: The three-way handshake with real sequence numbers, SYN floods and SYN cookies, the four-way close, why TIME_WAIT lasts twice the maximum segment lifetime, the TCP state machine and when connections are reset.
---

TCP offers a **reliable, ordered byte stream** between two endpoints. Normal establishment synchronises sequence spaces and checks bidirectional reachability; this is not cryptographic peer authentication. Data can accompany handshake segments, and extensions such as TCP Fast Open can allow early application delivery. Graceful closure acknowledges the byte stream in each direction, not application processing or durable storage of those bytes. That bookkeeping is **connection management**.

The rules come from RFC 793 (1981), now consolidated in [RFC 9293](https://www.rfc-editor.org/rfc/rfc9293) (2022).

## The TCP header, briefly

The fields that matter for connection management:

- **Sequence number** (32 bits): the first sequence-space position in the segment; a SYN occupies its own position before any data.
- **Acknowledgement number** (32 bits): the next byte the sender expects to receive. Only valid when the ACK flag is set.
- **Flags**: `SYN` (synchronise sequence numbers), `ACK`, `FIN` (no more data from me), `RST` (abort), plus `PSH`, `URG`, `ECE`, `CWR`.
- **Window** (16 bits): flow control (lesson 4).
- **Options**: MSS, window scale, SACK-permitted, timestamps. MSS, window scale and SACK permission are exchanged on SYN segments. Negotiated timestamps accompany later segments, and SACK blocks can appear on later ACKs.

The header is 20 bytes without options and at most 60 with them. The limit comes from the 4-bit **data offset** field, which gives the header length in 4-byte words:

```formula
H_max = D_max × 4 B = 15 × 4 B = 60 B
O_max = H_max − H_min = 60 B − 20 B = 40 B
where
H_max: the largest possible TCP header, in bytes (B)
D_max: the largest value a 4-bit field can hold, 15 (binary 1111)
O_max: the most space left for TCP options
H_min: the fixed part of the header, 20 bytes
B: bytes; one byte is 8 bits
In words: the header can be at most 15 four-byte words (60 bytes); 20 of those are fixed fields, so options get at most 40 bytes.
```

That 40-byte option budget is small, and options compete for it (lesson 3 shows SACK running into it).

## The three-way handshake

Each side picks an **initial sequence number** (ISN). The handshake exchanges and acknowledges both:

```
Client                       Server
  |  SYN seq=1000              |
  |--------------------------->|
  |                            |
  |  SYN+ACK seq=5000 ack=1001 |
  |<---------------------------|
  |                            |
  |  ACK seq=1001 ack=5001     |
  |--------------------------->|
  |  (data can now flow)       |
```

Two rules make the numbers work:

1. **SYN and FIN each consume one sequence number**, independently of any data carried in the same segment. That is why the server acknowledges 1001, not 1000.
2. The cumulative ACK identifies the next expected sequence-space position in that direction, going back to 0 after 2^32 values ("modulo 2^32", explained below). It acknowledges contiguous received stream data/control positions, not successful application processing.

Applied to the trace above, rule 1 gives the numbers each side uses next:

```formula
N_c = ISN_c + 1 = 1000 + 1 = 1001
N_s = ISN_s + 1 = 5000 + 1 = 5001
where
N_c: the client's next sequence number after its SYN: the number of its first data byte, and the ACK number the server sends
ISN_c: the client's initial sequence number, 1000 in the trace
N_s: the server's next sequence number after its SYN+ACK, and the ACK number the client sends
ISN_s: the server's initial sequence number, 5000 in the trace
In words: a SYN uses up one sequence number, so each side's data starts one after its ISN, and that is the number the other side acknowledges.
```

Rule 2's "modulo 2^32" is because the sequence number is a 32-bit field. Arithmetic on it wraps round like a clock: after the largest 32-bit value comes 0 again.

```formula
N_next = (N + L) mod 2^32
(4,294,967,295 + 1) mod 2^32 = 0
where
N_next: the sequence number just after a segment: the ACK number that acknowledges it
N: the segment's sequence number (its first position)
L: how many sequence numbers the segment uses: its data bytes, plus 1 for a SYN and 1 for a FIN
mod: modulo, the remainder after dividing; "mod 2^32" divides by 4,294,967,296 (32 twos multiplied together) and keeps the remainder, so totals wrap back into the range 0 to 4,294,967,295
In words: add the segment's length to its first number; if the total passes the largest 32-bit value, wrap round to 0 and keep counting.
```

So the client's first data byte will be numbered 1001, and the server's 5001. The final ACK may carry data itself; clients often send the HTTP request or TLS ClientHello right behind it.

### Why three messages, not two?

Each side must learn that the **other** side received its ISN. The client's SYN is acknowledged by the server's SYN+ACK; the server's SYN is acknowledged by the client's final ACK. Two messages would leave the server not knowing whether its ISN arrived.

There is also the **old duplicate** problem. A SYN delayed in the network from a long-dead attempt could arrive at the server. With three messages, the server's SYN+ACK reaches a client that is not expecting it, and the client replies with RST. If that response arrives, the server abandons the stale attempt. With no reply, it can retain half-open state until timeout; the handshake is not a defence against every spoof or replay scenario.

### Why random ISNs?

If ISNs were predictable (say, always 0), two problems arise:

- **Stale segments**: a delayed segment from a previous connection with the same 5-tuple could fall inside the new connection's sequence space and be accepted as data.
- **Spoofing**: an off-path attacker who can guess the server's ISN can forge the final ACK and inject data while pretending to be another IP. Predictable sequence numbers have historically enabled off-path spoofing; reachability and other validation assumptions also matter.

[RFC 6528](https://www.rfc-editor.org/rfc/rfc6528), incorporated into RFC 9293, describes a clock component plus a keyed function of endpoint addresses/ports. RFC 9293 discusses an approximately 4 µs clock; actual implementations can differ. The construction aims to make new ISNs hard for an off-path attacker to predict while separating connection incarnations.

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

### SYN cookies

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

### TIME_WAIT in production

TIME_WAIT is cheap (Linux keeps a small, stripped-down structure), but it constrains reuse of the **5-tuple** under the implementation’s rules:

- A client or proxy making many short connections to **one** backend can exhaust ephemeral ports (lesson 1).
- A server that actively closes connections accumulates TIME_WAIT entries, but on a single listening port a large connection count is still possible because peers have distinct tuples. Memory, churn and reuse patterns can nevertheless matter.

Possible approaches, chosen for the application and deployment:

1. **Reuse connections**: HTTP keep-alive, connection pools.
2. Changing which endpoint performs the sequential active close moves TIME_WAIT ownership; it does not create spare ports or solve the problem universally.
3. `net.ipv4.tcp_tw_reuse`: enables reuse subject to Linux’s checks that reuse is safe for the protocol; timestamps are not a cryptographic proof. The retrieved Linux documentation lists default 2 (loopback only) and a separate reuse delay. Do not treat this as a universal replacement for pooling.

> [!warning] Never use tcp_tw_recycle
> The old `tcp_tw_recycle` option dropped SYNs whose timestamps went backwards, which broke clients behind NAT whose clocks differ. It was removed in Linux 4.12. Advice to enable it is outdated.

## The state machine

RFC 9293 defines 11 states. The table below abbreviates successful ordinary events. Sequence/ACK validity, acceptable in-order FIN processing, queued data, duplicate packets, reset/error paths and API details are omitted:

| From | Event | To |
|---|---|---|
| CLOSED | `listen()` | LISTEN |
| CLOSED | `connect()`, send SYN | SYN_SENT |
| LISTEN | recv SYN, send SYN+ACK | SYN_RCVD |
| SYN_SENT | recv SYN+ACK, send ACK | ESTABLISHED |
| SYN_RCVD | recv ACK | ESTABLISHED |
| ESTABLISHED | `close()`, send FIN | FIN_WAIT_1 |
| ESTABLISHED | recv FIN, send ACK | CLOSE_WAIT |
| FIN_WAIT_1 | own FIN acknowledged; no peer FIN processed | FIN_WAIT_2 |
| FIN_WAIT_1 | peer FIN processed; own FIN not acknowledged | CLOSING |
| FIN_WAIT_1 | peer FIN processed and own FIN acknowledged | TIME_WAIT |
| FIN_WAIT_2 | recv FIN, send ACK | TIME_WAIT |
| CLOSING | own FIN acknowledged | TIME_WAIT |
| CLOSE_WAIT | `close()`, send FIN | LAST_ACK |
| LAST_ACK | own FIN acknowledged | CLOSED |
| TIME_WAIT | 2×MSL timer | CLOSED |

CLOSING happens when both sides send FIN before receiving the other’s FIN and then process the crossing FINs before ACKs of their own FINs (a **simultaneous close**). Both then go through TIME_WAIT.

You can see live states with `ss -tan`:

```
$ ss -Htan state close-wait | wc -l
```

> [!tip] Investigate persistent CLOSE_WAIT growth
> CLOSE_WAIT means a peer FIN has been processed and the local send direction remains open. The application may legitimately still be preparing a response. Persistent unexplained growth can indicate leaked sockets or stalled handlers; use process-level descriptor and application evidence before diagnosing a leak. `shutdown(SHUT_WR)` or closing the final relevant descriptor can initiate the local FIN; process exit or an abort can also change the state.

## RST: aborting a connection

An accepted, valid RST tells the peer "this connection does not exist, or is being torn down now". A reset is not itself acknowledged and normally aborts the connection without a graceful FIN/TIME_WAIT sequence. Invalid RSTs can be ignored or challenged, and existing TIME_WAIT handling has additional rules. Common causes:

- **SYN to a port nobody listens on**: normal unfiltered TCP processing replies with RST, which the client can report as `ECONNREFUSED` ("connection refused"). If a firewall silently drops the SYN instead, the client sees a timeout.
- **Segment for an unknown connection**: for example after a server reboots and forgets its connections. The client can receive a reset once traffic reaches the rebooted peer; the exact API error depends on state and operations.
- **Abortive close**: on Linux, enabled `SO_LINGER` with a timeout of 0, then `close()`, sends RST instead of FIN. Load balancers sometimes do this to avoid TIME_WAIT.
- **Closing with unread data**: Linux sends RST if the application closes a socket while received data sits unread in its buffer, because that data will never be delivered.
- **Middleboxes**: firewalls and NATs that time out an idle connection may reset it.

A forged valid RST can abort a connection. For synchronized connections, [RFC 5961](https://www.rfc-editor.org/rfc/rfc5961) specifies accepting an RST only when its sequence number exactly matches the next expected sequence-space position. Opening-state reset validation follows separate rules. If it is merely in the window, the stack sends a **challenge ACK** instead, which can elicit a correctly sequenced reset from a peer that has lost the connection. This is a robustness check, not cryptographic authentication; rate limits and side channels affect practical attack resistance.

## Key takeaways
- The three-way handshake exchanges and acknowledges both initial sequence numbers; SYN and FIN each consume one sequence number.
- ISNs are randomised to reject stale segments and resist spoofed injection.
- SYN floods can exhaust establishment resources; SYN cookies avoid an ordinary per-attempt half-open entry while still relying on server-wide secrets and consuming processing resources. A valid cookie acknowledgement only shows the client can receive packets at its address; it is not cryptographic client identity.
- Each direction of an ordinary graceful close uses its own FIN. In the sequential close model, the active closer ends in TIME_WAIT for twice the MSL (60 s in Linux v6.12) to ACK a retransmitted FIN and let old duplicates expire.
- TIME_WAIT is normal; unexplained CLOSE_WAIT growth warrants investigation of application lifecycle and descriptor ownership.
- An accepted valid RST normally aborts the connection; invalid resets may be ignored or challenged. Refused attempts, unknown connections and some close paths can generate resets.

## Further reading
- [RFC 9293: Transmission Control Protocol](https://www.rfc-editor.org/rfc/rfc9293)
- [RFC 4987: TCP SYN Flooding Attacks and Common Mitigations](https://www.rfc-editor.org/rfc/rfc4987)
- [SYN cookies — Wikipedia](https://en.wikipedia.org/wiki/SYN_cookies)
- [Coping with the TCP TIME-WAIT state on busy Linux servers — Vincent Bernat](https://vincent.bernat.ch/en/blog/2014-tcp-time-wait-state-linux)
- [SYN packet handling in the wild — Cloudflare blog](https://blog.cloudflare.com/syn-packet-handling-in-the-wild/)
- [RFC 6528: Defending against Sequence Number Attacks](https://www.rfc-editor.org/rfc/rfc6528)

> [!note] Content omitted after review
> A universal request-socket byte size, original cookie bit layout, historical attacker attribution and unconditional timeout/option guarantees are omitted because this pass did not establish adequate implementation-dependent evidence. Cookie handling and state diagrams here are teaching models, not an exhaustive TCP implementation.

- [Linux TCP configuration defaults](https://kernel.org/doc/html/latest/networking/ip-sysctl.html)
