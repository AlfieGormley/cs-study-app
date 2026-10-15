---
id: io-xdp-packet-classification
title: eBPF, XDP and safe packet parsing
level: advanced
minutes: 4
summary: Native XDP can reject early or pass traffic to the normal stack.
sourceLesson: io-network-stack
---

The conventional receive path normally builds packet metadata and passes traffic through IP, transport and socket processing. Native XDP provides an earlier classification point in supporting drivers.

## eBPF and XDP: program the kernel

**eBPF** lets you load small programs into the kernel and attach them to hooks: sockets, tracepoints, cgroups, the traffic-control layer and more. The **eBPF verifier** checks permitted control flow, pointer types and memory access before execution. Packet accesses must have provable bounds; this does not mean every access needs its own runtime check. Programs may be JIT-compiled to native code depending on architecture/configuration and share data with user space through **BPF maps** (hash tables, arrays, ring buffers).

**Native XDP** (eXpress Data Path) runs early in a supporting driver's receive path, before the normal skb-based stack path. Generic XDP operates after skb allocation, and hardware offload runs elsewhere. The program returns a verdict:

| Action | Effect |
|---|---|
| `XDP_DROP` | Discard before normal stack |
| `XDP_PASS` | Continue to normal stack |
| `XDP_TX` | Bounce out same NIC |
| `XDP_REDIRECT` | Other NIC, CPU or AF_XDP |
| `XDP_ABORTED` | Drop, with a trace event |

This parsing fragment classifies untagged, unfragmented IPv4 UDP destination port 9999. It deliberately passes other formats, fragments and the invalid IP-length cases checked below onward; it is not a complete firewall or fragment-reassembly policy. Supply Linux/BPF headers, a BPF loader program and license declaration:

```c
SEC("xdp")
int drop9999(struct xdp_md *ctx)
{
  void *data =
      (void *)(long)ctx->data;
  void *end =
      (void *)(long)ctx->data_end;
  /* Bounds checks precede packet reads. */
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
  /* IPv4 options change header length. */
  unsigned hlen = ip->ihl * 4;
  unsigned total = bpf_ntohs(ip->tot_len);
  if (total < hlen + sizeof(struct udphdr))
    return XDP_PASS;
  if ((void *)ip + total > end)
    return XDP_PASS;
  struct udphdr *udp = (void *)ip + hlen;
  if ((void *)(udp + 1) > end)
    return XDP_PASS;
  /* Drop only the selected UDP port. */
  if (udp->dest == bpf_htons(9999))
    return XDP_DROP;
  return XDP_PASS;
}
```

The bounds checks establish that the packet fields being read are available. The verifier must be able to prove those accesses safe; an earlier sufficient check may cover several reads. This fragment has been exercised as native C with synthetic packets, and compiled to a BPF object, but has not been loaded through a real BPF verifier in this audit.

Why XDP is attractive compared with DPDK:

- **It cooperates with the kernel.** Packets you don't care about get `XDP_PASS` and follow the normal stack, so TCP, `ss` and iptables keep working.
- **No dedicated polling core required.** In the conventional driver receive path, native XDP processes packets during NAPI handling.
- **Early rejection.** Native XDP can skip later stack work for dropped packets; achieved throughput must be measured for the particular program and hardware.
- **AF_XDP** sockets give DPDK-like user-space packet access for selected traffic, while the rest stays with the kernel.

Modes: **native** (in the driver, needs driver support), **generic** (after skb allocation, with broader support but retaining allocation costs) and **offloaded** (runs on SmartNICs that support it).

> [!example] In production
> Published examples include Cloudflare's XDP packet-filtering work and Meta's XDP-based **Katran** layer-4 load balancer. **Cilium** supports eBPF Kubernetes networking and a kube-proxy replacement. Its exact use of iptables depends on configuration and kernel features; these examples do not guarantee a particular deployment's throughput.

> [!note] Implementation and measurement gaps
> No reproducible DRAM/syscall-latency, DPDK/XDP per-core throughput or universal tuning benchmark accompanies this lesson, so fixed performance claims are omitted. The XDP fragment does not implement VLAN/IPv6 parsing, fragment reassembly, UDP length consistency or checksum validation; passing those cases is deliberate, not proof they are safe. Kernel budgets, offloads and driver modes must be checked on the actual system.

## Key takeaways
- Native XDP can reject early or pass traffic to the normal stack.
- Provable packet bounds protect field accesses.
- The example deliberately passes unsupported formats; it is not a complete firewall.

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
