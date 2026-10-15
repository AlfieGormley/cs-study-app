---
id: compu-thesis-boundaries
title: Finite computers and different Church–Turing theses
level: intermediate
minutes: 3
summary: A closed fixed finite machine has finitely many complete configurations.
sourceLesson: compu-church-turing
---

## Real computers are finite

A closed deterministic computer with fixed finite RAM, registers, storage and other state has finitely many configurations. External inputs must also be fixed or modelled before state repetition implies a loop. We model it as a TM because its memory is big enough that the finite limit is rarely the interesting constraint, and because the program text does not depend on the memory size. When a program runs out of memory, we treat that as a resource failure, not a change in what the language can express.

## Versions of the thesis

- **The Church–Turing thesis** (above) is about what can be computed *at all*.
- The **physical Church–Turing thesis** claims that any function computable by a *physical* device is TM-computable. Proposed "hypercomputers" (machines that perform infinitely many steps in finite time, or use exact real numbers) appear to require physically unrealistic resources.
- The **extended (strong) Church–Turing thesis** is commonly stated using efficient simulation by a probabilistic classical TM, with only **polynomial** overhead. This one is in doubt. Shor's algorithm factors integers in polynomial time on a machine using the standard quantum circuit model, and no polynomial-time classical factoring algorithm is known.

Machines using the standard quantum circuit model do **not** threaten the original thesis. For the standard effective quantum circuit model, a classical computer can approximate amplitudes and outcome probabilities to a specified accuracy, generally using exponential resources. This assumes effectively specified quantum gates; arbitrary exact real-number oracles are not part of that model. Their possible advantage concerns what is computable efficiently, a question for complexity theory; a general BQP-versus-BPP separation is not known.

## Pitfalls

- **"Turing complete" does not mean "useful" or "fast".** Brainfuck and Rule 110 are complete but hopeless for real work. Completeness is about what is possible, not practical.
- **Finite memory systems are not Turing complete in the strict sense.** All storage must be bounded, including the call stack and external storage. Fixed-width integers and no heap allocation alone do not establish this.
- **The thesis is not a theorem.** You can't prove it; you can cite it to justify replacing "algorithm" with "Turing machine" in a proof.

## Key takeaways

- A closed fixed finite machine has finitely many complete configurations.
- The original thesis concerns computability; the extended thesis concerns efficient simulation.
- Standard effective quantum computation challenges efficiency claims without computing uncomputable functions.

## Further reading

- [The Church–Turing thesis — Stanford Encyclopedia](https://plato.stanford.edu/entries/church-turing/)
- [Sipser: TM variants and the Church–Turing thesis](https://ocw.mit.edu/courses/18-404j-theory-of-computation-fall-2020/resources/mit18_404f20_lec6-1/)
