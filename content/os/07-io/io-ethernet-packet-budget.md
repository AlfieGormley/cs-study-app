---
id: io-ethernet-packet-budget
title: Ethernet wire occupancy and packet budgets
level: advanced
minutes: 3
summary: Minimum-frame rates count preamble and inter-frame gaps as link occupancy.
sourceLesson: io-network-stack
---

Everything in this module so far ends at a socket: epoll says it's readable, `recv()` returns bytes. This lesson opens up what happens underneath, between the wire and the socket buffer.

It matters because at high packet rates kernel per-packet work can become a bottleneck, depending on the application and workload. Knowing the code path tells you where packets get dropped, which knobs to turn, and when it's worth leaving the kernel out altogether.

## The budget

Start with the numbers. For the standard untagged minimum-frame calculation, use 64 frame bytes including FCS, plus 8 bytes of preamble/SFD and a 12-byte-time inter-frame gap: 84 byte-times, or 672 bit-times. This is link occupancy, not all payload or frame bytes.

The table below comes from two short calculations: how many bits one minimum frame occupies on the wire, then how many such slots fit into one second at the link's bit rate.

```formula
L = (64 + 8 + 12) B × 8 bit/B = 672 bit
P = C / L
P = (10^10 bit/s) / (672 bit)
P ≈ 14.88 × 10^6 /s
T = 1 / P = L / C
T = (672 bit) / (10^10 bit/s) = 67.2 ns
where
L: the wire occupancy of one minimum-size frame, in bits (bit): 64 bytes of frame including the FCS, 8 bytes of preamble and SFD, and a 12-byte inter-frame gap
B: byte, 8 bits; bit/B means bits per byte
bit: binary digit, the unit of data on the wire
C: the link's bit rate, in bits per second (bit/s); here 10 Gbit/s = 10^10 bit/s
P: the maximum packet rate, in packets per second (/s)
T: the time budget per packet, in nanoseconds (ns)
s: second; "/s" means per second
ns: nanosecond, one billionth (10^−9) of a second
≈: approximately equal to (the result is rounded)
In words: a minimum frame occupies 672 bit-times, so a 10 Gbit/s link can deliver about 14.88 million of them a second, one every 67.2 nanoseconds.
```

The same arithmetic at 1 Gbit/s gives 672 ns per packet, and at 100 Gbit/s 6.72 ns. It assumes untagged minimum frames back to back; larger transmitted frames lower the packet rate. Adding a VLAN tag to a given frame can increase its size, but minimum-frame padding rules mean a tag alone does not universally determine the new frame length.

| Link | Max packets/s | Time per packet |
|---|---|---|
| 1 Gbit/s | 1.49 M | 672 ns |
| 10 Gbit/s | 14.88 M | 67 ns |
| 100 Gbit/s | 148.8 M | 6.7 ns |

The serial time budget is small, but hardware latency is workload-dependent and multiple memory accesses can overlap. The table alone does not prove a fixed DRAM/syscall cost or a universal single-core throughput limit. Everything below is a strategy for spending less time per packet, or spreading packets across more cores.

## Key takeaways
- Minimum-frame rates count preamble and inter-frame gaps as link occupancy.
- An aggregate link budget is not a per-core execution guarantee.

## Further reading
- [Ethernet frame fields — Cisco Press](https://www.ciscopress.com/articles/article.asp?p=3089352&seqNum=4)
- [Inter-packet gaps — Cisco](https://www.cisco.com/c/en/us/support/docs/switches/catalyst-9600-series-switches/217413-understand-why-fcs-errors-input-errors.html)
- [NAPI — Linux kernel documentation](https://docs.kernel.org/networking/napi.html)
- [Scaling in the Linux Networking Stack (RSS, RPS, RFS, XPS) — kernel documentation](https://docs.kernel.org/networking/scaling.html)
- [The eXpress Data Path (XDP paper and data)](https://github.com/tohojo/xdp-paper)
- [What is eBPF? — ebpf.io](https://ebpf.io/what-is-ebpf/)
- [About DPDK — dpdk.org](https://www.dpdk.org/about/)
- [How to drop 10 million packets per second — Cloudflare blog](https://blog.cloudflare.com/how-to-drop-10-million-packets/)
- [Open-sourcing Katran, a scalable network load balancer — Engineering at Meta](https://engineering.fb.com/2018/05/22/open-source/open-sourcing-katran-a-scalable-network-load-balancer/)
