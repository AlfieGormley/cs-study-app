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
> - **Storage.** Full capture fills disks quickly (worked out below). A physical link rate is not identical to recorded packet bytes, because link-layer framing and gaps also consume capacity. Choose retention from measured volume and budget.
> - **Privacy and law.** Captures contain personal data and credentials; handle them as sensitive.

### How much storage does full capture need?

Storage grows in direct proportion to both the recorded rate and the retention time: double either and you double the disk. Remember to divide a bit rate by 8 to get bytes. Recording packet bytes at a steady 1 Gbps writes 125 megabytes every second, which is about 10.8 terabytes (decimal) a day before capture-file overhead. Keeping 30 days of that needs about 324 TB; at 2 Gbps it is about 650 TB.

That is why full capture usually has short retention, often a rolling buffer of hours or days, or is triggered only when needed. Teams commonly keep much smaller evidence for longer: protocol logs and flow records summarise the same traffic at a small fraction of the size, at the cost of losing payload detail. Compression helps less than you might hope, because most web traffic is now encrypted, and encrypted bytes barely compress.

## Key takeaways
- Host offloads can expose large buffers and incomplete checksums before wire transmission.
- Capture volume uses recorded bytes, not physical link capacity alone.
- Full-capture storage scales with rate and retention; keep full packets briefly and summaries longer.

## Further reading
- [tcpdump and libpcap](https://www.tcpdump.org/)
- [Segmentation offloads — Linux kernel documentation](https://docs.kernel.org/networking/segmentation-offloads.html)
- [Wireshark display filters — Wireshark wiki](https://wiki.wireshark.org/DisplayFilters)
