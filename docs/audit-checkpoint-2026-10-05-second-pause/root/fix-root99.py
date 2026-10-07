from pathlib import Path
p=Path('content/networks/06-wireless-modern/wm-debugging.md');s=p.read_text()
def r(a,b):
 global s
 assert a in s,a[:70]
 s=s.replace(a,b)
r('"The network is down" is rarely true, and "the network is slow" is rarely specific enough to act on.','“The network is down” or “the network is slow” needs a precise symptom before it can guide diagnosis.')
r('Most incidents follow a change.','Correlate changes with evidence; a recent change is a hypothesis, not proof of cause.')
r('If it works from inside the data centre but not from the office, the problem is in between.','A difference narrows hypotheses, but source-specific policy, different DNS answers or server treatment can also explain it.')
r('**Connection refused** means a TCP RST came back: the host is reachable but nothing listens on that port (or a firewall actively rejects). A **timeout** means packets vanish: a firewall dropping silently, a routing problem, or the host is down. These two errors point to completely different places.','An immediate **connection refusal** commonly reflects a TCP reset or an explicit rejection reported by the stack. It does not prove the intended host generated the response. A **timeout** means the operation did not finish within its deadline; loss, filtering, routing, overload, peer behaviour and an unsuitable deadline are possible causes. Capture and endpoint evidence distinguish them.')
r('High **mdev** (jitter) under load suggests queueing, such as bufferbloat.','High **mdev**, the standard deviation of sampled RTTs, indicates variability. Queueing is one possible cause, alongside scheduling, path changes and measurement effects.')
r('five packets cannot measure 1% loss.','five probes cannot reliably estimate a 1% loss probability. Even 100 probes have substantial sampling uncertainty, and ICMP behaviour may differ from the application.')
r('Each router that decrements the TTL to zero discards the probe and returns an **ICMP Time Exceeded**, revealing itself.','A router discards a unicast probe whose TTL expires and normally generates **ICMP Time Exceeded**, subject to rate limits and exceptions. Missing or filtered replies can hide hops, and probe paths can differ.')
r('that router does not send Time Exceeded (or rate-limits it). Later hops respond, so traffic passes through it fine.','no reply was received for those probes. Filtering, loss, rate limits or different paths can explain it. Later replies show that some probes reached farther, not that every packet passed one identified router.')
r('is the transatlantic cable: about 5,600 km of fibre each way. Physics, not a fault.','could be consistent with a longer path, but hostnames and hop RTT differences alone cannot identify a cable, its distance or the exact forward-link delay.')
r('is the router being slow to *generate ICMP*, which it does in software at low priority. Only latency that persists to the destination matters.','can reflect reply processing, rate limits, differing return paths or different samples. It does not establish equivalent transit delay for application traffic.')
r('The same rule applies to loss: loss at an intermediate hop that does **not** continue to the final hop is ICMP rate-limiting, not packet loss. Real loss shows up at a hop *and every hop after it*.','Low intermediate response rates with healthy destination samples often suggest reply handling rather than persistent forwarding loss. They do not prove that explanation: probes are separate samples and can take different paths. End-to-end measurements and captures are needed; genuine forwarding loss need not appear identically at every later line.')
r('Compare answers from your configured resolver and a public one to spot stale caches or split-horizon DNS.','Compare resolvers with awareness of split-horizon policy, CDN/geographic responses, cache age and DNSSEC. Different answers are not automatically stale or incorrect.')
r('clients may hold the old address until it expires.','caches may retain an earlier answer for its remaining TTL, while application caching and resolver serve-stale policies can alter observed timing.')
r('curl can report cumulative timestamps for each phase of a request:','curl can report cumulative timing milestones. The subtraction example assumes one new, direct TCP/TLS connection without proxy, redirects, retries or reuse; HTTP/3 and multiplexing need different interpretation. The output below is illustrative:')
r('| Server wait | 0.910 − 0.262 | 648 ms |','| Post-TLS to first byte | 0.910 − 0.262 | 648 ms |')
r('The TCP handshake gives you the RTT: about 84 ms. TLS took about two round trips, which suggests TLS 1.2 (TLS 1.3 needs one). The time to first byte includes one RTT for the request, so the server spent roughly 648 − 84 ≈ 560 ms producing the response. **The network is not the problem here; the backend is.**','Under an ideal handshake model, 84 ms approximates RTT. Actual connect time can include scheduling, retries and address selection. The 174 ms TLS phase does not by itself identify the TLS version. The 648 ms interval can include request transmission, network/queueing, proxy and server work; subtracting one guessed RTT does not isolate backend processing. Confirm with protocol negotiation details, captures and server traces.')
a=s.index('import socket, ssl, time');b=s.index('\n```',a)
s=s[:a]+'''import socket, ssl, time

def phases(host, port=443, timeout=5):
    # First resolved address only; no fallback.
    ctx = ssl.create_default_context()
    ms = lambda a, b: round((b-a) * 1000)
    t0 = time.perf_counter()
    info = socket.getaddrinfo(
        host, port, type=socket.SOCK_STREAM)
    family, kind, proto, _, addr = info[0]
    t1 = time.perf_counter()
    with socket.socket(family, kind,
                       proto) as sock:
        sock.settimeout(timeout)
        sock.connect(addr)
        t2 = time.perf_counter()
        with ctx.wrap_socket(
                sock, server_hostname=host):
            t3 = time.perf_counter()
    return {"dns": ms(t0, t1),
            "tcp": ms(t1, t2),
            "tls": ms(t2, t3)}
''' +s[b:]
r('## ss: what the kernel knows about each connection','The function includes address resolution once, preserves IPv6 socket-address fields, verifies TLS using the default trust configuration and closes owned sockets. Its timeout applies to socket operations, not necessarily DNS or the whole procedure. It does not send HTTP, implement Happy Eyeballs or measure server response time.\n\n## ss: what the kernel knows about each connection')
r('**Send-Q** (here 1.8 MB) growing means the application is writing faster than the network delivers.','For an established TCP socket, a growing **Send-Q** indicates outstanding locally queued/unacknowledged data. Sender, path and receiver constraints can contribute; listener queue fields have different meanings.')
r('A small cwnd with many retransmissions points to packet loss.','A small cwnd and rising retransmission counters motivate recovery analysis, but counts can include spurious retransmissions and are not automatically an application-path loss probability.')
r('## tcpdump: the ground truth','## tcpdump: packet evidence')
r('Capture on both ends if you can, and open the files in Wireshark. Patterns to recognise:','Capture on both ends when authorised and compare timestamps and sequence numbers. Captures can drop packets; offloads can change apparent segmentation/checksums, and encryption hides payload details. Patterns below are hypotheses to investigate:')
a=s.index('- **SYN, then SYN retransmissions**');b=s.index('\n## Failure patterns',a)
s=s[:a]+'''- **Repeated SYNs without a observed reply**: setup is not completing at that capture point. Check endpoint availability, both directions, filtering and overload. Retry schedules are version/configuration-specific; current Linux also documents an initial linear-timeout feature, so 0/1/3/7/15 seconds is not universal.
- **SYN answered by RST**: consistent with an explicit refusal; identify who sent it before attributing it to the destination process.
- **Large packets repeatedly fail while small ones pass**: investigate PMTU and size-dependent policy rather than declaring an MTU black hole solely from symptoms.
- **Duplicate ACKs/retransmissions**: can reflect loss, reordering, duplication or spurious recovery. Correlate both ends.
- **Zero receive window**: the peer is advertising no further receive-window allowance. Slow application consumption is common, but receive-memory limits, protocol behaviour and other resource constraints need checking.
''' +s[b:]
r('Path MTU Discovery sends packets with Don\'t Fragment set; a router whose next link has a smaller MTU drops them and returns **ICMP "fragmentation needed"** (IPv6: "packet too big"). If a firewall blocks that ICMP, the sender never learns and keeps resending large packets that are silently dropped.','Classic IPv4 PMTUD uses DF and ICMP “fragmentation needed”; IPv6 routers do not fragment and use ICMPv6 Packet Too Big. Blocking those messages can prevent learning a smaller path MTU, but packetization-layer probing or black-hole detection may recover without them. A persistent black hole depends on the actual stack and path.')
r('ping -M do -s 1472 host   # 1500 total\nping -M do -s 1372 host   # 1400 total','ping -4 -M do -s 1472 host  # IPv4 1500\nping -4 -M do -s 1372 host  # IPv4 1400')
r('Find the largest size that passes. Fixes: allow ICMP type 3 code 4 (and ICMPv6 type 2), clamp TCP MSS on the tunnel, or lower the interface MTU.','These sizes assume IPv4 without options. Probe success/failure also depends on ICMP policy, reverse-path size and local cached PMTU; it is evidence, not proof of the application’s exact PMTU. Correct filtering of relevant ICMP errors, suitable MTU and, for TCP, carefully configured MSS clamping can help. MSS clamping does not repair UDP or every directional problem.')
r('The Mathis approximation for loss-based congestion control:','The ideal Reno congestion-avoidance Mathis approximation (adequate data/window, light/moderate loss and no RTO-dominated behaviour) is:')
r('rate <= (MSS / RTT) x (1.22 / sqrt(p))','rate ~= (MSS / RTT) x (1.22 / sqrt(p))')
r('So a 1 Gbit/s transatlantic link with just 0.01% loss gives a single loss-based TCP flow only about 14 Mbit/s. Tiny loss rates that `ping` would never show can cripple bulk transfers. That is why `iperf3` with several parallel streams can look fine while one big copy crawls.','The supplied Reno model returns about 14.2 Mbit/s; it is not a general law for CUBIC or BBR, nor a ceiling established by a ping loss estimate. Low loss can be missed in short samples. Parallel streams can also hide per-flow limits, so compare single- and multi-stream tests with endpoint resource measurements.')
r('If the socket buffers (or an application setting) cap the window at 4 MB, the flow tops out at 4 MB / 0.1 s = 320 Mbit/s however fast the link is.','If the measured effective flight window is 4,000,000 bytes at a fixed 100 ms RTT, the simple window/RTT limit is 320 Mbit/s. Socket-memory settings are not identical to that window; other bottlenecks can reduce achieved throughput.')
r('rising CRC/input errors on an interface (`ip -s link`) point to a bad cable or optic.','inspect driver/interface counters (`ip -s link`, and driver-specific tools where needed). CRC errors support a physical-link investigation, but aggregate input errors do not uniquely identify a cable or optic.')
r('the firewall sees only one direction of the handshake and drops the rest.','a stateful device may reject traffic when required state is absent; asymmetric routing need not fail if state is shared or policy supports it.')
a=s.index('> [!example] Putting it together');b=s.index('## Further reading',a)
s=s[:a]+'''> [!example] Putting it together
> Upload stalls after a VPN change, with large DF echo probes failing and smaller ones succeeding, support a PMTU hypothesis. Compare both-end captures, effective tunnel MTU and ICMP errors before concluding. If the evidence confirms an encapsulation/PMTU problem, correct the relevant MTU or error handling; apply TCP MSS clamping only where it addresses the measured path.

## Key takeaways
- Define, scope and reproduce a symptom; distinguish observation from inferred cause.
- Refusal, timeout, traceroute gaps and retransmissions each have multiple possible explanations.
- Separate curl timing milestones without treating their differences as pure server execution time or proof of TLS version.
- PMTU, queueing, recovery and effective-window models guide tests; they do not replace endpoint and path evidence.

> [!note] Evidence limits
> Fixed SYN retry schedules, universal timeout advice and diagnoses inferred from one counter or trace are intentionally omitted. Sample outputs are illustrative. Real-device captures, WAN impairments and production incident causes were not measured in this review.

''' +s[b:]
p.write_text(s)
