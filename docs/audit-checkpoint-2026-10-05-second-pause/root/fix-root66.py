from pathlib import Path
import json
p=Path('content/networks/02-ip-routing/ip-subnetting.md');s=p.read_text()
def r(a,b):
 global s
 assert a in s,a[:70]
 s=s.replace(a,b)
r('Every address has two parts: a **network prefix** that says which network the host is on, and a **host part** that says which host on that network. Routers only care about the prefix. That is what makes the Internet scale: a router needs one entry per network, not one per machine.','An address together with a prefix length divides into a **network prefix** and remaining **host bits**. The address alone does not tell you the split. An interface can have several addresses, and forwarding tables may contain aggregated prefixes or /32 host routes. Aggregation reduces the need for individual-host entries.')
r('| Class | First octet | Prefix | Hosts per net |','| Historical class | First octet bit range | Prefix | Conventional host capacity |')
r('This was hopelessly wasteful. An organisation needing 2,000 addresses was too big for a Class C and got a Class B with 65,534, stranding 97% of it. By the early 1990s Class B space was running out and routing tables were growing alarmingly.','These bit ranges do not make every included network assignable: 0/8 and 127/8 have special meanings. For a single classful network needing 2,000 conventional host addresses, a Class C was insufficient while a Class B left about 97% of its capacity unused. Multiple Class C allocations were another possibility, at the cost of routing entries. CIDR addressed allocation granularity and aggregation.')
r('Two hosts are on the same subnet if they get the same answer. That single comparison decides whether a packet is delivered directly or sent to the router (see the routing fundamentals lesson).','With the same configured mask, equal results identify the same numerical subnet. Actual next-hop selection uses routes and policy; a subnet comparison alone does not prove layer 2 connectivity or exclude a more-specific route.')
r('For any address and prefix:','For conventional IPv4 subnets through /30:')
r('the one where the mask is neither 255 nor 0.','the first mask octet below 255. It can be 0 for a byte-aligned prefix such as /24.')
r("The network address (all host bits 0) and broadcast (all host bits 1) can't be given to hosts, hence the −2.","This conventional capacity excludes all-zero and all-one host fields. /31 point-to-point and /32 uses differ, as explained below. Special address ranges and platform reservations can further reduce assignable addresses; the arithmetic is not an allocation policy.")
r('They are on **different** subnets, so A must send to B via a router, even though the addresses look close.','They are on **different** numerical subnets. With only connected subnet routes and a suitable gateway route, A sends to B via that gateway, even though the addresses look close.')
r('Allocate the largest first, so every block stays aligned:','Starting at the aligned beginning of this unused /24, allocate largest first at the lowest available address:')
r('    net = ip.ip_interface(cidr).network','    net = ip.IPv4Interface(cidr).network\n    count = net.num_addresses\n    usable = count if net.prefixlen >= 31 else (\n        count - 2)')
r('            net.num_addresses - 2)','            usable)')
r('Some blocks are reserved:','Some special-purpose blocks are listed below. This is not a complete registry:')
r('| 100.64.0.0/10 | Carrier-grade NAT |','| 100.64.0.0/10 | Shared address space, intended for CGN deployments |')
a=s.index('**Private** addresses');b=s.index('\n## Supernetting',a)
s=s[:a]+'''**Private** RFC 1918 addresses can be routed within cooperating private networks. They are not globally reachable address space and should not be advertised into the public Internet. NAT is one way to reach public services; application proxies and gateways are alternatives. `172.32.0.1` lies outside RFC 1918, but being outside a private block alone does not prove an address is assigned or reachable.

**100.64.0.0/10** (RFC 6598) is distinct shared address space intended to reduce conflict with customers' RFC 1918 networks in CGN deployments. It cannot guarantee absence of overlap when other networks also use shared space.

**169.254.0.0/16** is IPv4 link-local space. Automatic assignment can occur when routable configuration is unavailable, but the presence of a link-local address alone does not prove a DHCP failure. RFC 3927 reserves the first and last /24 within this block from automatic selection, and routers must not forward link-local traffic to other links.

> [!warning] Overlapping private ranges
> Connecting networks with overlapping addresses can make destination-only routing ambiguous. Coordinate an address plan with connected organisations and cloud networks. Renumbering, translation or separate routing contexts can address different cases; choosing a supposedly unusual RFC 1918 block does not guarantee uniqueness.
'''+s[b:]
r('Why it matters: the global IPv4 routing table holds roughly a million prefixes, and every full-table router must store them in fast, expensive memory. Aggregation keeps that growth in check. It also hides instability: if one customer\'s /24 flaps, the /22 stays put.','Aggregation reduces entries advertised to other networks, saving routing/forwarding state. How a router stores control-plane and forwarding tables is implementation-dependent. A maintained aggregate can hide a component route\'s changes from upstream peers, depending on advertisement policy.')
r('Routers resolve that with **longest-prefix match**, covered in the routing fundamentals lesson.','A more-specific route wins by **longest-prefix match**, but only if it exists. An aggregate can still attract traffic for unavailable destinations. The advertising router needs appropriate component routes and discard handling for unmatched portions to avoid forwarding loops.')
a=s.index('IANA handed out');b=s.index('\n## Key takeaways',a)
s=s[:a]+'''IPv4 has 2³² possible address values, and special-purpose ranges reduce the pool available for globally unique assignments. Address sharing, transfers and allocation policies address scarcity in different ways; IPv6 provides a much larger address space.

> [!note] Content omitted after review
> Current global route counts, address-market prices and a regional exhaustion/allocation timeline are absent because they require dated measurements and registry-policy evidence not established in this lesson. No universal purchase price or route-memory design is assumed.
'''+s[b:]
r('Allocate VLSM subnets largest first to keep blocks aligned.','For an initially empty aligned block, allocating descending block sizes from its start is a straightforward way to preserve alignment.')
r('RFC 1918 ranges are private and need NAT; 100.64/10 is for carrier-grade NAT; 169.254/16 means DHCP failed.','RFC 1918 space is private; 100.64/10 is distinct shared space for CGN; 169.254/16 is link-local and does not itself diagnose DHCP failure.')
s+='\n- [RFC 3927: IPv4 link-local addressing](https://www.rfc-editor.org/rfc/rfc3927.html)\n- [RFC 6598: Shared address space](https://www.rfc-editor.org/rfc/rfc6598.html)\n'
p.write_text(s)
p=Path('content/networks/02-ip-routing/ip-subnetting.questions.json');q=json.loads(p.read_text())
q[1]['prompt']='What is the conventional usable-address capacity of an IPv4 /28 subnet, excluding network and directed-broadcast addresses and any additional platform reservations?'
q[2]['prompt']='Which address is outside all three RFC 1918 private ranges?'
q[2]['options'][3]['explanation']='Correct. 172.16/12 ends at 172.31.255.255. This identifies range membership, not whether 172.32.0.1 is assigned or currently reachable.'
q[2]['workedExample']='The RFC 1918 blocks are 10/8, 172.16/12 and 192.168/16. The 172.16/12 block spans second octets 16–31, so 172.20.10.5 is inside while 172.32.0.1 is outside. The other options fall in 10/8 and 192.168/16. Address reachability is a separate routing/policy question.'
q[4]['prompt']+=' Use conventional IPv4 subnet capacity without extra provider reservations.'
q[5]['prompt']=q[5]['prompt'].replace('An ISP has four customer networks:','An organisation has four private networks to summarise internally:')
q[5]['options'][1]['explanation']=q[5]['options'][1]['explanation'].replace("the ISP doesn't have","the listed networks do not include")
q[7]['prompt']+=' Assume only its connected /25 and a working default route are configured, with no overriding policy or host route.'
q[8]['prompt']='An initially empty 10.0.0.0/24 must serve subnets needing 60, 60, 25 and 10 conventional IPv4 host addresses. Allocate largest first, choosing the smallest address block that fits and the lowest available aligned start each time. Which subnet does the 10-host network get?'
q[8]['workedExample']=q[8]['workedExample'].replace('Largest first guarantees every subsequent block starts aligned.','Starting from this empty aligned /24 and placing these descending sizes contiguously preserves alignment. Largest-first alone would not specify placement in an already fragmented allocation.')
q[10]['options'][1]['explanation']='Incorrect. RFC 3021 treats both addresses as endpoint addresses on the point-to-point link; neither is reserved as a directed broadcast.'
q[11]['prompt']='Two sites each contain a different server at 10.0.5.20 inside 10.0.0.0/16. A VPN joins them into one destination-only routing context. What addressing conflict must be resolved to make both servers unambiguously accessible?'
q[11]['options'][0]['explanation']='MTU issues can be path-specific, but changing MSS cannot distinguish two servers with the same destination address in this routing context.'
q[11]['options'][1]['explanation']='Correct. The same destination address names two intended endpoints. Coordinated renumbering removes this ambiguity; translation or separate routing contexts can be alternatives.'
q[11]['workedExample']='Both servers use 10.0.5.20. A destination address alone cannot express which site is intended within the stated shared context. Prefix metrics or equal-cost paths do not create distinct endpoint names. Renumber one side into coordinated, non-overlapping space; alternatively use deliberate translation or separate routing contexts. Merely picking a less familiar private prefix does not guarantee no future overlap.'
p.write_text(json.dumps(q,indent=2,ensure_ascii=False)+'\n')
