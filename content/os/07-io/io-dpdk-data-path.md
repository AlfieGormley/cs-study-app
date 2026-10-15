---
id: io-dpdk-data-path
title: DPDK and custom data paths
level: advanced
minutes: 2
summary: Exclusive busy-poll bypass changes CPU use, ownership and observability.
sourceLesson: io-network-stack
---

## Where per-packet costs accumulate

Even with NAPI, GRO and Receive Side Scaling, each packet costs: skb allocation, netfilter rules, routing lookup, socket lookup, locks, and finally a copy to user space plus a syscall. Whether those costs exceed the budget depends on packet mix, offloads, hardware and configuration; a link-speed label alone does not decide the architecture.

Two ways out exist: take the kernel out of the data path (**DPDK**), or run your code inside it before the expensive parts (**XDP**).

## DPDK: kernel bypass

The **Data Plane Development Kit** provides userspace packet-processing APIs and drivers. In a conventional exclusive VFIO poll-mode setup:

- The NIC is unbound from its kernel driver and bound to `vfio-pci`, so the normal kernel network stack no longer owns that data path; the kernel still manages VFIO and device resources.
- **Poll-mode drivers** in your process read the RX ring directly, in a busy loop. The steady-state polling data path can avoid per-packet syscalls and skbs; setup/control paths, optional interrupt modes and packet-processing copies still exist.
- Packet buffers live in **hugepages** to reduce TLB misses; work is pinned one thread per core.

Without a specified benchmark, no per-core packet rate is asserted. For the exclusive busy-poll model, costs include:

- Each polling core sits at 100% CPU even when idle.
- No kernel TCP/IP stack: you bring your own (or use one such as F-Stack or Seastar's), and lose `tcpdump`, `iptables`, `ss` and the rest of the familiar tooling on that NIC.
- The NIC is dedicated to the application.

DPDK is used in several packet-processing domains. Bifurcated drivers can coexist with a kernel driver, and power-saving/interrupt modes can change the exclusive busy-poll tradeoffs above.

## Choosing

| Need | Use |
|---|---|
| Normal server | Kernel + Receive Side Scaling and RFS tuning |
| Early packet filtering/load balancing | Evaluate supported XDP mode |
| Full custom data plane | DPDK |
| Observability | eBPF tracing |

## Key takeaways
- Exclusive busy-poll bypass changes CPU use, ownership and observability.
- Bifurcated drivers and other modes change those trade-offs.
- Choose architecture from measured packet-processing needs.

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
