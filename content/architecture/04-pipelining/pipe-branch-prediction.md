---
id: pipe-branch-prediction
title: Branch prediction
level: intermediate
minutes: 14
summary: How CPUs guess the direction and target of branches before they are executed, from 2-bit counters to gshare and TAGE, what a misprediction costs, and how to write code that predicts well.
---

A processor can fetch and execute instructions beyond a branch before its direction and target are known. If its prediction is wrong, it must discard younger wrong-path work and redirect execution. How much work is lost depends on the processor and when the branch resolves.

> [!note] Evidence limits
> Universal branch frequencies, prediction accuracies, pipeline depths and product-specific predictor details are omitted: they need a named workload and reliable documentation or measurements. The numerical examples below are explicit teaching models.

## What a misprediction costs

In an additive model with a fixed average recovery penalty and no overlap with other counted stalls, mispredictions add this many cycles to every instruction on average:

```formula
CPI_br = F_br × m × c_mis
m = 1 − A
where
CPI_br: the extra cycles per instruction caused by branch mispredictions
F_br: the branch fraction: the share of executed instructions that are branches, between 0 and 1
m: the misprediction rate: the share of branches predicted wrongly, between 0 and 1
A: the predictor's accuracy: the share of branches predicted correctly, between 0 and 1
c_mis: the misprediction penalty: the cycles lost recovering from each wrong prediction
In words: only mispredicted branches cost anything, so the extra CPI is how often branches occur, times how often they are guessed wrong, times what each wrong guess costs.
```

### Why 95% isn't good enough

Assume unchanged retired instruction count and clock frequency, with additive penalties. 20% of instructions are branches, the predictor is 95% accurate, and the penalty is 15 cycles. The core is 4-wide, with an ideal CPI of 0.25 when every prediction is right:

```formula
CPI_br = 0.2 × (1 − 0.95) × 15 = 0.15
CPI = CPI_base + CPI_br
CPI = 0.25 + 0.15 = 0.40
S = CPI / CPI_base = 0.40 / 0.25 = 1.6
where
CPI_br: the extra cycles per instruction from mispredictions
CPI_base: the CPI with perfect prediction, 0.25 for this 4-wide core (it can finish up to 4 instructions per cycle)
CPI: the actual average cycles per instruction
S: the slowdown factor relative to perfect prediction; with the same instruction count and clock, time is proportional to CPI
In words: 5% of branches being wrong adds 0.15 cycles to every instruction, which makes this core 1.6 times slower than with perfect prediction.
```

The program runs **1.6× slower** than with perfect prediction. Getting to 98% accuracy brings the extra CPI down to 0.2 × 0.02 × 15 = 0.06.

Lower base CPI makes a given additional CPI more significant. Width and pipeline organisation can affect recovery, but neither alone determines a universal penalty or area cost.

## Static prediction

The simplest predictors use fixed rules with no history:

- **Always not taken**: just keep fetching sequentially. Simple; it misses each taken iteration of a loop-back branch.
- **Backward taken, forward not taken (BTFN)**: a branch that jumps backwards is probably a loop, so predict taken; a forward branch is probably an `if`, so predict not taken. This is a heuristic, not a guarantee about source-level control flow.

Compilers help by laying out code so the likely path falls through. GCC and Clang's `__builtin_expect`, C++20's `[[likely]]` and `[[unlikely]]`, and profile-guided optimisation can inform these layout and optimisation decisions; they do not guarantee a particular hardware predictor action.

## Dynamic prediction: learning from history

### The branch history table

A **branch history table** (BHT, or pattern history table) is a small array indexed by the low bits of the branch's address (PC). Each entry remembers how that branch has behaved.

A **1-bit** entry stores the last outcome and predicts it will happen again. It has a flaw with loops. Consider a loop branch that is taken 9 times and then falls through, with the loop itself run repeatedly:

```
T T T T T T T T T N | T T T ...
                  ^   ^
          mispredict   mispredict again
```

The exit mispredicts, then flips the bit to N, so the first iteration of the *next* run mispredicts too: 2 misses per 10, or 80% accuracy.

### The 2-bit saturating counter

A **2-bit saturating counter** adds hysteresis: a strongly biased state needs two consecutive opposite outcomes to reverse its prediction. From a weak state, one opposite outcome is enough:

```
state  meaning             predict
  3    strongly taken      T
  2    weakly taken        T
  1    weakly not taken    N
  0    strongly not taken  N
```

Taken increments the counter (stopping at 3), not taken decrements it (stopping at 0), and the top bit is the prediction:

```formula
c′ = min(c + 1, 3)   if o = T
c′ = max(c − 1, 0)   if o = N
d = T   if c ≥ 2, else N
where
c: the current state of the counter, a whole number from 0 to 3 (two bits)
c′: the state of the counter after the branch outcome is known
o: the branch's actual outcome
d: the direction the counter predicts before the outcome is known
T: taken: the branch jumps to its target
N: not taken: execution falls through to the next instruction
min: the smaller of the two values, which stops the count at 3
max: the larger of the two values, which stops the count at 0
≥: is greater than or equal to
In words: count up on taken and down on not taken, never leaving 0 to 3, and predict taken whenever the count is in the top half.
```

A single loop exit moves "strongly taken" to "weakly taken", which still predicts taken next time. Now there is only 1 miss per 10.

```python
def two_bit(outcomes, start=1):
    if (type(start) is not int
            or not 0 <= start <= 3):
        raise ValueError("bad start")
    c, miss = start, 0     # 0..3; >=2 = T
    for taken in outcomes:
        if (c >= 2) != taken:
            miss += 1
        c = min(c + 1, 3) if taken \
            else max(c - 1, 0)
    return miss

def one_bit(outcomes, start=False):
    last, miss = start, 0
    for taken in outcomes:
        if last != taken:
            miss += 1
        last = taken
    return miss

# loop branch: taken 9 times, then exits
loop = ([True] * 9 + [False]) * 100
print(one_bit(loop), two_bit(loop))
# 200 101
```

One-bit: 200 misses in 1,000 (80%). Two-bit: 101 (about 90%; the extra 1 is the first warm-up miss).

### Predictor aliasing

The table is indexed by only some PC bits, so two different branches can share an entry and corrupt each other's counters. This is **predictor aliasing**. More capacity can reduce interference. Tags help distinguish entries, but finite capacity and partial tags do not eliminate every collision or replacement effect.

## Correlation: using global history

A 2-bit saturating counter only sees one branch's own past. But branches are often correlated with each other:

The following is source-level pseudocode; assume x and y stay unchanged. Compiler lowering may introduce, remove or invert machine branches.

```text
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
    table = [1] * size     # 2-bit counters
    hist, miss = 0, 0
    for taken in outcomes:
        i = (pc ^ hist) % size
        if (table[i] >= 2) != taken:
            miss += 1
        if taken:
            table[i] = min(table[i] + 1, 3)
        else:
            table[i] = max(table[i] - 1, 0)
        hist = ((hist << 1) | taken) % size
    return miss

alt = [True, False] * 500
print(gshare(alt))   # 3
```

Starting weakly not-taken, a lone 2-bit saturating counter mispredicts **all 1,000** of these (it bounces between the two weak states). gshare, after a 3-miss warm-up, gets every one right, because "last outcome was T" and "last outcome was N" select different counters.

The same gshare with only 4 bits of history produces 108 misses in the 1,000-outcome trace above (10.8%) on the 9-taken loop: it can't see far enough back to count to 9. That is the motivation for long histories.

## Modern predictors

- **Tournament predictors** combine different predictors, such as local and global history, with a chooser trained to select between them.
- **TAGE** (Seznec and Michaud, 2006) combines a base predictor with tagged tables using geometrically increasing history lengths. Long histories can distinguish contexts that short histories merge. Matching and alternate-prediction policies vary with the TAGE design.
- **Perceptron predictors** (Jiménez and Lin, 2001) predict using a learned weighted sum of signed history bits and a bias. A single perceptron has a linear-separability limitation; it cannot represent every Boolean history pattern.

These are predictor families, not a verified inventory of any current commercial CPU. Product-specific implementation claims are omitted because sufficiently reliable documentation was not established here.

## Predicting the target, not just the direction

Direction alone does not supply the next fetch address. An early target prediction can redirect fetch before decoding and executing the branch; exact stages and latencies depend on the design.

- The **branch target buffer** (BTB) is a cache, indexed by PC, of "there is a branch at this address, and last time it went to that address". In the teaching design, IF looks up the BTB in parallel with the instruction cache; real organisations can differ.
- The **return address stack** (RAS) predicts `ret` instructions. Conceptually, recognised calls push return addresses and returns pop them. Real structures have finite capacity and may lose synchronisation; prediction is not guaranteed correct. The BTB can't do this well, because one function returns to many callers.
- **Indirect branch predictors** handle jumps through registers (virtual method calls, `switch` jump tables, interpreter dispatch) by combining the PC with history to pick among several targets.

> [!warning] Predictors are shared state
> On affected processors, predictor state can allow one security context to influence indirect-branch speculation in another. Spectre variant 2 exploits such mistraining, together with a disclosure mechanism. Sharing and isolation depend on the processor, firmware, operating system and enabled mitigations; this is not a claim that every CPU exposes all predictor state across domains.

## Writing code that predicts well

### Data-dependent branches

Illustrative C loop body: assume `data` is a valid array of `uint8_t`, `n` is its length (`size_t`), and `sum` is `uint64_t` initially zero. Include `<stdint.h>` and `<stddef.h>`. Unsigned accumulation is defined modulo 2^64:

```c
for (size_t i = 0; i < n; i++)
    if (data[i] >= 128)
        sum += data[i];
```

If byte values are independently uniform over 0–255 and unpredictable from available history, the condition is a fair coin flip. If a machine branch remains, history prediction has expected accuracy 50%. Sorting the same values produces long runs of false then true conditions, which simple predictors learn. This can reduce misprediction cost, but supplies no guaranteed speedup: inspect the generated code and exclude or amortise sorting cost. The compiler may remove the branch in both versions.

### Branchless code

For an unpredictable branch, consider a branchless implementation and measure it. A conditional move (x86 `cmov`, ARM `csel`) selects a value without a jump:

```c
sum += (data[i] >= 128) ? data[i] : 0;
```

Compilers often emit `cmov` for this, and at higher optimisation levels may vectorise the loop and remove the branch entirely, which is why naive benchmarks of this effect are often misleading.

> [!tip] Branchless is not always faster
> Branchless selection can introduce data dependencies or work on both alternatives, whereas a predicted branch permits speculative execution. Either source form may compile to the same machine code. Compare generated code and measure the actual workload; on supported Linux systems, `perf stat -e branches,branch-misses` provides useful counters, subject to hardware availability and permissions.

### Other habits

- Keep hot loops simple, with predictable trip counts.
- In interpreters, "threaded" dispatch (a separate indirect jump per opcode handler) can give a PC-indexed indirect predictor more context than one central `switch`, if the compiler preserves separate dispatch sites. This does not guarantee a speedup.
- Sort or partition data by the condition you'll branch on, if changing order preserves semantics and repeated processing amortises the rearrangement cost.

## Key takeaways
- Additive branch CPI estimates require explicit penalty and overlap assumptions.
- Two-bit counters tolerate isolated opposite outcomes from strong states; global history can distinguish patterns they miss.
- Direction and target prediction solve different parts of speculative fetching.
- Branchless source does not guarantee branchless machine code or faster execution: inspect and measure.
- Cross-domain predictor influence is a security issue on affected systems; isolation and mitigations are implementation-specific.

## Further reading
- [Branch predictor — Wikipedia](https://en.wikipedia.org/wiki/Branch_predictor)
- [Branch prediction, by Dan Luu](https://danluu.com/branch-prediction/)
- [A case for (partially) tagged geometric history length branch prediction (TAGE), JILP](https://jilp.org/vol8/v8paper1.pdf)
- [Dynamic branch prediction with perceptrons (Jiménez and Lin)](https://www.cs.utexas.edu/~lin/papers/hpca01.pdf)
- [Branch target predictor — Wikipedia](https://en.wikipedia.org/wiki/Branch_target_predictor)
- [The microarchitecture of Intel, AMD and VIA CPUs, by Agner Fog (PDF)](https://www.agner.org/optimize/microarchitecture.pdf)

- [Combining Branch Predictors (McFarling, original DEC technical report; mirror)](https://shiftleft.com/mirrors/www.hpl.hp.com/techreports/Compaq-DEC/WRL-TN-36.pdf)
- [Spectre attacks: exploiting speculative execution (original paper)](https://spectreattack.com/spectre.pdf)
