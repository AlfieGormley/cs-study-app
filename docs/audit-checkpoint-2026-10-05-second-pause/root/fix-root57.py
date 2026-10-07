from pathlib import Path
import json
p=Path('content/networks/01-foundations/nf-performance.md');s=p.read_text()
s=s.replace('Adding lanes lets more cars through per hour but does not shorten anyone\'s journey.', 'Adding capacity does not shorten the physical route, but it can reduce congestion delays. Likewise, greater link rate can reduce transmission and queueing delay without changing propagation speed.')
s=s.replace('where L is the packet length in bits and R the link rate in bits per second.', 'where L is the number of bits counted at the modelled layer and R is the corresponding rate. The table ignores additional framing and encoding overhead.')
s=s.replace('In fibre and copper, s is roughly', 'For a common teaching approximation to solid-glass fibre and some cables, s is roughly')
a=s.index('> [!example] London to New York');b=s.index('### 3. Queueing delay',a)
s=s[:a]+'''> [!example] A hypothetical 5,600 km fibre route
> Assume 200,000 km/s propagation in both directions. One-way propagation is 5,600 / 200,000 s = 28 ms, so the propagation contribution to RTT is 56 ms. Longer routes and equipment add delay. This is a specified model, not a measured or universal city-pair RTT; such measured figures are omitted without a route and measurement source.

'''+s[b:]
s=s.replace('It is the most variable component, and the variation is what you experience as **jitter**.', 'Variation in packet delay is commonly called **jitter**; queueing is one contributor, not the only possible source.')
s=s.replace('On modern hardware routers this is typically microseconds or less. Software (a firewall VM, a busy host) can be much slower.', 'The value depends on the hardware, software, configured processing and load; no universal per-router timing is established here.')
s=s.replace('Routers and switches are usually **store-and-forward**:', 'The calculations below assume **store-and-forward**:')
s=s.replace('so the transmission delay is paid again on every link.', 'so the transmission delay is paid again on every link. Cut-through forwarding can overlap reception with onward transmission and needs a different model.')
s=s.replace('> Host A sends a 1500-byte packet', '> Ignore framing overhead and assume store-and-forward. Host A sends a 1500-byte packet')
s=s.replace('    trans = bits / rate', '    if (rate <= 0 or speed <= 0\n            or min(bits, km, proc, queue) < 0):\n        raise ValueError("invalid delay input")\n    trans = bits / rate')
s=s.replace('Let a be the average packet arrival rate (packets per second).', 'Let a be the average packet arrival rate (packets per second), and L the mean packet length in bits.')
s=s.replace('If ρ > 1, the queue grows without limit and packets are dropped once the buffer fills.', 'With sustained offered load above service capacity, an ideal infinite queue has no stable finite backlog; a finite buffer instead reaches capacity and drops or otherwise rejects excess traffic.')
s=s.replace('In the simplest queueing model (M/M/1: random arrivals, one server), the average wait in the queue is ρ / (1 − ρ) times the time to send one packet:', 'For an M/M/1 queue with Poisson arrivals, independent exponential service times, one server, infinite waiting space and ρ < 1, mean queueing wait is ρ / (1 − ρ) times the **mean** service time. Fixed-size packets have deterministic rather than exponential transmission times, so this table is an illustrative queue model:')
s=s.replace('Real traffic is burstier than this model, so it is usually worse.', 'Real traffic, packet lengths and scheduling differ; this model is neither a universal prediction nor a bound.')
s=s.replace('How much data is "in flight" on a path at once? Multiply the rate by the round-trip time:', 'For a steady window-limited flow, how much unacknowledged data corresponds to a target payload rate? Multiply that rate by its acknowledgement round-trip time, using consistent units:')
s=s.replace('On a 1 Gbit/s path with a 70 ms RTT:', 'For a hypothetical payload rate of 1 Gbit/s and a 70 ms RTT:')
s=s.replace('The original TCP window field is 16 bits, so at most 65,535 bytes may be unacknowledged.', 'Without negotiated window scaling, TCP’s 16-bit advertised receive window cannot represent more than 65,535 bytes. This bounds steady new-data throughput when that window is the active constraint.')
s=s.replace('lifts this, and every modern OS uses it.', 'allows larger receive windows when both endpoints negotiate it; support and configuration must be checked.')
s=s.replace('On gigabit Ethernet with 1500-byte packets, each frame carries 1460 bytes of TCP data in 1538 byte-times of wire, so the best possible goodput is about 949 Mbit/s (about 941 with TCP timestamps). With 2% of packets retransmitted, goodput drops by roughly another 2% on top.', 'In a one-direction untagged full-duplex 1 Gbit/s Ethernet model with 1500-byte IPv4 packets, minimal headers and nominal preamble/gap accounting, each full frame carries 1460 TCP payload bytes in 1538 byte-times: about 949 Mbit/s. Twelve bytes of TCP options reduce that to about 941 Mbit/s. These exclude application/TLS overhead and assume hosts, ACKs and congestion do not limit the rate. If 2% of equal-sized transmissions represent extra attempts, a saturated-link accounting model loses another 2% of useful rate; actual loss can also trigger congestion control.')
s=s.replace('Small transfers are dominated by latency; large ones by bandwidth.', 'Small transfers are often sensitive to round trips, while sufficiently large transfers can be limited by sustained goodput. Server work, congestion and host performance can dominate either.')
s=s.replace('> Path: 100 Mbit/s, 40 ms RTT.', '> Hypothetical path: 100 Mbit/s payload rate, 40 ms RTT. Ignore DNS, server work, loss, slow start and additional overhead; use TCP plus a full TLS 1.3 handshake with no resumption, early data or retry.')
s=s.replace('But a fresh HTTPS connection needs at least a TCP handshake and a TLS 1.3 handshake before the request (two RTTs),', 'In this model TCP setup and TLS setup consume two RTTs before the request,')
s=s.replace('about 120 ms. Latency is 98% of the time.', 'about 120 ms before adding the 1.6 ms response transmission. Round trips account for about 99% of that simplified total.')
a=s.index('This is why web performance work');b=s.index('## Key takeaways',a)
s=s[:a]+'''Connection reuse and closer servers can cut round-trip costs. TLS/QUIC handshake choices also matter: 0-RTT requires prior connection state and appropriate replay-safe application handling; it is not available for every first connection. Which improvement helps most requires a workload and path measurement. A universal bandwidth threshold beyond which pages stop benefiting is omitted because no such general threshold is established here.

'''+s[b:]
s=s.replace('They are independent, and improving one does not improve the other.', 'They measure different properties; raising link rate can reduce transmission and queueing delay, but not propagation time on an unchanged path.')
s+='\n- [RFC 8290: FQ-CoDel](https://www.rfc-editor.org/rfc/rfc8290)\n- [RFC 8446: TLS 1.3 and early-data replay considerations](https://www.rfc-editor.org/rfc/rfc8446)\n- [MIT queueing lecture: M/M/1 assumptions](https://ocw.mit.edu/courses/6-041-probabilistic-systems-analysis-and-applied-probability-spring-2006/1a538356bf7a1f78408de525dd2d1032_lec21.pdf)\n'
p.write_text(s);p=p.with_suffix('.questions.json');q=json.loads(p.read_text())
q[0]['prompt']+=' Ignore all additional overhead.'
q[1]['prompt']+=' Assume signal speed 2 × 10⁸ m/s in both directions.'
q[1]['workedExample']=q[1]['workedExample'].replace('So the RTT between these sites can never be below about 30 ms.', 'For a round trip following that same fibre route at the assumed speed, propagation alone contributes about 30 ms.')
q[3]['workedExample']=q[3]['workedExample'].replace('In reality it would be a little longer, since headers cost about 5% and TCP takes time to ramp up.', 'Real transfers can take longer because of framing, setup, congestion, server and host limits; overhead is not universally 5%.')
q[4]['prompt']=q[4]['prompt'].replace('over a 10 Gbit/s path', 'at a target payload rate of 10 Gbit/s')
q[4]['workedExample']='BDP = 10¹⁰ bits/s × 0.1 s = 10⁹ bits = 125 MB (decimal). Sustaining that payload rate requires sufficient sender flight allowance and advertised receive window, plus suitable buffering and path capacity. Exact socket memory accounting and OS defaults vary; 125 MB is the payload in-flight target, not a universal socket-setting recipe.'
q[5]['prompt']='A TCP connection does not negotiate window scaling. Its receiver advertises at most 65,535 bytes. Over a 1 Gbit/s path with a 100 ms acknowledgement RTT, what approximate steady payload-rate upper bound follows from this receive-window constraint?'
q[5]['workedExample']='A sliding window allows new data as ACKs advance it; it is not necessarily sent in stop-and-wait batches. In the steady window-limited model, rate ≤ 65,535 × 8 / 0.1 ≈ 5.24 Mbit/s. The 1 Gbit/s × 0.1 s BDP is 12.5 MB, much larger than that window.'
q[6]['prompt']+=' Keep mean service time fixed.'
q[6]['options'][3]['explanation']='At ρ=0.9 the stable M/M/1 mean is finite. At or above 1, this infinite-buffer model has no stationary finite mean; a real finite buffer instead drops traffic.'
q[6]['workedExample']=q[6]['workedExample'].replace("Real traffic is burstier than M/M/1 assumes, so it's typically worse.", 'Actual delay depends on arrival and service distributions, buffers and scheduling; it can differ in either direction.')
q[7]['prompt']+=' Assume sequential requests, full TLS 1.2 handshakes with no resumption/False Start/TCP Fast Open, no server or congestion bottleneck, and negligible DNS/server work.'
q[7]['options'][0]['explanation']='Correct. Reuse avoids repeated connection setup under the stated full-handshake assumptions.'
q[7]['options'][3]['explanation']='Correct in this comparison: a full TLS 1.3 handshake without retry needs one protocol round trip rather than the stated conventional TLS 1.2 two-round-trip setup.'
q[8]['prompt']+=' Ignore per-packet header overhead and assume initially idle links with no other traffic.'
q[9]['workedExample']=q[9]['workedExample'].replace('This is why satellite operators use TCP accelerators (performance-enhancing proxies), and why low-earth-orbit constellations at around 550 km offer far lower latency.', 'Lower orbits reduce the geometric propagation component, although actual RTT also depends on satellite routing and ground paths. No universal operating altitude or measured end-to-end RTT is implied.')
q[10]['prompt']=q[10]['prompt'].replace('with 1500-byte packets and no TCP options.', 'with untagged full-size 1500-byte IPv4 packets, minimal IP/TCP headers and nominal Ethernet framing.')
q[10]['options'][0]['explanation']='That is the ideal clean-link payload rate. Extra transmission attempts consume capacity; count each successfully delivered payload byte only once.'
q[10]['options'][2]['explanation']='A retransmission may deliver previously lost data, but it required an extra transmission attempt. Goodput counts the useful delivered bytes once, not all attempted payload bytes.'
q[10]['workedExample']=q[10]['workedExample'].replace('5% of that payload is duplicates: useful fraction 0.95.', 'Under the stated completed-transfer accounting, 5% of attempts are extra retransmissions: useful fraction 0.95.').replace('goodput would collapse well below this', 'goodput could be substantially lower')
p.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n')
print('Network performance and 11 questions corrected')
