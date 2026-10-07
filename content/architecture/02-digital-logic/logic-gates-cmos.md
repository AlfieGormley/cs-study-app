---
id: logic-gates-cmos
title: Logic gates and CMOS
level: basic
minutes: 13
summary: The seven standard gates, why NAND and NOR are universal, and how CMOS transistors build a gate, which explains why inverting gates are cheapest and where a chip's power goes.
---

Boolean algebra is the maths. A **logic gate** is a physical device that computes one Boolean operation on voltages. Wire gates together and you can compute any Boolean function. Add memory (lesson 5) and you can build a computer.

Modern chips build gates from **CMOS** transistors, billions of them. Apple's M1, for example, has about 16 billion. This lesson starts with the gates as black boxes, then opens them up to see the transistors, because the transistor level explains facts that otherwise look arbitrary: why NAND is cheaper than AND, why designers avoid wide NOR gates, and why power grows with clock speed.

## The standard gates

Seven gates cover nearly everything. The schematic notation below labels each gate by name:

```
A --+-----+          A --+-----+
    | AND |-- Y          | OR  |-- Y
B --+-----+          B --+-----+

A --[NOT]o-- Y       A --+------+
                         | NAND |o-- Y
                     B --+------+
```

A small circle (`o`) on an output means "inverted". So NAND is AND followed by NOT, and NOR is OR followed by NOT.

```
 A B | AND OR NAND NOR XOR XNOR
-----+--------------------------
 0 0 |  0   0   1   1   0   1
 0 1 |  0   1   1   0   1   0
 1 0 |  0   1   1   0   1   0
 1 1 |  1   1   0   0   0   1
```

NOT (the **inverter**) has one input. A **buffer** is a gate whose output equals its input; it computes nothing, but it boosts a weak signal so it can drive a long wire or many other gates.

## Universal gates

A set of gates is **functionally complete** if it can build every Boolean function. AND, OR and NOT together are complete: the canonical sum of products from lesson 1 needs only those three.

Remarkably, **NAND on its own is complete**. So is NOR. Here is how NAND replaces the others:

```
NOT A   = NAND(A, A)
A AND B = NOT(NAND(A, B))
        = NAND(NAND(A,B), NAND(A,B))
A OR B  = NAND(NOT A, NOT B)
        = NAND(NAND(A,A), NAND(B,B))
```

The OR line is De Morgan in disguise: `(A'·B')' = A + B`.

XOR takes four NAND gates. Wiring diagrams of this get cluttered fast, so here it is as a **netlist**, a list of gates and the named wires between them, which is how real design tools describe circuits:

```
n1 = NAND(A,  B)
n2 = NAND(A,  n1)
n3 = NAND(B,  n1)
Y  = NAND(n2, n3)    # = A XOR B
```

Check one row: A = 1, B = 0. Then n1 = 1, n2 = NAND(1,1) = 0, n3 = NAND(0,1) = 1, Y = NAND(0,1) = 1. Correct.

### Two-level logic in NAND-NAND

The practical payoff: any sum of products converts directly to two layers of NAND. For `Y = AB + CD`:

```
A --+------+
    | NAND |o--+
B --+------+   |   +------+
               +---| NAND |o-- Y
C --+------+   +---|      |
    | NAND |o--+   +------+
D --+------+
```

Why it works: `NAND(NAND(A,B), NAND(C,D)) = ((AB)'·(CD)')' = AB + CD` by De Morgan. Draw the AND-OR circuit, replace every gate with NAND, and the function is unchanged. The inversion bubbles cancel in pairs.

## Inside the gate: CMOS transistors

A **MOSFET** acts as a voltage-controlled switch between two terminals. The **gate** terminal controls conduction between source and drain through relative terminal voltages. A MOSFET also has a body/bulk terminal, often tied to a supply in this simplified model.

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

That is `Y = (AB)'`, NAND, in **4 transistors**. NOR is the mirror image: pMOS in series, nMOS in parallel, also 4 transistors.

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

## Timing and power

### Propagation delay

A gate's output does not change instantly. Its output has to charge or discharge the capacitance of the wires and gate inputs it drives. Propagation delay characterises the input-to-output response under specified thresholds, load, slew, process, voltage and temperature. A timing model may bound the time until a valid output.

> [!note] Evidence gap
> A universal modern-gate delay is omitted because no process, library cell, load or operating corner was supplied to verify the previous ten-picosecond figure.

That sounds negligible until you do the arithmetic. A 3 GHz clock gives each cycle about 333 ps, and the logic between two registers must settle within it. How many gate stages fit depends on cell and wire delays and register overhead; which is why the depth of a circuit (the longest chain of gates, the **critical path**) matters as much as its size.

Delay grows with **fan-out**, the number of gate inputs one output drives, because each adds capacitance. Designers insert buffers to split large loads.

### Where the power goes

Each time a gate's output switches from 0 to 1, it charges its load capacitance from the supply; switching back to 0 dumps that charge to ground. The resulting **dynamic power** is approximately:

```
P_dynamic ≈ α · C · V² · f

α  mean number of 0-to-1 transitions
   per clock cycle
C  switched capacitance
V  supply voltage
f  clock frequency
```

The V² term makes voltage reduction powerful at fixed activity and capacitance, but voltage limits and performance requirements constrain it, and why phones scale voltage and frequency together (DVFS). **Clock gating**, which stops the clock to idle blocks, attacks α.

There is also **static (leakage) power**: real transistors are not perfect switches and leak a little current even when "off". At modern feature sizes, leakage is a significant share of total power, which is one reason the dream of ever-faster clocks ended in the mid-2000s (lesson 7 of the pipelining module covers the power wall).

## Beyond 0 and 1

- **Tri-state buffers** have a third output state, high-impedance (`Z`), which is effectively disconnected. Several tri-state outputs can share one wire, provided at most one drives at a time; when none drives, a pull resistor, keeper or protocol rule may be needed to define the idle level. If two drive opposite values, you get a short circuit and an undefined level.
- **Restoring logic**: the gates in this model restore valid input voltage ranges to valid output ranges within specified noise margins and loading. Excess noise or an input in the undefined region can still cause failure; regeneration is a benefit of digital abstraction, not an unlimited noise guarantee.

## Pitfalls

- **Counting gates instead of transistors or delay.** Equivalent two-level AND-OR and NAND-NAND designs can have the same number of logic boxes but different transistor counts and delays. Compare actual cells, fan-in, loading and wiring.
- **Leaving inputs floating.** An unconnected CMOS input drifts to an undefined voltage and can turn both transistors partly on, wasting current and producing random outputs. Tie unused inputs to VDD or ground.
- **Ignoring fan-out.** One signal driving hundreds of inputs (a clock, a reset, an enable) is slow unless it is buffered into a tree.

## Key takeaways
- The standard gates are AND, OR, NOT, NAND, NOR, XOR and XNOR. NAND alone, or NOR alone, can build any function.
- Any sum of products maps directly to two levels of NAND gates, thanks to De Morgan.
- CMOS uses nMOS pull-down and pMOS pull-up networks that are duals; in steady state there is no path from VDD to ground.
- In the conventional fully complementary construction, NAND2/NOR2 use four transistors; adding an inverter gives six-transistor AND2/OR2. NAND often has a favourable sizing tradeoff, depending on library and load.
- Capacitive switching power is about α·C·V²·f when α counts 0-to-1 transitions per cycle. Short-circuit current during transitions and leakage add other power costs.

## Further reading
- [Logic gate — Wikipedia](https://en.wikipedia.org/wiki/Logic_gate)
- [CMOS — Wikipedia](https://en.wikipedia.org/wiki/CMOS)
- [NAND logic — Wikipedia](https://en.wikipedia.org/wiki/NAND_logic)
- [Functional completeness — Wikipedia](https://en.wikipedia.org/wiki/Functional_completeness)
- [Processor power dissipation — Wikipedia](https://en.wikipedia.org/wiki/Processor_power_dissipation)
- [Nand2Tetris: build a computer from NAND gates](https://www.nand2tetris.org/)
