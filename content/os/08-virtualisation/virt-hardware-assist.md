---
id: virt-hardware-assist
title: Hardware-assisted virtualisation
level: intermediate
minutes: 13
summary: How VT-x and AMD-V add a guest mode to the CPU, how nested page tables avoid much shadow-paging synchronisation work, how virtio and SR-IOV make I/O fast, and how a running VM is live-migrated between hosts.
---

The previous lesson ended with x86 failing the Popek–Goldberg test and two clever software workarounds. In 2005–2006 Intel and AMD fixed the problem in silicon. This lesson covers what they added, the remaining bottlenecks (memory translation and I/O) and how modern clouds solve them.

## VT-x and AMD-V: a new CPU mode

Intel **VT-x** (2005) and AMD **AMD-V**, also called SVM (2006), take a simple approach. Rather than squeezing the guest into a less privileged ring, they add a whole new dimension of privilege:

```
       VMX root        VMX non-root
     (hypervisor)        (guests)
    +-----------+     +-----------+
    | ring 3    |     | ring 3    |
    | ring 0    |     | ring 0    |
    +-----------+     +-----------+
       ^   |  VM entry    ^
       |   +--------------+
       +------------------+
            VM exit
```

On Intel, a conventional guest kernel runs in **ring 0 of VMX non-root operation**. Guest privilege and virtualisation controls let the VMM preserve the intended guest semantics without classical ring compression; VM exits may be architecturally required or selected by controls. AMD uses its own host/guest terminology.

Control comes from a per-vCPU structure in memory, the **VMCS** (Intel) or **VMCB** (AMD). It holds:

- **Guest state**: architecturally specified control, segment and execution state. The VMCS does not automatically preserve every general-purpose register; VMM software handles additional state.
- **Host state**: Intel VMCS fields describe the resume context. AMD VMCB and host-save mechanisms differ; the structures are not identical layouts.
- **Execution controls**: which events cause a **VM exit**. The hypervisor picks: exit on `HLT`? On writes to CR3? On access to I/O port 0x60? On these MSRs? On external interrupts?

The hypervisor starts a guest with `VMLAUNCH`/`VMRESUME` (AMD: `VMRUN`). The guest runs natively until something configured to exit happens. The CPU then saves guest state, loads host state and jumps into the hypervisor with an **exit reason**.

### KVM: the loop at the heart of a cloud

On x86 Linux, **KVM** drives VT-x/AMD-V, and a userspace program (QEMU, Firecracker, crosvm, Cloud Hypervisor) handles devices. Each vCPU is a thread running this loop:

```c
for (;;) {
  if (ioctl(vcpu_fd, KVM_RUN, 0) < 0) {
    if (errno == EINTR) continue;
    fail("KVM_RUN"); /* exits process */
  }
  switch (run->exit_reason) {
  case KVM_EXIT_IO:
    emulate_port_io(run);
    break;
  case KVM_EXIT_MMIO:
    emulate_mmio(run);
    break;
  case KVM_EXIT_HLT:
    return; /* toy: stop on guest HLT */
  default:
    fail("unhandled KVM exit");
  }
}
```

This is a control-flow fragment, not a complete VMM: initialise and map the KVM run structure, provide handlers and error support, and define a real halt/wakeup policy. Many hardware exits are handled in KVM without userspace return. Userspace exits also include shutdown, internal errors and other events, not only device emulation. Reducing unnecessary transitions can reduce overhead.

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

> [!example] Counting a two-dimensional walk
> With n guest levels and m nested levels, an idealised uncached walk with ordinary pages reads (n + 1)(m + 1) − 1 page-table entries, excluding the final data access and accessed/dirty-bit update traffic. For 4-level guest and 4-level EPT tables that is 5 × 5 − 1 = **24 memory references**, against 4 natively. Five guest-physical addresses need translating (the guest CR3, the three lower table addresses and the final data address), each by a 4-step nested walk: 20. Add the 4 guest entries themselves: 24.

In practice, TLBs and page-walk caches hide most of this, and **huge pages** help a lot. With 2 MiB leaves in a four-level EPT (3 entries traversed), the worst case falls to 4 × 3 + 4 + 3 = 19; with compatible 2 MiB mappings in both stages, it falls further. A 2 MiB translation covers 512 times the bytes of a 4 KiB translation, but TLB entry counts and achieved performance differ by page size and CPU.

A further feature, **VPID** (AMD: ASID), tags TLB entries with the VM they belong to, so the TLB need not be flushed on every VM entry and exit.

## I/O: emulation, virtio and passthrough

CPU, memory and I/O costs depend on workload and configuration. Three common I/O approaches illustrate different tradeoffs.

### 1. Full emulation

QEMU can pretend to be an Intel e1000 network card. The guest driver accesses an emulated hardware interface. Trapped register accesses can require device-model work and userspace transitions; batching and acceleration affect the exact count. Emulation provides compatibility but can add overhead.

### 2. virtio: paravirtual devices

**virtio** (Rusty Russell, 2008, now an OASIS standard) defines devices designed for VMs. The guest driver and the host back end share **virtqueues** in guest memory:

```
 guest driver          host back end
 ------------          -------------
 put buffer in
 descriptor table
 add index to   ---->  read avail ring
 avail ring            do the I/O
 notify if needed
              <-----   write used ring
 read used ring        inject interrupt
```

One notification can cover a batch of buffers, and both sides can suppress notifications while busy. A kick need not even reach userspace: **vhost-net** handles virtio-net in the host kernel, and **vhost-user** hands it to a userspace switch such as DPDK. Supported device types depend on the VMM: do not assume that KVM itself, Firecracker and every cloud expose the same virtio devices.

### 3. Device passthrough and SR-IOV

Direct assignment gives the guest access to a hardware function and can reduce emulation overhead. With **VFIO** and an **IOMMU** (Intel VT-d, AMD-Vi), the hypervisor maps a PCI device straight into the guest. The IOMMU translates and restricts the device's DMA, so properly configured device DMA is limited to the assigned mappings. IOMMU groups, device topology and interrupt isolation also matter. Normal data transfers can avoid emulation exits; control and interrupt work do not universally disappear.

One device per VM does not scale, so **SR-IOV** (Single Root I/O Virtualisation) lets one physical card present itself as many:

- One **physical function (PF)**: the full device, managed by the host.
- Many **virtual functions (VFs)**: lightweight PCI functions, each with its own queues, passed to a different VM.

NIC switching and VF-to-VF connectivity depend on hardware and configuration. Cloud platforms can offload networking and storage to dedicated hardware; AWS describes **Nitro** as such an architecture with a lightweight KVM-based hypervisor. This does not establish a universal implementation or available-CPU percentage for cloud services.

| Approach | Guest driver | Speed | Live migration |
|---|---|---|---|
| Emulation | Stock | Device-model overhead | Device support needed |
| virtio | virtio | Batching/acceleration | Backend support needed |
| SR-IOV | Vendor VF | Direct-assignment path | Hardware support/failover |

## Live migration

Because a VM is just state, you can move a running one between hosts: to patch a host, drain failing hardware or rebalance load. The standard technique is **pre-copy** (Clark et al., NSDI 2005):

1. Copy all guest memory to the destination while the VM keeps running. Track pages the guest **dirties** during the copy (the hypervisor write-protects pages or uses hardware dirty logging).
2. Copy dirty pages again. Rounds shrink only when the effective dirty set and transfer capacity permit convergence.
3. When the remaining dirty set is small enough, **pause** the VM, copy the last dirty pages plus CPU and device state.
4. Resume on the destination; redirect network traffic (for example, with a gratuitous ARP).

The pause in step 3 is the **downtime**. Its duration depends on remaining state, device handling, transfer rate and orchestration; no universal downtime range is asserted here.

> [!example] Will it converge?
> In a decimal-unit toy model, a 16 GB VM has an effective 1.25 GB/s copy rate and 200 MB/s of distinct newly dirty page data. Assume constant rates and no protocol/state-transfer overhead; a nominal 10 Gbit/s link does not guarantee that effective rate.
> - Round 1: 16 GB takes 12.8 s; 2.56 GB dirtied meanwhile.
> - Round 2: 2.56 GB takes 2.05 s; 410 MB dirtied.
> - Round 3: 410 MB takes 0.33 s; 66 MB dirtied.
> - Stop before round 4 and copy the remaining roughly 66 MB while paused: about 52 ms of memory-transfer time, plus CPU/device and switchover work.
>
> In this model each round shrinks by 0.16. If distinct dirty-page production stays at least as fast as effective copying, the set need not shrink. Raw write bandwidth alone is insufficient: repeatedly writing an already-dirty page does not add another page to the set.

For write-heavy guests, hypervisors have fallbacks:

- **Auto-converge**: throttle the guest's vCPUs so it dirties memory more slowly.
- **Post-copy**: move CPU state first, start the VM on the destination, and fetch pages on demand as it faults on them. This can shorten the stop phase, but missing-page faults stall execution. If indispensable pages exist only on the source when it fails, the destination cannot reconstruct them.

SR-IOV is the awkward case: VF state lives in hardware and requires explicit device/driver migration support to export and restore. Common workarounds are to hot-unplug the VF and fail over to virtio during migration, or to use devices designed with migration support.

## Pitfalls

- **Nested virtualisation** (a hypervisor inside a VM) is supported by some KVM configurations and cloud instance types. Exposed CPU features and provider restrictions matter; extra translation and exit handling can add cost, but there is no fixed per-level multiplier.
- **CPU feature masking.** A VM migrated to an older CPU model would crash on missing instructions, so clusters advertise a common baseline (for example, a named QEMU CPU model) instead of the host's real features.
- **Huge pages in the guest only** help less than you hope if the host backs memory with 4 KB pages.

## Key takeaways

- VT-x and AMD-V add a non-root mode, so guest kernels run in a real ring 0 and the hypervisor chooses which events cause VM exits through the VMCS/VMCB.
- EPT/NPT avoids much shadow synchronisation work. Four-level tables in both stages need 24 uncached page-table entry reads in the stated structural model; this excludes data and update traffic.
- virtio uses shared-memory rings and batched notifications; SR-IOV and VFIO give guests real hardware, protected by the IOMMU.
- Pre-copy convergence depends on distinct dirty-page production versus effective copying; throttling, post-copy or a longer stop phase have different costs and failure modes.

> [!note] Execution and performance gaps
> The KVM loop is a source-reviewed teaching fragment, not a complete executed VMM. No live migration, VF assignment or device-throughput benchmark was run for this lesson. Exact downtime, exit counts and device performance therefore remain deployment-dependent; unsupported universal figures are omitted.

## Further reading

- [Second Level Address Translation — Wikipedia](https://en.wikipedia.org/wiki/Second_Level_Address_Translation)
- [The KVM API — Linux kernel documentation](https://docs.kernel.org/virt/kvm/api.html)
- [Virtual I/O Device (VIRTIO) Version 1.2 — OASIS](https://docs.oasis-open.org/virtio/virtio/v1.2/virtio-v1.2.html)
- [PCI Express I/O Virtualization Howto — Linux kernel documentation](https://docs.kernel.org/PCI/pci-iov-howto.html)
- [Live Migration of Virtual Machines (NSDI 2005, PDF)](https://www.usenix.org/legacy/event/nsdi05/tech/full_papers/clark/clark.pdf)
