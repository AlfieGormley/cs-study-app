---
id: io-flow-steering-transmit
title: Flow steering and the transmit path
level: advanced
minutes: 3
summary: Hardware queues, interrupt affinity and software steering are separate mappings.
sourceLesson: io-network-stack
---

## Spreading packets across cores

One RX queue handled by one core caps you at what one core can do. Modern NICs have many queues.

### Receive Side Scaling (RSS)

The NIC hashes each packet's flow (typically source and destination IP and port; the Toeplitz hash is common) and uses the hash to pick an RX queue. Queue interrupt mappings and affinity determine which CPUs handle them; one dedicated pinned CPU per queue is a possible configuration, not automatic.

```
          hash(5-tuple)
 packet -----> indirection table
               | q0 | q1 | q2 | q3 |
                 |    |    |    |
               CPU0 CPU1 CPU2 CPU3
```

With a stable Receive Side Scaling configuration, a flow generally maps to one RX queue. IRQ affinity and software steering can move later processing to other CPUs. That keeps packets in order and caches warm. The downside: one huge flow (an elephant flow) can't use more than one queue.

The listing shows Linux inspection commands and one configuration example. `eth0` is an illustrative interface name. The `-L` command changes queue configuration and may disrupt traffic; inspect driver support and plan an appropriate maintenance change before using it. This course does not run it against your interfaces:

```
ethtool -l eth0         # queue counts
ethtool -L eth0 combined 8
ethtool -x eth0         # RSS table
cat /proc/interrupts    # IRQs per CPU
```

### RPS, RFS and XPS

- **RPS** (Receive Packet Steering) is Receive Side Scaling done in software: for NICs with too few queues, the kernel hashes the packet in softirq and hands it to another CPU's backlog queue.
- **RFS** (Receive Flow Steering) goes further: it steers a flow to the CPU where the application thread that reads it last ran, so the socket data is hot in that core's cache. Accelerated RFS asks the NIC to do the steering.
- **XPS** (Transmit Packet Steering) can select transmit queues using CPU or receive-queue mappings, avoiding contention on a shared TX queue.

> [!tip] Line up the whole receive path
> Alignment can improve locality, but Receive Side Scaling, reuseport selection, IRQ affinity and worker affinity are separate mechanisms. A worker pinned to a CPU does not automatically receive flows from the RX queue with that same number; verify steering and NUMA behavior before claiming no cross-core traffic. `irqbalance` can undo careful manual pinning, so check `/proc/interrupts`.

## The transmit path

Sending is the mirror image:

1. `send()` copies your bytes into the socket's **send buffer** (or blocks / returns `EAGAIN` if it's full).
2. TCP builds segments as the congestion and receive windows allow. With **TSO/GSO** it hands down larger skbs (size limits depend on supported offload features) and the NIC (TCP segmentation offload) or the kernel just before the driver (generic segmentation offload, GSO) cuts it into MTU-sized frames.
3. The packet passes through a **queueing discipline** (qdisc). The configured/default qdisc depends on kernel build, distribution, interface and administrator settings. Inspect the actual qdisc and choose it for the congestion-control and latency goals.
4. The driver puts descriptors on a TX ring and writes the NIC's doorbell register. The NIC DMAs the frame out.
5. TX completion lets the driver free or reuse resources when ownership/reference rules allow it. Polling, interrupts and NAPI participation depend on the driver; completion is not necessarily an acknowledgement from the remote application.

## Key takeaways
- Hardware queues, interrupt affinity and software steering are separate mappings.
- A stable flow can concentrate receive work despite many queues.
- TCP segmentation offload and TX completion do not prove remote application receipt.

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
