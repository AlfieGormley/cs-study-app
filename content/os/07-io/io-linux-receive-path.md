---
id: io-linux-receive-path
title: From the RX ring to recv
level: advanced
minutes: 2
summary: DMA, NAPI, skbs, GRO and protocol processing precede ordinary copied recv.
sourceLesson: io-network-stack
---

Follow one packet through a conventional Linux receive path. NIC means network interface card; an RX ring holds receive descriptors, and DMA lets the device transfer bytes into mapped memory.

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

1. **DMA into a ring.** The driver has given the NIC a ring of descriptors pointing at empty buffers (covered elsewhere in this module). The NIC writes the frame into the next buffer and marks the descriptor done.
2. **Interrupt.** The NIC raises an interrupt. The driver's top half does almost nothing: it schedules NAPI and masks further interrupts from that queue.
3. **NAPI poll.** In softirq context, the driver's poll function pulls completed descriptors off the ring and wraps each in an **`sk_buff`** (skb), the kernel's packet structure: metadata plus pointers to header and data.
4. **GRO.** Generic Receive Offload merges consecutive TCP segments of the same flow into one large skb, so the layers above process fewer larger skbs. Eligible protocols, limits and aggregation depend on kernel, driver and packet layout; GRO does not blindly merge every consecutive segment.
5. **Protocol layers.** IP checks the header, consults routing and netfilter (iptables/nftables). TCP finds the socket by its 5-tuple, processes ACKs and sequence numbers, and appends data to the socket's receive queue.
6. **Wake-up.** The socket is marked readable; any epoll instance watching it gets the fd on its ready list (covered elsewhere in this module) and the sleeping thread is woken.
7. **Copy.** A conventional copied recv consumes available bytes into your buffer. Partly consumed or shared skbs need not be freed immediately, and flags such as MSG_PEEK do not consume the data.

## Key takeaways
- DMA, NAPI, skbs, GRO and protocol processing precede ordinary copied recv.
- Wakeup and partial/shared packet ownership complicate the simplified path.

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
