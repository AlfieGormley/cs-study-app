---
id: pipe-branch-prediction-global-history
sourceLesson: pipe-branch-prediction
title: Use global history with gshare
level: intermediate
minutes: 4
summary: Mix branch address bits with recent outcomes to distinguish correlated contexts.
---

The preceding unit’s two-bit counter uses one state to predict one branch. Here, recent history selects among counters. The executable model observes outcomes in order; it is an algorithm demonstration, not a cycle-accurate predictor in a current commercial CPU.

## Correlation: using global history

A dedicated two-bit counter without a history-based index learns only from the outcomes sent to that counter. But branches are often correlated with each other:

The following is source-level pseudocode; assume x and y stay unchanged. Compiler lowering may introduce, remove or invert machine branches.

```c
// Schematic conditions, not a full program.
if (x == 0) a = 1;   // branch B1
if (y == 0) b = 1;   // branch B2
if (x == 0 && y == 0) ...  // B3
```

The third condition is determined by the first two conditions. When corresponding machine branches and relevant history are available, this provides a learnable correlation. A predictor that knows the last few outcomes of *all* branches can learn this.

A **global history register** (GHR) is a shift register holding the outcomes of the most recent branches (1 = taken). The **gshare** predictor (McFarling, 1993) XORs the GHR with the branch's PC to index a table of 2-bit counters:

```formula
i = (PC ⊕ GHR) mod 2^h
i = 1011₂ ⊕ 0110₂ = 1101₂ = 13
where
i: the index of the 2-bit counter to use, from 0 to 2^h − 1
PC: the program counter: the address of the branch instruction
GHR: the global history register: the last h branch outcomes, one bit each (1 = taken)
⊕: XOR (exclusive or), bit by bit: a result bit is 1 when exactly one of the two input bits is 1
mod: the remainder after division; mod 2^h keeps only the low h bits
h: the number of history bits, which sets the table size to 2^h counters; 4 in the example (16 counters)
₂: the number is written in binary (base 2)
In words: gshare mixes the branch's address with the recent history of all branches, so the same branch uses a different counter in each recent context.
```

In the example, a branch whose low PC bits are 1011 sees history 0110 and uses counter 13. The same branch now gets a different counter for each recent history, so it can learn patterns.

For the following single-branch model, pass Boolean outcomes and an integer PC; it uses the low PC bits directly, without modelling instruction alignment or speculative history recovery. A pattern that defeats a plain 2-bit saturating counter is strictly alternating outcomes, T N T N:

```python
def gshare(outcomes, pc=0x40, hbits=4):
    if (type(hbits) is not int
            or not 1 <= hbits <= 16):
        raise ValueError("bad hbits")
    size = 1 << hbits
    # Start every counter weakly not taken.
    table = [1] * size     # 2-bit counters
    hist, miss = 0, 0
    for taken in outcomes:
        # Mix address with recent outcomes.
        i = (pc ^ hist) % size
        if (table[i] >= 2) != taken:
            miss += 1
        if taken:
            table[i] = min(table[i] + 1, 3)
        else:
            table[i] = max(table[i] - 1, 0)
        # Keep just the last hbits outcomes.
        hist = ((hist << 1) | taken) % size
    return miss

alt = [True, False] * 500
# Output counts three warm-up misses.
print(gshare(alt))   # 3
```

Starting weakly not-taken, a lone 2-bit saturating counter mispredicts **all 1,000** of these (it bounces between the two weak states). gshare, after a 3-miss warm-up, gets every one right, because "last outcome was T" and "last outcome was N" select different counters.

The same gshare with only 4 bits of history produces 108 misses in the 1,000-outcome nine-taken-then-exit loop from the preceding counter unit (10.8%): it can't see far enough back to count to 9. That is the motivation for long histories.

## Key takeaways
- Global history carries context from recent branch outcomes.
- Gshare mixes that history with a branch address to select a counter.
- The trace model uses raw low PC bits and omits alignment and speculative history repair.

## Further reading
- [McFarling: Combining Branch Predictors (original report)](https://shiftleft.com/mirrors/www.hpl.hp.com/techreports/Compaq-DEC/WRL-TN-36.pdf)
- [BOOM implementation: branch prediction](https://docs.boom-core.org/en/latest/sections/branch-prediction/index.html)
