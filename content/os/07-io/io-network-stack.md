---
id: io-network-stack
title: The kernel network stack, NAPI, RSS, DPDK, eBPF/XDP
level: advanced
minutes: 15
summary: The path a packet takes from the NIC to your recv() and back, how NAPI, GRO and RSS keep up with millions of packets a second, and when to bypass the kernel with DPDK or program it with eBPF and XDP.
---

Everything in this module so far ends at a socket: epoll says it's readable, `recv()` returns bytes. This lesson opens up what happens underneath, between the wire and the socket buffer.

It matters because at high packet rates kernel per-packet work can become a bottleneck, depending on the application and workload. Knowing the path tells you where packets get dropped, which knobs to turn, and when it's worth leaving the kernel out altogether.

## The budget

Start with the numbers. For the standard untagged minimum-frame calculation, use 64 frame bytes including FCS, plus 8 bytes of preamble/SFD and a 12-byte-time inter-frame gap: 84 byte-times, or 672 bit-times. This is link occupancy, not all payload or frame bytes.

| Link | Max packets/s | Time per packet |
|---|---|---|
| 1 Gbit/s | 1.49 M | 672 ns |
| 10 Gbit/s | 14.88 M | 67 ns |
| 100 Gbit/s | 148.8 M | 6.7 ns |

The serial time budget is small, but hardware latency is workload-dependent and multiple memory accesses can overlap. The table alone does not prove a fixed DRAM/syscall cost or a universal single-core throughput limit. Everything below is a strategy for spending less time per packet, or spreading packets across more cores.

## The receive path

```
 wire
  |  NIC DMAs frame into RX ring
  v
 [RX ring] --IRQ--> driver
  |  NAPI poll (softirq)
  v
 build sk_buff, GRO merges
  |
 netif_receive_skb
  |  (XDP ran earlier, in driver)
  v
 IP: route, netfilter
  |
 TCP/UDP: find socket
  |
 socket receive queue
  |  wake epoll / reader
  v
 recv() copies to user
```

For a conventional interrupt-driven, native-driver receive path (other modes differ):

1. **DMA into a ring.** The driver has given the NIC a ring of descriptors pointing at empty buffers (lesson 1). The NIC writes the frame into the next buffer and marks the descriptor done.
2. **Interrupt.** The NIC raises an interrupt. The driver's top half does almost nothing: it schedules NAPI and masks further interrupts from that queue.
3. **NAPI poll.** In softirq context, the driver's poll function pulls completed descriptors off the ring and wraps each in an **`sk_buff`** (skb), the kernel's packet structure: metadata plus pointers to header and data.
4. **GRO.** Generic Receive Offload merges consecutive TCP segments of the same flow into one large skb, so the layers above process fewer larger skbs. Eligible protocols, limits and aggregation depend on kernel, driver and packet layout; GRO does not blindly merge every consecutive segment.
5. **Protocol layers.** IP checks the header, consults routing and netfilter (iptables/nftables). TCP finds the socket by its 5-tuple, processes ACKs and sequence numbers, and appends data to the socket's receive queue.
6. **Wake-up.** The socket is marked readable; any epoll instance watching it gets the fd on its ready list (lesson 3) and the sleeping thread is woken.
7. **Copy.** A conventional copied recv consumes available bytes into your buffer. Partly consumed or shared skbs need not be freed immediately, and flags such as MSG_PEEK do not consume the data.

## NAPI: interrupts when idle, polling when busy

One interrupt per packet would melt a CPU at millions of packets a second (the "receive livelock" problem from lesson 1). **NAPI** (historically "New API") mixes the two approaches:

- In a conventional interrupt-driven configuration, arrivals while idle can trigger notification; interrupt coalescing may batch even light traffic.
- On the first interrupt, the driver disables the queue's interrupt and **polls** the ring in softirq context.
- Each poll handles up to a per-driver weight (typically 64 packets). If the ring still has work, NAPI keeps polling.
- When the ring is empty, the driver re-enables interrupts.

Network receive polling has packet and time budgets, configured through netdev_budget and netdev_budget_usecs. Inspect actual values rather than assuming defaults. When the budget/time test triggers, Linux increments time_squeeze and can reschedule softirq work; later processing may run in ksoftirqd depending on softirq scheduling. These controls do not guarantee zero starvation or identify an exact number of packets left.

You can see this per CPU in `/proc/net/softnet_stat` (hex columns: processed, dropped, time_squeeze, ...):

```python
for row, line in enumerate(
        open("/proc/net/softnet_stat")):
    f = [int(x, 16) for x in line.split()]
    print(row, "done", f[0],
          "drop", f[1], "squeeze", f[2])
```

A rising squeeze count indicates the budget/time condition was reached, not a complete diagnosis of ring backlog or CPU capacity. Correlate rates with queue, drop and CPU metrics before adjusting budgets or steering. The code labels rows; use the kernel-version layout/CPU identifier fields when offline CPUs make row numbers differ from CPU IDs.

## Spreading packets across cores

One RX queue handled by one core caps you at what one core can do. Modern NICs have many queues.

### RSS: Receive Side Scaling

The NIC hashes each packet's flow (typically source and destination IP and port; the Toeplitz hash is common) and uses the hash to pick an RX queue. Queue interrupt mappings and affinity determine which CPUs handle them; one dedicated pinned CPU per queue is a possible configuration, not automatic.

```
          hash(5-tuple)
 packet -----> indirection table
               | q0 | q1 | q2 | q3 |
                 |    |    |    |
               CPU0 CPU1 CPU2 CPU3
```

With a stable RSS configuration, a flow generally maps to one RX queue. IRQ affinity and software steering can move later processing to other CPUs. That keeps packets in order and caches warm. The downside: one huge flow (an elephant flow) can't use more than one queue.

Useful commands:

```
ethtool -l eth0         # queue counts
ethtool -L eth0 combined 8
ethtool -x eth0         # RSS table
cat /proc/interrupts    # IRQs per CPU
```

### RPS, RFS and XPS

- **RPS** (Receive Packet Steering) is RSS in software: for NICs with too few queues, the kernel hashes the packet in softirq and hands it to another CPU's backlog queue.
- **RFS** (Receive Flow Steering) goes further: it steers a flow to the CPU where the application thread that reads it last ran, so the socket data is hot in that core's cache. Accelerated RFS asks the NIC to do the steering.
- **XPS** (Transmit Packet Steering) can select transmit queues using CPU or receive-queue mappings, avoiding contention on a shared TX queue.

> [!tip] Line up the whole path
> Alignment can improve locality, but RSS, reuseport selection, IRQ affinity and worker affinity are separate mechanisms. A worker pinned to CPU N does not automatically receive flows from RX queue N; verify steering and NUMA behavior before claiming no cross-core traffic. `irqbalance` can undo careful manual pinning, so check `/proc/interrupts`.

## The transmit path

Sending is the mirror image:

1. `send()` copies your bytes into the socket's **send buffer** (or blocks / returns `EAGAIN` if it's full).
2. TCP builds segments as the congestion and receive windows allow. With **TSO/GSO** it hands down larger skbs (size limits depend on supported offload features) and the NIC (TSO) or the kernel just before the driver (GSO) cuts it into MTU-sized frames.
3. The packet passes through a **queueing discipline** (qdisc). The configured/default qdisc depends on kernel build, distribution, interface and administrator settings. Inspect the actual qdisc and choose it for the congestion-control and latency goals.
4. The driver puts descriptors on a TX ring and rings the NIC's doorbell. The NIC DMAs the frame out.
5. TX completion lets the driver reclaim resources when ownership/reference rules allow it. Polling, interrupts and NAPI participation depend on the driver; completion is not necessarily an acknowledgement from the remote application.

## Where per-packet costs accumulate

Even with NAPI, GRO and RSS, each packet costs: skb allocation, netfilter rules, routing lookup, socket lookup, locks, and finally a copy to user space plus a syscall. Whether those costs exceed the budget depends on packet mix, offloads, hardware and configuration; a link-speed label alone does not decide the architecture.

Two escape routes exist: take the kernel out of the path (**DPDK**), or run your code inside it before the expensive parts (**XDP**).

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

## eBPF and XDP: program the kernel

**eBPF** lets you load small programs into the kernel and attach them to hooks: sockets, tracepoints, cgroups, the traffic-control layer and more. A **verifier** checks permitted control flow, pointer types and memory access before execution. Packet accesses must have provable bounds; this does not mean every access needs its own runtime check. Programs may be JIT-compiled to native code depending on architecture/configuration and share data with user space through **maps** (hash tables, arrays, ring buffers).

**Native XDP** (eXpress Data Path) runs early in a supporting driver's receive path, before the normal skb-based stack path. Generic XDP operates after skb allocation, and hardware offload runs elsewhere. The program returns a verdict:

| Action | Effect |
|---|---|
| `XDP_DROP` | Discard; cheapest path |
| `XDP_PASS` | Continue to normal stack |
| `XDP_TX` | Bounce out same NIC |
| `XDP_REDIRECT` | Other NIC, CPU or AF_XDP |
| `XDP_ABORTED` | Drop, with a trace event |

This parsing fragment classifies untagged, unfragmented IPv4 UDP destination port 9999. It deliberately passes other formats, fragments and malformed lengths onward; it is not a complete firewall or fragment-reassembly policy. Supply Linux/BPF headers, a loader and license declaration:

```c
SEC("xdp")
int drop9999(struct xdp_md *ctx)
{
  void *data =
      (void *)(long)ctx->data;
  void *end =
      (void *)(long)ctx->data_end;
  struct ethhdr *eth = data;
  if ((void *)(eth + 1) > end)
    return XDP_PASS;
  if (eth->h_proto !=
      bpf_htons(ETH_P_IP))
    return XDP_PASS;
  struct iphdr *ip =
      (void *)(eth + 1);
  if ((void *)(ip + 1) > end ||
      ip->protocol != IPPROTO_UDP)
    return XDP_PASS;
  if (ip->version != 4 || ip->ihl < 5)
    return XDP_PASS;
  if (bpf_ntohs(ip->frag_off) & 0x3fff)
    return XDP_PASS; /* MF or offset */
  unsigned hlen = ip->ihl * 4;
  unsigned total = bpf_ntohs(ip->tot_len);
  if (total < hlen + sizeof(struct udphdr))
    return XDP_PASS;
  if ((void *)ip + total > end)
    return XDP_PASS;
  struct udphdr *udp = (void *)ip + hlen;
  if ((void *)(udp + 1) > end)
    return XDP_PASS;
  if (udp->dest == bpf_htons(9999))
    return XDP_DROP;
  return XDP_PASS;
}
```

The bounds checks establish that the packet fields being read are available. The verifier must be able to prove those accesses safe; an earlier sufficient check may cover several reads. This fragment has been exercised as native C with synthetic packets, but has not been compiled and loaded through a real BPF verifier in this audit.

Why XDP is attractive compared with DPDK:

- **It cooperates with the kernel.** Packets you don't care about get `XDP_PASS` and follow the normal stack, so TCP, `ss` and iptables keep working.
- **No dedicated cores.** It runs only when packets arrive, inside NAPI.
- **Early rejection.** Native XDP can skip later stack work for dropped packets; achieved throughput must be measured for the particular program and hardware.
- **AF_XDP** sockets give DPDK-like user-space packet access for selected traffic, while the rest stays with the kernel.

Modes: **native** (in the driver, needs driver support), **generic** (after skb allocation, with broader support but retaining allocation costs) and **offloaded** (runs on SmartNICs that support it).

> [!example] In production
> Published examples include Cloudflare's XDP packet-filtering work and Meta's XDP-based **Katran** layer-4 load balancer. **Cilium** supports eBPF Kubernetes networking and a kube-proxy replacement. Its exact use of iptables depends on configuration and kernel capabilities; these examples do not guarantee a particular deployment's throughput.

## Choosing

| Need | Use |
|---|---|
| Normal server | Kernel + RSS/RFS tuning |
| Early packet filtering/load balancing | Evaluate supported XDP mode |
| Full custom data plane | DPDK |
| Observability | eBPF tracing |

## Key takeaways
- At 10 Gbit/s with minimum-size frames you get about 67 ns per packet, which is an aggregate link occupancy budget, not a guarantee about a particular core's execution time.
- Receive path: NIC DMAs into an RX ring, an interrupt schedules NAPI, the poll builds skbs, GRO merges them, IP and TCP deliver to the socket queue and wake epoll, and `recv()` copies to user space.
- NAPI switches from interrupts to budgeted polling under load; `/proc/net/softnet_stat` shows drops and time squeezes.
- RSS hashes flows to hardware RX queues; IRQ affinity and software steering determine CPU placement. RPS, RFS and XPS help tune locality and distribution.
- Exclusive DPDK polling can bypass the normal kernel packet path, trading CPU/resources and tooling for a different processing model; bifurcated modes differ. Native XDP can reject packets before the normal skb path or pass them onward.

> [!note] Implementation and measurement gaps
> No reproducible DRAM/syscall-latency, DPDK/XDP per-core throughput or universal tuning benchmark accompanies this lesson, so fixed performance claims are omitted. The XDP fragment does not implement VLAN/IPv6 parsing, fragment reassembly or checksum validation; passing those cases is deliberate, not proof they are safe. Kernel budgets, offloads and driver modes must be checked on the actual system.

## Further reading
- [Ethernet throughput calculation — Infineon](https://community.infineon.com/t5/Knowledge-Base-Articles/AURIX-Ethernet-throughput-vs-bandwidth/ta-p/1123904)
- [NAPI — Linux kernel documentation](https://docs.kernel.org/networking/napi.html)
- [Scaling in the Linux Networking Stack (RSS, RPS, RFS, XPS) — kernel documentation](https://docs.kernel.org/networking/scaling.html)
- [The eXpress Data Path (XDP paper and data)](https://github.com/tohojo/xdp-paper)
- [What is eBPF? — ebpf.io](https://ebpf.io/what-is-ebpf/)
- [About DPDK — dpdk.org](https://www.dpdk.org/about/)
- [How to drop 10 million packets per second — Cloudflare blog](https://blog.cloudflare.com/how-to-drop-10-million-packets/)
- [Open-sourcing Katran, a scalable network load balancer — Engineering at Meta](https://engineering.fb.com/2018/05/22/open-source/open-sourcing-katran-a-scalable-network-load-balancer/)
