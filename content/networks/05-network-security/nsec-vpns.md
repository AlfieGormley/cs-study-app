---
id: nsec-vpns
title: IPsec, WireGuard, tunnels and VXLAN
level: advanced
minutes: 15
summary: How tunnels encapsulate one network inside another, what IPsec and WireGuard add on top, how anti-replay windows work, why every tunnel shrinks the MTU and by how much, and why VXLAN overlays need protecting.
---

A **tunnel** carries packets of one network as the payload of packets on another. Wrap a packet addressed to `10.20.0.5` inside a packet addressed to your office's public IP, send it across the internet, unwrap it at the far end, and the office network sees what looks like a local packet.

Tunnels on their own provide reachability, not security. Here, **VPN** means a cryptographically protected IP tunnel: it authenticates the two ends, and encrypts and integrity-protects what flows between them. This lesson covers the plain tunnels (GRE, VXLAN), two examples of protected VPN protocols (IPsec and WireGuard), and the practical problem they all share: overhead and MTU.

## Encapsulation and the MTU tax

Every tunnel adds headers. The physical link's MTU (usually 1,500 bytes for Ethernet) does not change, so the inner packet must shrink:

```
 outer packet on the wire (<= 1500)
+--------+-------+-----+---------------+
| outer  | UDP   | tun | inner packet  |
| IP hdr | (opt) | hdr | (<= MTU - oh) |
+--------+-------+-----+---------------+
```

Because the outer packet still has to fit the link, the room left for the inner packet is the link MTU minus every header the tunnel adds:

```formula
MTU_inner = MTU_link − H_total
H_total = H_1 + H_2 + … + H_k
where
MTU_inner: the largest inner IP packet that fits without fragmentation, in bytes
MTU_link: the maximum transmission unit (MTU) of the underlying link or path, in bytes; usually 1,500 for Ethernet
H_total: the total overhead the tunnel adds, in bytes
H_1: the size of the first added header, in bytes (for example, an outer IPv4 header, 20 bytes)
H_2: the size of the second added header, in bytes
H_k: the size of the last added header, in bytes
k: the number of headers the tunnel adds
…: and so on, for every header in between
In words: every byte of tunnel header comes straight out of the space available for the packet inside.
```

Applying it to three common tunnels, with the header sizes used in the code below:

```formula
M_GRE = 1500 − (20 + 4) = 1476 B
M_WG = 1500 − (40 + 8 + 32) = 1420 B
M_VX = 1500 − (20 + 8 + 8 + 14)
M_VX = 1500 − 50 = 1450 B
where
M_GRE: inner MTU for GRE over IPv4: a 20-byte outer IPv4 header plus a 4-byte basic GRE header
M_WG: inner MTU for WireGuard over IPv6: a 40-byte outer IPv6 header, an 8-byte UDP header, and 32 bytes of WireGuard data overhead (a 16-byte header plus a 16-byte authentication tag)
M_VX: inner MTU for VXLAN over IPv4: outer IPv4 (20), UDP (8), the VXLAN header (8) and the inner Ethernet header it carries (14)
B: bytes
In words: on a 1,500-byte link, these tunnels leave 1,476, 1,420 and 1,450 bytes for the inner IP packet.
```

The same arithmetic as code, with a header-size table you can extend:

```python
HDR = {"ipv4": 20, "ipv6": 40, "udp": 8,
       "wg": 32, "vxlan": 8, "eth": 14,
       "gre": 4}

def inner_mtu(link_mtu, *layers):
    if type(link_mtu) is not int:
        raise TypeError("integer MTU")
    used = sum(HDR[x] for x in layers)
    if link_mtu <= used:
        raise ValueError("no capacity")
    return link_mtu - used

print(inner_mtu(1500, "ipv4", "gre"))
print(inner_mtu(1500, "ipv6", "udp", "wg"))
print(inner_mtu(1500, "ipv4", "udp",
                "vxlan", "eth"))
```

This prints `1476`, `1420` and `1450`: inner IP size budgets for these exact header assumptions: basic GRE over IPv4, WireGuard over IPv6, and untagged VXLAN over IPv4. They are not universal interface defaults. Options, VLAN tags, extra tunnels and path MTU change the budget; WireGuard padding is bounded so it does not exceed the selected MTU.

### When the MTU is wrong

If a host sends 1,500-byte packets into a 1,420-byte tunnel, the packets must be fragmented or dropped. With the IPv4 Don't Fragment bit set (as TCP normally does) or with IPv6, the router drops the packet and sends back an ICMP "packet too big" message so the sender can shrink. This is **path MTU discovery** (PMTUD).

Firewalls that block all ICMP break it. The result is a **PMTU black hole**: the TCP handshake and small requests work, but anything large stalls. "SSH connects but `git clone` hangs" through a VPN is the classic symptom.

The usual fixes:

- Set the tunnel interface MTU correctly (using the actual underlay budget; wg-quick can infer an initial value).
- **Clamp the TCP MSS** at the tunnel edge to advertise an appropriate data budget. The maximum segment size (MSS) is how much TCP data fits in one packet once the IP and TCP headers are taken out (the formula follows this list). Senders must account for options, and an MSS clamp does not fix UDP or later path changes.
- Allow ICMP "packet too big" (ICMPv4 type 3 code 4, ICMPv6 type 2) through firewalls.

The MSS to clamp to, with minimum-size IPv4 and TCP headers:

```formula
MSS = MTU − (H_IP + H_TCP)
MSS = 1420 B − (20 B + 20 B) = 1380 B
where
MSS: maximum segment size: the most TCP payload in one segment, in bytes
MTU: the maximum transmission unit of the tunnel interface, in bytes; here 1,420
H_IP: the IPv4 header without options, 20 bytes (an IPv6 header is 40)
H_TCP: the TCP header without options, 20 bytes
B: bytes
In words: inside a 1,420-byte tunnel, each TCP segment can carry at most 1,380 bytes of data once the 40 bytes of IPv4 and TCP headers are subtracted.
```

Over IPv6 the subtraction is 60 bytes instead of 40, and TCP options such as timestamps reduce the data further.

## GRE: a plain tunnel

**GRE** (Generic Routing Encapsulation, IP protocol 47) has a 4-byte base header, with optional fields adding overhead, and can encapsulate different payload protocols. It is simple and widely supported by routers, and it gives **no confidentiality or authentication at all**. Anyone on the path can read it, and forged traffic may be accepted if it reaches an endpoint without effective filtering or other validation. GRE is therefore often run *inside* IPsec when routing protocols need a tunnel interface.

## IPsec

**IPsec** secures IP packets at the network layer, and can protect selected traffic without application changes, according to configured policies. It is the standard for site-to-site VPNs between offices, data centres and cloud VPCs (AWS Site-to-Site VPN, Azure VPN Gateway).

It has two halves:

1. **IKEv2** (UDP 500) is the control plane. The peers authenticate each other (with certificates or a pre-shared key), agree on algorithms and derive keys. IKE establishes a bidirectional IKE SA (with separate 64-bit initiator/responder SPIs) and negotiates Child SAs for data traffic. An ESP Child-SA pair contains unidirectional SAs with 32-bit SPIs.
2. **ESP** (IP protocol 50) is the data plane: it protects the selected data packets using the negotiated SA algorithms. The encrypted-and-authenticated examples here use AEAD; ESP also permits other protection combinations, including integrity without encryption.

There is also **AH** (protocol 51), which authenticates without encrypting. AH also authenticates relevant immutable IP-header fields; mutable fields receive special treatment. Address-rewriting NAT normally conflicts with that authentication.

### Transport and tunnel mode

```
Transport mode:
 [IP][ESP hdr]{TCP|data|trailer}[ICV]

Tunnel mode:
 [new IP][ESP hdr]
   {inner IP|TCP|data|trailer}[ICV]

 {braces} = encrypted portion
```

For these confidentiality-enabled ESP examples, **tunnel mode** encrypts the original IP packet, including its inner addresses, and is suitable for site-to-site VPNs. **Transport mode** leaves the original IP header outside encryption. The ESP trailer is encrypted; the ESP header and authentication tag are not. Actual protection follows the negotiated algorithms.

With a 16-byte tag, no extra options or traffic-flow padding, ESP tunnel mode using AES-GCM adds 54 to 57 bytes over IPv4. Padding varies because ESP must make the encrypted part end on a 4-byte boundary:

```formula
O_ESP = H_IP + H_ESP + IV + P + T + ICV
O_min = 20 + 8 + 8 + 0 + 2 + 16 = 54 B
O_max = 20 + 8 + 8 + 3 + 2 + 16 = 57 B
where
O_ESP: the total bytes ESP tunnel mode adds to each packet
O_min: the overhead with no padding needed
O_max: the overhead with the most padding (3 bytes)
H_IP: the new outer IPv4 header, 20 bytes
H_ESP: the ESP header: SPI (4 bytes) and sequence number (4 bytes), 8 bytes
IV: initialisation vector sent with each packet for AES-GCM, 8 bytes
P: padding, 0 to 3 bytes, so the encrypted part ends on a 4-byte boundary
T: the trailer's pad-length and next-header fields, 1 byte each, 2 bytes
ICV: integrity check value: the 16-byte authentication tag
B: bytes
In words: AES-GCM ESP tunnel mode over IPv4 costs between 54 and 57 bytes per packet, depending on how much padding the inner packet needs.
```

### NAT traversal

ESP has no TCP/UDP ports, complicating port-based NAT multiplexing; some devices implement ESP-specific passthrough. When IKE detects a NAT on the path, both peers switch to **NAT-T**: ESP is wrapped in UDP on port 4500, adding another 8 bytes. If a site-to-site VPN negotiates but no traffic flows, check that UDP 500 and 4500 (and protocol 50, if there is no NAT) are allowed.

### Anti-replay

Each ESP packet carries a sequence number. The receiver keeps a **sliding window** (RFC 4303 recommends 64 packets) so that it tolerates packets arriving slightly out of order but rejects duplicates and anything too old. WireGuard and DTLS use the same idea.

The receiver accepts an authenticated packet only when both conditions on the first line hold, and then updates its highest-seen number:

```formula
s > s_top − W   and   s ∉ S
s_new = max(s_top, s)
where
s: the sequence number of the arriving packet
s_top: the highest sequence number accepted so far
W: the window size, in packets; RFC 4303 recommends 64
S: the set of sequence numbers already accepted inside the window
∉: "is not a member of": s has not been accepted before
s_new: the highest accepted sequence number after this packet
max: the larger of the two values
In words: a packet is accepted only if it is newer than the bottom of the window and has not been seen before; a new highest number slides the window forward.
```

For example, with *W* = 4 and *s_top* = 5, the window covers 2 to 5: packet 3 is accepted if unseen, packet 1 is rejected because it is not greater than 5 − 4 = 1, and packet 9 is accepted and moves *s_top* to 9.

```python
class ReplayWindow:
    def __init__(self, size):
        if (type(size) is not int
                or size < 1):
            raise ValueError("size > 0")
        self.size = size
        self.top = 0       # highest seen
        self.seen = set()  # seqs in window

    def accept(self, seq):
        if type(seq) is not int or seq < 1:
            return False
        if seq <= self.top - self.size:
            return False   # too old
        if seq in self.seen:
            return False   # duplicate
        self.seen.add(seq)
        self.top = max(self.top, seq)
        low = self.top - self.size
        self.seen = {s for s in self.seen
                     if s > low}
        return True

w = ReplayWindow(4)
for seq in [1, 2, 5, 3, 5, 1, 9, 6]:
    print(seq, w.accept(seq))
```

Trace it with a window of 4:

| seq | top before | Result | Why |
|---|---|---|---|
| 1, 2, 5 | 0, 1, 2 | accept | new |
| 3 | 5 | accept | in window (2..5), unseen |
| 5 | 5 | reject | duplicate |
| 1 | 5 | reject | 1 ≤ 5 − 4, too old |
| 9 | 5 | accept | new top |
| 6 | 9 | accept | in window (6..9), unseen |

This toy handles already authenticated positive sequence numbers for one SA, without wrapping. Never update replay state before integrity verification: a forged high counter could otherwise evict legitimate packets. Its set pruning takes time proportional to the window size for every accepted packet. Efficient implementations can use bitmaps. The window size is a trade-off: too small and legitimate reordering (common with multi-core senders or ECMP paths) causes drops; too large costs memory per SA.

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

```
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

This laptop uses a **split tunnel**: only the two internal ranges go through the VPN. With suitable OS routes, `AllowedIPs = 0.0.0.0/0, ::/0` supports a **full tunnel** for ordinary IPv4/IPv6 destinations. Endpoint, local and policy-route exceptions still need handling. `PersistentKeepalive = 25` enables periodic authenticated empty packets when needed during idle periods, intended to keep a NAT mapping open when its timeout and policy permit (lesson 2's idle timeouts again).

WireGuard avoids replies to random invalid probes. This is not absolute invisibility: under load, a packet with a valid MAC derived from the responder's public key can elicit a cookie reply before full peer authentication. Other network behaviour can also leak information.

## VXLAN and overlays

Data centres and clouds need far more isolated layer 2 segments than VLANs allow. **VXLAN** (RFC 7348) carries whole Ethernet frames in UDP (port 4789), with a 24-bit **VNI** (VXLAN network identifier). The number of network segments an ID field can name doubles with every bit:

```formula
N_VLAN = 2^12 − 2 = 4094
N_VNI = 2^24 = 16777216
where
N_VLAN: usable VLAN IDs: a 12-bit field holds 2^12 (12 copies of 2 multiplied together) = 4,096 values, and IDs 0 and 4095 are reserved
N_VNI: possible VXLAN network identifiers in a 24-bit field: 24 copies of 2 multiplied together
In words: a 12-bit VLAN ID allows about four thousand network segments, while VXLAN's 24-bit VNI allows about 16.8 million.
```

The VXLAN encapsulation looks like this:

```
[outer Eth][outer IP][UDP 4789][VXLAN]
  14         20        8         8
[inner Eth frame ...]
```

For the inner IP budget, subtract outer IPv4 (20), UDP (8), VXLAN (8), and inner Ethernet (14): 50 bytes, which is the 1,500 − 50 = 1,450 calculation at the start of this lesson. The outer Ethernet header shown above is outside the underlay IP MTU. Under these assumptions, either the underlay MTU is raised (data centres often run 9,000-byte jumbo frames) or the overlay MTU drops to 1,450. The devices that wrap and unwrap are **VTEPs**, usually hypervisors or top-of-rack switches. Fabrics can use **BGP EVPN** to distribute MAC reachability, reducing flood-based learning; broadcast, unknown-unicast and multicast handling may still involve replication or flooding. **Geneve** (RFC 8926, UDP 6081) is a more extensible successor, used for example by AWS Gateway Load Balancer.

> [!warning] VXLAN has no security
> VXLAN has no authentication and no encryption; RFC 7348 says so explicitly. An untrusted sender may inject frames if a VTEP accepts its packets and the selected VNI is configured. The VNI alone is not authentication; underlay filtering and endpoint policy can reject the traffic. Keep the underlay private and filtered, never expose VTEPs to the internet, and run VXLAN over IPsec or WireGuard if it must cross untrusted links.

## VPNs in a security architecture

A remote-access VPN puts a device "on the network", which is exactly the location-based trust lesson 2 warned about. Stolen VPN credentials or vulnerabilities in exposed VPN gateways can give attackers a way in. Internet-facing VPN gateways therefore require restricted administration, monitoring and timely fixes.

> [!note] Content gap
> A vendor-by-vendor list of recently exploited VPN vulnerabilities and an incident-frequency claim are omitted here because the individual advisories and a comparable incident dataset were not verified.

Good practice:

- MFA for remote access, and certificate-based device authentication.
- Prioritise fixes for known exploitation and high-risk exposed vulnerabilities; follow the applicable vendor advisory and incident response process.
- Treat VPN users as a separate, segmented zone, not as the office LAN.
- Prefer per-application access (identity-aware proxies) for most users, and keep network-level VPNs for site-to-site links and administrators.

> [!note] Content omitted after review
> A universal WireGuard/IPsec code-size comparison, protocol popularity ranking and fixed tunnel-MTU defaults are not asserted: implementation versions, options and path configurations were not specified for those claims. The lesson instead gives explicit header-budget models.

## Key takeaways
- Tunnels encapsulate packets for reachability; VPNs add authentication, encryption and integrity.
- Encapsulation reduces the inner no-fragmentation budget. The worked 1,500-byte examples yield 1,476, 1,450 and 1,420 under their specified headers; actual paths differ, and MSS clamping covers only TCP.
- IPsec uses IKEv2 to build SAs and ESP to protect packets, with tunnel mode for site-to-site and NAT-T over UDP 4500.
- Sequence numbers plus a sliding window reject replayed and stale packets while tolerating reordering.
- WireGuard trades negotiation for a fixed modern design; AllowedIPs both routes and filters by peer key.
- VXLAN gives 16 million layer 2 segments over UDP but has no security, so the underlay must be protected.

## Further reading
- [RFC 4301: Security Architecture for the Internet Protocol](https://www.rfc-editor.org/rfc/rfc4301)
- [RFC 4303: IP Encapsulating Security Payload (ESP)](https://www.rfc-editor.org/rfc/rfc4303)
- [WireGuard: Next Generation Kernel Network Tunnel (whitepaper)](https://www.wireguard.com/papers/wireguard.pdf)
- [WireGuard: protocol and cryptography](https://www.wireguard.com/protocol/)
- [RFC 7348: Virtual eXtensible Local Area Network (VXLAN)](https://www.rfc-editor.org/rfc/rfc7348)
- [RFC 4459: MTU and Fragmentation Issues with In-the-Network Tunneling](https://www.rfc-editor.org/rfc/rfc4459)
