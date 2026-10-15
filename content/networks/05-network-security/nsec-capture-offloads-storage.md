---
id: nsec-capture-offloads-storage
title: Capture artefacts and storage budgets
level: advanced
minutes: 3
summary: Host offloads can expose large buffers and incomplete checksums before wire transmission.
sourceLesson: nsec-detection
---

A packet capture is shaped by its observation point and retention settings. Before diagnosing impossible packet sizes or promising a month of retention, separate host-buffer artefacts from bytes actually stored.

> [!warning] Capture pitfalls
> - **Offloads.** Depending on the capture hook and enabled offloads, host captures can show large buffers before transmit segmentation or after receive coalescing, and outbound checksums before hardware fills them in. Such apparent errors need not occur on the wire.
> - **Drops.** A busy capture can drop packets; tcpdump reports "dropped by kernel" on exit.
> - **Storage.** Recording bytes at a constant 1 Gbps is 125 MB/s, or 10.8 decimal TB/day before capture-file overhead (calculated below). A physical link rate is not identical to recorded packet bytes because link-layer framing and gaps also consume capacity. Choose retention from measured volume and budget.
> - **Privacy and law.** Captures contain personal data and credentials; handle them as sensitive.

The storage a full capture needs is the recorded rate, converted from bits to bytes, multiplied by how long you record:

```formula
V = (R / 8) × T
V = (10^9 bit/s / 8) × 86400 s
V = 1.25 × 10^8 B/s × 86400 s
V = 1.08 × 10^13 B = 10.8 TB
where
V: the storage needed, in bytes (B)
R: the recorded data rate, in bits per second; here 1 Gbps = 10^9 bit/s. Dividing it by 8 converts bits to bytes, because a byte is 8 bits
T: the recording time, in seconds (s); one day = 86,400 s
bit: one binary digit
B: bytes; 1 B = 8 bits
s: seconds
TB: terabytes, in decimal units: 1 TB = 10^12 bytes
In words: recording packet bytes at 1 Gbps writes 125 megabytes every second, about 10.8 terabytes a day before file overhead. This is a recorded-byte model, not a claim about a physical link’s usable capacity.
```

Keeping 30 days of that is about 324 TB, which is why full capture usually has short retention or is triggered only when needed.

## Key takeaways
- Host offloads can expose large buffers and incomplete checksums before wire transmission.
- Capture volume uses recorded bytes, not physical link capacity alone.
- Storage calculations exclude file overhead, replication and compression unless stated.

## Further reading
- [Suricata rules format — Suricata docs](https://docs.suricata.io/en/latest/rules/intro.html)
- [tcpdump and libpcap](https://www.tcpdump.org/)
- [Wireshark display filters — Wireshark wiki](https://wiki.wireshark.org/DisplayFilters)
- [Logging IP traffic using VPC Flow Logs — AWS](https://docs.aws.amazon.com/vpc/latest/userguide/flow-logs.html)
- [RFC 7011: IPFIX Protocol Specification](https://www.rfc-editor.org/rfc/rfc7011)
- [Zeek documentation](https://docs.zeek.org/en/v7.1.1/logs/index.html)
- [Base rate fallacy — Wikipedia](https://en.wikipedia.org/wiki/Base_rate_fallacy)
