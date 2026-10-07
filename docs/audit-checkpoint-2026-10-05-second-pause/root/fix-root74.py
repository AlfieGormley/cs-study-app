from pathlib import Path
p=Path('content/networks/02-ip-routing/ip-dhcp.md');s=p.read_text()
def r(a,b):
 global s
 assert a in s,a[:90]
 s=s.replace(a,b)
r('Open a laptop in a café and within a couple of seconds it has an IP address, a subnet mask, a default gateway and DNS servers. Nobody typed them in. The **Dynamic Host Configuration Protocol** (DHCP, RFC 2131) did it,','A laptop joining a café network can obtain an IPv4 address, subnet mask, gateway and DNS settings automatically. A common mechanism is the **Dynamic Host Configuration Protocol** (DHCPv4, RFC 2131),')
r('which every host on the local link receives and no router forwards.','addressed to the local link rather than forwarded as an ordinary IP broadcast across routers. Delivery can still be filtered or lost.')
r('Here\'s my MAC address.','Here is my client identification.')
r('each server that hears it offers an address and settings. Several servers might reply.','an eligible server may offer an address and settings, subject to pool availability and policy. Several servers might reply.')
r('so they return those addresses to their pools.','so any temporary offer reservations can be released. A server need not reserve an offered address.')
r('The client may now use the address.','The client validates the configuration and checks for an address conflict before using it.')
r('If someone answers, it sends **DHCPDECLINE** and starts again.','A conflicting ARP announcement/reply or another host\'s simultaneous probe can reveal a collision. The client sends **DHCPDECLINE** and restarts after a delay (RFC 2131 recommends at least ten seconds).')
r('which also updates stale ARP caches on the link.','which can refresh peers\' ARP caches; it cannot guarantee every peer updates its cache.')
r("A server that can't honour a Request (say the client moved to a different subnet) sends **DHCPNAK**, and the client restarts from Discover.","A server can send **DHCPNAK** when it determines that a requested configuration is invalid, such as an address on the wrong subnet. Other cases require silence rather than a NAK—for example, an unselected server hearing a Request selecting another server. A client receiving a NAK restarts configuration.")
r('Every DHCP message is a fixed-format BOOTP header (DHCP grew out of the older BOOTP) followed by options:','A DHCPv4 message uses the BOOTP-format header, a magic cookie and options. Option overload can also place options in designated BOOTP fields:')
r('Client hardware (MAC) address','Client hardware address (a MAC for Ethernet)')
r('Options are a simple type-length-value encoding, easy to parse:','Most options use type-length-value encoding; Pad and End are single-byte exceptions. This teaching parser accepts one options field **after** the magic cookie, checks lengths, concatenates repeated option payloads (RFC 3396) and requires End. It does not validate option-specific semantics or process overloaded fields:')
r('''        n = b[i + 1]
        opts[code] = b[i + 2:i + 2 + n]
        i += 2 + n
    return opts''','''        if i + 1 >= len(b):
            raise ValueError("missing option length")
        n = b[i + 1]
        if i + 2 + n > len(b):
            raise ValueError("truncated option payload")
        opts[code] = opts.get(code, b"") + b[i + 2:i + 2 + n]
        i += 2 + n
    else:
        raise ValueError("missing End option")
    return opts''')
r('DHCP doesn\'t give addresses away; it **leases** them. That lets a pool of 200 addresses serve a café with thousands of visitors a week.','Dynamic allocation uses **leases**, allowing addresses to be reused after clients release them or leases expire. DHCP also supports other allocation arrangements; reuse depends on concurrent demand and lease retention, not just visitor count.')
r('The client tracks two timers, by default:','For a finite lease, nominal default timers are below. Servers can supply different T1/T2 values; RFC 2131 recommends random timing variation, and a client may seek renewal early:')
r('so *any* server can extend it.','so another server with sufficient state and authority may extend it.')
r('For a 24-hour lease, T1 is at 12 hours and T2 at 21 hours.','Ignoring timing variation and explicit overrides, a 24-hour lease gives T1 = 12 hours and T2 = 21 hours, measured from the lease-start reference—not simply from delayed ACK arrival.')
r('def timers(lease):\n    return lease * 0.5, lease * 0.875','def timers(lease):\n    # Nominal defaults only; 0xffffffff represents infinity in DHCPv4.\n    if type(lease) is not int or not 0 < lease < 0xffffffff:\n        raise ValueError("expected a positive finite lease in seconds")\n    return lease * 0.5, lease * 0.875')
r('**Reservations** pin an address to a MAC for printers and servers, giving them stable addresses with central management.','**Reservations** associate a stable address with configured client identification, which may be a MAC or a client identifier depending on the server. MAC randomisation or identifier changes can affect that association.')
r('DHCP has no authentication in practice. Any device can answer a Discover.','Base DHCPv4 exchanges do not authenticate the server. Authentication extensions exist (RFC 3118), but without an enforced authentication or network-access policy, a device able to inject replies may impersonate a server.')
r('Every client that accepts its offer now sends traffic through it: a perfect man-in-the-middle.','A client accepting those settings may send off-link traffic through that device or use its DNS service. This can enable interception or denial of service; it does not automatically reveal correctly authenticated TLS plaintext or intercept every local flow.')
r('use that table to drop spoofed ARP replies and packets with forged source addresses.','can use these bindings to enforce configured source checks. Static addresses and trusted infrastructure require appropriate bindings or exceptions; these features do not make a compromised trusted server safe.')
r('If nobody answers, most systems give themselves a **link-local** address from **169.254.0.0/16** (RFC 3927, called APIPA on Windows), choosing a random address and checking it with ARP. It works for talking to neighbours on the same link but has no gateway.','Depending on operating-system configuration, a host may self-configure an IPv4 **link-local** address (RFC 3927, called APIPA on Windows). Automatic selection uses 169.254.1.0 through 169.254.254.255, excluding the first and last /24 of 169.254.0.0/16, and probes for conflicts. Such traffic remains on the link; routers must not forward it.')
r('A 169.254.x.x address on an interface almost always means "DHCP failed": a dead server, a broken relay, a wrong VLAN or a blocked port. Look there before anything else.','An automatically configured 169.254.x.x address can suggest missing routable IPv4 configuration, so check DHCP logs, VLANs, relays and server reachability when DHCP was expected. The address alone does not prove DHCP failed: link-local can be intentional and can coexist with other configuration.')
r('IPv6 hosts usually configure themselves with SLAAC from router advertisements','IPv6 hosts can configure addresses with SLAAC from suitable router advertisements')
r('with its own four messages: Solicit, Advertise, Request, Reply. Note that DHCPv6 never supplies the default router; that always comes from router advertisements. ISPs use DHCPv6 **prefix delegation** to hand a home router its /56 or /48.','with a common four-message exchange: Solicit, Advertise, Request, Reply. Rapid Commit permits a two-message exchange, and other exchanges serve other purposes. DHCPv6 does not provide the standard default-router discovery mechanism: hosts normally learn default routers from RAs, but static routes are also possible. **Prefix delegation** can give a requesting router a prefix, such as /56 or /48; actual sizes depend on provider policy.')
r('Now put the whole module together. A laptop connects to a home network and fetches a page from a server at 198.51.100.80.','This hypothetical IPv4 trace assumes Ethernet-like LAN/WAN links, a fresh DHCP lease, uncached DNS using the gateway resolver, a TCP connection, one NAPT gateway and ordinary IP forwarding. The public-looking addresses are documentation ranges, not live endpoints. Other networks may use different discovery, DNS, transport and forwarding mechanisms.')
r('All of that, typically in tens of milliseconds, and each step is a place to look when things break:','No end-to-end timing bound follows from this trace: association, address-conflict checks, DNS and network latency all contribute. These symptoms suggest investigations rather than unique diagnoses:')
r('| Symptom | Likely layer |','| Symptom | Possible investigation |')
r('| 169.254.x.x address | DHCP |','| Unexpected automatic 169.254.x.x address | DHCP and interface configuration |')
r('| Can ping 1.1.1.1, not names | DNS |','| Reachable known IP but name resolution fails | DNS configuration and resolver path |')
r('| Small pages load, large hang | MTU / PMTUD |','| Small transfers work, large transfers hang | MTU / PMTUD, loss and transport behaviour |')
r('| Intermittent, two devices | Duplicate IP |','| Two devices interfere with each other | Check for duplicate IPs and link faults |')
r('Leases renew at T1 (50%) by unicast and rebind at T2 (87.5%) by broadcast.','Nominal default renewal/rebinding thresholds are 50% and 87.5%; overrides, early renewal and timing variation exist.')
r('knowing the chain makes faults easy to localise.','knowing the assumed chain helps organise troubleshooting without treating symptoms as proof.')
s+='\n> [!note] Content omitted after review\n> Universal setup times, operating-system fallback behaviour and provider prefix-size prevalence are omitted because this review did not establish reliable versioned evidence. The packet trace is an illustrative model, not a measured deployment.\n\n- [RFC 3396: long DHCPv4 options](https://www.rfc-editor.org/rfc/rfc3396)\n- [RFC 3927: IPv4 link-local addressing](https://www.rfc-editor.org/rfc/rfc3927)\n- [RFC 3118: DHCP authentication](https://www.rfc-editor.org/rfc/rfc3118)\n'
p.write_text(s)
