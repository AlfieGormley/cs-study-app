---
id: logic-fsm-design
title: Design and simulate a finite-state machine
level: intermediate
minutes: 5
sourceLesson: logic-sequential
summary: Moore outputs depend on state; Mealy outputs also depend on inputs.
---

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

- **Moore machine**: outputs depend only on state. In a synchronous model, an input affects them after a state update. Combinational decoding of state bits can glitch during transitions as bits arrive at different times; register the output or design a suitable glitch-free encoding when needed. The latency comparison with Mealy depends on when inputs and outputs are sampled.
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

**Step 2: encode the states.** Three states need two bits, named Q1 and Q0. Encode S0 as `00`, S1 as `01` and S2 as `10`. Code 11 is unreachable from the intended reset state under these equations. Treating it as a don't-care assumes that reachability invariant; fault recovery requires an explicit additional requirement.

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

```formula essential
N_1 = X·(Q_1 + Q_0)
N_0 = X·Q_1′·Q_0′
Z = Q_1
where
Q_1, Q_0: the current state bits (Q1 and Q0 in the table)
N_1, N_0: the next state bits, loaded at the next clock edge (N1 and N0 in the table)
X: the input
Z: the output
Q_1′, Q_0′: NOT Q_1, NOT Q_0
·: AND: 1 only when both sides are 1
+: OR: 1 when at least one side is 1
In words: A sampled high input enters the detected state if the machine has already seen a high input. From the initial state it enters the one-high state instead. The output is the high state bit.
```

**Step 5: build it**: two D flip-flops whose D inputs are N1 and N0, a few gates, and Z wired straight from Q1. Simulating it in Python confirms the behaviour:

```python
def step(state, x):
    # Decode the current two-bit state.
    q1, q0 = state
    # A second consecutive one enters S2.
    n1 = x & (q1 | q0)
    # Only S0 followed by one enters S1.
    n0 = x & (1 - q1) & (1 - q0)
    return (n1, n0)

state = (0, 0)
for x in [1, 1, 1, 0, 1, 1, 0]:
    # Advance once per sampled input edge.
    state = step(state, x)
    print(x, "Z =", state[0])
# Z: 0 1 1 0 0 1 0
```

A Mealy version needs only two states (S0: last input 0, S1: last input 1). Its output follows the current input in S1 and is low in S0. With X stable before an edge, the Mealy output can assert before that edge; the Moore state output asserts after the edge sampling the second 1. It does not wait an additional full cycle after that sampling edge.

### State encoding

Binary encoding uses the fewest state bits. Each additional bit doubles the number of available codes. Choose enough bits to give each state a distinct code; any spare codes need an explicit policy if fault recovery is required.

**One-hot** encoding uses one flip-flop per state, with exactly one set at a time. It needs more flip-flops but its next-state logic is usually simpler and faster, which suits FPGAs, where flip-flops are plentiful. Synthesis tools often re-encode FSMs automatically.

## Key takeaways
- Moore outputs depend on state; Mealy outputs also depend on inputs.
- State tables, encoding and next-state logic turn a behaviour into hardware.

## Further reading
- [MIT — Finite-state machines](https://computationstructures.org/notes/fsms/notes.html)
- [MIT Computation Structures — supporting notes](https://computationstructures.org/notes/sequential_logic/notes.html)
- [Flip-flop (electronics) — Wikipedia](https://en.wikipedia.org/wiki/Flip-flop_(electronics))
- [Latch (electronics) — Wikipedia](https://en.wikipedia.org/wiki/Latch_(electronics))
- [Metastability (electronics) — Wikipedia](https://en.wikipedia.org/wiki/Metastability_(electronics))
- [Static timing analysis — Wikipedia](https://en.wikipedia.org/wiki/Static_timing_analysis)
- [Finite-state machine — Wikipedia](https://en.wikipedia.org/wiki/Finite-state_machine)
- [Clock domain crossing — Wikipedia](https://en.wikipedia.org/wiki/Clock_domain_crossing)
