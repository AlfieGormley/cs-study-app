---
id: nsec-flow-record-investigations
title: Flow records and bounded scan heuristics
level: advanced
minutes: 4
summary: Flow definitions, sampling and time windows vary across export systems.
sourceLesson: nsec-detection
---

Flow records trade raw packet detail for selected counters and attributes. This unit uses that summary to investigate communication patterns while keeping sampling, logging gaps and legitimate scanning in view.

## Flow records

A **flow record** summarises packets grouped by selected attributes within an observation interval. Common fields include a 5-tuple, timestamps, counters and TCP flags, but templates and the rules for grouping packets into records vary. One TCP connection can produce multiple records.

- **NetFlow** (Cisco, v5 and v9) and its IETF standard successor **IPFIX** (RFC 7011): routers or probes export flow records to a collector.
- **sFlow** statistically samples packets at a configured average rate and exports sampled packet-header data plus counters. This is not necessarily a strict count such as exactly every 1,000th packet; sampled header bytes can include some payload.
- Where flow export uses **packet sampling** (for example an average of 1 in 1,000 packets), it reduces observation volume but can miss short flows and introduces uncertainty into estimates.

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

`action` reports ACCEPT or REJECT. A rejection can arise from security groups, NACLs or packets arriving after a connection has closed; this field alone does not identify a particular rule. They have blind spots: traffic to the Amazon-provided DNS resolver, DHCP and the instance metadata service is not logged, so DNS-based activity needs Route 53 Resolver query logs instead. The default maximum time window for each record is 10 minutes, with a 1-minute option; Nitro interfaces use at most 1 minute regardless. Publication adds delay, and SKIPDATA records disclose some logging gaps.

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
    # Deduplicate destination pairs.
    targets[src].add((dst, int(port)))
    if action == "REJECT":
        # Count rejected records.
        rejects[src] += 1

for src in sorted(targets):
    n, r = len(targets[src]), rejects[src]
    # Use the example threshold.
    flag = "SCAN?" if n >= 4 else ""
    print(src, n, r, flag)
```

Ignoring the trailing space on the unflagged line, this prints `10.0.2.7 1 0` and `203.0.113.9 5 4 SCAN?`. The app server's two connections go to one `(host, port)` pair; the external address probes five pairs, mostly rejected. Real detectors add a time window, thresholds tuned to the environment and allowlists for legitimate scanners, and distinct destination pairs per source are one useful heuristic, not proof of a malicious scan.

Within its coverage, flow data can help investigate questions such as: which hosts did this compromised machine talk to? Did anything inside send unusual volumes to the internet (exfiltration)? When did this start? Retention depends on record volume, cost and policy; small individual records do not guarantee months of affordable storage.

## Putting it together

A practical network-detection stack for a medium organisation:

1. **Flow logs at relevant observation points** (budgeted retention) for investigation and anomaly detection.
2. **DNS and proxy logs** for destinations.
3. **Zeek and Suricata** at key choke points (internet edge, between major network segments).
4. **Short-retention or triggered full capture** where the detail is worth the storage.
5. Everything into a **SIEM**, correlated with host (EDR) and identity logs, with detections tuned for precision.

Segmentation (the earlier firewall and segmentation units) helps detection too: a denied connection between network segments can merit investigation, but configuration errors and legitimate discovery can also produce it.

## Key takeaways
- Flow definitions, sampling and time windows vary across export systems.
- VPC Flow Logs have documented coverage gaps and aggregation behaviour.
- Distinct destination pairs are a useful scan heuristic, not proof of malicious intent.

## Further reading
- [Suricata rules format — Suricata docs](https://docs.suricata.io/en/latest/rules/intro.html)
- [tcpdump and libpcap](https://www.tcpdump.org/)
- [Wireshark display filters — Wireshark wiki](https://wiki.wireshark.org/DisplayFilters)
- [Logging IP traffic using VPC Flow Logs — AWS](https://docs.aws.amazon.com/vpc/latest/userguide/flow-logs.html)
- [RFC 7011: IPFIX Protocol Specification](https://www.rfc-editor.org/rfc/rfc7011)
- [Zeek documentation](https://docs.zeek.org/en/v7.1.1/logs/index.html)
- [Base rate fallacy — Wikipedia](https://en.wikipedia.org/wiki/Base_rate_fallacy)
