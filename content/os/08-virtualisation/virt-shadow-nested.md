---
id: virt-shadow-nested
title: From shadow to nested page tables
level: intermediate
minutes: 2
sourceLesson: virt-hardware-assist
summary: Shadow tables combine guest and host mappings and require synchronisation.
---

This unit focuses on from shadow to nested page tables. It builds on the earlier virtualisation units in this module.

## Memory: shadow page tables

A guest has its own page tables mapping **guest virtual** addresses (GVA) to what it thinks are physical addresses, **guest physical** addresses (GPA). The hypervisor maps those to real **host physical** addresses (HPA). The hardware MMU only does one translation, so before nested paging the hypervisor had to fake it.

**Shadow page tables** are hypervisor-built tables mapping GVA directly to HPA, which the real CR3 points at. One synchronisation strategy **write-protects** guest page-table pages and intercepts writes. Implementations can also use batching, unsynchronised pages and other optimisations; not every write must cause a separate exit.

That works, but a guest that forks processes or maps memory heavily generates a storm of exits.

## Nested page tables: EPT and NPT

The second generation of hardware support added a second level of translation in the MMU itself: Intel **EPT** (Extended Page Tables, Nehalem, 2008) and AMD **NPT/RVI** (Barcelona, 2007).

```
 GVA --guest page tables--> GPA
          (guest owns)
 GPA --EPT / NPT----------> HPA
          (hypervisor owns)
```

Nested paging normally lets guest page-table writes proceed without shadow-table synchronisation exits. EPT violations can arise from missing mappings or read/write/execute permission restrictions, including monitoring such as dirty logging; they are not limited to first allocation. Other exit reasons remain.

The catch is the cost of a **TLB miss**. Every pointer in the guest's page-table walk is itself a guest-physical address that must be translated through the nested tables.

## Key takeaways

- Shadow tables combine guest and host mappings and require synchronisation.
- EPT/NPT performs a second translation in hardware; permission and other exits remain.

## Further reading

- [Second Level Address Translation — Wikipedia](https://en.wikipedia.org/wiki/Second_Level_Address_Translation)
- [The KVM API — Linux kernel documentation](https://docs.kernel.org/virt/kvm/api.html)
- [Virtual I/O Device (VIRTIO) Version 1.2 — OASIS](https://docs.oasis-open.org/virtio/virtio/v1.2/virtio-v1.2.html)
- [PCI Express I/O Virtualization Howto — Linux kernel documentation](https://docs.kernel.org/PCI/pci-iov-howto.html)
- [Live Migration of Virtual Machines (NSDI 2005, PDF)](https://www.usenix.org/legacy/event/nsdi05/tech/full_papers/clark/clark.pdf)
