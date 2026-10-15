---
id: virt-live-migration
title: Pre-copy convergence and transfer time
level: intermediate
minutes: 4
sourceLesson: virt-hardware-assist
summary: Pre-copy shrinks only when effective distinct dirty-page production permits it.
---

This unit focuses on pre-copy convergence and migration failures. It builds on the earlier virtualisation units in this module.

## Live migration

Because a VM is just state, you can move a running one between hosts: to patch a host, drain failing hardware or rebalance load. The standard technique is **pre-copy** (Clark et al., NSDI 2005):

1. Copy all guest memory to the destination while the VM keeps running. Record pages the guest **dirties** during the copy (the hypervisor write-protects pages or uses hardware dirty logging).
2. Copy dirty pages again. Rounds shrink only when the effective dirty set and transfer capacity permit convergence.
3. When the remaining dirty set is small enough, **pause** the VM, copy the last dirty pages plus CPU and device state.
4. Resume on the destination; steer network traffic to the new host (for example, with a gratuitous ARP).

The pause in step 3 is the **downtime**. Its duration depends on remaining state, device handling, transfer rate and orchestration; no universal downtime range is asserted here.

### Will it converge?

Whether pre-copy ever finishes depends on two rates: how fast the hypervisor can copy memory, and how fast the guest dirties *distinct* pages. Each round copies whatever the guest dirtied while the previous round was copying:

```formula
r = d / b
t_k = D_k / b
D_{k+1} = d t_k = r D_k
where
r: the shrink ratio: each round's data as a fraction of the previous round's (no unit)
d: the rate at which the guest dirties distinct pages, in gigabytes per second (GB/s)
b: the effective copy rate actually achieved, in GB/s (not the link's nominal speed)
D_k: the data copied in round k, in gigabytes (GB); round 1 copies all guest memory
t_k: the time round k takes, in seconds (s)
D_{k+1}: the data dirtied during round k, which round k + 1 must copy, in GB
In words: every round copies what the guest managed to dirty during the previous round, so the remaining data shrinks by the factor r each round while r is below 1, and never shrinks if r is 1 or more.
```

A decimal-unit toy model: a 16 GB VM, an effective 1.25 GB/s copy rate and 0.2 GB/s (200 MB/s) of distinct newly dirtied page data. Assume constant rates and no protocol or state-transfer overhead; a nominal 10 Gbit/s link does not guarantee that effective rate.

```formula
r = (0.2 GB/s) / (1.25 GB/s) = 0.16
t_1 = 16 GB / (1.25 GB/s) = 12.8 s
D_2 = 0.2 GB/s × 12.8 s = 2.56 GB
t_2 = 2.56 GB / (1.25 GB/s) ≈ 2.05 s
D_3 = 2.56 GB × 0.16 = 0.4096 GB
t_3 = 0.4096 GB / (1.25 GB/s) ≈ 0.33 s
D_4 = 0.4096 GB × 0.16 ≈ 0.0655 GB
t_4 = 0.0655 GB / (1.25 GB/s) ≈ 0.052 s
where
r: the shrink ratio, dirtying rate divided by copy rate (no unit)
t_1, t_2, t_3, t_4: the time each copy round takes, in seconds (s)
D_2, D_3, D_4: the data dirtied during the previous round, which this round must copy, in gigabytes (GB)
GB: gigabyte, 1,000,000,000 bytes (decimal units in this model); 0.4096 GB ≈ 410 MB and 0.0655 GB ≈ 66 MB
GB/s: gigabytes per second
s: seconds
≈: approximately equal to (rounded)
In words: with a shrink ratio of 0.16, the data left to copy falls from 16 GB to about 66 MB in three rounds.
```

So stop before round 4 and copy the remaining roughly 66 MB while paused: about 52 ms of memory-transfer time, plus CPU/device and switchover work.

## Key takeaways

- Pre-copy repeatedly copies the distinct pages dirtied during earlier rounds.
- The constant-rate model predicts memory-transfer time, excluding device and orchestration costs.

## Further reading

- [Second Level Address Translation — Wikipedia](https://en.wikipedia.org/wiki/Second_Level_Address_Translation)
- [The KVM API — Linux kernel documentation](https://docs.kernel.org/virt/kvm/api.html)
- [Virtual I/O Device (VIRTIO) Version 1.2 — OASIS](https://docs.oasis-open.org/virtio/virtio/v1.2/virtio-v1.2.html)
- [PCI Express I/O Virtualization Howto — Linux kernel documentation](https://docs.kernel.org/PCI/pci-iov-howto.html)
- [Live Migration of Virtual Machines (NSDI 2005, PDF)](https://www.usenix.org/legacy/event/nsdi05/tech/full_papers/clark/clark.pdf)
