---
id: compu-language-restrictions
title: Universal constructions and deliberate restrictions
level: intermediate
minutes: 3
summary: Universality claims idealise resource limits away and require specific simulation constructions.
sourceLesson: compu-church-turing
---

## Universal and restricted languages

### Accidental Turing completeness

Because the bar is so low, systems keep crossing it by accident:

- **C++ templates** can express universal computation when compiler resource limits and limits on how deeply templates nest are idealised away.
- **x86-style `mov` operations**, plus a final unconditional jump back to the start, simulate a TM in Stephen Dolan's 2013 construction. It assumes unbounded addressable memory; a finite straight-line sequence of `mov` instructions alone is not universal.
- **SQL with recursive CTEs and suitable data operations** can encode TM simulation when storage and value sizes are unbounded. PostgreSQL `WITH RECURSIVE` supplies iteration, but the keyword alone is not a proof and a real database has finite resource/type limits.
- **Magic: The Gathering** has a card combination that simulates a universal TM (Churchill, Biderman and Herrick, 2019).
- **Conway's Game of Life** and **Rule 110** have universal constructions with suitable initial configurations and unbounded space. Cook's Rule 110 simulation includes repeating backgrounds extending away from the encoded input.

### Deliberately not Turing complete

Turing completeness has a price: as the later Rice theorem lesson shows, every non-trivial property of the recognised language is undecidable for arbitrary TMs. This does not make every useful question undecidable. So some designers avoid it on purpose:

| System | Restriction | Benefit |
|---|---|---|
| Formal regular expressions | finite automata | linear input scan for a fixed DFA |
| eBPF in Linux | verifier restricts accepted programs, including loop bounds | termination and safety checking under its model; not a guarantee against implementation bugs |
| Bitcoin Script | no loops | every script terminates |
| Starlark core | no recursion, finite iteration | core evaluation terminates; extensions and external build commands need separate analysis |
| Total fragments of Agda and Rocq; Dhall | termination restrictions | stronger evaluation guarantees; Agda/Rocq also have guarded coinduction and features requiring separate treatment |

Ethereum bounds the execution of each Ethereum transaction with **gas**. Continuing computation consumes the finite budget; some terminating instructions, including `STOP`, have zero base cost, so it is false that every instruction costs at least one gas. Every Ethereum transaction eventually stops normally, exceptionally or out of gas. This guarantees termination under EVM semantics, not successful completion or an elapsed-time deadline. Calling the EVM Turing complete also idealises away its actual resource and fixed-width addressing limits.

## Key takeaways

- Universality claims idealise resource limits away and require specific simulation constructions.
- Restricting recursion and iteration can guarantee termination of core language evaluation.
- A finite Ethereum gas budget ends execution under EVM semantics without guaranteeing success or an elapsed-time deadline.

## Further reading

- [Dolan: mov is Turing-complete](https://harrisonwl.github.io/assets/courses/malware/spring2017/papers/mov-is-turing-complete.pdf)
- [Cook: a concrete view of Rule 110 computation](https://arxiv.org/abs/0906.3248)
- [Starlark language specification](https://github.com/bazelbuild/starlark/blob/master/spec.md)
- [Ethereum: EVM opcode costs](https://ethereum.org/developers/docs/evm/opcodes/)
