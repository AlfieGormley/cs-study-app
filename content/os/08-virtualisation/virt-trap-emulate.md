---
id: virt-trap-emulate
title: Trap-and-emulate and virtual interrupt state
level: basic
minutes: 3
sourceLesson: virt-hypervisors
summary: Run ordinary instructions directly and intercept privileged operations.
---

This unit focuses on trap-and-emulate and virtual interrupt state. It builds on the earlier virtualisation units in this module.

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
    # Refuse privileged guest instructions.
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
            # Emulate, then resume.
            emulate(t.args[0], vcpu)

def emulate(insn, vcpu):
    # Only change the virtual flag.
    if insn == "cli":
        vcpu.interrupts = False
    elif insn == "sti":
        vcpu.interrupts = True
```

The guest never touches the real interrupt flag. It only changes its virtual copy, which the hypervisor consults when deciding whether to deliver a virtual interrupt.

## Key takeaways

- Run ordinary instructions directly and intercept privileged operations.
- Emulation updates virtual guest state rather than the physical interrupt flag.

## Further reading

- [Formal requirements — Popek and Goldberg (1974, PDF)](https://www.cs.columbia.edu/~cdall/candidacy/pdf/Popek.pdf)
- [Software and hardware virtualisation — Adams and Agesen (2006, PDF)](https://iitd-plos.github.io/col718/ref/asplos235_adams.pdf)
- [Virtual Machine Monitors — OSTEP appendix (PDF)](https://pages.cs.wisc.edu/~remzi/OSTEP/vmm-intro.pdf)
- [Popek and Goldberg virtualization requirements — Wikipedia](https://en.wikipedia.org/wiki/Popek_and_Goldberg_virtualization_requirements)
- [Xen and the Art of Virtualization (SOSP 2003, PDF)](https://www.cl.cam.ac.uk/research/srg/netos/papers/2003-xensosp.pdf)
- [Hypervisor — Wikipedia](https://en.wikipedia.org/wiki/Hypervisor)
- [x86 virtualization — Wikipedia](https://en.wikipedia.org/wiki/X86_virtualization)
