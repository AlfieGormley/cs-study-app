---
id: nsec-packet-filter-reading
title: Capture filters, display filters and TCP flags
level: advanced
minutes: 3
summary: tcpdump capture filters and Wireshark display filters use different syntax.
sourceLesson: nsec-detection
---

Packet captures preserve observations at one point in a path. This unit shows how to choose packets and read TCP flag output without confusing a reset, silence or a heuristic retransmission label with a complete diagnosis.

## Packet capture with tcpdump

When you need ground truth, capture packets. `tcpdump` uses **BPF capture filters**. On supported live-capture platforms filtering can run in the kernel; offline capture-file filtering runs in userspace:

```sh
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

SYNs to many ports can indicate a scan, but may also be authorised diagnostics. A reset indicates active rejection or abort somewhere along the path, possibly by a middlebox. Silence could reflect filtering, loss, an unavailable host or replies travelling by a path the sensor cannot see; it does not identify a firewall by itself.

### Wireshark

Wireshark decodes hundreds of protocols and is the tool for understanding a capture. Its **display filters** use a different syntax from BPF capture filters, a constant source of confusion:

| Capture (libpcap) | Display (Wireshark) |
|---|---|
| `tcp port 80` | `tcp.port == 80` |
| `host 10.0.0.5` | `ip.addr == 10.0.0.5` |

Useful display filters for investigations:

- `tcp.flags.syn == 1 && tcp.flags.ack == 0`: connection attempts.
- `tcp.analysis.retransmission`: packets Wireshark heuristically classifies as retransmissions; investigate capture loss and reordering before inferring network loss.
- `dns.flags.rcode == 3`: NXDOMAIN answers. Bursts of random-looking names can indicate malware using domain-generation algorithms.
- `tls.handshake.type == 1`: visible ClientHellos; ECH can hide the real server name in the encrypted inner ClientHello.

"Follow TCP Stream" reassembles a conversation. For TLS you can decrypt your *own* captures if the client writes its session secrets to a file: browsers and many libraries honour the `SSLKEYLOGFILE` environment variable, and Wireshark reads it.

## Key takeaways
- tcpdump capture filters and Wireshark display filters use different syntax.
- Flags and lengths describe packet observations rather than proving intent.
- Name-resolution controls, capture loss and TCP stream reconstruction context affect interpretation.

## Further reading
- [Suricata rules format — Suricata docs](https://docs.suricata.io/en/latest/rules/intro.html)
- [tcpdump and libpcap](https://www.tcpdump.org/)
- [Wireshark display filters — Wireshark wiki](https://wiki.wireshark.org/DisplayFilters)
- [Logging IP traffic using VPC Flow Logs — AWS](https://docs.aws.amazon.com/vpc/latest/userguide/flow-logs.html)
- [RFC 7011: IPFIX Protocol Specification](https://www.rfc-editor.org/rfc/rfc7011)
- [Zeek documentation](https://docs.zeek.org/en/v7.1.1/logs/index.html)
- [Base rate fallacy — Wikipedia](https://en.wikipedia.org/wiki/Base_rate_fallacy)
