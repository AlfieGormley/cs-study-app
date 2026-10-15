---
id: compu-halting-undecidable
title: The halting problem and self-reference
level: advanced
minutes: 3
summary: Halting includes both accepting and rejecting termination.
sourceLesson: compu-halting
---

## The halting problem

```formula
HALT_TM = { ⟨M, w⟩ : M(w)↓ }
where
HALT_TM: the halting problem for Turing machines, as a set of strings
M: any Turing machine
w: any input string
⟨M, w⟩: angle brackets: one string encoding the machine M and the input w
M(w)↓: "M halts on w": run on w, M eventually stops, by accepting or by rejecting
{ … : … }: set-builder notation: the set of all encodings that satisfy the condition after the colon
In words: HALT_TM holds every machine-and-input pair where the machine eventually stops on that input.
```

The pair for the binary increment machine and input 1011 is in HALT_TM (it stops after 8 steps). A pair whose machine just keeps moving right forever, never entering a halting state, is not.

**Theorem.** HALT_TM is undecidable.

The proof is the same trick, and it reads well as Python. Suppose someone hands you `halts(f, x)`, which always returns, and correctly says whether `f(x)` would finish:

```python
def halts(f, x):
    # Proof placeholder, not an algorithm.
    raise NotImplementedError

def paradox(f):
    if halts(f, f):
        while True:   # loop forever
            pass
    else:
        return        # halt at once

# Hypothetically call paradox(paradox).
```

- If `halts(paradox, paradox)` returns True, `paradox(paradox)` loops forever. So `halts` was wrong.
- If it returns False, `paradox(paradox)` returns immediately. So `halts` was wrong again.

No implementation of `halts` can be right on this input. So no correct, always-terminating `halts` exists. ∎

> [!note] Programs as data
> The proof works because a program can receive its own source (or a reference to itself) as input. Python functions can be passed as objects, but a real program need not have access to its source file. The formal proof uses an encoding that can be passed as data; Kleene’s recursion theorem supplies a general formal account of effective self-reference, not a guarantee that a running program may read its own source file.

## Key takeaways

- Halting includes both accepting and rejecting termination.
- A total halting predictor can be contradicted by a program that reverses its prediction.
- The formal proof passes effective encodings as data; programs need not read their own source files.

## Further reading

- [Sipser: undecidability and diagonalisation](https://ocw.mit.edu/courses/18-404j-theory-of-computation-fall-2020/resources/mit18_404f20_lec8-1/)
- [Lynch: self-reference and the recursion theorem](https://ocw.mit.edu/courses/6-045j-automata-computability-and-complexity-spring-2011/resources/mit6_045js11_lec10/)
