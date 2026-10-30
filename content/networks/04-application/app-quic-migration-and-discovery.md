---
id: app-quic-migration-and-discovery
title: "QUIC address changes and HTTP/3 discovery"
level: intermediate
minutes: 3
sourceLesson: app-http2-quic
summary: "Suitable connection IDs and routing let QUIC retain connection state across some address changes."
---

## Connection migration

Ordinary TCP identifies an established connection by its endpoint addresses and ports. A changed externally visible tuple cannot simply continue that connection without additional mechanisms. A brief outage can recover if the tuple and state survive; VPNs, stable addressing or Multipath TCP can change handover behaviour. NAT rebinding can disrupt ordinary TCP, but neither every handover nor every idle period necessarily changes that tuple.

A QUIC connection is identified by **connection IDs**, not addresses. So the server can keep a connection alive when packets arrive from a new address:

```
Client (Wi-Fi 192.0.2.7)    Server
  | 1-RTT DCID=A ----------->|
  .. switches to 5G ........
Client (5G 198.51.100.4)
  | 1-RTT DCID=B ----------->| new path!
  |<---- PATH_CHALLENGE(x) --|
  | PATH_RESPONSE(x) ------->|
  |       path validated     |
```

1. **Spare connection IDs.** When nonzero connection IDs are used, endpoints can issue spare IDs with NEW_CONNECTION_ID. On a deliberate new local-address path, a fresh peer-issued ID avoids linking paths by reusing that ID. It does not prevent correlation by timing, packet sizes or an observer that sees both paths.
2. **Path validation.** The server sends PATH_CHALLENGE with 8 random bytes to the new address and needs them echoed in PATH_RESPONSE. A matching protected response validates reachability on that path. It does not establish a user’s physical location or defeat an attacker that can relay traffic. Until validation, the anti-amplification limit applies.
3. **Congestion state is reset.** The new path may have completely different bandwidth and RTT, so validation normally triggers resetting congestion and RTT state. RFC 9000 permits retaining state for a port-only address change, with caution about potentially different path characteristics.

> [!analogy] Real-world analogy: Moving house without closing your bank account
> When you move, your bank keeps your account because it is identified by an account number, not your address. Before posting statements to the new address, a careful bank sends a random code there and waits for you to read it back.
>
> **How it maps:** The account number is the connection ID, which keeps the QUIC connection alive when the client's address changes. The random code is PATH_CHALLENGE, and reading it back is PATH_RESPONSE. Until the code comes back, the bank sends little to the new address, as the anti-amplification limit requires. Using a fresh connection ID on the new path is like quoting a new reference so observers cannot easily link the two addresses.
>
> **Where it stops:** In QUIC, the connection's encryption keys show that packets come from the same peer; path validation itself only proves that someone at the new address can receive and return packets, which a relay could also do. A bank also does not reset anything when you move, whereas QUIC normally restarts congestion control because the new network may be much slower or faster.

Only the **client** may migrate actively. A server can advertise preferred_address during the handshake. disable_active_migration restricts deliberate migration to the specified server address; it does not prohibit NAT rebinding or a permitted move to the server’s preferred address.

> [!warning] Migration and load balancers
> If a layer-4 load balancer hashes the 4-tuple, a changed tuple may select a different server without connection state; hash collisions or state shared between servers can produce other outcomes. A coordinated CID-aware design can maintain routing across issued IDs, using a mapping or an encoded routing hint. It must also handle Initial routing and ID lifecycle.

## HTTP/3 discovery

A client can learn HTTP/3 support from configuration, cached knowledge, DNS or an `Alt-Svc: h3=":443"` response header, and may then open a QUIC connection. The `HTTPS` DNS record ([RFC 9460](https://www.rfc-editor.org/rfc/rfc9460)) can advertise `alpn=h3` before the first connection. Clients can race or fall back to TCP when QUIC is unavailable; policy varies and UDP blocking is one possible cause.

## Key takeaways
- Suitable connection IDs and routing let QUIC retain connection state across some address changes.
- Path validation checks reachability; migration does not guarantee availability or anonymity.

## Further reading
- [RFC 9000](https://www.rfc-editor.org/rfc/rfc9000)
- [RFC 9460](https://www.rfc-editor.org/rfc/rfc9460)
- [RFC 7838](https://www.rfc-editor.org/rfc/rfc7838)
