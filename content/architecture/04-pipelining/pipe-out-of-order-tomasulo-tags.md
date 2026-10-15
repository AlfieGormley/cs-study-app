---
id: pipe-out-of-order-tomasulo-tags
sourceLesson: pipe-out-of-order
title: Schedule with Tomasulo producer tags
level: advanced
minutes: 4
summary: Follow reservation-station values, waiting tags and result broadcasts through a worked snapshot.
---

The previous renaming unit used a separate physical register file. Tomasulo’s original design instead tracks producers with tags in reservation stations and the register status table. Both distinguish versions, but the data structures and recovery mechanisms are different.

## Tomasulo's algorithm

Robert Tomasulo devised the original scheme for the floating-point unit of the IBM System/360 Model 91 (1967). Its tag-based scheduling and renaming ideas are foundational; modern implementations need not use the original structure.

Three structures:

- **Reservation stations** (RS) sit in front of each functional unit. Each holds one waiting instruction and, for each operand, either its value (V) or the **producer tag** (Q) of the reservation station that will produce it.
- A **register status table** records, for each register, which RS tag will write it next (blank if the register file value is current).
- A **common data bus** (CDB) broadcasts every result as a (tag, value) pair to all reservation stations and the register file at once.

Each instruction goes through:

1. **Issue**: take the next instruction in order, if a matching RS is free. For each source, copy the value from the register file if it is current, or else copy the producing tag. Then set the destination register's status to this RS's tag.
2. **Execute**: when both operands are values, start executing. Independent instructions overtake stalled ones here.
3. **Write result**: broadcast (tag, value) on the CDB. Every RS waiting on that tag grabs the value. The register file is updated only if its status still names this tag.

Tags distinguish producer versions, providing renaming without requiring the separate physical register file used in the preceding example. A reservation station is not literally a physical register.

### A worked snapshot

```
1: L.D   F6, 0(R2)
2: MUL.D F0, F6, F4
3: ADD.D F6, F8, F2
4: SUB.D F2, F6, F4
```

Assume enough reservation stations, ready initial registers and sufficiently long operation latencies for all four to issue before any result broadcasts. This is a schematic floating-point instruction trace, not literal IBM instruction syntax:

| RS | Op | Operand j | Operand k |
|---|---|---|---|
| Load1 | L.D | addr R2+0 | |
| Mult1 | MUL | Q = Load1 | V = F4 |
| Add1 | ADD | V = F8 | V = F2 |
| Add2 | SUB | Q = Add1 | V = F4 |

Register status: F0 ← Mult1, F2 ← Add2, F6 ← Add1.

What happens next:

- **Add1 can start immediately.** It copied F8 and F2 at issue, so it waits for neither the load nor the multiply.
- When **Load1** broadcasts, Mult1 captures the value. But F6's status says Add1, not Load1, so the **register file is not updated**. The load's F6 is now an orphan that only Mult1 needed. That is the WAW hazard with instruction 3, resolved.
- When **Add1** broadcasts, Add2 (the SUB) captures it, and F6 in the register file is updated.
- SUB overwrites F2, which ADD read. That WAR is harmless: ADD copied F2's value into its RS at issue.
- **Mult1** can finish last despite issuing second; exact completion order depends on latencies and resource availability.

### What the original lacked

The Model 91 wrote results to registers as soon as they were computed, out of order, so a fault in an earlier, slower instruction left a state where later instructions had already taken effect. It could produce **imprecise floating-point exceptions**. The original tag-and-broadcast algorithm described here lacks the modern speculative branch-recovery machinery.

## Key takeaways
- Reservation stations hold copied values or tags naming unfinished producers.
- A broadcast wakes matching operands and updates a register only if its status still names that producer.
- Original Tomasulo scheduling is distinct from modern precise retirement and branch recovery.

## Further reading
- [University of Edinburgh: executable HASE Tomasulo model](https://www.icsa.inf.ed.ac.uk/research/groups/hase/models/tomasulo/tomasulo.html)
- [Smith and Pleszkun: precise interrupts (original paper)](https://american.cs.ucdavis.edu/academic/readings/papers/smithpleszkun.pdf)
- [BOOM implementation: rename stage](https://docs.boom-core.org/en/latest/sections/rename-stage.html)

- [Tomasulo: original 1967 paper](https://courses.grainger.illinois.edu/ece511/fa2005/papers/Tomasulo.1967.IBMJRD.pdf)
