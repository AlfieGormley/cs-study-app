---
id: nsec-encrypted-traffic-evidence
title: Evidence available in encrypted traffic
level: advanced
minutes: 3
summary: Encrypted application payloads require appropriate keys to inspect.
sourceLesson: nsec-detection
---

A passive sensor without session secrets cannot read protected application contents. It can still correlate observable traffic patterns, provided each conclusion respects what was actually captured.

## Encrypted traffic

When traffic is encrypted, a passive sensor without decryption keys cannot inspect application plaintext. Defenders lean on metadata:

- **Who talks to whom**, how often and how much. Malware **beaconing** to its command server at regular intervals shows up in timing even when encrypted.
- **Visible TLS handshake metadata**: ordinary ClientHello SNI can reveal a requested name; ECH hides the inner name while an outer public name can remain visible. TLS 1.3 encrypts certificate messages, so a passive observer without keys cannot generally read them.
- **TLS fingerprints**: features of the ClientHello can help group similar clients, but are not authenticated software identities. Different clients may share a fingerprint, and an attacker can imitate one. Changes in parameter ordering can also affect order-sensitive fingerprints.
- **DNS logs**, which can reveal names looked up through the observed resolver. Cached answers, direct IP connections and unobserved encrypted DNS create gaps.

The alternative is **TLS interception** at a proxy, which restores payload visibility at the cost of the risks described in the earlier firewall and segmentation units. Any interception policy must define which traffic it can inspect and which traffic it exempts.

**Zeek** sits in between: it parses traffic into structured logs (`conn.log`, `dns.log`, `http.log`, `ssl.log`, `files.log`) whose record units depend on the log type. These logs retain selected metadata; encrypted application contents remain unavailable without decryption. Storage and usefulness depend on the enabled analysers and traffic.

## Key takeaways
- Encrypted application payloads require appropriate keys to inspect.
- Visible names, addresses, timing and fingerprints are useful but incomplete signals.
- ECH, caching and unobserved DNS paths limit what a passive sensor can infer.

## Further reading
- [Suricata rules format — Suricata docs](https://docs.suricata.io/en/latest/rules/intro.html)
- [tcpdump and libpcap](https://www.tcpdump.org/)
- [Wireshark display filters — Wireshark wiki](https://wiki.wireshark.org/DisplayFilters)
- [Logging IP traffic using VPC Flow Logs — AWS](https://docs.aws.amazon.com/vpc/latest/userguide/flow-logs.html)
- [RFC 7011: IPFIX Protocol Specification](https://www.rfc-editor.org/rfc/rfc7011)
- [Zeek documentation](https://docs.zeek.org/en/v7.1.1/logs/index.html)
- [Base rate fallacy — Wikipedia](https://en.wikipedia.org/wiki/Base_rate_fallacy)
