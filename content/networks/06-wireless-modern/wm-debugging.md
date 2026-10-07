---
id: wm-debugging
title: Debugging networks, tools and method
level: advanced
minutes: 16
summary: A repeatable method for "the network is slow" or "it can't connect", and how to read ping, traceroute, mtr, dig, curl timings, ss and tcpdump, including MTU black holes and loss-limited throughput.
---

“The network is down” or “the network is slow” needs a precise symptom before it can guide diagnosis. Good network debugging is mostly method: pin down the symptom, find which layer and which segment it lives in, and test a hypothesis with the right tool.

This lesson gives you the method first, then the tools, then the failure patterns that come up again and again.

## The method

1. **Define the symptom precisely.** Which client, which destination (hostname, IP, port), what error, what timing? "Checkout API calls from the London office take 3 s instead of 200 ms since 14:05" is debuggable. "It's slow" is not.
2. **Scope it.** One user or everyone? One region, ISP, Wi-Fi network, or all? IPv4 and IPv6? Always or intermittent? Scope tells you where to look.
3. **Ask what changed.** Deploys, config pushes, certificate renewals, DNS changes, firewall rules. Correlate changes with evidence; a recent change is a hypothesis, not proof of cause.
4. **Walk the layers, bottom up**, until something fails:

| Layer | Question | Tools |
|---|---|---|
| Link | Interface up? Errors? Signal? | `ip link`, RSSI |
| IP | Address, route, gateway? | `ip addr`, `ip route` |
| Name | Does it resolve correctly? | `dig` |
| Transport | Does the port connect? | `nc`, `curl` |
| TLS | Does the handshake work? | `openssl s_client` |
| App | Right response, how fast? | `curl -w`, logs |

5. **Divide the path.** Test from the client, from a host near the server, and from somewhere in between. A difference narrows hypotheses, but source-specific policy, different DNS answers or server treatment can also explain it.
6. **Change one thing at a time** and re-measure against a baseline.

> [!tip] Refused or timed out?
> An immediate **connection refusal** commonly reflects a TCP reset or an explicit rejection reported by the stack. It does not prove the intended host generated the response. A **timeout** means the operation did not finish within its deadline; loss, filtering, routing, overload, peer behaviour and an unsuitable deadline are possible causes. Capture and endpoint evidence distinguish them.

## ping: reachability and RTT

`ping` sends ICMP echo requests and reports round-trip time and loss.

```
$ ping -c 5 10.0.3.7
64 bytes from 10.0.3.7: time=0.41 ms
...
5 packets transmitted, 5 received
rtt min/avg/max/mdev =
  0.38/0.42/0.47/0.03 ms
```

Read it carefully:

- Many networks block or deprioritise ICMP. No reply does not prove the host is down; try a TCP connect too.
- High **mdev**, the standard deviation of sampled RTTs, indicates variability. Queueing is one possible cause, alongside scheduling, path changes and measurement effects.
- Run it for a while (`-c 100`) when hunting intermittent loss; five probes cannot reliably estimate a 1% loss probability. Even 100 probes have substantial sampling uncertainty, and ICMP behaviour may differ from the application.

## traceroute and mtr: where the path goes

`traceroute` sends probes with TTL 1, 2, 3, and so on. A router discards a unicast probe whose TTL expires and normally generates **ICMP Time Exceeded**, subject to rate limits and exceptions. Missing or filtered replies can hide hops, and probe paths can differ. Linux `traceroute` uses UDP probes to high ports by default (`-I` for ICMP, `-T` for TCP); Windows `tracert` uses ICMP.

```
 1  10.0.0.1          1.2 ms
 2  100.64.12.1       8.9 ms
 3  * * *
 4  ldn-core-2       10.4 ms
 5  nyc-core-1       78.1 ms
 6  nyc-edge-3       77.9 ms
 7  203.0.113.80     78.6 ms
```

How to read it:

- **`* * *`** at hop 3: no reply was received for those probes. Filtering, loss, rate limits or different paths can explain it. Later replies show that some probes reached farther, not that every packet passed one identified router.
- **The jump at hop 5** (10 ms → 78 ms) could be consistent with a longer path, but hostnames and hop RTT differences alone cannot identify a cable, its distance or the exact forward-link delay.
- **Latency that rises at one hop and falls again** at later hops can reflect reply processing, rate limits, differing return paths or different samples. It does not establish equivalent transit delay for application traffic.
- Paths are often **asymmetric**: replies may come back a different way, which traceroute cannot show. Run it in both directions when you can.

**mtr** runs traceroute continuously and shows loss and latency per hop. Low intermediate response rates with healthy destination samples often suggest reply handling rather than persistent forwarding loss. They do not prove that explanation: probes are separate samples and can take different paths. End-to-end measurements and captures are needed; genuine forwarding loss need not appear identically at every later line.

## dig: is it DNS?

```
$ dig +short api.example.com
203.0.113.80
$ dig @1.1.1.1 api.example.com
$ dig +trace api.example.com
```

- Compare resolvers with awareness of split-horizon policy, CDN/geographic responses, cache age and DNSSEC. Different answers are not automatically stale or incorrect.
- Check the **TTL** in the answer section: after a migration, caches may retain an earlier answer for its remaining TTL, while application caching and resolver serve-stale policies can alter observed timing.
- `+trace` walks from the root, showing which authoritative servers answer and where delegation breaks.
- Do not forget the client's own resolution path: `/etc/hosts`, search domains, and whether the app prefers IPv6 (an AAAA record pointing somewhere broken causes delays before falling back).

## curl timings: where the time goes

curl can report cumulative timing milestones. The subtraction example assumes one new, direct TCP/TLS connection without proxy, redirects, retries or reuse; HTTP/3 and multiplexing need different interpretation. The output below is illustrative:

```
$ cat fmt.txt
dns     %{time_namelookup}\n
connect %{time_connect}\n
tls     %{time_appconnect}\n
ttfb    %{time_starttransfer}\n
total   %{time_total}\n
$ curl -so /dev/null -w @fmt.txt \
    https://api.example.com/orders
dns     0.004
connect 0.088
tls     0.262
ttfb    0.910
total   0.955
```

Each value is measured from the start, so subtract to get each phase:

| Phase | Calculation | Time |
|---|---|---|
| DNS | 0.004 | 4 ms |
| TCP handshake | 0.088 − 0.004 | 84 ms (≈ 1 RTT) |
| TLS | 0.262 − 0.088 | 174 ms (≈ 2 RTT) |
| Post-TLS to first byte | 0.910 − 0.262 | 648 ms |
| Download | 0.955 − 0.910 | 45 ms |

Under an ideal handshake model, 84 ms approximates RTT. Actual connect time can include scheduling, retries and address selection. The 174 ms TLS phase does not by itself identify the TLS version. The 648 ms interval can include request transmission, network/queueing, proxy and server work; subtracting one guessed RTT does not isolate backend processing. Confirm with protocol negotiation details, captures and server traces.

The same breakdown from inside an application:

```python
import socket, ssl, time

def phases(host, port=443, timeout=5):
    # First address only; no fallback.
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

```

The function includes address resolution once, preserves IPv6 socket-address fields, verifies TLS using the default trust configuration and closes owned sockets. Its timeout applies to socket operations, not necessarily DNS or the whole procedure. It does not send HTTP, implement Happy Eyeballs or measure server response time.

## ss: what the kernel knows about each connection

`ss` (the modern `netstat`) shows sockets, and with `-i` the kernel's TCP state for each one:

```
$ ss -tni dst 203.0.113.80
ESTAB 0 1843200 10.0.0.5:51234
                203.0.113.80:443
  cubic rtt:84.2/3.1 cwnd:10
  retrans:0/57 send 1.4Mbps
```

- For an established TCP socket, a growing **Send-Q** indicates outstanding locally queued/unacknowledged data. Sender, path and receiver constraints can contribute; listener queue fields have different meanings.
- **rtt** is the kernel's smoothed estimate; **cwnd** the congestion window in segments.
- **retrans 0/57**: 57 retransmissions in total. A small cwnd and rising retransmission counters motivate recovery analysis, but counts can include spurious retransmissions and are not automatically an application-path loss probability.
- `ss -ltnp` lists listening sockets with their processes: the first check when you get "connection refused".

## tcpdump: packet evidence

When tools disagree, look at the packets.

```
tcpdump -ni eth0 -w cap.pcap \
  'host 203.0.113.80 and tcp port 443'
```

Capture on both ends when authorised and compare timestamps and sequence numbers. Captures can drop packets; offloads can change apparent segmentation/checksums, and encryption hides payload details. Patterns below are hypotheses to investigate:

- **Repeated SYNs without an observed reply**: setup is not completing at that capture point. Check endpoint availability, both directions, filtering and overload. Retry schedules are version/configuration-specific; current Linux also documents an initial linear-timeout feature, so 0/1/3/7/15 seconds is not universal.
- **SYN answered by RST**: consistent with an explicit refusal; identify who sent it before attributing it to the destination process.
- **Large packets repeatedly fail while small ones pass**: investigate PMTU and size-dependent policy rather than declaring an MTU black hole solely from symptoms.
- **Duplicate ACKs/retransmissions**: can reflect loss, reordering, duplication or spurious recovery. Correlate both ends.
- **Zero receive window**: the peer is advertising no further receive-window allowance. Slow application consumption is common, but receive-memory limits, protocol behaviour and other resource constraints need checking.

## Failure patterns worth knowing

### MTU black holes

Classic IPv4 PMTUD uses DF and ICMP “fragmentation needed”; IPv6 routers do not fragment and use ICMPv6 Packet Too Big. Blocking those messages can prevent learning a smaller path MTU, but packetization-layer probing or black-hole detection may recover without them. A persistent black hole depends on the actual stack and path.

Symptoms: TCP connects; small requests work; anything large hangs. SSH logs in but freezes on a long directory listing. TLS hangs during the handshake when the certificate chain is big. Common around VPNs, tunnels and overlays.

Test with "don't fragment" pings of decreasing size (Linux):

```
ping -4 -M do -s 1472 host  # IPv4 1500
ping -4 -M do -s 1372 host  # IPv4 1400
```

1,472 bytes of payload + 8 ICMP + 20 IP = 1,500. These sizes assume IPv4 without options. Probe success/failure also depends on ICMP policy, reverse-path size and local cached PMTU; it is evidence, not proof of the application’s exact PMTU. Correct filtering of relevant ICMP errors, suitable MTU and, for TCP, carefully configured MSS clamping can help. MSS clamping does not repair UDP or every directional problem.

### Loss-limited throughput

TCP throughput falls sharply with loss, especially over long RTTs. The simplified Reno congestion-avoidance Mathis model below assumes periodic loss, one ACK per segment, adequate data/window, light/moderate loss and no RTO-dominated behaviour:

```
rate ~= (MSS / RTT) x (1.22 / sqrt(p))

MSS 1460 B, RTT 100 ms, p = 0.0001
1460 x 8 / 0.1   = 116,800 bit/s
x 1.22 / 0.01    = ~14.2 Mbit/s
```

The supplied Reno model returns about 14.2 Mbit/s; it is not a general law for CUBIC or BBR, nor a ceiling established by a ping loss estimate. Low loss can be missed in short samples. Parallel streams can also hide per-flow limits, so compare single- and multi-stream tests with endpoint resource measurements.

### Window-limited throughput

Without loss, a single flow is capped at **window / RTT**. To fill 1 Gbit/s at 100 ms RTT, TCP needs a window equal to the bandwidth-delay product:

```
1e9 bit/s x 0.1 s / 8 = 12.5 MB
```

If the measured effective flight window is 4,000,000 bytes at a fixed 100 ms RTT, the simple window/RTT limit is 320 Mbit/s. Socket-memory settings are not identical to that window; other bottlenecks can reduce achieved throughput.

### Other usual suspects

- **DNS**: stale records after a migration; resolver timeouts adding seconds; broken AAAA records.
- **Duplex or link errors**: inspect driver/interface counters (`ip -s link`, and driver-specific tools where needed). CRC errors support a physical-link investigation, but aggregate input errors do not uniquely identify a cable or optic.
- **Asymmetric routing through a stateful firewall**: a stateful device may reject traffic when required state is absent; asymmetric routing need not fail if state is shared or policy supports it.
- **Conntrack or NAT table exhaustion**: new connections fail under load while established ones work; Linux conntrack may log a rate-limited "table full" message; remote NAT services expose different telemetry.
- **Ephemeral port exhaustion**: a client opening many short connections to one destination runs out of source ports, with many sockets in TIME_WAIT. Reuse connections.

> [!example] Putting it together
> Upload stalls after a VPN change, with large DF echo probes failing and smaller ones succeeding, support a PMTU hypothesis. Compare both-end captures, effective tunnel MTU and ICMP errors before concluding. If the evidence confirms an encapsulation/PMTU problem, correct the relevant MTU or error handling; apply TCP MSS clamping only where it addresses the measured path.

## Key takeaways
- Define, scope and reproduce a symptom; distinguish observation from inferred cause.
- Refusal, timeout, traceroute gaps and retransmissions each have multiple possible explanations.
- Separate curl timing milestones without treating their differences as pure server execution time or proof of TLS version.
- PMTU, queueing, recovery and effective-window models guide tests; they do not replace endpoint and path evidence.

> [!note] Evidence limits
> Fixed SYN retry schedules, universal timeout advice and diagnoses inferred from one counter or trace are intentionally omitted. Sample outputs are illustrative. Real-device captures, WAN impairments and production incident causes were not measured in this review.

## Further reading
- [Traceroute — Wikipedia](https://en.wikipedia.org/wiki/Traceroute)
- [mtr on GitHub](https://github.com/traviscross/mtr)
- [Write out (curl -w) — Everything curl](https://everything.curl.dev/usingcurl/verbose/writeout.html)
- [ss(8) — Linux manual page](https://man7.org/linux/man-pages/man8/ss.8.html)
- [tcpdump(1) manual page](https://www.tcpdump.org/manpages/tcpdump.1.html)
- [Path MTU Discovery — Wikipedia](https://en.wikipedia.org/wiki/Path_MTU_Discovery)
- [RFC 2923: TCP Problems with Path MTU Discovery](https://www.rfc-editor.org/rfc/rfc2923)
- [The USE Method — Brendan Gregg](https://www.brendangregg.com/usemethod.html)
- [Mathis et al.: The Macroscopic Behavior of the TCP Congestion Avoidance Algorithm](https://www.cs.utexas.edu/~lam/395t/papers/Mathis1998.pdf)
