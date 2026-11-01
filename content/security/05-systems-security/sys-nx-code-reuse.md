---
id: sys-nx-code-reuse
title: Non-executable pages and existing code
level: intermediate
minutes: 3
sourceLesson: sys-mitigations
summary: NX prevents instruction fetch from a page configured as non-executable.
---

## DEP / NX: data is not code

**DEP/NX** prevents instruction execution from pages marked non-executable. Write and execute permissions are separate: NX alone does not enforce **W^X**, the stronger policy that a page is never writable and executable simultaneously. The table illustrates common permissions, not a guarantee for every mapping.

| Region | Read | Write | Execute |
|---|---|---|---|
| Code (.text) | yes | no | yes |
| Stack | yes | yes | no |
| Heap | yes | yes | no |

An attempt to fetch instructions from a non-executable stack or heap page faults. Whether the process then terminates depends on OS handling. A process can have executable mappings, including code produced by a JIT compiler at run time; enabling DEP does not mean every data allocation is necessarily non-executable.

Attackers responded with **code-reuse** attacks: rather than injecting new code, they redirect control through short snippets of code that already exist in the program and its libraries, which are legitimately executable. The best-known form is **return-oriented programming** (ROP). Code reuse is why DEP alone is not enough, and why the attacker's "know where" step became so important.

> [!analogy] Real-world analogy: a ransom note cut from magazines
> Someone who must not leave handwriting can still write a message by cutting words out of magazines and gluing them in order.
>
> **How it maps:** Handwriting is injected code, which NX blocks by refusing to execute writable data pages. The magazines are the program's own executable code and libraries. Each cut-out word is a ROP gadget, a short instruction sequence ending in `ret`, and the glued order is the list of addresses the attacker writes onto the stack so that each `ret` jumps to the next gadget.
>
> **Where it stops:** The note-writer can see where every word is printed; a ROP attacker must first learn where the code is loaded, which is the job ASLR makes harder. And unlike paper, a CPU can check where each return goes: shadow stacks, covered later, do exactly that.

JIT compilers generate executable code at run time. Their permission transitions and aliases need careful protection; a writable alias of executable storage can undermine the intended restriction. The exact mechanism is platform-specific.

## Key takeaways
- NX prevents instruction fetch from a page configured as non-executable.
- W^X additionally forbids a page being writable and executable at the same time.
- Existing executable instructions and writable aliases require additional protection.

## Further reading
- [Data execution prevention — Microsoft](https://learn.microsoft.com/en-us/windows/win32/memory/data-execution-prevention)
- [Instrumentation options — GCC](https://gcc.gnu.org/onlinedocs/gcc/Instrumentation-Options.html)
