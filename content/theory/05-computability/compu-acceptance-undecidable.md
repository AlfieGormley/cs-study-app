---
id: compu-acceptance-undecidable
title: Why machine acceptance has no decider
level: advanced
minutes: 4
summary: Universal simulation recognises machine acceptance.
sourceLesson: compu-halting
---

## The acceptance problem

Define the acceptance problem as a language of encoded machine-input pairs:

```formula
A_TM = { ⟨M, w⟩ : w ∈ L(M) }
where
A_TM: the acceptance problem for Turing machines, as a set of strings
M: any Turing machine (TM)
w: any input string
⟨M, w⟩: angle brackets: one string that encodes both the machine M (its finite machine instructions) and the input w
L(M): the language of M: the set of strings M accepts
∈: is a member of
{ … : … }: set-builder notation: the set of all encodings that satisfy the condition after the colon
In words: A_TM holds every machine-and-input pair where the machine accepts that input.
```

For example, the pair for the earlier crossing-off unit’s aⁿbⁿcⁿ machine and input aabbcc is in A_TM, while the pair for the same machine and aabbc is not (it rejects).

A_TM is **recognisable**: the universal TM U simulates M on w and accepts if M does. If M loops, U loops, which a recogniser is allowed to do.

**Theorem.** A_TM is not decidable.

**Proof.** Suppose, for contradiction, that some TM H decides A_TM:

```formula
H(⟨M, w⟩) = 1   if ⟨M, w⟩ ∈ A_TM
H(⟨M, w⟩) = 0   otherwise
where
H: the hypothetical decider for A_TM
M: any Turing machine
w: any input string
⟨M, w⟩: the encoding of M and w as one string
A_TM: the acceptance problem: all pairs where M accepts w
1, 0: H's answer: 1 means accept ("yes"), 0 means reject ("no")
∈: is a member of
In words: H always stops and correctly answers whether M accepts w.
```

H always halts. Use it to build a TM D that takes a machine description and flips H’s answer to whether that machine accepts its own description:

```
D(⟨M⟩):
  1. run H on ⟨M, ⟨M⟩⟩
  2. if H accepts: reject
     if H rejects: accept
```

On malformed machine descriptions, D rejects immediately. On valid descriptions, D always halts, because H does. Now run D on its own description ⟨D⟩:

- If H accepts the encoded self-input pair, it predicts that D accepts its own description. But step 2 makes D reject that description.
- If H rejects that pair, it predicts that D does not accept its own description. But step 2 makes D accept that description.

Either way D does the opposite of what it does. That is impossible, so H cannot exist. ∎

### Why this is diagonalisation

Make a table: rows are machines M₁, M₂, …, columns are their descriptions, and each entry is M's answer on that description.

```
         ⟨M₁⟩  ⟨M₂⟩  ⟨M₃⟩  ⟨D⟩
  M₁    [acc]  rej   acc   ...
  M₂     rej  [rej]  rej   ...
  M₃     acc   acc  [rej]  ...
  D      rej   acc   acc    ?
```

The rows for arbitrary recognisers may also contain a looping outcome. D uses H to distinguish acceptance from both rejection and looping, and is built to differ in acceptance from every machine on the diagonal. But D is itself a machine, so it has a row, and that row must cross the diagonal at the cell (D, ⟨D⟩). There, D would have to differ from itself. The only escape is that H, the tool used to compute the diagonal, does not exist.

## Key takeaways

- Universal simulation recognises machine acceptance.
- A hypothetical total acceptance decider permits an always-halting diagonal machine.
- Running that diagonal machine on its own encoding yields contradictory answers.

## Further reading

- [Sipser: undecidability and diagonalisation](https://ocw.mit.edu/courses/18-404j-theory-of-computation-fall-2020/resources/mit18_404f20_lec8-1/)
