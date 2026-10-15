---
id: virt-nested-walk-cost
title: Counting an uncached nested page walk
level: intermediate
minutes: 4
sourceLesson: virt-hardware-assist
summary: The structural walk model excludes the final data access, accessed/dirty updates and all caching.
---

This unit focuses on counting an uncached nested page walk. It builds on the earlier virtualisation units in this module.

## Counting a two-dimensional walk

How many memory reads does one TLB miss cost? The guest's walk reads one entry per guest level. Every table address it follows, and the final data address, is a guest-physical address, so each needs its own walk through the nested tables. This formula counts the reads for an idealised walk with ordinary (4 KiB) pages and nothing cached:

```formula
R_2D = (n + 1)m + n
R_2D = (n + 1)(m + 1) − 1
where
R_2D: the number of page-table entries read from memory for one complete two-dimensional (guest plus nested) walk. It excludes the final data access and any accessed/dirty-bit updates
n: the number of levels in the guest's own page tables, typically 4 on x86-64 (5 with five-level paging)
m: the number of levels in the nested (EPT or NPT) tables, typically 4
In words: n + 1 guest-physical addresses (the guest CR3, the n − 1 lower table addresses and the final data address) each need an m-step nested walk, plus the n guest entries themselves; tidied up, that is (n + 1)(m + 1) − 1.
```

For 4-level guest tables and 4-level EPT:

```formula
R_2D = (n + 1)(m + 1) − 1
R_2D = (4 + 1) × (4 + 1) − 1
R_2D = 24
where
R_2D: page-table entries read for one uncached nested walk
n: guest page-table levels, here 4
m: nested (EPT) page-table levels, here 4
In words: a 4-by-4 nested walk reads 24 page-table entries, against 4 for the same walk on bare metal.
```

Five guest-physical addresses need translating (the guest CR3, the three lower table addresses and the final data address), each by a 4-step nested walk: 20 reads. Add the 4 guest entries themselves: **24 memory references**. The model assumes every walk misses every cache; real hardware almost never pays the full 24.

In practice, TLBs and page-walk caches hide most of this, and **huge pages** help a lot. A 2 MiB EPT leaf ends each nested walk one level early, so each nested walk reads 3 entries instead of 4:

```formula
R_2D = (n + 1)m_eff + n
R_2D = (4 + 1) × 3 + 4
R_2D = 19
where
R_2D: page-table entries read for one uncached nested walk
n: guest page-table levels, here 4, with ordinary 4 KiB guest pages
m_eff: nested-table entries actually read per nested walk; 3 when the EPT maps 2 MiB pages, instead of 4
In words: 2 MiB pages in the nested tables cut the worst case from 24 reads to 19; huge pages in both stages cut it further.
```

A 2 MiB translation covers 512 times the bytes of a 4 KiB translation, but TLB entry counts and achieved performance differ by page size and CPU.

A further feature, **VPID** (AMD: ASID), tags TLB entries with the VM they belong to, so the TLB need not be flushed on every VM entry and exit.

## Key takeaways

- The structural walk model excludes the final data access, accessed/dirty updates and all caching.
- Huge pages shorten walks and extend translation coverage; realised performance needs measurement.

## Further reading

- [Second Level Address Translation — Wikipedia](https://en.wikipedia.org/wiki/Second_Level_Address_Translation)
- [The KVM API — Linux kernel documentation](https://docs.kernel.org/virt/kvm/api.html)
- [Virtual I/O Device (VIRTIO) Version 1.2 — OASIS](https://docs.oasis-open.org/virtio/virtio/v1.2/virtio-v1.2.html)
- [PCI Express I/O Virtualization Howto — Linux kernel documentation](https://docs.kernel.org/PCI/pci-iov-howto.html)
- [Live Migration of Virtual Machines (NSDI 2005, PDF)](https://www.usenix.org/legacy/event/nsdi05/tech/full_papers/clark/clark.pdf)
