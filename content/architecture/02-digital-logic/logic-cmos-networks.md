---
id: logic-cmos-networks
title: Build CMOS gates from transistor networks
level: basic
minutes: 4
sourceLesson: logic-gates-cmos
summary: Complementary pull-up and pull-down networks implement inverting gates.
---

## Inside the gate: CMOS transistors

A **MOSFET** acts as a voltage-controlled switch between two terminals. The **gate terminal** controls conduction between source and drain through relative terminal voltages. A MOSFET also has a body/bulk terminal, often tied to a supply in this simplified model.

CMOS (complementary metal-oxide-semiconductor) uses two kinds:

| Type | Conducts when gate is | Good at passing |
|---|---|---|
| nMOS | high (1) | a strong 0 |
| pMOS | low (0) | a strong 1 |

The rule that follows: **nMOS transistors connect the output to ground (0), and pMOS transistors connect it to the supply, VDD (1).** An nMOS trying to pass a 1 loses a threshold voltage and delivers a weak, degraded high, and a pMOS passing a 0 has the same problem in reverse.

### The inverter

```
         VDD (1)
          |
       [pMOS] <-- A   on when A = 0
          |
          +---------- Y
          |
       [nMOS] <-- A   on when A = 1
          |
         GND (0)
```

When A = 0 the pMOS is on and the nMOS is off: Y is connected to VDD, so Y = 1. When A = 1 it flips: Y connects to ground, Y = 0. Two transistors, one NOT gate.

Crucially, in either steady state **one transistor is off**, so there is no direct path from VDD to ground. Ideally, a CMOS gate that is not switching draws no current. This is the property that let CMOS win over earlier logic families.

### The NAND gate

The fully complementary static CMOS gates constructed here have a **pull-up network** of pMOS transistors and a **pull-down network** of nMOS transistors, and the two are **duals**: series in one becomes parallel in the other.

```
        VDD          VDD
         |            |
     [pMOS]<-A    [pMOS]<-B
         |            |
         +-----+------+
               |
               +---------- Y
               |
           [nMOS]<-A
               |
           [nMOS]<-B
               |
              GND
```

- The nMOS pair is in **series**: Y is pulled to 0 only when A **and** B are both 1.
- The pMOS pair is in **parallel**: Y is pulled to 1 if A **or** B is 0.

That is NOT (A AND B), the NAND function, in **4 transistors**. The pull-down conducts only for two high inputs. Every other valid input combination enables the pull-up instead.

NOR is the mirror image: pMOS connected in series, nMOS connected in parallel, also 4 transistors.

### Why AND costs more than NAND

Look at the pattern: a rising input turns on an nMOS, which pulls the output *down*. A fully complementary series/parallel stage using uncomplemented control inputs implements an inverting (negative-unate) function. Other CMOS circuit styles and complemented inputs need separate treatment. To get AND you need NAND followed by an inverter: 4 + 2 = **6 transistors**, and two stages of delay.

| Gate | Transistors (static CMOS) |
|---|---|
| NOT | 2 |
| NAND2, NOR2 | 4 |
| AND2, OR2 | 6 |
| NAND3 | 6 |
| XOR2 | circuit-dependent; complemented-input generation also counts |

This is why synthesis tools and standard-cell libraries think in NAND, NOR and AND-OR-invert cells, not in textbook AND and OR.

### Why NAND beats NOR

In conventional silicon design models, nMOS often has greater drive strength than a comparably sized pMOS. Designers commonly widen pMOS devices to balance rise and fall times; the ratio depends on process, device geometry and operating point.

NOR puts its pMOS transistors **in series**, so a 4-input NOR has four slow transistors stacked between VDD and the output. NAND puts the fast nMOS in series instead. In the conventional sizing model, balancing a wide NOR can cost more area and input capacitance than a NAND. Real choices depend on the cell library and load. Deep series stacks increase resistance, so wide functions are often factored into smaller gates; there is no universal four-device cutoff.

## Key takeaways
- Complementary pull-up and pull-down networks implement inverting gates.
- Transistor counts and drive trade-offs depend on the chosen construction.

## Further reading
- [MIT Computation Structures — supporting notes](https://computationstructures.org/notes/cmos/notes.html)
- [Logic gate — Wikipedia](https://en.wikipedia.org/wiki/Logic_gate)
- [CMOS — Wikipedia](https://en.wikipedia.org/wiki/CMOS)
- [NAND logic — Wikipedia](https://en.wikipedia.org/wiki/NAND_logic)
- [Functional completeness — Wikipedia](https://en.wikipedia.org/wiki/Functional_completeness)
- [Processor power dissipation — Wikipedia](https://en.wikipedia.org/wiki/Processor_power_dissipation)
- [Nand2Tetris: build a computer from NAND gates](https://www.nand2tetris.org/)
