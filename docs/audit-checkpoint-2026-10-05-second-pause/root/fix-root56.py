from pathlib import Path
import json
p=Path('content/networks/01-foundations/nf-layered-models.md');s=p.read_text()
s=s.replace('No single piece of software could sensibly handle all of that.', 'Dividing these responsibilities makes the system easier to build and reason about.')
s=s.replace('Each layer solves one problem, relies only on the service of the layer below,', 'In the model, each layer groups related responsibilities, relies on services below,')
s=s.replace('The **OSI model** (ISO, 1984) has seven layers. It was designed by committee as the blueprint for a protocol suite (the OSI protocols) that largely lost out.', 'The **OSI reference model** has seven layers.')
s=s.replace('using local addresses (MAC addresses).', 'using link-specific framing and, on Ethernet or Wi-Fi, MAC addresses.')
s=s.replace('using global addresses (IP) and routing.', 'using IP addresses and routing; not all IP addresses are globally routable or uniquely identify one host.')
s=s.replace('deliver data between *processes* (ports), optionally reliably and in order (TCP), and control the sending rate.', 'deliver data between transport endpoints using ports and addresses. Services vary: TCP offers an ordered reliable byte stream and congestion control; UDP itself does not.')
s=s.replace('| TCP, UDP, QUIC |', '| TCP, UDP; QUIC over UDP |')
s=s.replace('`6` is TCP, `17` UDP, `1` ICMP.', '`6` is TCP, `17` UDP, `1` ICMPv4 and `58` ICMPv6. IPv6 Next Header can also identify an extension header.')
s=s.replace('TCP and UDP **port numbers** pick the process: 443 for HTTPS, 53 for DNS.', 'TCP and UDP **port numbers**, together with addresses and other socket context, select transport endpoints. Port 443 conventionally serves HTTPS and 53 serves DNS; port numbers alone do not prove the application protocol or uniquely identify one process.')
s=s.replace('Assume minimal headers (no TCP or IP options).', 'Assume the complete 100 bytes fit in one TCP segment, no TLS, minimal TCP/IPv4 headers and untagged Ethernet. Ignore ACK traffic, retransmission, PHY coding and other overhead beyond the fields counted below.')
s=s.replace('then must stay silent for a 12-byte **inter-frame gap**.', 'then leaves a nominal 12-byte-time **inter-frame gap** between frames. The PHY may transmit idle signalling during this interval, so it is not necessarily electrically silent.')
s=s.replace('Headers are just fixed byte layouts.', 'Many header fields have defined byte layouts; optional and variable-length fields need additional parsing.')
s=s.replace('def parse_eth(frame: bytes):\n', 'def parse_eth(frame: bytes):\n    if len(frame) < 14:\n        raise ValueError("short header")\n')
s=s.replace('That frame is a broadcast (all-ones destination) carrying ARP,', 'This is a synthetic header followed by placeholder bytes, not a valid complete ARP frame. Its all-ones destination denotes broadcast and its EtherType selects ARP,')
s=s.replace('A tool such as Wireshark is doing exactly this, layer by layer.', 'This parser demonstrates an untagged Ethernet II header only. It does not handle VLAN tags, 802.3 length/LLC framing, frame length validation or FCS stripping/verification; packet-capture APIs may omit the FCS.')
s=s.replace('Ethernet went from 10 Mbit/s to 400 Gbit/s without TCP changing. HTTP/2 arrived without any change to routers.', 'A faster Ethernet link does not inherently require a new TCP wire format. An application protocol can evolve without redesigning link framing.')
s=s.replace('Supporting IP is the one thing a new network or application must do.', 'IP is the common internetworking service in this model; applications normally use higher-level APIs, while lower-layer devices need not implement an IP endpoint.')
s=s.replace('A switch only needs layers 1 and 2. A router needs 1 to 3. That keeps them cheap and fast.', 'Basic bridging uses link-layer information, while IP routing uses network-layer information. Real switches and routers can also inspect higher layers for filtering, load distribution or other functions.')
s=s.replace('anything that rewrites IP addresses (NAT) must also fix up the TCP checksum.', 'address translation must preserve checksum correctness by adjusting or recomputing it; particular changes can cancel numerically.')
s=s.replace('The network layer has to know the largest frame the link layer can carry.', 'The network layer needs the link MTU: the maximum network-layer packet that fits, rather than the whole Ethernet frame including its header and FCS.')
s=s.replace('This **ossification** made it nearly impossible to deploy new transport protocols or TCP options, which is a large part of why QUIC runs on top of UDP and encrypts almost everything.', 'Such **ossification** can impede new transports and extensions. QUIC uses UDP to improve deployability and protects packet contents and selected header fields to limit unwanted dependencies; some headers remain visible and some networks block UDP or QUIC.')
s=s.replace('so Wi-Fi retransmits at the link layer to hide loss from TCP.', 'and link-layer retransmissions can recover some radio loss before TCP sees it. Wi-Fi retry mechanisms also benefit other traffic; TCP is not their sole reason for existing.')
s=s.replace('Tunnels (VPNs, VXLAN) put a whole link layer frame inside a transport payload, so the stack repeats.', 'Some tunnels, such as VXLAN, carry an inner Ethernet frame inside UDP (without the original FCS); other VPNs tunnel IP packets or application data instead.')
s=s.replace('Most teaching uses a five-layer hybrid.', 'This course uses a five-layer teaching model.')
s+='\n- [IANA IP protocol number registry](https://www.iana.org/assignments/protocol-numbers/protocol-numbers.xhtml)\n- [RFC 9001: QUIC packet and header protection](https://www.rfc-editor.org/rfc/rfc9001)\n- [RFC 7348: VXLAN framing](https://www.rfc-editor.org/rfc/rfc7348)\n'
p.write_text(s);p=p.with_suffix('.questions.json');q=json.loads(p.read_text())
q[0]['prompt']='For ordinary layer-2 destination forwarding within one VLAN, which address does a basic Ethernet bridge look up?'
q[0]['options'][0]['explanation']='IP destination lookup is a routing function. This question isolates ordinary bridging; real switches may implement routing and filtering too.'
q[0]['options'][1]['explanation']='Correct. It looks up the destination MAC within the VLAN’s forwarding context. Unknown unicast or broadcast traffic can be flooded rather than sent to one known port.'
q[0]['options'][2]['explanation']='TCP ports can be inspected for filtering or load distribution, but are not the address used in the basic bridge lookup asked about here.'
q[0]['options'][3]['explanation']='HTTP Host can guide an application proxy, not this basic MAC-table lookup.'
q[1]['options'][3]['explanation']='In the specified standard IP stack, TCP is inside IP and selected by protocol number 6; EtherType 0x86DD selects IPv6 first.'
q[1]['workedExample']=q[1]['workedExample'].replace('Ethernet only knows how to pick the next layer up, which is the network layer.', 'EtherType selects the encapsulated protocol, which need not always be IP (ARP is another example).')
q[3]['prompt']+=' Assume untagged Ethernet II and no additional encapsulation.'
q[4]['prompt']+=' Assume distinct ordinary Ethernet interfaces/next-hop MACs, no IP options, tunnelling or fragmentation, and successful forwarding.'
q[4]['options'][1]['explanation']='Correct. IPv4 forwarding reduces TTL by at least one; expiry prevents indefinite routing loops.'
q[4]['options'][3]['explanation']='It stays unchanged under the stated ordinary-forwarding assumptions. Address translation and some routing/tunnelling mechanisms require separate treatment.'
q[4]['workedExample']=q[4]['workedExample'].replace('Every router decrements the TTL by one','Every forwarding router decrements TTL by at least one').replace('If the router also did NAT, the source IP, source port and TCP checksum would change as well.', 'NAT can change an address and optionally a port, requiring checksum correctness to be maintained; not every translation changes every field.')
q[5]['options'][0]['explanation']='Correct. Addresses and TCP ports are checksum inputs, so translation must maintain the checksum by adjustment or recomputation. Some numerical changes can cancel, leaving the checksum value unchanged.'
q[5]['options'][2]['explanation']='TCP includes a pseudo-header and its own header as well as data. Ignoring changed checksum inputs can cause validation failure.'
q[5]['workedExample']='TCP covers its IP pseudo-header, TCP header and data. Translation changes some of these inputs. The translator must maintain a valid checksum, usually through incremental adjustment or recomputation. It need not become numerically different for every possible pair of changes.'
q[6]['prompt']='A full-size IPv4 TCP segment contains 12 bytes of options including negotiated timestamps. With a 1500-byte IP MTU and untagged full-duplex 1 Gbit/s Ethernet, what ideal one-direction TCP payload rate follows from the lesson’s framing model? Ignore loss, ACK contention and other limits.'
q[6]['options'][1]['text']='About 965 Mbit/s'
q[6]['options'][1]['explanation']='1448 / 1500 ≈ 96.5% counts the IP/TCP overhead but omits Ethernet header, FCS, preamble and nominal gap.'
q[6]['workedExample']=q[6]['workedExample'].replace('This is exactly the number iperf typically reports on a clean gigabit link, which surprises people who expect 1000.', 'This is an ideal framing calculation, not a promise of an iperf result; actual throughput depends on the path, hosts and negotiated options.')
q[7]['prompt']+=' Assume no tunnelling, fragmentation, retransmission or frame duplication.'
q[7]['workedExample']=q[7]['workedExample'].replace("Switches inside a link don't count: they forward the same frame unchanged.", 'Ordinary bridges within a LAN do not create another routed IP hop; VLAN tags and per-link FCS handling may still change frame representation.')
q[8]['options'][1]['explanation']='IP protocol numbers are not exhausted. The relevant concern is support by deployed networks and endpoints.'
q[8]['options'][2]['text']='UDP improves deployability through existing endpoint APIs and many NATs and firewalls compared with an unfamiliar IP transport protocol'
q[8]['options'][2]['explanation']='Correct. This is not universal reachability: some networks block UDP or QUIC. QUIC protects packet contents and selected header fields; it does not encrypt every header field.'
q[8]['workedExample']='A new IP transport number can require middlebox and endpoint support. UDP provides an already supported transport substrate in many environments, making deployment easier. QUIC adds transport and security functionality above UDP. Its protected contents and selected protected header fields reduce some ossification risks, while fields such as connection IDs remain visible. Neither UDP reachability nor freedom from ossification is guaranteed.'
q[9]['prompt']+=' Assume no VLAN tags or IP options.'
q[9]['workedExample']=q[9]['workedExample'].replace('raise the underlay MTU (often to 9000 with jumbo frames)', 'configure every underlay hop for a sufficient MTU (1550 accommodates an inner 1500-byte IP packet under these assumptions)')
q[10]['prompt']='Which examples show interaction across layers or an intermediate system processing higher-layer information? Select all that apply.'
q[10]['options'][0]['text']='Wi-Fi link retries can recover radio losses before TCP sees them and responds with congestion control'
q[10]['options'][0]['explanation']='Correct. This is a cross-layer performance interaction, but retries also serve other protocols and do not exist solely because of TCP.'
q[10]['options'][1]['explanation']='Correct. An application proxy processes layer-7 information. That does not itself prove ossification or violate the layering model.'
q[10]['options'][2]['explanation']='Correct. MTU is a link service property used by IP. Depending on IP version and policy, an oversized packet can be fragmented, rejected or dropped; such an interface is not inherently a design flaw.'
q[10]['workedExample']='Link retries affect what TCP observes; an HTTP proxy processes application messages in the path; and IP uses the MTU exposed by its link interface. All are interactions to consider when reasoning across layers. HTTP/2 changing independently of Ethernet illustrates separation of responsibilities. Cross-layer interaction is not automatically a violation or a bug.'
p.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n')
print('Layered models and 11 questions corrected')
