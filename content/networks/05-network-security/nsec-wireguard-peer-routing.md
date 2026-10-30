---
id: nsec-wireguard-peer-routing
title: WireGuard keys, routes and AllowedIPs
level: advanced
minutes: 3
summary: WireGuard fixes its cryptographic suite rather than negotiating cipher suites.
sourceLesson: nsec-vpns
---

WireGuard ties public-key identities to address prefixes. This unit distinguishes the operating system’s route decision, the peer chosen for an outbound packet, and the source check on a decrypted inbound packet.

## WireGuard

**WireGuard** (in the Linux kernel since 5.6, 2020) is a deliberately minimal VPN. Its design choices are the opposite of IPsec's:

| | IPsec | WireGuard |
|---|---|---|
| Algorithms | Negotiated | Fixed set |
| Configuration model | Many suites and policy choices | Fixed cryptographic suite |
| Identity | Certs or PSK | Public keys |
| Transport | ESP or UDP | UDP only |

There is no cipher negotiation: WireGuard uses Curve25519, ChaCha20-Poly1305 and BLAKE2s inside a Noise-protocol handshake. If those ever need replacing, the protocol version changes. This removes cipher-suite negotiation as a downgrade surface, while key distribution, routing, access policy and implementation security still matter.

A data packet carries a 16-byte header (type, receiver index, 64-bit counter) and a 16-byte authentication tag: 32 bytes, plus outer UDP and IP. Rekeying uses message and time thresholds. For example, an active initiator triggers a new handshake when sending after a session key reaches the 120-second threshold; this is not a guarantee of a handshake every two minutes while idle.

### Cryptokey routing

Each peer is a public key with **AllowedIPs** prefixes. OS routing must first select the WireGuard interface; its cryptokey table then selects a peer. The following is a wg-quick-style configuration; the wrapper normally installs routes derived from AllowedIPs:

```ini
[Interface]
PrivateKey = <laptop-private-key>
Address = 10.8.0.2/32

[Peer]
PublicKey = <server-public-key>
Endpoint = vpn.example.com:51820
AllowedIPs = 10.8.0.0/24, 10.20.0.0/16
PersistentKeepalive = 25
```

- **Outbound**: a packet routed into WireGuard selects the peer by longest-prefix match on its destination in the cryptokey table.
- **Inbound**: after authentication, the inner source address must select that same sending peer in the cryptokey table. Merely matching one of its broader prefixes is insufficient if a more-specific prefix selects a different peer.

> [!analogy] Real-world analogy: couriers with named delivery rounds
> A company uses several trusted couriers, each recognised by a personal seal and each assigned a list of districts. Outgoing parcels for a district go to the courier whose list covers it most precisely. When a courier hands in a parcel, reception checks the seal and then checks that the parcel's sender address is in that courier's districts; a parcel claiming to come from someone else's district is refused.
>
> **How it maps:** The seal is the peer's public key, the district list is AllowedIPs, choosing the most precise list is longest-prefix matching on the destination, and the reception check is the inbound source-address test after decryption. Together they are cryptokey routing.
>
> **Where it stops:** A parcel only reaches the courier desk if the building's own routing sends it there: the operating system's route table must first send the packet to the WireGuard interface. And there is no negotiation of seal types: WireGuard's algorithms are fixed.

This laptop uses a **split tunnel**: only the two internal ranges go through the VPN. With suitable OS routes, `AllowedIPs = 0.0.0.0/0, ::/0` supports a **full tunnel** for ordinary IPv4/IPv6 destinations. Endpoint, local and policy-route exceptions still need handling. `PersistentKeepalive = 25` enables periodic authenticated empty packets when needed during idle periods, intended to keep a NAT mapping open when its timeout and policy permit (the earlier firewall units’ idle timeouts again).

WireGuard avoids replies to random invalid probes. This is not absolute invisibility: under load, a packet with a valid MAC derived from the responder's public key can elicit a cookie reply before full peer authentication. Other network behaviour can also leak information.

## Key takeaways
- WireGuard fixes its cryptographic suite rather than negotiating cipher suites.
- OS routing selects the interface before AllowedIPs selects the peer.
- Inbound source lookup must select the authenticated sending peer; split and full tunnels also depend on OS routes.

## Further reading
- [WireGuard: Next Generation Kernel Network Tunnel (whitepaper)](https://www.wireguard.com/papers/wireguard.pdf)
- [WireGuard: protocol and cryptography](https://www.wireguard.com/protocol/)
- [wg-quick(8) manual page](https://man7.org/linux/man-pages/man8/wg-quick.8.html)
