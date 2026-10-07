---
id: nsec-detection
title: Detecting intrusions with IDS, packet captures and flow logs
level: advanced
minutes: 15
summary: How IDS and IPS work and why the base-rate problem drowns analysts in false alarms, how to capture and read traffic with tcpdump and Wireshark, and how NetFlow, IPFIX and cloud flow logs let you investigate at scale when payloads are encrypted.
---

Every previous lesson in this module was about prevention. Prevention can fail: a password is phished, a VPN appliance is unpatched, a firewall rule is too broad. The question then is how quickly you notice. **Dwell time** is the interval from intrusion to detection.

> [!note] Content gap
> No industry-wide dwell-time estimate, rule-count estimate or typical retention period is supplied: a dated, comparable measurement was not verified for this lesson.

Detection on the network rests on three kinds of evidence, which trade detail against cost:

| Source | Detail | Cost to keep |
|---|---|---|
| Packet capture | Captured packet bytes, subject to truncation and loss | Potentially high |
| Protocol logs (Zeek) | Selected connection, transaction or file events | Depends on logging |
| Flow records | Aggregated traffic sharing selected attributes | Depends on export |

On top of the evidence sit detection systems that raise alerts. This lesson starts with those, then works down to the raw data.

## IDS and IPS

An **intrusion detection system** (IDS) watches traffic and raises alerts. An **intrusion prevention system** (IPS) sits inline and can also drop traffic.

```
 IDS (passive):
 net ---+---> switch ---> LAN
        | SPAN/TAP copy
        v
      [IDS] --> alerts

 IPS (inline):
 net ---> [IPS] ---> LAN
            |
       drop or pass
```

- An IDS is fed a copy of traffic from a switch **SPAN** (mirror) port or a network **TAP**, or in the cloud via traffic mirroring. A passive sensor is outside the forwarding path; automatic response integrations can still affect traffic. An oversubscribed mirror can lose packets.
- An IPS can stop an attack in progress, but it adds latency and becomes a point of failure. You must choose **fail-open** (traffic flows if the IPS dies, unprotected) or **fail-closed** (the network goes down with it). A false positive on a blocking rule can disrupt legitimate traffic; alert-only rules do not themselves block it.

Network IDS (NIDS) watch the wire; host IDS (HIDS) and EDR agents watch processes and files on each machine. They complement each other: hosts see what happened inside encrypted sessions, networks see machines that have no agent, such as printers, cameras and anything the attacker brought.

### Signatures and anomalies

**Signature-based** detection matches known patterns. Snort and Suricata are examples of open-source engines. A Suricata rule (backslashes continue a rule across lines):

```
alert http any any -> $HOME_NET any ( \
  msg:"SQLi attempt in URI"; \
  flow:established,to_server; \
  http.uri; content:"union select"; \
  nocase; \
  classtype:web-application-attack; \
  sid:1000001; rev:1;)
```

The header (`alert http any any -> $HOME_NET any`) says what traffic to consider; the options say what to look for. `flow:established,to_server` selects traffic towards the server in a flow the engine considers established. This is connection tracking, not cryptographic peer authentication or a guarantee against forged traffic; midstream handling also depends on configuration. `http.uri` selects the normalized URI buffer. The string match is only a teaching example, not a complete SQL-injection detector.

Signatures match specified patterns, which can occur in both known and previously unseen attacks, or in benign traffic. **Anomaly-based** detection learns a baseline (normal hosts, ports, volumes and times) and alerts on deviations: a workstation suddenly talking SMB to fifty others, a server uploading gigabytes at 3 a.m. It can flag previously unseen behaviour, but deviations can be legitimate. Relative false-positive rates depend on the detector, data and threshold.

### The base-rate problem

Even a small false-positive rate can overwhelm true alerts when malicious events are rare. If prevalence is p, sensitivity is t and the false-positive rate is f, expected alert precision is t × p / (t × p + f × (1 − p)), when the denominator is nonzero.

> [!example] Working it out
> A network sees 10,000,000 connections a day, of which 100 are malicious. A detector catches 99% of attacks and flags only 0.1% of benign connections.
>
> - Expected true alerts: 100 × 0.99 = **99**
> - Expected false alerts: 9,999,900 × 0.001 ≈ **10,000**
> - Precision: 99 / (99 + 10,000) ≈ **1%**
>
> About 99% of alerts are false in this model. That workload can make triage difficult; it does not prove that every analyst will miss the true alerts.

This is why mature teams tune aggressively, suppress noisy rules, correlate network alerts with host and identity signals in a SIEM, and measure precision in their own environment. Malware-domain and honeypot alerts can be useful, but shared infrastructure, research traffic and mistakes can still create false positives.

## Packet capture with tcpdump

When you need ground truth, capture packets. `tcpdump` uses **BPF capture filters**. On supported live-capture platforms filtering can run in the kernel; offline capture-file filtering runs in userspace:

```
# 20 packets to or from one host, no DNS
# or port-name lookups
tcpdump -i eth0 -nn -c 20 host 10.0.0.5

# request the maximum snapshot length
tcpdump -i eth0 -nn -s 0 \
  -w web.pcap 'tcp port 443'

# IPv4 SYN set, ACK clear
tcpdump -nn \
  'tcp[tcpflags] & (tcp-syn|tcp-ack)
     == tcp-syn'

# ring buffer: 10 files of 100 MB
tcpdump -i eth0 -w ring.pcap -C 100 -W 10
```

`-nn` matters on a busy box: name resolution can add delay and generate DNS traffic. Cached results and local host databases mean this is not necessarily a DNS query for every address. A line of output looks like this (wrapped to fit):

```
12:00:01.000123 IP 10.0.0.5.51812 >
  203.0.113.10.443: Flags [S],
  seq 3021930120, win 64240, length 0
```

The flags are the quickest way to read a conversation:

| Flags | Meaning |
|---|---|
| `[S]` | SYN, opening |
| `[S.]` | SYN-ACK |
| `[.]` | ACK flag; payload may still be present |
| `[P.]` | PSH and ACK flags; inspect length for payload |
| `[F.]` | FIN, closing |
| `[R]` | RST, refused or aborted |

SYNs to many ports can indicate a scan, but may also be authorized diagnostics. A reset indicates active rejection or abort somewhere along the path, possibly by a middlebox. Silence could reflect filtering, loss, an unavailable host or an unseen return path; it does not identify a firewall by itself.

### Wireshark

Wireshark decodes hundreds of protocols and is the tool for understanding a capture. Its **display filters** use a different syntax from BPF capture filters, a constant source of confusion:

| Capture (BPF) | Display (Wireshark) |
|---|---|
| `tcp port 80` | `tcp.port == 80` |
| `host 10.0.0.5` | `ip.addr == 10.0.0.5` |

Useful display filters for investigations:

- `tcp.flags.syn == 1 && tcp.flags.ack == 0`: connection attempts.
- `tcp.analysis.retransmission`: packets Wireshark heuristically classifies as retransmissions; investigate capture loss and reordering before inferring network loss.
- `dns.flags.rcode == 3`: NXDOMAIN answers. Bursts of random-looking names can indicate malware using domain-generation algorithms.
- `tls.handshake.type == 1`: visible ClientHellos; ECH can hide the real server name in the encrypted inner ClientHello.

"Follow TCP Stream" reassembles a conversation. For TLS you can decrypt your *own* captures if the client writes its session secrets to a file: browsers and many libraries honour the `SSLKEYLOGFILE` environment variable, and Wireshark reads it.

> [!warning] Capture pitfalls
> - **Offloads.** Depending on the capture hook and enabled offloads, host captures can show large buffers before transmit segmentation or after receive coalescing, and outbound checksums before hardware fills them in. Such apparent errors need not occur on the wire.
> - **Drops.** A busy capture can drop packets; tcpdump reports "dropped by kernel" on exit.
> - **Storage.** Recording bytes at a constant 1 Gbps is 125 MB/s, or 10.8 decimal TB/day before capture-file overhead. A physical link rate is not identical to recorded packet bytes because framing and gaps also consume capacity. Choose retention from measured volume and budget.
> - **Privacy and law.** Captures contain personal data and credentials; handle them as sensitive.

## Encrypted traffic

When traffic is encrypted, a passive sensor without decryption keys cannot inspect application plaintext. Defenders lean on metadata:

- **Who talks to whom**, how often and how much. Malware **beaconing** to its command server at regular intervals shows up in timing even when encrypted.
- **Visible TLS handshake metadata**: ordinary ClientHello SNI can reveal a requested name; ECH hides the inner name while an outer public name can remain visible. TLS 1.3 encrypts certificate messages, so a passive observer without keys cannot generally read them.
- **TLS fingerprints**: features of the ClientHello can help group similar clients, but are not authenticated software identities. Different clients may share a fingerprint, and an attacker can imitate one. Changes in parameter ordering can also affect order-sensitive fingerprints.
- **DNS logs**, which can reveal names looked up through the observed resolver. Cached answers, direct IP connections and unobserved encrypted DNS create gaps.

The alternative is **TLS interception** at a proxy, which restores payload visibility at the cost of the risks described in lesson 2. Any interception policy must define which traffic it can inspect and which traffic it exempts.

**Zeek** sits in between: it parses traffic into structured logs (`conn.log`, `dns.log`, `http.log`, `ssl.log`, `files.log`) whose record units depend on the log type. These logs retain selected metadata; encrypted application contents remain unavailable without decryption. Storage and usefulness depend on the enabled analyzers and traffic.

## Flow records

A **flow record** summarizes packets grouped by selected attributes within an observation interval. Common fields include a 5-tuple, timestamps, counters and TCP flags, but templates and aggregation policies vary. One TCP connection can produce multiple records.

- **NetFlow** (Cisco, v5 and v9) and its IETF standard successor **IPFIX** (RFC 7011): routers or probes export flow records to a collector.
- **sFlow** statistically samples packets at a configured average rate and exports sampled packet-header data plus counters. This is not necessarily every Nth packet; sampled header bytes can include some payload.
- Where flow export uses **sampling** (for example an average of 1 in 1,000 packets), it reduces observation volume but can miss short flows and introduces uncertainty into estimates.

In AWS, **VPC Flow Logs** record traffic on network interfaces. A default-format record looks like this (shown one field per line):

```
version       2
account-id    123456789012
interface-id  eni-0a1b2c3d
srcaddr       203.0.113.9
dstaddr       10.0.1.5
srcport       40001
dstport       22
protocol      6 (TCP)
packets       1
bytes         44
start, end    epoch seconds
action        REJECT
log-status    OK
```

`action` reports ACCEPT or REJECT. A rejection can arise from security groups, NACLs or packets arriving after connection closure; this field alone does not identify a particular rule. They have blind spots: traffic to the Amazon-provided DNS resolver, DHCP and the instance metadata service is not logged, so DNS-based activity needs Route 53 Resolver query logs instead. The default maximum aggregation interval is 10 minutes, with a 1-minute option; Nitro interfaces use at most 1 minute regardless. Publication adds delay, and SKIPDATA records disclose some logging gaps.

A simple scan detector over simplified flow records (source, destination, port, action):

```python
from collections import defaultdict

LOG = """
203.0.113.9 10.0.1.5 22 REJECT
203.0.113.9 10.0.1.5 23 REJECT
203.0.113.9 10.0.1.5 80 ACCEPT
203.0.113.9 10.0.1.5 3389 REJECT
203.0.113.9 10.0.1.6 22 REJECT
10.0.2.7 10.0.1.5 5432 ACCEPT
10.0.2.7 10.0.1.5 5432 ACCEPT
"""

targets = defaultdict(set)
rejects = defaultdict(int)
for line in LOG.strip().splitlines():
    src, dst, port, action = line.split()
    targets[src].add((dst, int(port)))
    if action == "REJECT":
        rejects[src] += 1

for src in sorted(targets):
    n, r = len(targets[src]), rejects[src]
    flag = "SCAN?" if n >= 4 else ""
    print(src, n, r, flag)
```

This prints `10.0.2.7 1 0` and `203.0.113.9 5 4 SCAN?`. The app server's two connections go to one `(host, port)` pair; the external address probes five pairs, mostly rejected. Real detectors add a time window, thresholds tuned to the environment and allow-lists for legitimate scanners, and distinct destination pairs per source are one useful heuristic, not proof of a malicious scan.

Within its coverage, flow data can help investigate questions such as: which hosts did this compromised machine talk to? Did anything inside send unusual volumes to the internet (exfiltration)? When did this start? Retention depends on record volume, cost and policy; small individual records do not guarantee months of affordable storage.

## Putting it together

A practical network-detection stack for a medium organisation:

1. **Flow logs at relevant observation points** (budgeted retention) for investigation and anomaly detection.
2. **DNS and proxy logs** for destinations.
3. **Zeek and Suricata** at key choke points (internet edge, between major segments).
4. **Short-retention or triggered full capture** where the detail is worth the storage.
5. Everything into a **SIEM**, correlated with host (EDR) and identity logs, with detections tuned for precision.

Segmentation (lesson 2) helps detection too: a denied cross-segment connection can merit investigation, but configuration errors and legitimate discovery can also produce it.

## Key takeaways
- An IDS watches a copy of traffic and alerts; an IPS sits inline and blocks, forcing a fail-open or fail-closed choice.
- Both signature and anomaly detectors can miss attacks and raise false alerts; measure precision using the actual prevalence and operating threshold.
- tcpdump uses BPF capture filters and Wireshark uses a different display-filter syntax; read TCP flags to follow a conversation, and beware offload artefacts.
- For encrypted traffic, visible metadata can support detection, but ECH, encrypted certificate messages and missing observations limit visibility.
- Flow records can support communication analysis within their sampling, aggregation and coverage limits; retention costs depend on volume.

## Further reading
- [Suricata rules format — Suricata docs](https://docs.suricata.io/en/latest/rules/intro.html)
- [tcpdump and libpcap](https://www.tcpdump.org/)
- [Wireshark display filters — Wireshark wiki](https://wiki.wireshark.org/DisplayFilters)
- [Logging IP traffic using VPC Flow Logs — AWS](https://docs.aws.amazon.com/vpc/latest/userguide/flow-logs.html)
- [RFC 7011: IPFIX Protocol Specification](https://www.rfc-editor.org/rfc/rfc7011)
- [Zeek documentation](https://docs.zeek.org/en/v7.1.1/logs/index.html)
- [Base rate fallacy — Wikipedia](https://en.wikipedia.org/wiki/Base_rate_fallacy)
