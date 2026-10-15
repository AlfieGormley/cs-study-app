---
id: compu-dovetailing
title: Deciding with two recognisers
level: advanced
minutes: 3
summary: A language is decidable exactly when it and its complement are recognisable.
sourceLesson: compu-halting
---

## Decidable means recognisable both ways

**Theorem.** L is decidable if and only if both L and its complement L̄ are recognisable.

```formula
L̄ = Σ* − L
L ∈ R   ⇔   L ∈ RE  and  L̄ ∈ RE
R = RE ∩ coRE
where
L: any language over the alphabet Σ (sigma)
L̄: the complement of L: every string outside L
Σ*: every finite string over the alphabet
−: set difference: everything on the left except what is on the right
R: the class of decidable languages (also called recursive)
RE: the class of Turing-recognisable languages (also called recursively enumerable)
coRE: the class of co-recognisable languages: those whose complement is in RE
∈: is a member of
⇔: if and only if: each side implies the other
∩: intersection: the languages in both classes
In words: a language has a decider exactly when both it and its complement have recognisers.
```

**Proof.**
- Forward direction: a decider for L recognises L. Swap its accept and reject states and it decides, so recognises, L̄.
- Reverse direction: let R₁ recognise L and R₂ recognise L̄. On input x, run both **side by side**, alternating one step of each. Every x is in L or L̄, so one of them eventually accepts. If R₁ accepts, accept; if R₂ accepts, reject. This always halts. ∎

The parallel trick is called **dovetailing**. For nonnegative integers in the example, model each recogniser as a generator that yields once per step and returns when it accepts (a recogniser that would reject just loops):

```python
def is_square(n):        # halts iff square
    k = 0
    while k * k != n:
        k += 1
        yield

def not_square(n):       # halts iff not
    k = 0
    while not (k*k < n < (k+1)*(k+1)):
        k += 1
        yield

def decide(rec_yes, rec_no, x):
    runs = [(rec_yes(x), True),
            (rec_no(x), False)]
    while True:          # alternate steps
        for gen, answer in runs:
            try:
                # Give each recogniser
                # one step per round.
                next(gen)
            except StopIteration:
                return answer

print([n for n in range(20)
       if decide(is_square, not_square, n)])
# [0, 1, 4, 9, 16]
```

Neither displayed recogniser decides the square-number language by itself: `is_square(5)` runs forever. Together, one of them always finishes.

**Corollary.** The complement of A_TM (pairs where M does *not* accept w) is **not even recognisable**. If it were, A_TM would be recognisable on both sides and hence decidable, which it is not. The same holds for the complement of HALT_TM.

So the landscape has four regions:

| Class | Example |
|---|---|
| Decidable | aⁿbⁿcⁿ, "does DFA D accept w?" |
| Recognisable, not decidable | A_TM, HALT_TM |
| Co-recognisable, not decidable | complement of A_TM |
| Neither | EQ_TM: do two TMs accept the same language? |

Decidable is exactly the overlap of recognisable and co-recognisable. EQ_TM is in neither, as the later machine-equivalence lesson shows.

## Key takeaways

- A language is decidable exactly when it and its complement are recognisable.
- Dovetailing gives both recognisers a fair share of steps.
- The complements of acceptance and halting are not recognisable.

## Further reading

- [Sipser: undecidability and diagonalisation](https://ocw.mit.edu/courses/18-404j-theory-of-computation-fall-2020/resources/mit18_404f20_lec8-1/)
- [Lynch: mapping reductions and Rice’s theorem](https://ocw.mit.edu/courses/6-045j-automata-computability-and-complexity-spring-2011/resources/mit6_045js11_lec09/)
