---
id: virt-vm-purpose-types
title: Why VMs exist and where hypervisors run
level: basic
minutes: 3
sourceLesson: virt-hypervisors
summary: A VM gives a guest its own virtual hardware while a hypervisor retains resource control.
---

An operating system assumes it owns the machine. It expects to run in the CPU's most privileged mode, to load its own page tables, to disable interrupts when it likes and to talk directly to disks and network cards.

**Virtualisation** lets several operating systems believe that at once, on one physical computer. The software that pulls this off is the **hypervisor**, or **virtual machine monitor (VMM)**. Each OS it hosts is a **guest operating system**, running inside a **virtual machine (VM)**.

## Why bother?

- **Server consolidation.** Separate lightly loaded physical servers can share one host as VMs, potentially reducing hardware, power and space when capacity and isolation requirements permit.
- **Isolation.** A guest kernel panic is normally confined to that VM. Hypervisor/device-model vulnerabilities, shared resources and host failures can still affect other guests.
- **Encapsulation.** A VM has disk, memory, CPU and virtual-device state. Supported configurations can snapshot or live-migrate that state; external services, passthrough devices and destination compatibility can constrain this.
- **Compatibility.** Run Windows on a Linux host, or a 2008-era OS that would never boot on today's hardware.
- **The cloud.** Cloud virtual-machine offerings use hypervisors to share hardware. Bare-metal offerings such as EC2 metal instances are an exception; cloud provisioning itself does not require a guest hypervisor.

## Type 1 and type 2 hypervisors

The classic split is about what the hypervisor runs on.

```
 Type 1 (bare metal)    Type 2 (hosted)
+-------+-------+      +-------+-------+
|Guest A|Guest B|      |Guest A|Guest B|
+-------+-------+      +-------+-------+
|  Hypervisor   |      | Hypervisor app|
+---------------+      +---------------+
|   Hardware    |      |   Host OS     |
+---------------+      +---------------+
                       |   Hardware    |
                       +---------------+
```

| | Type 1 | Type 2 |
|---|---|---|
| Runs on | Hardware | A host OS |
| Examples | ESXi, Xen, Hyper-V | VirtualBox, VMware Workstation, Parallels |
| Used for | Servers, cloud | Desktops, dev |
| Overhead | Implementation/workload dependent | Implementation/workload dependent |

Real systems blur the line. **KVM** is a Linux kernel module that turns Linux itself into a hypervisor: a userspace VMM commonly represents each VM as a process with vCPU threads, while KVM provides kernel virtualisation support. It is commonly classified as type 1. **Hyper-V** looks hosted (you install Windows first) but actually slides underneath Windows, which then runs as a privileged guest. The labels matter less than the question "who controls the hardware?"

## Key takeaways

- A VM gives a guest its own virtual hardware while a hypervisor retains resource control.
- The type 1/type 2 distinction describes placement; actual overhead depends on implementation and workload.

## Further reading

- [Formal requirements — Popek and Goldberg (1974, PDF)](https://www.cs.columbia.edu/~cdall/candidacy/pdf/Popek.pdf)
- [Software and hardware virtualisation — Adams and Agesen (2006, PDF)](https://iitd-plos.github.io/col718/ref/asplos235_adams.pdf)
- [Virtual Machine Monitors — OSTEP appendix (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/vmm-intro.pdf)
- [Popek and Goldberg virtualization requirements — Wikipedia](https://en.wikipedia.org/wiki/Popek_and_Goldberg_virtualization_requirements)
- [Xen and the Art of Virtualization (SOSP 2003, PDF)](https://www.cl.cam.ac.uk/research/srg/netos/papers/2003-xensosp.pdf)
- [Hypervisor — Wikipedia](https://en.wikipedia.org/wiki/Hypervisor)
- [x86 virtualization — Wikipedia](https://en.wikipedia.org/wiki/X86_virtualization)
