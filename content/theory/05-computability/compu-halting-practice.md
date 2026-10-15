---
id: compu-halting-practice
title: Timeouts, termination checks and mathematical search
level: advanced
minutes: 3
summary: Undecidability rules out a total exact answer for every program; many particular instances remain solvable.
sourceLesson: compu-halting
---

## Why it matters in practice

- **No perfect infinite-loop detector.** Compilers and linters can establish nontermination in simple cases such as `while True: pass` in the idealised model, but an automatic tool that always returns a definite yes/no answer must either miss some loops or wrongly flag some terminating programs. A sound tool may instead report unknown or fail to terminate on some cases.
- **Timeouts are the engineering answer.** Continuous-integration jobs, database queries and serverless functions all get time limits. A timeout does not decide halting; it caps resources, accepting that some slow-but-correct runs will be killed.
- **Proof assistants accept only some terminating programs.** Coq/Rocq and Agda support termination-checked definitions, including structural and well-founded approaches. Their exact accepted forms and escape hatches differ; it is not simply a requirement that every invocation of the same function visibly use a smaller source argument. Some terminating functions are rejected and must be restructured, because the checker cannot be complete.
- **A halting oracle would settle some mathematical statements.** This short program halts if and only if Goldbach's conjecture (every even integer at least four is a sum of two primes) is false:

```python
from math import isqrt

def is_prime(k):
    return k > 1 and all(
        k % d for d in
        range(2, isqrt(k) + 1))

def two_primes(n):
    return any(is_prime(p) and
               is_prime(n - p)
               for p in range(2, n//2 + 1))

# Define the unbounded search; do not call
# it.
def goldbach_search():
    n = 4
    while True:
        if not two_primes(n):
            return n   # counterexample!
        # Only even candidates
        # need checking.
        n += 2
```

A working `halts` applied to `goldbach_search` would settle a problem open since 1742. This reasoning assumes idealised unbounded integers, time and memory; real execution may fail from resource limits. The same oracle could decide whether an effectively axiomatized formal system has a finite proof of contradiction, by deciding whether a proof search halts. That does not resolve every mathematical statement or define a single "consistency of mathematics" question. The diagonal proof, not the fact that a conjecture is open, establishes impossibility.

## Pitfalls

- **Undecidable means no algorithm for all inputs.** Halting is easy for many particular programs. Tools like termination provers succeed often; they just can't succeed always.
- **Undecidable is not unrecognisable.** HALT_TM is recognisable: run the program and say yes if it stops. You only lose the ability to say no.
- **Bounded versions are decidable.** "Does M halt within 10⁶ steps?" is decided by simulating M for that many steps. Undecidability needs an unbounded question.
- **The proof needs the decider to be total.** If `halts` were allowed to loop, `paradox` could loop too and there is no contradiction.

## Key takeaways

- Undecidability rules out a total exact answer for every program; many particular instances remain solvable.
- A time limit bounds execution without predicting eventual termination.
- A counterexample search can halt exactly when a conjecture is false; bounded tests never prove the universal conjecture.

## Further reading

- [Agda: termination checking](https://agda.readthedocs.io/en/latest/language/termination-checking.html)
- [Oliveira e Silva: bounded Goldbach verification](https://sweet.ua.pt/tos/goldbach.html)
