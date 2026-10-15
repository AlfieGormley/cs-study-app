---
id: ip-bgp-sessions-reflectors
title: BGP sessions and route reflectors
level: advanced
minutes: 4
sourceLesson: ip-bgp
summary: Trace BGP’s TCP session and compare base iBGP mesh requirements with reflection.
---

Trace BGP’s TCP session and compare base iBGP mesh requirements with reflection.

### Sessions

BGP routers ("speakers") form sessions over **TCP port 179**, using configured peer relationships. Base BGP has no OSPF-style multicast Hello discovery, although implementations can automate provisioning or accept dynamic peers under configured rules. Its four base message types are:

| Message | Purpose |
|---|---|
| OPEN | Start session, exchange ASN and hold time |
| UPDATE | Announce or withdraw prefixes |
| KEEPALIVE | Maintain liveness at a suggested interval of at most a third of the hold time |
| NOTIFICATION | Error; close the session |

Once established, the hold timer limits how long a router waits without an accepted KEEPALIVE or UPDATE before closing the session. RFC 4271 suggests a default hold time of 90 seconds and a reasonable maximum KEEPALIVE interval of one third of the hold time:

```formula
t_KA ≤ t_hold / 3
t_KA ≤ 90 s / 3 = 30 s
where
t_KA: the interval between KEEPALIVE messages, in seconds (s)
t_hold: the negotiated hold time, in seconds; RFC 4271 suggests 90 s, and zero turns the hold timer and KEEPALIVEs off
≤: is at most
s: seconds
In words: the suggested interval schedules a KEEPALIVE at least three times per nonzero hold time when updates do not already maintain liveness. BGP uses TCP; packet loss, retransmission and delivery stalls affect when the next complete message reaches the receiver.
```

After the initial permitted route exchange, normal updates are incremental. Route-refresh extensions can request re-advertisements. KEEPALIVE or UPDATE receipt can reset the hold timer; negotiated hold time zero disables this timer and KEEPALIVEs. Memory needs depend on prefixes, paths, attributes and implementation.

### eBGP and iBGP

- **eBGP** runs between different ASes, usually over a direct link.
- **iBGP** runs between routers in the *same* AS, to distribute BGP reachability internally, subject to selection and export policy.

iBGP does not prepend the local ASN, so the AS_PATH cannot record internal router traversal. In base iBGP, an iBGP-learned route is not re-advertised to another internal peer, so every BGP router must have a session with every other one, a full mesh:

```formula
S = n(n − 1) / 2
S = 100 × 99 / 2 = 4,950
where
S: the number of iBGP sessions in a full mesh
n: the number of BGP routers in the AS, here 100
In words: each of the n routers needs a session with the n − 1 others, and dividing by 2 counts each shared session once. Doubling the routers roughly quadruples the sessions.
```

**Route reflectors** (RFC 4456) relax that restriction: selected client routes can be reflected to clients and non-clients, while non-client routes are reflected to clients. ORIGINATOR_ID and CLUSTER_LIST support reflection-loop detection. Confederations are another scaling approach.

## Key takeaways
- Base BGP uses configured TCP peer sessions on port 179.
- OPEN, UPDATE, KEEPALIVE and NOTIFICATION serve different purposes.
- Hold-time zero disables the hold timer and KEEPALIVEs.
- Route reflectors relax base iBGP redistribution restrictions and add loop-detection attributes.

## Further reading
- [RFC 4271: A Border Gateway Protocol 4 (BGP-4)](https://www.rfc-editor.org/rfc/rfc4271)
- [Border Gateway Protocol — Wikipedia](https://en.wikipedia.org/wiki/Border_Gateway_Protocol)
- [Understanding how Facebook disappeared from the Internet — Cloudflare blog](https://blog.cloudflare.com/october-2021-facebook-outage/)
- [How Verizon and a BGP Optimizer Knocked Large Parts of the Internet Offline — Cloudflare blog](https://blog.cloudflare.com/how-verizon-and-a-bgp-optimizer-knocked-large-parts-of-the-internet-offline-today/)
- [RFC 6811: BGP Prefix Origin Validation](https://www.rfc-editor.org/rfc/rfc6811)
- [BGP hijacking — Wikipedia](https://en.wikipedia.org/wiki/BGP_hijacking)
- [MANRS](https://www.manrs.org/)

- [RIPE NCC: YouTube hijacking presentation and timeline](https://ripe56.ripe.net/presentations/Refice-YouTube_Prefix_Hijacking.pdf)
- [Meta: October 2021 outage details](https://engineering.fb.com/2021/10/05/networking-traffic/outage-details/)
- [Cloudflare: BGP leaks and cryptocurrencies](https://blog.cloudflare.com/bgp-leaks-and-crypto-currencies/)
- [Cisco: BGP best-path algorithm](https://www.cisco.com/c/en/us/support/docs/ip/border-gateway-protocol-bgp/13753-25.html)
- [IETF: ASPA verification draft](https://datatracker.ietf.org/doc/draft-ietf-sidrops-aspa-verification/)
- [RFC 9319: RPKI maxLength](https://www.rfc-editor.org/rfc/rfc9319)
