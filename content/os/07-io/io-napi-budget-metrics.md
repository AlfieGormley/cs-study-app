---
id: io-napi-budget-metrics
title: NAPI polling budgets and softnet metrics
level: advanced
minutes: 2
summary: NAPI combines notification with bounded receive polling.
sourceLesson: io-network-stack
---

NAPI is Linux’s network-driver polling interface. In the conventional interrupt-driven receive model, a device notification schedules polling and interrupts stay masked while queued work is processed.

## NAPI: interrupts when idle, polling when busy

One interrupt per packet would melt a CPU at millions of packets a second (the "receive livelock" problem introduced earlier in this module). **NAPI** (historically "New API") mixes the two approaches:

- In a conventional interrupt-driven configuration, arrivals while idle can trigger notification; interrupt coalescing may batch even light traffic.
- On the first interrupt, the driver disables the queue's interrupt and **polls** the ring in softirq context.
- Each poll handles up to a per-driver weight (typically 64 packets). If the ring still has work, NAPI keeps polling.
- When the ring is empty, the driver re-enables interrupts.

Network receive polling has packet and time budgets, configured through netdev_budget and netdev_budget_usecs. Inspect actual values rather than assuming defaults. When the budget/time test triggers, Linux increments time_squeeze and can reschedule softirq work; later processing may run in ksoftirqd depending on softirq scheduling. These controls do not guarantee zero starvation or identify an exact number of packets left.

You can see this per CPU in `/proc/net/softnet_stat` (hex columns: processed, dropped, time_squeeze, ...):

```python
for row, line in enumerate(
        open("/proc/net/softnet_stat")):
    # Kernel counters are hexadecimal.
    f = [int(x, 16) for x in line.split()]
    # Totals need comparison over time.
    print(row, "done", f[0],
          "drop", f[1], "squeeze", f[2])
```

A rising squeeze count indicates the budget/time condition was reached, not a complete diagnosis of ring backlog or CPU capacity. Correlate rates with queue, drop and CPU metrics before adjusting budgets or steering. The code labels rows; use the kernel-version layout/CPU identifier fields when offline CPUs make row numbers differ from CPU IDs.

## Key takeaways
- NAPI combines notification with bounded receive polling.
- time_squeeze identifies a budget/time condition, rather than a complete diagnosis.

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
