---
id: ip-dhcp-relays-security
title: Relay DHCP and constrain rogue servers
level: intermediate
minutes: 3
sourceLesson: ip-dhcp
summary: Use giaddr and relay information to select a pool, then apply managed-switch DHCP protections.
---

Use giaddr and relay information to select a pool, then apply managed-switch DHCP protections.

## Relays: one server for many subnets

The initial DHCP limited broadcast is not forwarded across routers as an ordinary IP packet, so a server on another subnet needs a relay to receive that discovery. Rather than run a server on every VLAN, routers act as **relay agents** (Cisco's `ip helper-address`):

```
client --bcast--> router --unicast--> DHCP
VLAN 20       giaddr 10.20.0.1      server
```

1. The router hears the broadcast Discover on its VLAN 20 interface.
2. It fills in **giaddr** with that interface's address (10.20.0.1) and unicasts the message to the server.
3. The server sees giaddr, uses its configured subnet mapping to pick an address from the pool for 10.20.0.0/24, and replies to the relay.
4. The relay passes the reply back onto VLAN 20.

The relay can also add **option 82** (relay agent information), identifying the switch port or circuit the request came from. ISPs use it to tie addresses to a physical line.

## DHCP security

Base DHCPv4 exchanges do not authenticate the server. Authentication extensions exist (RFC 3118), but without enforced authentication or a policy controlling network access, a device able to inject replies may impersonate a server.

A **rogue DHCP server**, whether an attacker or a consumer router connected with its DHCP service exposed to the LAN, can hand out its own address as the gateway and DNS. A client accepting those settings may send off-link traffic through that device or use its DNS service. This can enable interception or denial of service; it does not automatically reveal correctly authenticated TLS plaintext or intercept every local flow.

The defence on managed switches is **DHCP snooping**:

- Ports are marked **trusted** (towards real servers) or **untrusted** (everything else).
- Server messages (Offer, Ack) arriving on untrusted ports are dropped.
- The switch records a **binding table** of MAC, IP, port and VLAN from the Acks it sees. **Dynamic ARP inspection** and **IP source guard** can use these bindings to enforce configured source checks. Static addresses and trusted infrastructure require appropriate bindings or exceptions; these features do not make a compromised trusted server safe.

## Key takeaways
- A relay carries initial local broadcasts to a configured remote server.
- giaddr supplies subnet context; option 82 can identify a circuit.
- An accepted rogue server can misconfigure gateway or DNS without automatically defeating TLS.
- Snooping trust and bindings support DHCP, ARP and source checks within their configured limits.

## Further reading
- [RFC 2131: Dynamic Host Configuration Protocol](https://www.rfc-editor.org/rfc/rfc2131)
- [RFC 2132: DHCP Options and BOOTP Vendor Extensions](https://www.rfc-editor.org/rfc/rfc2132)
- [Dynamic Host Configuration Protocol — Wikipedia](https://en.wikipedia.org/wiki/Dynamic_Host_Configuration_Protocol)
- [DHCP snooping — Wikipedia](https://en.wikipedia.org/wiki/DHCP_snooping)
- [RFC 5227: IPv4 Address Conflict Detection](https://www.rfc-editor.org/rfc/rfc5227)
- [RFC 9915: DHCP for IPv6 (replaces RFC 8415)](https://www.rfc-editor.org/rfc/rfc9915.html)


- [RFC 3396: long DHCPv4 options](https://www.rfc-editor.org/rfc/rfc3396)
- [RFC 3927: IPv4 link-local addressing](https://www.rfc-editor.org/rfc/rfc3927)
- [RFC 3118: DHCP authentication](https://www.rfc-editor.org/rfc/rfc3118)
