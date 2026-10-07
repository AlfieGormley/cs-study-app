---
id: virt-hypervisors
title: Virtualisation basics
level: basic
minutes: 11
summary: Why we run operating systems inside other operating systems, type 1 and type 2 hypervisors, trap-and-emulate, the Popek–Goldberg rules, and the binary translation and paravirtualisation tricks x86 needed.
---

An operating system assumes it owns the machine. It expects to run in the CPU's most privileged mode, to load its own page tables, to disable interrupts when it likes and to talk directly to disks and network cards.

**Virtualisation** lets several operating systems believe that at once, on one physical computer. The software that pulls this off is the **hypervisor**, or **virtual machine monitor (VMM)**. Each OS it hosts is a **guest**, running inside a **virtual machine (VM)**.

## Why bother?

- **Consolidation.** Separate lightly loaded physical servers can share one host as VMs, potentially reducing hardware, power and space when capacity and isolation requirements permit.
- **Isolation.** A guest kernel panic is normally confined to that VM. Hypervisor/device-model vulnerabilities, shared resources and host failures can still affect other guests.
- **Encapsulation.** A VM has disk, memory, CPU and virtual-device state. Supported configurations can snapshot or migrate that state; external services, passthrough devices and destination compatibility can constrain this.
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

## The core trick: trap-and-emulate

The obvious way to virtualise would be to *interpret* every guest instruction in software. That works (it is what an emulator like Bochs does) but its overhead depends on the emulator and workload.

The insight of the 1960s IBM mainframe VMs was that **most instructions are harmless**. An `add` or a `load` in the guest does exactly what it would do on real hardware, so let it run directly on the CPU at full speed. Only a few instructions touch global machine state, and those need the hypervisor.

So the hypervisor runs the guest kernel **deprivileged**, in user mode (or a less privileged ring). Now:

1. Ordinary instructions run natively.
2. When the guest kernel executes a **privileged instruction** (load a page table base, disable interrupts, halt), the CPU refuses, because it is not in kernel mode, and **traps** to the most privileged code: the hypervisor.
3. The hypervisor **emulates** the instruction against the guest's *virtual* CPU state (for example, it records "this vCPU has interrupts disabled") and resumes the guest at the next instruction.

```
guest kernel    hypervisor
------------    ----------
 add  r1,r2     (never sees it)
 cli   ---trap--> vcpu.if = 0
       <-resume-- skip insn
 mov  r3,[x]    (never sees it)
```

Here is the idea as a toy in Python:

```python
PRIV = {"cli", "sti"}

class Trap(Exception):
    pass

def cpu_exec(insn, user_mode):
    if insn in PRIV and user_mode:
        raise Trap(insn)
    return "ran natively"

class VCPU:
    def __init__(self):
        self.interrupts = True

def run_guest(code, vcpu):
    for insn in code:
        try:
            cpu_exec(insn, user_mode=True)
        except Trap as t:
            emulate(t.args[0], vcpu)

def emulate(insn, vcpu):
    if insn == "cli":
        vcpu.interrupts = False
    elif insn == "sti":
        vcpu.interrupts = True
```

The guest never touches the real interrupt flag. It only changes its virtual copy, which the hypervisor consults when deciding whether to deliver a virtual interrupt.

## The Popek–Goldberg requirements

In 1974 Gerald Popek and Robert Goldberg formalised when trap-and-emulate works. A VMM must provide three properties:

- **Equivalence (fidelity).** A program behaves the same in the VM as on real hardware, apart from timing and resource availability.
- **Resource control (safety).** The VMM is in complete control of the real resources; a guest cannot grab memory or devices it was not given.
- **Efficiency.** The vast majority of instructions run directly on the hardware, without VMM intervention.

They then split instructions into two groups:

- **Privileged**: traps if executed in user mode.
- **Sensitive**: reads or changes machine configuration (control-sensitive), or behaves differently depending on the mode or location it runs in (behaviour-sensitive).

Their theorem gives a **sufficient condition**, within its formal machine model: a VMM can be constructed if every sensitive instruction is privileged. Then every instruction the VMM needs to see is guaranteed to trap.

> [!warning] x86 failed the test
> Robin and Irvine's 2000 Pentium analysis identified 17 instructions violating its trap-based virtualisation requirement. The infamous one is `POPF`. In kernel mode it can change the interrupt flag. In the conventional protected-mode case with CPL greater than IOPL (excluding virtual-8086 complications), it leaves IF unchanged without trapping merely because of that attempted change. A deprivileged guest kernel that runs `POPF` to re-enable interrupts gets no error and no trap; the hypervisor never finds out. Others, like `SGDT` and `SIDT`, let user code read where the *real* descriptor tables are, revealing the hypervisor.

Because some instructions never trapped, pure trap-and-emulate on x86 was impossible. Two important software approaches made x86 virtualisation work anyway.

## Workaround 1: binary translation

VMware's 1999 product scanned guest **kernel** code just before running it, a basic block at a time, and rewrote it into a **translation cache**:

- Most instructions are copied unchanged ("identical" translation).
- Problem instructions like `POPF` are replaced with short sequences that call into the VMM or update the virtual CPU directly.
- Translated blocks are cached and chained together, so hot kernel code is translated once and reused.

Guest **user** code normally ran directly at its expected privilege level, with the VMM controlling memory and handling traps as needed. This avoids translating the application instruction stream; it does not imply every observable machine detail or timing is identical.

Binary translation needs no changes to the guest, so it runs unmodified Windows. It is complex, though: self-modifying code, precise exceptions and translating indirect jumps are all fiddly. Surprisingly, it was fast. A 2006 VMware paper (Adams and Agesen) found the first generation of hardware support was often *slower* than mature binary translation, because hardware traps were so expensive.

## Workaround 2: paravirtualisation

The **Xen** project (Cambridge, 2003) took a different route: if the guest is trouble, change the guest. In **paravirtualisation**, the guest kernel is modified to know it is virtualised:

- Instead of executing sensitive instructions, it makes explicit **hypercalls**, the VM equivalent of system calls.
- Instead of loading its own page tables, it asks Xen to validate and install updates, often batched into one hypercall.
- Instead of emulated hardware devices, it uses simple **split drivers**: a front end in the guest passes requests through shared memory rings to a back end in a privileged domain.

```
 guest kernel             Xen
 ------------             ---
 hypercall(mmu_update,
   [pte1, pte2, pte3]) --> validate, apply
                      <--  return
```

The 2003 Xen paper reported low overhead for its evaluated workloads. Kernel adaptation was required; its Windows XP port was incomplete but already ran some user-space programs. Unmodified Windows was not supported by that PV interface.

## Where things stand today

Since 2005–2006, Intel VT-x and AMD-V have made x86 satisfy the spirit of Popek–Goldberg in hardware (next lesson). Binary translation is mostly gone from x86 servers.

Paravirtualisation survived in a different form. Instead of rewriting the whole kernel, modern guests run unmodified on hardware support but use **paravirtual drivers** (virtio, Xen PV drivers, Hyper-V's VMBus), paravirtual clocks and paravirtual spinlocks. Emulating a real network card register by register is slow; a driver that knows it is talking to a hypervisor is fast.

| Technique | Guest changes? | Main cost |
|---|---|---|
| Interpretation | None | Per-instruction software work |
| Trap-and-emulate | None | Needs a virtualisable CPU |
| Binary translation | None | Complexity |
| Paravirtualisation | Kernel adapted | Porting and maintenance |
| Hardware assist | None | Exit cost |

## Pitfalls and misconceptions

- **"VMs are slow."** CPU-bound code can approach native speed, but there is no universal overhead percentage. The costs show up in I/O, in memory-heavy workloads (address translation) and in anything that causes many exits.
- **Timing is not virtualised perfectly.** Popek and Goldberg exempted timing from equivalence on purpose. A guest can detect it is virtualised by timing instructions, which malware uses to hide from sandboxes.
- **Overcommit.** Hypervisors can promise more vCPUs or memory than exist. Overcommit can improve utilisation but is not required for consolidation. Contention can produce noisy-neighbour effects and steal time: reported periods when a vCPU was runnable but not scheduled.

## Key takeaways

- A hypervisor multiplexes one machine between guest OSes, each of which believes it owns the hardware.
- Type 1 runs on hardware (ESXi, Xen, Hyper-V, effectively KVM); type 2 runs on a host OS (VirtualBox, Workstation).
- Trap-and-emulate runs guest code natively and lets privileged instructions trap to the hypervisor.
- Popek–Goldberg gives a sufficient virtualisability condition in its model. Classic x86 had sensitive instructions that did not reliably trap (`POPF`, `SGDT`), obstructing simple trap-and-emulate.
- VMware's binary translation and Xen's paravirtualisation worked around x86 until hardware support arrived; paravirtual *drivers* are still everywhere.

> [!note] Evidence gaps
> No reproducible benchmark supports a universal VM overhead, interpretation slowdown or historical server-utilisation percentage here, so those figures are omitted. Snapshot/migration support and isolation depend on the actual platform and configuration.

## Further reading

- [Formal requirements — Popek and Goldberg (1974, PDF)](https://www.cs.columbia.edu/~cdall/candidacy/pdf/Popek.pdf)
- [Software and hardware virtualisation — Adams and Agesen (2006, PDF)](https://iitd-plos.github.io/col718/ref/asplos235_adams.pdf)
- [Virtual Machine Monitors — OSTEP appendix (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/vmm-intro.pdf)
- [Popek and Goldberg virtualization requirements — Wikipedia](https://en.wikipedia.org/wiki/Popek_and_Goldberg_virtualization_requirements)
- [Xen and the Art of Virtualization (SOSP 2003, PDF)](https://www.cl.cam.ac.uk/research/srg/netos/papers/2003-xensosp.pdf)
- [Hypervisor — Wikipedia](https://en.wikipedia.org/wiki/Hypervisor)
- [x86 virtualization — Wikipedia](https://en.wikipedia.org/wiki/X86_virtualization)
