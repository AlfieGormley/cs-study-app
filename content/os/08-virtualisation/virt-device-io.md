---
id: virt-device-io
title: Emulated devices, virtio and DMA isolation
level: intermediate
minutes: 3
sourceLesson: virt-hardware-assist
summary: Virtio batches requests through shared queues; acceleration can avoid userspace transitions.
---

This unit focuses on emulated devices, virtio and DMA isolation. It builds on the earlier virtualisation units in this module.

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

## Key takeaways

- Virtio batches requests through shared queues; acceleration can avoid userspace transitions.
- Passthrough needs correctly configured DMA, group/topology and interrupt isolation.

## Further reading

- [Second Level Address Translation — Wikipedia](https://en.wikipedia.org/wiki/Second_Level_Address_Translation)
- [The KVM API — Linux kernel documentation](https://docs.kernel.org/virt/kvm/api.html)
- [Virtual I/O Device (VIRTIO) Version 1.2 — OASIS](https://docs.oasis-open.org/virtio/virtio/v1.2/virtio-v1.2.html)
- [PCI Express I/O Virtualization Howto — Linux kernel documentation](https://docs.kernel.org/PCI/pci-iov-howto.html)
- [Live Migration of Virtual Machines (NSDI 2005, PDF)](https://www.usenix.org/legacy/event/nsdi05/tech/full_papers/clark/clark.pdf)
