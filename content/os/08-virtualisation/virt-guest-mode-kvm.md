---
id: virt-guest-mode-kvm
title: Guest CPU modes and the KVM run loop
level: intermediate
minutes: 3
sourceLesson: virt-hardware-assist
summary: Guest ring privilege and virtualisation root/non-root operation are separate dimensions.
---

Earlier units explained x86 failing the Popek–Goldberg test and two clever software workarounds. In 2005–2006 Intel and AMD fixed the problem in silicon. This lesson covers what they added, the remaining bottlenecks (memory translation and I/O) and how modern clouds solve them.

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

The hypervisor starts a guest with `VMLAUNCH`/`VMRESUME` (AMD: `VMRUN`). The guest runs natively until an architecturally required event or an enabled execution control causes a VM exit. The CPU then saves guest state, loads host state and jumps into the hypervisor with an **exit reason**.

### KVM: the loop at the heart of a cloud

On x86 Linux, **KVM** drives VT-x/AMD-V, and a userspace program (QEMU, Firecracker, crosvm, Cloud Hypervisor) handles devices. Each vCPU is a thread running this loop:

```c
for (;;) {
  /* Enter again after a handled exit. */
  if (ioctl(vcpu_fd, KVM_RUN, 0) < 0) {
    if (errno == EINTR) continue;
    fail("KVM_RUN"); /* exits process */
  }
  /* Only exits returned to userspace. */
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

This control-flow fragment was compiled with synthetic KVM API responses to exercise interrupt retry, port I/O, MMIO and halt. It did not run an actual guest VM. To build a complete VMM: initialise and map the KVM run structure, provide handlers and error support, and define a real halt/wakeup policy. Many hardware exits are handled in KVM without userspace return. Userspace exits also include shutdown, internal errors and other events, not only device emulation. Reducing unnecessary transitions can reduce overhead.

## Key takeaways

- Guest ring privilege and virtualisation root/non-root operation are separate dimensions.
- KVM handles many exits internally; a userspace VMM handles only the exits returned through its API.

## Further reading

- [Second Level Address Translation — Wikipedia](https://en.wikipedia.org/wiki/Second_Level_Address_Translation)
- [The KVM API — Linux kernel documentation](https://docs.kernel.org/virt/kvm/api.html)
- [Virtual I/O Device (VIRTIO) Version 1.2 — OASIS](https://docs.oasis-open.org/virtio/virtio/v1.2/virtio-v1.2.html)
- [PCI Express I/O Virtualization Howto — Linux kernel documentation](https://docs.kernel.org/PCI/pci-iov-howto.html)
- [Live Migration of Virtual Machines (NSDI 2005, PDF)](https://www.usenix.org/legacy/event/nsdi05/tech/full_papers/clark/clark.pdf)
