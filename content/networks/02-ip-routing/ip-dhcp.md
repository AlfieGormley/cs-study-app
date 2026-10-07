---
id: ip-dhcp
title: DHCP and joining a network
level: intermediate
minutes: 15
summary: How a device with no address gets one through DHCP's four-message exchange, how leases, relays and snooping work, and a step-by-step trace of everything that happens from plugging in to the first packet reaching a remote server.
---

A laptop joining a café network can obtain an IPv4 address, subnet mask, gateway and DNS settings automatically. A common mechanism is the **Dynamic Host Configuration Protocol** (DHCPv4, RFC 2131), using a protocol designed for a host that doesn't yet have an address.

This lesson covers DHCP itself, then ties the whole module together by following a device from "link up" to its first packet crossing the Internet.

## The chicken-and-egg problem

To ask a server for an address, you normally need an address. DHCP gets around this with two tricks:

- The client sends from source **0.0.0.0**, meaning "I don't have one yet".
- It sends to **255.255.255.255**, the limited broadcast, addressed to the local link rather than forwarded as an ordinary IP broadcast across routers. Delivery can still be filtered or lost.

DHCP runs over UDP: servers listen on **port 67**, clients on **port 68**. Fixed ports on both sides matter, because replies may be broadcast, and the client needs to recognise them.

## DORA: the four-message exchange

```
Client                       Server
  |--- DISCOVER (broadcast) --->|
  |<-- OFFER  192.168.1.42 -----|
  |--- REQUEST (broadcast) ---->|
  |<-- ACK -------------------- |
```

1. **Discover**: "Is there a DHCP server? Here is my client identification." The client picks a random 32-bit **transaction ID** (`xid`) to match replies to this request.
2. **Offer**: an eligible server may offer an address and settings, subject to pool availability and policy. Several servers might reply.
3. **Request**: the client picks one offer and broadcasts a Request naming that server (option 54, server identifier) and the address (option 50). Broadcasting it tells the *other* servers their offers were declined, so any temporary offer reservations can be released. A server need not reserve an offered address.
4. **Ack**: the chosen server confirms. The client validates the configuration and checks for an address conflict before using it.

Before using it, the client should check nobody else already does: it sends **ARP probes** for the address (RFC 5227). A conflicting ARP announcement/reply or another host's simultaneous probe can reveal a collision. The client sends **DHCPDECLINE** and restarts after a delay (RFC 2131 recommends at least ten seconds). If all is clear, it announces itself with a **gratuitous ARP**, which can refresh peers' ARP caches; it cannot guarantee every peer updates its cache.

A server can send **DHCPNAK** when it determines that a requested configuration is invalid, such as an address on the wrong subnet. Other cases require silence rather than a NAK—for example, an unselected server hearing a Request selecting another server. A client receiving a NAK restarts configuration.

### The message

A DHCPv4 message uses the BOOTP-format header, a magic cookie and options. Option overload can also place options in designated BOOTP fields:

| Field | What it holds |
|---|---|
| xid | Transaction ID |
| ciaddr | Client's current IP, if any |
| yiaddr | "Your" address: the one offered |
| giaddr | Relay agent's address |
| chaddr | Client hardware address (a MAC for Ethernet) |
| options | Type-length-value list |

The options carry everything interesting:

| Code | Option |
|---|---|
| 1 | Subnet mask |
| 3 | Router (default gateway) |
| 6 | DNS servers |
| 50 | Requested IP address |
| 51 | Lease time |
| 53 | Message type (1 = Discover … 5 = Ack) |
| 54 | Server identifier |
| 55 | Parameter request list |

Most options use type-length-value encoding; Pad and End are single-byte exceptions. This teaching parser accepts one options field **after** the magic cookie, checks lengths, concatenates repeated option payloads (RFC 3396) and requires End. It does not validate option-specific semantics or process overloaded fields:

```python
def parse_options(b):
    opts, i = {}, 0
    while i < len(b):
        code = b[i]
        if code == 255:      # End
            break
        if code == 0:        # Pad
            i += 1
            continue
        if i + 1 >= len(b):
            raise ValueError(
                "missing option length")
        n = b[i + 1]
        if i + 2 + n > len(b):
            raise ValueError(
                "truncated option payload")
        part = b[i + 2:i + 2 + n]
        previous = opts.get(code, b"")
        opts[code] = previous + part
        i += 2 + n
    else:
        raise ValueError("missing End")
    return opts

raw = bytes([53, 1, 5,
             51, 4, 0, 0, 0x0e, 0x10,
             3, 4, 192, 168, 1, 1,
             255])
o = parse_options(raw)
print(o[53][0])                    # 5
print(int.from_bytes(o[51], "big"))  # 3600
```

Message type 5 is an Ack; the lease is 0x0e10 = 3,600 seconds; the gateway is 192.168.1.1.

## Leases

Dynamic allocation uses **leases**, allowing addresses to be reused after clients release them or leases expire. DHCP also supports other allocation arrangements; reuse depends on concurrent demand and lease retention, not just visitor count.

For a finite lease, nominal default timers are below. Servers can supply different T1/T2 values; RFC 2131 recommends random timing variation, and a client may seek renewal early:

- **T1 = 50%** of the lease: start **renewing**. Unicast a Request directly to the server that granted the lease.
- **T2 = 87.5%** of the lease: if the server hasn't answered, start **rebinding**. Broadcast a Request so another server with sufficient state and authority may extend it.

If the lease expires with no answer, the client must stop using the address. Ignoring timing variation and explicit overrides, a 24-hour lease gives T1 = 12 hours and T2 = 21 hours, measured from the lease-start reference—not simply from delayed ACK arrival.

```python
def timers(lease):
    # Nominal defaults for finite seconds.
    # 0xffffffff represents infinity.
    if (type(lease) is not int
            or not 0 < lease < 0xffffffff):
        raise ValueError("bad finite lease")
    return lease * 0.5, lease * 0.875

print(timers(86400))  # (43200.0, 75600.0)
```

A client leaving cleanly can send **DHCPRELEASE**, but many just disappear and let the lease expire.

Lease length is a trade-off. Short leases (an hour) recycle addresses quickly in busy guest networks but generate more traffic and make the server more critical. Long leases (days) suit stable office networks.

Servers usually hand the same client the same address again where they can, keyed on its MAC or client identifier. **Reservations** associate a stable address with configured client identification, which may be a MAC or a client identifier depending on the server. MAC randomisation or identifier changes can affect that association.

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

Base DHCPv4 exchanges do not authenticate the server. Authentication extensions exist (RFC 3118), but without an enforced authentication or network-access policy, a device able to inject replies may impersonate a server.

A **rogue DHCP server**, whether an attacker or a consumer router connected with its DHCP service exposed to the LAN, can hand out its own address as the gateway and DNS. A client accepting those settings may send off-link traffic through that device or use its DNS service. This can enable interception or denial of service; it does not automatically reveal correctly authenticated TLS plaintext or intercept every local flow.

The defence on managed switches is **DHCP snooping**:

- Ports are marked **trusted** (towards real servers) or **untrusted** (everything else).
- Server messages (Offer, Ack) arriving on untrusted ports are dropped.
- The switch records a **binding table** of MAC, IP, port and VLAN from the Acks it sees. **Dynamic ARP inspection** and **IP source guard** can use these bindings to enforce configured source checks. Static addresses and trusted infrastructure require appropriate bindings or exceptions; these features do not make a compromised trusted server safe.

## When there's no DHCP server

Depending on operating-system configuration, a host may self-configure an IPv4 **link-local** address (RFC 3927, called APIPA on Windows). Automatic selection uses 169.254.1.0 through 169.254.254.255, excluding the first and last /24 of 169.254.0.0/16, and probes for conflicts. Such traffic remains on the link; routers must not forward it.

> [!tip] Diagnosing with the address
> An automatically configured 169.254.x.x address can suggest missing routable IPv4 configuration, so check DHCP logs, VLANs, relays and server reachability when DHCP was expected. The address alone does not prove DHCP failed: link-local can be intentional and can coexist with other configuration.

### And IPv6?

IPv6 hosts can configure addresses with SLAAC from suitable router advertisements (see the NAT and IPv6 lesson). **DHCPv6** exists alongside it, on UDP ports 546 (client) and 547 (server), with a common four-message exchange: Solicit, Advertise, Request, Reply. Rapid Commit permits a two-message exchange, and other exchanges serve other purposes. DHCPv6 does not provide the standard default-router discovery mechanism: hosts normally learn default routers from RAs, but static routes are also possible. **Prefix delegation** can give a requesting router a prefix, such as /56 or /48; actual sizes depend on provider policy.

## Joining a network, end to end

This hypothetical IPv4 trace assumes Ethernet-like LAN/WAN links, a fresh DHCP lease, uncached DNS using the gateway resolver, a TCP connection, one NAPT gateway and ordinary IP forwarding. The public-looking addresses are documentation ranges, not live endpoints. Other networks may use different discovery, DNS, transport and forwarding mechanisms.

```
laptop          home router (NAT)
192.168.1.42 -> 192.168.1.1
                203.0.113.7 -> ISP
ISP routers (OSPF inside, BGP at edge)
  -> ... -> server 198.51.100.80
```

**1. Link up.** The Wi-Fi association completes. The laptop has a MAC but no IP.

**2. DHCP.** DORA gives it 192.168.1.42/24, gateway 192.168.1.1, DNS 192.168.1.1, 24-hour lease. It probes for conflicts with ARP and sends a gratuitous ARP. Its routing table is now a connected route for 192.168.1.0/24 and a default route via 192.168.1.1. In parallel, SLAAC may give it IPv6 addresses.

**3. ARP for the gateway.** The laptop needs 192.168.1.1's MAC, for DNS and for everything off-link. It broadcasts an ARP request and caches the reply.

**4. DNS.** It resolves the server's name by sending a UDP query to 192.168.1.1, which forwards it to the ISP's resolvers. (With Happy Eyeballs, it asks for AAAA and A records and may race IPv6 and IPv4.)

**5. Route lookup.** For 198.51.100.80, longest-prefix match finds only the default route. The SYN goes in a frame addressed to the router's MAC, with IP destination 198.51.100.80 and TTL 64.

**6. The home router.** It decrements TTL to 63, looks up the destination (its own default route, towards the ISP), and applies NAPT: source 192.168.1.42:51000 becomes 203.0.113.7:40000. It fixes the IP and TCP checksums and sends a new frame on its WAN link.

**7. Across the ISP.** Each router decrements TTL and does LPM. Inside the ISP, an IGP such as OSPF or IS-IS provides paths to the ISP's own border routers. At the border, a BGP-learnt route for the server's prefix (perhaps a /24 announced by a hosting provider) says which neighbouring AS to hand it to.

**8. The server and back.** The SYN arrives with source 203.0.113.7:40000. The SYN-ACK goes back to that address, perhaps by a different path. The home router finds the mapping, rewrites the destination to 192.168.1.42:51000 and delivers it. The TCP handshake completes.

No end-to-end timing bound follows from this trace: association, address-conflict checks, DNS and network latency all contribute. These symptoms suggest investigations rather than unique diagnoses:

| Symptom | Possible investigation |
|---|---|
| Unexpected automatic 169.254.x.x address | DHCP and interface configuration |
| Reachable known IP but name resolution fails | DNS configuration and resolver path |
| LAN works, Internet doesn't | Gateway, NAT, ISP |
| Small transfers work, large transfers hang | MTU / PMTUD, loss and transport behaviour |
| Two devices interfere with each other | Check for duplicate IPs and link faults |

## Key takeaways
- DHCP bootstraps a host with no address using broadcasts from 0.0.0.0 to 255.255.255.255 on UDP ports 68 and 67.
- DORA: Discover, Offer, Request (broadcast, so other servers withdraw their offers), Ack; then an ARP check, and Decline on conflict.
- Nominal default renewal/rebinding thresholds are 50% and 87.5%; overrides, early renewal and timing variation exist.
- Relay agents forward broadcasts to a central server, using giaddr to choose the pool and option 82 to identify the port.
- Rogue servers enable man-in-the-middle attacks; DHCP snooping, ARP inspection and source guard defend against them.
- Joining a network chains DHCP, ARP, DNS, longest-prefix match, NAT, IGPs and BGP; knowing the assumed chain helps organise troubleshooting without treating symptoms as proof.

## Further reading
- [RFC 2131: Dynamic Host Configuration Protocol](https://www.rfc-editor.org/rfc/rfc2131)
- [RFC 2132: DHCP Options and BOOTP Vendor Extensions](https://www.rfc-editor.org/rfc/rfc2132)
- [Dynamic Host Configuration Protocol — Wikipedia](https://en.wikipedia.org/wiki/Dynamic_Host_Configuration_Protocol)
- [DHCP snooping — Wikipedia](https://en.wikipedia.org/wiki/DHCP_snooping)
- [RFC 5227: IPv4 Address Conflict Detection](https://www.rfc-editor.org/rfc/rfc5227)
- [RFC 9915: DHCP for IPv6 (replaces RFC 8415)](https://www.rfc-editor.org/rfc/rfc9915.html)

> [!note] Content omitted after review
> Universal setup times, operating-system fallback behaviour and provider prefix-size prevalence are omitted because this review did not establish reliable versioned evidence. The packet trace is an illustrative model, not a measured deployment.

- [RFC 3396: long DHCPv4 options](https://www.rfc-editor.org/rfc/rfc3396)
- [RFC 3927: IPv4 link-local addressing](https://www.rfc-editor.org/rfc/rfc3927)
- [RFC 3118: DHCP authentication](https://www.rfc-editor.org/rfc/rfc3118)
