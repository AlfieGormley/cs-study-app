from pathlib import Path
import json
p=Path('content/networks/02-ip-routing/ip-routing-basics.md');s=p.read_text()
def r(a,b):
 global s
 assert a in s,a[:80]
 s=s.replace(a,b)
r('how hardware does billions of lookups a second.','how tries and hardware tables accelerate lookup.')
r('It reacts in seconds or minutes.','Reaction time depends on failure detection, protocol timers, implementation and topology.')
r('It happens for every packet, in nanoseconds.','It is performed per packet; latency and throughput depend on implementation and workload.')
r('Connected** routes appear automatically when you give an interface an address.','Connected** routes are commonly installed when an interface is configured and usable; options can suppress automatic prefix-route installation.')
r('A /24 learnt from a flaky protocol still beats a /16 you configured by hand.','An eligible /24 installed in the selected forwarding table takes precedence over an installed /16. Rejected routes or unresolved next hops do not participate, and policy can select a different table.')
r('    return max(hits)[1]','    if not hits:\n        return None\n    return max(hits, key=lambda x: x[0])[1]')
r("This is O(N) per packet. With around a million routes in a full Internet table, that's hopeless at line rate. Real routers use better structures (see below).","This is O(N) per lookup for fixed-width IPv4, allocating a list of matches. The example assumes routes already selected by the control plane and one entry per prefix; it does not implement metrics, ECMP or policy routing. None means no matching route. Large tables motivate structures that avoid scanning every entry.")
a=s.index('Sometimes two sources offer');b=s.index("\n| Source | Distance |",a)
s=s[:a]+'''Route selection and packet lookup are separate stages. For a Cisco-style destination-based setup:

1. A routing protocol selects candidate paths using its own rules and metrics.
2. For the same exact prefix, the routing table compares eligible candidates from different sources using administrative distance. Lower values are preferred; next-hop reachability also matters.
3. Selected usable routes are programmed for forwarding. A packet lookup then uses **longest-prefix match** among installed prefixes, without comparing administrative distances again.

Metrics from different protocols are not directly interchangeable. Policy routing can choose another table or action before this lookup.

Selected Cisco default administrative distances (configurable and not a universal IP standard):
'''+s[b:]
r('Linux has no administrative distance as such. It uses the route\'s **metric** (lower wins), and routing daemons like FRR apply distances before installing routes in the kernel.','The Linux kernel exposes route priorities/metrics and policy-rule tables, rather than the Cisco source-distance table as a universal kernel mechanism. Routing daemons can apply their own source preferences before installing routes. A lower metric is relevant among otherwise comparable routes, not a replacement for prefix matching or policy.')
r('It sits unused while the dynamic route exists and takes over when that route disappears.','It can take over after the preferred route is withdrawn, provided the backup remains eligible and its next hop resolves. Upstream failure need not immediately withdraw a route.')
r('The **RIB** (routing information base) holds everything the control plane knows, including losing candidates from every protocol.','The control plane has routing databases (**RIBs**) and protocol-specific state. Which losing candidates are kept in a shared RIB versus a protocol database depends on the implementation.')
r('The **FIB** (forwarding information base) holds only the winners, in a form optimised for lookup.','The **FIB** (forwarding information base) represents selected forwarding actions, potentially with multiple next hops, recursive resolution and special local/discard entries.')
r('On a large router the FIB lives in each line card\'s hardware, so a busy or crashed control-plane CPU doesn\'t stop forwarding.','Distributed hardware routers can retain programmed forwarding while the control plane is busy or restarting. That does not guarantee continued correct service: failed adjacencies, stale state, shared resources and recovery behaviour still matter.')
r('When a packet arrives, the router:','For an ordinary forwarded IPv4 unicast packet on Ethernet, with no NAT, tunnel, options processing or fragmentation, the logical work includes (the hardware pipeline order can differ):')
r('If it hits 0, drops the packet and sends ICMP Time Exceeded.','If it expires, drops the packet and normally reports ICMP Time Exceeded, subject to suppression/rate rules.')
r('Recomputes the header checksum (TTL changed).','Updates the header checksum, possibly incrementally.')
r('Resolves the next hop\'s MAC address (ARP for IPv4, Neighbor Discovery for IPv6), from cache if possible.','Resolves the Ethernet next-hop MAC through ARP, using a valid cached mapping when available. IPv6 instead uses Neighbor Discovery and has no base-header checksum.')
r('The key point: the **IP addresses stay the same** end to end (ignoring NAT), but the **MAC addresses are rewritten at every hop**. The destination MAC is always the *next hop\'s*, never the final host\'s, unless the final host is on the same link.','In this Ethernet unicast example, IP source/destination remain unchanged while each routed link uses its next-hop MAC addressing. Other link technologies need not use MAC addresses, and tunnels, NAT and special routing mechanisms need separate treatment.')
r('Otherwise it ARPs for its **default gateway** and hands the packet over.','For a route via a gateway, it resolves that route\'s next hop. That may be a more-specific gateway route rather than the default; no matching route is also possible.')
r('at most 32 steps for IPv4, 128 for IPv6','at most 32 bit-consuming edges for IPv4, 128 for IPv6 (including the root gives at most 33 or 129 visited nodes)')
r('High-end hardware uses **TCAM**','Some forwarding hardware uses **TCAM**')
r('The chip compares the destination against **every entry in parallel** and returns the first match. Entries are sorted longest prefix first, so the first match is the longest.','In a simplified priority-TCAM model, entries are compared in parallel and a priority encoder selects a match. Ordering longer prefixes before shorter ones implements LPM in that model. Real designs can combine banks, stages, tries and separate priority logic.')
a=s.index('| | Trie in DRAM | TCAM |');b=s.index('\n## Multiple paths',a)
s=s[:a]+'''| Structure | Principal trade-off |
|---|---|
| Trie | Follows address bits through memory; compression and layout influence accesses and capacity |
| Priority TCAM | Parallel masked matching with explicit priority; resource cost and lookup timing depend on implementation |

Cisco's 2014 field notice FN63866 documents FIB TCAM exhaustion on specified Catalyst 6500/7600 configurations, including software switching of some entries and possible elevated CPU usage or instability. This is a platform-specific capacity example, not evidence that every router behaves the same when full.

> [!note] Content omitted after review
> Universal one-cycle lookup claims, nanosecond forwarding promises and a current global prefix count are omitted because no matching hardware specification or dated measurement is established here.
'''+s[b:]
r('If two routes for the same prefix tie on distance and metric, the router can install both:','If the routing implementation and policy select multiple eligible paths for the same prefix, the router can install a next-hop group:')
r("ECMP doesn't round-robin individual packets, because TCP treats reordering as loss. Instead it **hashes the flow's 5-tuple** (source and destination IP and port, protocol) and picks a path from the hash. Every packet of one flow takes the same path; different flows spread out.","A common ECMP policy hashes flow-identifying fields, often the IP/port/protocol 5-tuple. Keeping a stable flow on a stable path reduces reordering, which can trigger spurious loss recovery in TCP. Hash inputs vary, and per-packet or flowlet policies also exist. Path changes and fragmentation can disrupt flow affinity; neither ECMP nor TCP treats every reordered packet as lost.")
r('Routers mix in a per-device seed to avoid it.','Different hash seeds can reduce correlated choices, without guaranteeing perfect balance.')
r('Each router makes its own decision based on the destination only.','With ordinary destination-based forwarding, each router makes its own decision; policy routing can consider other fields.')
r('Stateful firewalls** that see only one direction of a TCP connection drop it as invalid.','Stateful firewalls** may reject traffic when the necessary connection state is absent. Asymmetric-routing support or shared state can change the outcome.')
r("**Reverse path filtering** (uRPF, and Linux's `rp_filter`) drops packets whose source address wouldn't be routed back out of the interface they arrived on. It's a good anti-spoofing measure at the edge but breaks multi-homed hosts if set to strict.","**Strict reverse path filtering** checks whether the ingress interface is a best reverse path to the source. It can reject legitimate asymmetric traffic. Loose modes instead check source reachability without requiring the same interface; Linux policy and configuration affect the lookup. Choose a mode appropriate to the routing design.")
r('traceroute shows the same pair of addresses repeating.','traceroute may show repeated responders, but filtering, rate limits and varying paths can obscure the pattern.')
r('At each hop TTL is decremented, the checksum recomputed and the frame rebuilt with new MACs, while the IP addresses stay the same.','In ordinary IPv4/Ethernet unicast forwarding, TTL is decremented, its header checksum updated and link addressing rebuilt for the next hop.')
r('Tries give O(address width) lookups and TCAMs give one-cycle lookups, at the cost of limited, expensive capacity.','Binary tries bound bit-consuming lookup steps by address width; TCAM uses masked comparisons and priority, with hardware-dependent cost and timing.')
r('ECMP hashes flows so packets within a flow stay in order; asymmetric paths are normal and break stateful middleboxes.','Flow-hashed ECMP reduces path-induced reordering. Asymmetric routing can be valid, but filtering and stateful processing must support it.')
s+='\n- [Cisco: Administrative distance versus forwarding](https://www.cisco.com/c/en/us/support/docs/ip/border-gateway-protocol-bgp/15986-admin-distance.html)\n- [Linux LC-trie implementation notes](https://docs.kernel.org/networking/fib_trie.html)\n- [RFC 2992: ECMP analysis](https://www.rfc-editor.org/rfc/rfc2992.html)\n- [Cisco FN63866: TCAM exhaustion](https://www.cisco.com/c/en/us/support/docs/field-notices/638/fn63866.html)\n'
p.write_text(s)
