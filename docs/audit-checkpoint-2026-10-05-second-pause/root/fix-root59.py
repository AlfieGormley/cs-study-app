from pathlib import Path
import json
p=Path('content/networks/01-foundations/nf-ethernet.md');s=p.read_text()
a=s.index('The link layer\'s job');b=s.index('## The Ethernet frame',a)
s=s[:a]+'''The link layer moves frames across a link or bridged LAN. Ethernet is a widely used family of link technologies with a common MAC framing model. Its PHYs and optional encapsulations vary; this lesson starts with ordinary untagged Ethernet II frames.

'''+s[b:]
s=s.replace('## The Ethernet frame\n', '## The Ethernet frame\n\nThe following is the basic untagged format. Tagged/envelope frames and specific PHY rules need additional accounting.\n')
s=s.replace('a switch can start deciding where to send the frame after reading just 6 bytes.', 'a switch can begin a destination lookup early, though VLAN classification and other policy may require more header information.')
s=s.replace('a leftover from the IEEE 802.3 frame format. In practice almost all traffic uses EtherType.', 'the IEEE 802.3 length/LLC interpretation. Values 1501–1535 are neither a valid length in that range nor an EtherType.')
s=s.replace('the largest standard frame is **1518 bytes**.', 'the largest basic untagged frame here is **1518 bytes**; that is not a universal maximum for every Ethernet encapsulation.')
s=s.replace('The **FCS** is a CRC-32 over the frame.', 'The **FCS** is a CRC-32 over the destination address through payload and pad (including any tags), excluding preamble/SFD and the FCS itself.')
s=s.replace('Ethernet does not retransmit;', 'Ordinary full-duplex Ethernet MAC service does not acknowledge/retransmit a frame after an FCS failure;')
s=s.replace('After every frame a sender must leave an **inter-frame gap** of 96 bit-times (12 bytes).', 'Use a nominal **inter-frame gap** of 96 bit-times (12 byte-times) for the steady-rate calculations here. Some PHYs use alignment/deficit-idle rules; gap timing is not literal extra payload bytes.')
s=s.replace('The first three bytes are usually an **OUI** (organisationally unique identifier) assigned by the IEEE to a manufacturer. The rest is assigned by that manufacturer.', 'For an IEEE MA-L allocation, the first three bytes are an **OUI** assigned to an organisation, which assigns the remaining bits. Other allocation sizes and locally administered addresses do not follow a universal three-byte manufacturer rule.')
s=s.replace('0 for a globally unique, manufacturer-assigned address,', '0 for universally administered addressing (intended to be unique under its allocation rules, not proof of authenticity),')
s=s.replace('Every device on the LAN accepts it.', 'It addresses all stations in the broadcast domain, subject to filtering and policy.')
s=s.replace('Modern phones and laptops use **randomised MAC addresses** per Wi-Fi network for privacy.', 'Many phones and laptops support **private/randomised MAC addresses** for Wi-Fi; persistence, rotation and defaults depend on OS version and configuration.')
s=s.replace('This is why MAC-based tracking and some MAC-based network access controls stopped working.', 'This reduces some cross-network tracking and can conflict with hardware-address allow-lists; it neither prevents all tracking nor makes a MAC a secure identity.')
s=s.replace('IP addresses (hierarchical, location-based)', 'IP prefixes (hierarchically aggregated for routing, rather than a reliable geographical location)')
s=s.replace('wait K × 512 bit-times before trying again.', 'wait K slot times before retrying, still obeying carrier-sense rules. At 10/100 Mbit/s the slot is 512 bit-times; historical half-duplex Gigabit uses 4096 bit-times.')
s=s.replace('That **slot time** bounded the size of a 10 Mbit/s collision domain to roughly 2.5 km including repeaters.', 'The **slot time**, propagation and repeater delays together constrain the collision domain; physical topology rules cannot be inferred from cable speed alone.')
s=s.replace('but almost nobody deployed it.', 'an historical half-duplex mechanism distinct from modern full-duplex operation.')
s=s.replace('Each direction has its own wire pairs (or fibre), so there is nothing to collide with.', 'Each endpoint can send and receive concurrently. Some PHYs separate directions physically; 1000BASE-T uses both directions on the same four pairs with echo cancellation. A shared half-duplex collision domain is absent.')
s=s.replace('If one end is hard-set to full duplex and the other auto-negotiates (and falls back to half duplex),', 'On legacy 10/100BASE-T links, if one end is forced to full duplex and the auto-negotiating peer detects speed but falls back to half duplex,')
s=s.replace('Leave both ends on auto-negotiation, or set both explicitly.', 'Use compatible settings, normally auto-negotiation at both ends. Do not generalise the legacy fallback behaviour to every Gigabit PHY; follow the equipment requirements.')
s=s.replace('a switch sends each frame only where it needs to go.', 'a bridge can restrict known unicast forwarding, while some traffic is still flooded.')
s=s.replace('1. **Learn**: when a frame arrives', 'Assume valid frames, one VLAN, eligible forwarding ports, ordinary learning and no configured exceptions.\n\n1. **Learn**: when a frame arrives')
s=s.replace('**flood** it out of every port except the one it came in on.', '**flood** it to eligible forwarding ports in the same VLAN, excluding ingress. Multicast snooping/filtering can narrow the set.')
s=s.replace('No configuration is needed: switches are **transparent** and self-learning.', 'Basic learning can work automatically, but VLANs, spanning tree, security and management still require suitable configuration.')
s=s.replace('```python\nclass Switch:', 'This toy models ordinary unicast labels plus an unknown broadcast label on one VLAN. It omits FCS validation, MAC-format checks, multicast policy, aging, VLANs, spanning tree, capacity and special ingress-reflection modes.\n\n```python\nclass Switch:')
s=s.replace('        self.ports = ports', '        self.ports = tuple(ports)')
s=s.replace('    def receive(self, port, src, dst):\n', '    def receive(self, port, src, dst):\n        if port not in self.ports:\n            raise ValueError("unknown port")\n')
a=s.index('Hardware switches do this lookup');b=s.index('## VLANs',a)
s=s[:a]+'''Hardware forwarding capacity and latency depend on the switch and enabled features. **Store-and-forward** receives and checks the full frame before forwarding. **Cut-through** can begin earlier and may propagate part or all of a frame later found corrupt; its latency is not universally below one microsecond.

> [!warning] MAC-table exhaustion
> Large numbers of spoofed source addresses can exhaust learning capacity. Depending on the device and configuration, unknown unicast may then be flooded within its VLAN, exposing frames to additional ports or causing disruption. Existing learned entries need not all disappear, and flooding is not guaranteed. Configured per-port learning limits and appropriate violation actions can constrain this attack; encrypted payloads remain protected when the encryption is correctly implemented and endpoints are uncompromised.

'''+s[b:]
s=s.replace('A switch on its own makes one LAN: every port can reach every other, and broadcasts reach all of them.', 'A basic single-VLAN bridge joins eligible ports into one broadcast domain; port isolation and filtering can further restrict connectivity.')
s=s.replace('0 and 4095 are reserved, so **4094 usable VLANs**.', '0 indicates priority tagging without a VLAN identifier and 4095 is reserved, leaving **4094 assignable VLAN IDs**. Equipment may support fewer active VLANs.')
s=s.replace('An **access port** belongs to one VLAN and sends and receives untagged frames: the host never sees a tag.', 'An ordinary **access port** presents one untagged data VLAN to a host; voice VLANs, priority tags and vendor-specific configurations are exceptions.')
s=s.replace('with each frame tagged. Untagged frames on a trunk belong to its **native VLAN**.', 'usually with tags distinguishing VLANs. Depending on configuration, untagged traffic may use a native VLAN or be rejected; a native VLAN can also be tagged.')
s=s.replace('so **4094 usable VLANs**.', 'so **4094 assignable VLAN IDs**.')
s=s.replace('Fewer, larger frames mean fewer per-packet interrupts and lookups,', 'Fewer, larger frames can reduce per-packet work (interrupt moderation and offloads mean interrupts are not necessarily one per frame),')
s=s.replace('**every** device on the path must agree.', 'every traversed link/interface must support the sizes actually sent, or the sender must adapt to a smaller path MTU; configured MTUs need not all be identical.')
s=s.replace('An MTU **mismatch** produces a nasty failure:', 'An MTU **mismatch** can produce a black-hole failure if fragmentation or path-MTU adaptation does not resolve it:')
s=s.replace('age entries after about 5 minutes.', 'age learned entries according to implementation and configuration.')
s=s.replace('Mismatches cause "small works, large hangs" failures.', 'Unresolved path-MTU problems can cause "small works, large hangs" failures.')
s+='\n- [IEEE address-allocation guidelines](https://standards-support.ieee.org/hc/en-us/articles/4888705676564-Guidelines-for-Use-of-Extended-Unique-Identifier-EUI-Organizationally-Unique-Identifier-OUI-and-Company-ID-CID)\n- [Cisco auto-negotiation and duplex guidance](https://www.cisco.com/c/en/us/support/docs/lan-switching/ethernet/10561-3.html)\n- [Cisco unicast flooding behaviour](https://www.cisco.com/c/en/us/support/docs/switches/catalyst-6000-series-switches/23563-143.html)\n- [Apple private Wi-Fi address modes](https://support.apple.com/en-ie/102509)\n'
p.write_text(s);p=p.with_suffix('.questions.json');q=json.loads(p.read_text())
q[1]['options'][1]['explanation']='0xda has the local-administration bit set and the group bit clear. It is locally administered unicast; that does not alone prove it was randomised.'
q[1]['options'][3]['explanation']='Correct: the I/G bit is 1. IPv4 mDNS address 224.0.0.251 maps here, but IPv4 multicast-to-MAC mapping is not one-to-one, so the MAC alone does not prove mDNS.'
q[2]['prompt']+=' Assume a valid unknown-unicast frame, ordinary learning, one VLAN, all listed ports forwarding, and no isolation, filtering or hairpin mode.'
q[2]['options'][1]['explanation']='Basic destination bridging learns from source MACs; it does not use ARP to resolve an output port. A switch acting as an IP endpoint/router can separately use ARP.'
q[2]['options'][3]['explanation']='In the stipulated ordinary bridging mode, the ingress port is excluded. Special hairpin/reflection modes are outside this question.'
q[3]['prompt']+=' Use the lesson’s toy switch and assume no aging or filtering between frames.'
q[4]['prompt']+=' Use nominal 96-bit gap accounting and count one direction.'
q[4]['workedExample']=q[4]['workedExample'].replace('A firewall that does a few hundred nanoseconds of work per packet might reach line rate with large frames (about 813,000 per second) and still fall over on a flood of small ones.', 'Per-packet processing latency alone does not set throughput if work is pipelined or parallel. Capacity should be tested at specified frame sizes, features and traffic patterns.')
q[5]['prompt']='On a legacy 100BASE-TX link, a server is forced to 100 Mbit/s full duplex while the switch detects the speed but uses half duplex. The link is up. Which symptoms are consistent with this duplex mismatch under bidirectional load?'
q[5]['options'][0]['explanation']='Possible. The half-duplex side detects overlapping transmissions, which can include late collisions depending on timing.'
q[5]['options'][1]['explanation']='Possible. Aborted/truncated transmissions from the half-duplex side can cause FCS/alignment or fragment counters; exact counter classification varies.'
q[5]['options'][2]['explanation']='Possible. Light traffic may avoid overlap, while heavier bidirectional traffic exposes the mismatch.'
q[5]['options'][3]['explanation']='The question explicitly states that this mismatched legacy link is up. Other negotiation/configuration failures can prevent links coming up.'
q[5]['workedExample']='The full-duplex side can transmit while receiving. The half-duplex side treats overlapping transmissions as collisions and backs off. Error counters and heavy-load performance can reveal the mismatch even when small pings pass. Align supported settings, normally auto-negotiation on both ends; this legacy 100BASE-TX scenario does not describe every Gigabit PHY.'
q[6]['options'][0]['explanation']='A consistent locally administered address is compatible with deliberate configuration or privacy behaviour. The bit pattern alone cannot prove or rule out all faults.'
q[6]['options'][1]['explanation']='Spoofing is possible, but not established by these observations. Check the phone’s current private-address setting before assuming an attacker.'
q[6]['options'][2]['explanation']='This is a plausible likely cause on a privacy-enabled phone. The local bit identifies administration type, not proof of randomisation.'
q[6]['workedExample']='0xda ends in binary 10: individual/unicast and locally administered. Check the device’s per-network private-address setting and any fixed/rotating mode. Resolve enrolment using the network’s supported device-authentication policy. A MAC can be changed or copied, so an allow-list alone is not strong authentication.'
q[7]['options'][0]['text']='A single tag adds four bytes: a 1518-byte basic frame becomes 1522 bytes'
q[7]['options'][4]['explanation']='Correct as the assignable ID space: 1–4094. VID 0 carries priority without a VLAN ID; 4095 is reserved. Hardware may support fewer simultaneous VLANs.'
q[7]['workedExample']=q[7]['workedExample'].replace('minus the reserved 0 and 4095', 'minus priority-only VID 0 and reserved 4095').replace('Access ports carry one VLAN untagged; trunks carry many, tagged.', 'Ordinary access ports carry untagged data; trunk/native/voice-tag behaviour depends on configuration.')
q[8]['prompt']=q[8]['prompt'].replace('What is the most likely cause?', 'Which hypothesis most directly explains this size-dependent pattern and should be tested?')
q[8]['options'][0]['explanation']='Server work is another possible cause of hangs, but the new tunnel and size-dependent pattern make path MTU a strong hypothesis to test, not a diagnosis by elimination.'
q[8]['options'][3]['explanation']='A duplex problem is possible on some links, but these observations alone do not establish it. Check counters and packet sizes rather than ruling it out categorically.'
q[8]['workedExample']='A tunnel adds overhead. If the resulting packet exceeds an underlay MTU and neither fragmentation nor path-MTU adaptation succeeds, small exchanges may pass while large ones stall. On Linux, an authorised IPv4 test can use `ping -4 -s 1472 -M do <destination>`: 1472 payload + 8 ICMP + 20 IPv4 = 1500 bytes, without IP options. Failure alone is not proof of MTU trouble because ICMP can be filtered. Confirm with size variation, captures and tunnel settings; fix MTU/PMTU handling, or use TCP MSS adjustment where appropriate (it does not fix all UDP traffic).'
q[9]['options'][0]['explanation']='2.5 km is not the result of this propagation-only hypothetical. The calculation gives 51.2 m; historical Ethernet topology limits also include equipment delays.'
q[9]['workedExample']=q[9]['workedExample'].replace('Gigabit\'s designers added carrier extension (padding frames to 512 bytes on the wire) to restore a usable 200 m or so, but full duplex made the problem moot.', 'Historical half-duplex Gigabit used a 4096-bit-time slot with non-data carrier-extension symbols after short frames. These symbols do not turn the MAC payload into a 512-byte frame. Modern full-duplex operation avoids this collision-domain constraint.')
q[10]['prompt']=q[10]['prompt'].replace('the longest the sender might now wait before trying again?', 'the maximum randomly selected backoff interval, excluding additional carrier-sense deferral?')
q[11]['prompt']+=' Consider possible behaviour of an ordinarily flooding switch without existing per-port learning limits, rather than a guarantee for every device.'
q[11]['options'][0]['text']='Table exhaustion can prevent new learning or cause eviction, potentially increasing unknown-unicast flooding'
q[11]['options'][0]['explanation']='True as a possible effect. Existing learned destinations may still be forwarded normally; capacity and overflow policies vary.'
q[11]['options'][1]['text']='If affected unknown-unicast frames are flooded to the attacker’s eligible VLAN port, the attacker can capture those frames'
q[11]['options'][1]['explanation']='True under that condition. The attack does not automatically expose all unicast traffic or bypass VLAN forwarding policy.'
q[11]['options'][2]['text']='Enforced per-port MAC limits with suitable violation actions can constrain source-address flooding from that port'
q[11]['options'][2]['explanation']='True. The protection depends on configuration and implementation; it is not a guarantee against every disruption or attack.'
q[11]['options'][4]['explanation']='Frame capture alone does not decrypt properly secured TLS application data; exposed metadata and endpoint compromise are separate issues.'
q[11]['workedExample']='Spoofed sources can consume learning capacity. If legitimate destinations then lack table entries and the switch floods unknown unicast, eligible ports in that VLAN may receive those frames. Existing entries, capacity rules and suppression settings affect the result. Per-port learning limits can contain the source flood. Capturing frames does not itself decrypt properly secured TLS payloads.'
p.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n')
print('Ethernet and 12 questions corrected')
