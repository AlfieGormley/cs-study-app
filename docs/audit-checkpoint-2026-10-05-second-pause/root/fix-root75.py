import json
from pathlib import Path
p=Path('content/networks/02-ip-routing/ip-dhcp.questions.json');q=json.loads(p.read_text())
q[0]['prompt']='An IPv4 DHCP client on an Ethernet LAN has no assigned address and starts discovery. What are the DHCPDISCOVER IP source, destination and UDP ports before any relay processes it?'
q[0]['options'][0]['explanation']='This initial DHCPDISCOVER uses source 0.0.0.0 and the limited broadcast destination. IPv4 link-local addresses have separate use and do not establish this packet’s source.'
q[0]['options'][1]['explanation']='Correct. Initial discovery uses 0.0.0.0 to 255.255.255.255, UDP client port 68 to server port 67. The limited broadcast targets the local link; delivery is not guaranteed.'
q[0]['workedExample']=q[0]['workedExample'].replace('which every host on the link receives and routers don\'t forward','which is link-scoped and is not forwarded as an ordinary IP broadcast')
q[1]['prompt']='What is the message order for a successful initial DHCPv4 assignment using the normal four-message exchange, without Rapid Commit?'
q[1]['workedExample']=q[1]['workedExample'].replace('confirmed, lease starts now','confirmed, here are the lease parameters')
q[2]['prompt']='A desktop is configured to use DHCPv4 with automatic link-local fallback. Its logs show unanswered DHCP requests followed by self-configuration of 169.254.37.200. What happened?'
q[2]['options'][0]['explanation']='169.254.0.0/16 is IPv4 link-local, not the 100.64.0.0/10 shared address space reserved for uses such as carrier-grade NAT.'
q[2]['options'][1]['explanation']='RFC 3927 says link-local addresses must not be configured by DHCP. The logs identify local fallback, not a normal lease; office networks are not restricted to RFC 1918 addressing.'
q[2]['options'][3]['explanation']='Correct in this explicitly logged case. The host fell back after unanswered DHCP requests. The link-local address itself would not prove the cause without that context.'
q[2]['workedExample']='1. 169.254.37.200 lies in the automatically selectable IPv4 link-local range.\n2. Here the configuration and logs establish that unanswered DHCP requests preceded fallback. Link-local alone does not establish that sequence in every system.\n3. Check server reachability, pool availability, VLAN membership, relay configuration and packet filtering. Link-local traffic cannot be forwarded off-link.'
q[2]['link']={'title':'RFC 3927: IPv4 link-local addressing','url':'https://www.rfc-editor.org/rfc/rfc3927'}
q[3]['prompt']='A finite 8-hour DHCP lease has a lease-start reference of 09:00. Use exactly T1 = 50% and T2 = 87.5%, with no early renewal, timer overrides or random variation. When do renewal and, if unanswered, rebinding start?'
q[4]['options'][1]['text']='So server B can see it was not chosen and release any temporary reservation for its offer'
q[4]['options'][1]['explanation']='Correct. Option 54 identifies A. B can treat its offer as declined; servers need not reserve addresses merely because they offered them.'
q[4]['options'][3]['explanation']='Recording the lease at a gateway is not the reason for this broadcast. A gateway may have additional roles such as server, relay or snooping switch.'
q[4]['workedExample']='1. A and B offer addresses; each may temporarily reserve its offer.\n2. The selecting client broadcasts DHCPREQUEST with option 54 naming A and option 50 naming A’s offered address.\n3. A confirms with ACK if the allocation is still valid.\n4. B sees it was not selected and may release any temporary reservation.\n5. This explains the selection-state broadcast; later renewal requests normally use unicast.'
q[5]['prompt']+=' Assume matching relay/subnet configuration, available addresses and no policy denying this client.'
q[7]['prompt']='Which managed-switch measures help defend an office LAN against rogue DHCP replies or related source-address spoofing? Assume the bindings and trusted-port settings are correct. Select all that apply.'
q[7]['options'][0]['explanation']='Correct. DHCP snooping filters server replies entering untrusted ports. This does not protect against a rogue server reachable through a mistakenly trusted path.'
q[7]['options'][1]['explanation']='Correct for related ARP spoofing: DAI checks ARP against permitted bindings or configured ACLs. Static infrastructure needs suitable entries; DAI alone is not DHCP-server authentication.'
q[7]['options'][3]['explanation']='Correct for related source spoofing. Enforcement depends on configured bindings and platform behaviour, with appropriate allowances for initial DHCP traffic.'
q[7]['workedExample']='1. A rogue server injects offers with misleading gateway or DNS settings; clients need not always choose the first offer.\n2. Snooping filters these replies on untrusted ingress ports.\n3. DAI and source guard use configured bindings to limit related address spoofing, with proper static-host exceptions.\n4. Neither longer leases nor edge NAT authenticates a local DHCP reply.\n5. Compromised trusted paths or incorrect bindings remain limitations.'
q[8]['prompt']+=' Assume this illustrative IPv4 router decrements TTL by exactly one and uses Ethernet on the WAN.'
q[8]['options'][2]['explanation']='In this ordinary forwarding example, the IP destination stays the remote server. The Ethernet destination identifies the ISP next hop.'
q[8]['options'][3]['explanation']='The prompt explicitly assigns translated port 40000, and this router decrements TTL to 63. NAPT can preserve a source port when its mapping policy permits; it does not universally change it.'
q[9]['prompt']+=' Packet capture confirms those affected clients accepted DHCPACKs from an unauthorised device on their access VLAN.'
q[9]['options'][0]['explanation']='The capture identifies an unauthorised DHCP server. Pool exhaustion alone does not cause a server to invent a new subnet; fallback and additional configured pools are implementation/configuration dependent.'
q[9]['options'][2]['text']='An unauthorised DHCP server, possibly a consumer router, supplied the settings those clients accepted'
q[9]['options'][2]['explanation']='Correct. The capture establishes the rogue source. Clients can select offers by different policies, so this does not require a universal “first offer wins” rule.'
q[9]['workedExample']='1. The address mismatch is a clue; the accepted ACK from an unauthorised device supplies stronger evidence.\n2. Inspect DHCP option 54, frame source addresses and switch forwarding records to trace that device.\n3. Offer-selection policy varies; some clients may keep legitimate leases while others choose the rogue offer.\n4. Correctly placed DHCP snooping trust boundaries can block server replies from unauthorised access ports.'
q[10]['prompt']='A client has a 24-hour DHCP lease with lease-start reference 00:00 and exact default T1/T2 fractions. A fails at 11:00. B uses a different IP, shares the lease state and is authorised and reachable to renew it. Assume no early renewal, random timing variation, server-address takeover or other failover mechanism. When does normal rebinding first let B answer?'
q[10]['options'][0]['explanation']='Under the stated timer-driven model, failure at 11:00 does not itself initiate rebinding. Other designs can have failover mechanisms, which are excluded here.'
q[10]['options'][2]['explanation']='Rebinding gives B a chance at T2 before expiry. Here B is assumed reachable and able to extend the lease; in general successful delivery is not guaranteed.'
q[11]['options'][0]['text']='DHCPv6 does not supply the standard IPv6 default-router discovery mechanism; hosts normally learn default routers through RAs'
q[11]['options'][0]['explanation']='Correct. Address leasing and default-router discovery are separate. Static default routes are also possible, so “always from RAs” would be too strong.'
q[11]['options'][3]['text']='DHCPv6 prefix delegation can give a requesting router a /56, from which it can form 256 /64 prefixes'
q[11]['options'][3]['explanation']='Correct. 64 − 56 = 8 subnet bits, giving 2^8 = 256 /64s. Delegation size and usable subnets depend on provider policy and configuration.'
q[11]['workedExample']='1. DHCPv6 is separate from the standard RA-based default-router discovery mechanism: true. Static routes are an alternative.\n2. DHCPv6 uses UDP 546 for clients and 547 for servers/relays: true.\n3. IPv4 broadcast 255.255.255.255 is not used by IPv6 DHCP: false.\n4. A /56 contains 256 /64 prefixes: true; this arithmetic does not assert every provider delegates /56.'
for i in (1,5):q[i]['link']={'title':'RFC 2131: DHCP','url':'https://www.rfc-editor.org/rfc/rfc2131'}
p.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n')
