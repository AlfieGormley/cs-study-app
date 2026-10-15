---
id: pipe-branch-prediction-target-and-predictor-families
sourceLesson: pipe-branch-prediction
title: Predict targets and compare predictor families
level: intermediate
minutes: 3
summary: Separate direction, target and return prediction and understand what newer history structures add.
---

Earlier units taught one-bit/two-bit counters, predictor aliasing and gshare’s global history. This unit keeps that direction-prediction context and adds target selection: knowing that a branch is taken does not by itself tell fetch which address to read next.

## Modern predictors

- **Tournament predictors** combine different predictors, such as local and global history, with a chooser trained to select between them.
- **TAGE** (Seznec and Michaud, 2006) combines a base predictor with tagged tables using geometrically increasing history lengths. Long histories can distinguish contexts that short histories merge. Matching and alternate-prediction policies vary with the TAGE design.
- **Perceptron predictors** (Jiménez and Lin, 2001) predict using a learned weighted sum of signed history bits and a bias. A single perceptron has a linear-separability limitation; it cannot represent every Boolean history pattern.

These are predictor families, not a verified inventory of any current commercial CPU. Product-specific implementation claims are omitted because sufficiently reliable documentation was not established here.

## Predicting the target, not just the direction

Direction alone does not supply the next fetch address. An early target prediction can redirect fetch before decoding and executing the branch; exact stages and latencies depend on the design.

- The **branch target buffer** (BTB) is a cache, indexed by PC, of "there is a branch at this address, and last time it went to that address". In the teaching design, IF looks up the BTB in parallel with the instruction cache; real organisations can differ.
- The **return address stack** (RAS) predicts `ret` instructions. Conceptually, recognised calls push return addresses and returns pop them. Real structures have finite capacity and may lose synchronisation; prediction is not guaranteed correct. A last-target BTB does not track nested caller context at the same return instruction; a return stack supplies that context.
- **Indirect branch predictors** handle jumps through registers (virtual method calls, `switch` jump tables, interpreter dispatch) by combining the PC with history to pick among several targets.

> [!warning] Predictors are shared state
> On affected processors, predictor state can allow one security context to influence indirect-branch speculation in another. Spectre variant 2 exploits such mistraining, together with a disclosure mechanism. Sharing and isolation depend on the processor, firmware, operating system and enabled mitigations; this is not a claim that every CPU exposes all predictor state across domains.

## Key takeaways
- TAGE, tournament and perceptron predictors are families rather than a product inventory.
- A taken direction also needs a target for early redirection.
- Return prediction uses call context; predictor isolation depends on the processor and mitigations.

## Further reading
- [Seznec and Michaud: TAGE (original paper)](https://jilp.org/vol8/v8paper1.pdf)
- [Jiménez and Lin: perceptron prediction (original paper)](https://www.cs.utexas.edu/~lin/papers/hpca01.pdf)
- [BOOM implementation: branch prediction](https://docs.boom-core.org/en/latest/sections/branch-prediction/index.html)
- [Spectre: original research paper](https://spectreattack.com/spectre.pdf)
