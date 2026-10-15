---
id: virt-migration-failures
title: Migration failure modes and compatibility
level: intermediate
minutes: 3
sourceLesson: virt-hardware-assist
summary: Dirty-page production, post-copy dependencies and CPU/device compatibility constrain migration.
---

Pre-copy transfers memory while the VM still runs. That preserves a running source before switchover, but migration cannot promise progress or recovery under every workload and failure.

The model shows when pre-copy fails. If distinct dirty-page production stays at least as fast as effective copying, then the shrink ratio is one or more and the set need not shrink. Raw write bandwidth alone is insufficient: repeatedly writing an already-dirty page does not add another page to the set.

For write-heavy guests, hypervisors have fallbacks:

- **Auto-converge**: throttle the guest's vCPUs so it dirties memory more slowly.
- **Post-copy**: move CPU state first, start the VM on the destination, and fetch pages on demand as it faults on them. This can shorten the stop phase, but missing-page faults stall execution. If indispensable pages exist only on the source when it fails, the destination cannot reconstruct them.

SR-IOV is the awkward case: VF state lives in hardware and requires explicit device/driver live-migration support to export and restore. Common workarounds are to hot-unplug the VF and fail over to virtio during live migration, or to use devices designed with live-migration support.

## Pitfalls

- **Nested virtualisation** (a hypervisor inside a VM) is supported by some KVM configurations and cloud instance types. Exposed CPU features and provider restrictions matter; extra translation and exit handling can add cost, but there is no fixed per-level multiplier.
- **CPU feature masking.** A VM live-migrated to an older CPU model would crash on missing instructions, so clusters advertise a common baseline (for example, a named QEMU CPU model) instead of the host's real features.
- **Huge pages in the guest only** help less than you hope if the host backs memory with 4 KB pages.

> [!note] Execution and performance gaps
> The KVM loop is a source-reviewed teaching fragment, not a complete executed VMM. No live migration, VF assignment or device-throughput benchmark was run for this lesson. Exact downtime, exit counts and device performance therefore remain deployment-dependent; unsupported universal figures are omitted.

## Key takeaways

- A dirty set that does not shrink needs throttling, more effective bandwidth, post-copy or a longer pause.
- Post-copy depends on remaining source pages; passthrough devices and CPU features also constrain migration.

## Further reading

- [Second Level Address Translation — Wikipedia](https://en.wikipedia.org/wiki/Second_Level_Address_Translation)
- [The KVM API — Linux kernel documentation](https://docs.kernel.org/virt/kvm/api.html)
- [Virtual I/O Device (VIRTIO) Version 1.2 — OASIS](https://docs.oasis-open.org/virtio/virtio/v1.2/virtio-v1.2.html)
- [PCI Express I/O Virtualization Howto — Linux kernel documentation](https://docs.kernel.org/PCI/pci-iov-howto.html)
- [Live Migration of Virtual Machines (NSDI 2005, PDF)](https://www.usenix.org/legacy/event/nsdi05/tech/full_papers/clark/clark.pdf)
