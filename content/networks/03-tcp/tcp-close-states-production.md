---
id: tcp-close-states-production
sourceLesson: tcp-connections
title: Close states and tuple reuse in production
level: intermediate
minutes: 3
summary: Close states and tuple reuse in production, with worked examples and explicit assumptions.
---

## TIME_WAIT in production

TIME_WAIT is cheap (Linux keeps a small, stripped-down structure), but it constrains reuse of the **5-tuple** under the implementation’s rules:

- A client or proxy making many short connections to **one** backend can exhaust ephemeral ports (the UDP and ports units).
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

## Key takeaways

- Tuple reuse constraints can matter for short-lived clients even when a server shares one listening port.
- Simultaneous FINs can take both peers through CLOSING and TIME_WAIT under the stated event order.
- Persistent unexplained CLOSE_WAIT growth needs application and descriptor investigation.

## Further reading

- [RFC 9293: Transmission Control Protocol](https://www.rfc-editor.org/rfc/rfc9293)
- [RFC 4987: TCP SYN Flooding Attacks and Common Mitigations](https://www.rfc-editor.org/rfc/rfc4987)
- [SYN cookies — Wikipedia](https://en.wikipedia.org/wiki/SYN_cookies)
- [Coping with the TCP TIME-WAIT state on busy Linux servers — Vincent Bernat](https://vincent.bernat.ch/en/blog/2014-tcp-time-wait-state-linux)
- [SYN packet handling in the wild — Cloudflare blog](https://blog.cloudflare.com/syn-packet-handling-in-the-wild/)
- [RFC 6528: Defending against Sequence Number Attacks](https://www.rfc-editor.org/rfc/rfc6528)
- [Linux TCP configuration defaults](https://kernel.org/doc/html/latest/networking/ip-sysctl.html)
