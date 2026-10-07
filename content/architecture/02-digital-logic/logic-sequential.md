---
id: logic-sequential
title: Latches, flip-flops and state machines
level: intermediate
minutes: 15
summary: How feedback lets a circuit remember, the SR and D latches, edge-triggered flip-flops and their setup, hold and clock-to-Q timing, metastability, and how to design a finite-state machine from a state diagram to gates.
---

Everything so far has been **combinational**: outputs depend only on current inputs. A computer also needs to **remember**: the program counter, the registers, the contents of memory. Circuits whose outputs depend on past inputs as well are **sequential**.

The trick that makes memory possible is **feedback**: wire a gate's output back into its own input. This lesson goes from the simplest feedback loop to the clocked flip-flops and finite-state machines that every processor is built from.

## Two inverters that remember

Connect two inverters in a ring. If the first outputs 1, the second outputs 0, which keeps the first at 1. The opposite state is equally stable. This **bistable** loop stores one bit for as long as it has power, and it is exactly the core of an SRAM cell (next lesson). The only problem is that there is no way to change the bit. The SR latch adds that.

## The SR latch

Replace the inverters with NOR gates so that each gate gets an extra input:

```
       +-------+
R -----|       |
       |  NOR  |o----+----- Q
   +---|       |     |
   |   +-------+     |
   |                 |
   +--------------+  |
                  |  |
   +-----------------+
   |              |
   |   +-------+  |
   +---|       |  |
       |  NOR  |o-+-------- Q'
S -----|       |
       +-------+
```

Each NOR's output feeds the other's input. Recall that a NOR outputs 1 only when both inputs are 0, so a 1 on any input forces its output to 0.

| S | R | Q next | Meaning |
|---|---|---|---|
| 0 | 0 | Q | Hold |
| 1 | 0 | 1 | Set |
| 0 | 1 | 0 | Reset |
| 1 | 1 | 0 (and Q' = 0) | Invalid |

- **Set** (S = 1): the bottom NOR is forced to Q' = 0, so the top NOR sees R = 0 and Q' = 0 and outputs Q = 1.
- **Hold** (S = R = 0): each NOR just inverts the other's output, so the loop keeps its state.
- **S = R = 1** forces both outputs to 0, breaking the rule that Q' is the complement of Q. Worse, if S and R then fall together, the final stored bit can be unpredictable and the latch can become metastable. Designs must never do this.

## The D latch

The SR latch has two control inputs and a forbidden combination. The **D latch** (D for data) fixes both. It has a data input D and an enable E, and internally drives S = D·E and R = D'·E, so the ideal Boolean equations never assert both. Physical implementations still need timing constraints; propagation delays do not disappear.

- When **E = 1**, the latch is **transparent**: Q follows D.
- When **E = 0**, it is **opaque**: Q holds whatever D was when E fell.

Transparency needs deliberate timing design. Latches are useful storage elements and can support time borrowing, but a naive feedback path can race. In a CPU, a register's output feeds logic that eventually feeds back into the same register (think `pc = pc + 4`). If the register is transparent for the whole time the clock is high, a new value can race round the loop and change again within the same clock phase.

## The edge-triggered D flip-flop

The solution is to make storage happen at an **instant**, not over an interval. Put two D latches in series with opposite enables:

```
         +---------+     +---------+
D -------| master  |-----|  slave  |--- Q
         | latch   |     |  latch  |
         | E = CLK'|     | E = CLK |
         +---------+     +---------+
```

- While CLK = 0 the master is transparent and follows D; the slave is closed and holds Q.
- When CLK rises, the master closes, capturing D at that instant, and the slave opens, passing the captured value to Q.
- While CLK = 1 the master is closed, so changes on D cannot reach Q.

The result is a **positive-edge-triggered D flip-flop**: Q takes the value D had at the rising edge of the clock and holds it until the next rising edge. Here is the difference from a latch (enabled while CLK is high) in a timing diagram:

```
event              D   latch Q   FF Q
initial CLK=0      0      0        0
rising edge        0      0        0
D rises, CLK=1     1      1        0
D falls, CLK=1     0      0        0
falling edge       0      0        0
next rising edge   0      0        0
```

The latch passes the short pulse on D because the clock happens to be high. The flip-flop ignores it, because D was 0 at both surrounding edges. In the ideal single-clock model, registers sample at the same edge. Real clock skew, clock-to-Q, setup/hold and wire delays reduce or shift the available budget; synchronous designs can also use carefully timed latches.

## Flip-flop timing

A real flip-flop needs D to be stable for a short window around the edge:

- **Setup time** (t_su): D must be stable this long *before* the edge.
- **Hold time** (t_h): D must stay stable this long *after* the edge.
- **Clock-to-Q** (t_cq): Q changes this long after the edge.

```
CLK    ________/-----------
D      XXX=========XXXXXXXX
          |<su>|<h>|
               |<cq>|
Q      =============XX=====

= stable value, X may change
```

These numbers set the speed of the whole chip. Consider two registers with combinational logic between them:

```
+-----+                    +-----+
| FF1 |--> logic, t_pd --->| FF2 |
+-----+                    +-----+
   ^                          ^
   +----------- CLK ----------+
```

Data leaves FF1 at t_cq after an edge, takes up to t_pd to get through the logic, and must arrive t_su before the *next* edge:

```
T_clk >= t_cq(max) + t_pd(max) + t_su
```

With t_cq = 50 ps, t_pd = 400 ps and t_su = 30 ps, the period must be at least 480 ps, so the clock can run at about 2.08 GHz at most. The slowest such path on the chip is the **critical path**, and it sets the clock rate. (Clock skew, the difference in clock arrival time between FF1 and FF2, shifts this budget: if FF2's clock arrives earlier than FF1's, the logic has that much less time. If it arrives later, setup gets easier but hold, below, gets harder.)

There is a second, sneakier constraint. The *new* value from FF1 must not reach FF2 so fast that it corrupts what FF2 is capturing on the same edge:

```
t_cq(min) + t_pd(min) >= t_h
```

A **hold violation** cannot be fixed by slowing the clock, because the clock period does not appear in it. The fix is to add delay (buffers) to the short path. Static timing analysis tools check both constraints on every path.

## Metastability

What if D changes inside the setup/hold window? This is unavoidable when a signal comes from outside the clock domain: a button, a network chip with its own clock, another core running at a different frequency.

The flip-flop's internal loop can then be caught balanced between 0 and 1, like a ball on the top of a hill. This **metastable** state resolves to a valid 0 or 1 eventually, but the time it takes is unbounded in principle; the probability of still being unresolved falls off exponentially with the time you wait.

A common mitigation for a single-bit level is a two-flip-flop synchroniser, with both stages clocked by the destination clock:

```
async ---> [FF_a] ---> [FF_b] ---> logic
              ^           ^
              +--- CLK ---+
```

FF_a may go metastable. Resolution time is roughly a cycle minus stage, routing and setup overhead; placement matters. The failure rate depends on device parameters, clock frequency and asynchronous transition rate, so stage count must be justified against the required MTBF.

> [!note] Evidence gap
> A generic years-long MTBF is omitted because the required device and timing parameters were unavailable. A two-stage chain reduces risk but does not prove an acceptable failure rate.

A short pulse can be missed entirely; use pulse stretching or an appropriate handshake/toggle protocol when every event must be transferred. A push-button also requires debouncing separately. High-speed or high-reliability designs sometimes use three stages. Multi-bit values need more care (handshakes or asynchronous FIFOs with Gray-coded pointers), because separately synchronised bits can resolve on different cycles.

## Building blocks from flip-flops

- **Register**: n flip-flops sharing one clock. To make it hold its value unless `load` is asserted, put a 2-to-1 mux in front of each D: `D = load ? new : Q`. This avoids naive combinational clock gating. Proper integrated clock-gating cells or dedicated FPGA clock-enable resources can safely save power when used with their timing rules.
- **Shift register**: each flip-flop's Q feeds the next one's D; data moves one place per clock. Used for serial links and delay lines.
- **Counter**: a register plus an incrementer, `Q <= Q + 1`. The program counter is a fancy version.
- **Reset**: a **synchronous** reset only takes effect at a clock edge; an **asynchronous** reset acts immediately but must be released carefully (synchronously) to avoid metastability.

## Finite-state machines

A **finite-state machine** (FSM) is a state register plus combinational logic:

```
         +---------------+
 X ----->|  next-state   |   +-------+
    +--->|     logic     |-->| state |--+
    |    +---------------+   |  reg  |  |
    |                        +-------+  |
    +-----------------------------------+
    |    +---------------+
    +--->| output logic  |----> Z
         +---------------+
```

On each clock edge, the state register loads the next state, computed from the current state and the inputs. There are two kinds:

- **Moore machine**: outputs depend only on state. In a synchronous model, an input affects them after a state update. Combinational decoding of state bits can glitch during transitions as bits arrive at different times; register the output or design a suitable hazard-free encoding when needed. The latency comparison with Mealy depends on when inputs and outputs are sampled.
- **Mealy machine**: outputs depend on the **state and the current inputs**. It can respond in the same cycle and often needs fewer states, but the output can glitch as inputs change, and there is a combinational path from input to output.

### Worked example: detect two 1s in a row

Design a Moore machine with input X that outputs Z = 1 when the last two inputs (sampled at clock edges) were both 1.

**Step 1: states.**

- S0: the last input was 0 (or we just reset). Z = 0.
- S1: the last input was 1, but the one before was not. Z = 0.
- S2: the last two inputs were 1. Z = 1.

```
 X=0                      X=1
 +--+                     +--+
 |  v                     |  v
+-----+  X=1  +-----+ X=1 +-----+
| S0  |------>| S1  |---->| S2  |
| Z=0 |<------| Z=0 |     | Z=1 |
+-----+  X=0  +-----+     +-----+
   ^                         |
   +---------- X=0 ----------+
```

**Step 2: encode the states.** Three states need two bits Q1 Q0: S0 = 00, S1 = 01, S2 = 10. Code 11 is unreachable from the intended reset state under these equations. Treating it as a don't-care assumes that reachability invariant; fault recovery requires an explicit additional requirement.

**Step 3: next-state table.**

```
Q1 Q0 X | N1 N0 | Z
--------+-------+---
 0  0 0 |  0  0 | 0
 0  0 1 |  0  1 | 0
 0  1 0 |  0  0 | 0
 0  1 1 |  1  0 | 0
 1  0 0 |  0  0 | 1
 1  0 1 |  1  0 | 1
 1  1 x |  x  x | x
```

**Step 4: minimise** with K-maps, using the don't-cares:

```
N1 = X·Q1 + X·Q0 = X·(Q1 + Q0)
N0 = X·Q1'·Q0'
Z  = Q1
```

**Step 5: build it**: two D flip-flops whose D inputs are N1 and N0, a few gates, and Z wired straight from Q1. Simulating it in Python confirms the behaviour:

```python
def step(state, x):
    q1, q0 = state
    n1 = x & (q1 | q0)
    n0 = x & (1 - q1) & (1 - q0)
    return (n1, n0)

state = (0, 0)
for x in [1, 1, 1, 0, 1, 1, 0]:
    state = step(state, x)
    print(x, "Z =", state[0])
# Z: 0 1 1 0 0 1 0
```

A Mealy version needs only two states (S0: last input 0, S1: last input 1) with `Z = X` while in S1. With X stable before an edge, the Mealy output can assert before that edge; the Moore state output asserts after the edge sampling the second 1. It does not wait an additional full cycle after that sampling edge.

### State encoding

Binary encoding uses the fewest flip-flops (⌈log2 n⌉ for n states). **One-hot** encoding uses one flip-flop per state, with exactly one set at a time. It needs more flip-flops but its next-state logic is usually simpler and faster, which suits FPGAs, where flip-flops are plentiful. Synthesis tools often re-encode FSMs automatically.

## Key takeaways
- Feedback creates memory. An SR latch holds a bit; S = R = 1 is forbidden for a NOR latch.
- A D latch is transparent while enabled. A D flip-flop (one implementation uses master and slave latches) captures D only at the clock edge, which makes synchronous design possible.
- Setup: `T_clk >= t_cq(max) + t_pd(max) + t_su`. Hold: `t_cq(min) + t_pd(min) >= t_h`. Hold violations cannot be fixed by slowing the clock.
- Asynchronous inputs can cause metastability. Use a validated synchroniser for single-bit levels and an appropriate protocol for pulses or coherent multi-bit transfers; no finite synchroniser eliminates all risk.
- An FSM is a state register plus next-state and output logic. Moore outputs depend only on state; Mealy outputs also depend on inputs.

## Further reading
- [Flip-flop (electronics) — Wikipedia](https://en.wikipedia.org/wiki/Flip-flop_(electronics))
- [Latch (electronics) — Wikipedia](https://en.wikipedia.org/wiki/Latch_(electronics))
- [Metastability (electronics) — Wikipedia](https://en.wikipedia.org/wiki/Metastability_(electronics))
- [Static timing analysis — Wikipedia](https://en.wikipedia.org/wiki/Static_timing_analysis)
- [Finite-state machine — Wikipedia](https://en.wikipedia.org/wiki/Finite-state_machine)
- [Clock domain crossing — Wikipedia](https://en.wikipedia.org/wiki/Clock_domain_crossing)
