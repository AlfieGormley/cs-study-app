---
id: compu-halting
title: The halting problem and diagonalisation
level: advanced
minutes: 15
summary: Cantor's diagonal argument shows most problems have no algorithm at all; the same trick proves no program can decide whether programs halt.
---

Wouldn't it be useful to have a tool that reads any program and its input and tells you whether it will finish or run forever? Your CI could reject code with infinite loops. Your OS could kill hung processes the moment they hang.

Turing’s 1936 work established foundational undecidability results; the modern halting formulation proved below is a consequence of that framework. Not "we haven't found one yet": no effective algorithm decides halting for every program/input pair in a Turing-complete model with unbounded resources. A closed deterministic machine with a fixed finite state space is different: cycle detection decides halting in principle, though it may be infeasible. The proof uses a single idea, **diagonalisation**, that also shows something even stranger: almost every problem has no algorithm at all.

## Countable and uncountable

A set is **countable** if it is finite or its elements can be listed as a sequence e₁, e₂, e₃, … that eventually reaches every element. The natural numbers are countable, and so are the integers (0, 1, −1, 2, −2, …).

**Turing machines are countable.** Each TM M has a finite description ⟨M⟩, a string over a finite alphabet. List all strings by length, then alphabetically within a length, and skip the ones that aren't valid descriptions. Every TM appears at some finite position. The same goes for Python programs: each is a finite text file.

**Languages are not countable.** This is Cantor's diagonal argument.

## Cantor's diagonal argument

Fix the alphabet {0, 1} and list all strings in order: s₁ = ε, s₂ = 0, s₃ = 1, s₄ = 00, and so on. A language L is any set of these strings, so you can describe L by an infinite row of bits: bit i is 1 if sᵢ ∈ L.

**Claim.** No list L₁, L₂, L₃, … contains every language.

**Proof.** Take any such list and write the rows in a table:

```
        s₁  s₂  s₃  s₄  ...
  L₁   [1]  0   1   1
  L₂    0  [0]  0   1
  L₃    1   1  [1]  0
  L₄    0   1   0  [0]
  ...
```

Build a new language D by flipping the diagonal:

```
  D  = { sᵢ : sᵢ ∉ Lᵢ }
  D     0   1   0   1   ...
```

Compare D with any row Lᵢ. At column i they disagree, because D was defined to disagree there. So D ≠ Lᵢ for every i, and D is missing from the list. Since the list was arbitrary, no list contains every language. ∎

**Consequence.** There are countably many TMs but uncountably many languages, so all but countably many languages are not recognised by any TM. Each TM recognises one language; there are simply not enough TMs to go round.

That is an existence proof. It doesn't name a specific unsolvable problem. The halting problem does.

## The acceptance problem

Define

```
A_TM = { ⟨M, w⟩ : M is a TM
                  and M accepts w }
```

A_TM is **recognisable**: the universal TM U simulates M on w and accepts if M does. If M loops, U loops, which a recogniser is allowed to do.

**Theorem.** A_TM is not decidable.

**Proof.** Suppose, for contradiction, that some TM H decides A_TM:

```
H(⟨M, w⟩) = accept  if M accepts w
            reject  otherwise
```

H always halts. Use it to build a TM D that takes a machine description and flips H’s answer to whether that machine accepts its own description:

```
D(⟨M⟩):
  1. run H on ⟨M, ⟨M⟩⟩
  2. if H accepts: reject
     if H rejects: accept
```

D always halts, because H does. Now run D on its own description ⟨D⟩:

- If D accepts ⟨D⟩, then H accepted ⟨D, ⟨D⟩⟩, so by step 2 D rejects ⟨D⟩.
- If D rejects ⟨D⟩, then H rejected ⟨D, ⟨D⟩⟩, so by step 2 D accepts ⟨D⟩.

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

D is built to differ from every machine on the diagonal. But D is itself a machine, so it has a row, and that row must cross the diagonal at the cell (D, ⟨D⟩). There, D would have to differ from itself. The only escape is that H, the tool used to compute the diagonal, does not exist.

## The halting problem

```
HALT_TM = { ⟨M, w⟩ : M halts on w }
```

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
> The proof works because a program can receive its own source (or a reference to itself) as input. Python functions can be passed as objects, but a real program need not have access to its source file. The formal proof uses an encoding that can be passed as data; Kleene’s recursion theorem supplies a general formal account of effective self-reference, not a runtime source-file permission guarantee.

## Decidable = recognisable both ways

**Theorem.** L is decidable if and only if both L and its complement L̄ are recognisable.

**Proof.**
- (⇒) A decider for L recognises L. Swap its accept and reject states and it decides, so recognises, L̄.
- (⇐) Let R₁ recognise L and R₂ recognise L̄. On input x, run both **in parallel**, alternating one step of each. Every x is in L or L̄, so one of them eventually accepts. If R₁ accepts, accept; if R₂ accepts, reject. This always halts. ∎

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

Decidable is exactly the overlap of recognisable and co-recognisable. EQ_TM is in neither, as the next lesson shows.

## Why it matters in practice

- **No perfect infinite-loop detector.** Compilers and linters can establish nontermination in simple cases such as `while True: pass` in the idealised model, but an automatic tool that always returns a definite yes/no answer must either miss some loops or wrongly flag some terminating programs. A sound tool may instead report unknown or fail to terminate on some cases.
- **Timeouts are the engineering answer.** CI jobs, database queries and serverless functions all get time limits. A timeout does not decide halting; it caps resources, accepting that some slow-but-correct runs will be killed.
- **Proof assistants accept only some terminating programs.** Coq/Rocq and Agda support termination-checked definitions, including structural and well-founded approaches. Their exact accepted forms and escape hatches differ; it is not simply a requirement that every recursive call visibly use a smaller source argument. Some terminating functions are rejected and must be restructured, because the checker cannot be complete.
- **A halting oracle would settle some mathematical statements.** This short program halts if and only if Goldbach's conjecture (every even number ≥ 4 is a sum of two primes) is false:

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

def goldbach_search():
    n = 4
    while True:
        if not two_primes(n):
            return n   # counterexample!
        n += 2
```

A working `halts` applied to `goldbach_search` would settle a problem open since 1742. This reasoning assumes idealised unbounded integers, time and memory; real execution may fail from resource limits. The same oracle could decide whether an effectively axiomatized formal system has a finite proof of contradiction, by deciding whether a proof search halts. That does not resolve every mathematical statement or define a single "consistency of mathematics" question. The diagonal proof, not the fact that a conjecture is open, establishes impossibility.

## Pitfalls

- **Undecidable means no algorithm for all inputs.** Halting is easy for many particular programs. Tools like termination provers succeed often; they just can't succeed always.
- **Undecidable is not unrecognisable.** HALT_TM is recognisable: run the program and say yes if it stops. You only lose the ability to say no.
- **Bounded versions are decidable.** "Does M halt within 10⁶ steps?" is decided by simulation. Undecidability needs an unbounded question.
- **The proof needs the decider to be total.** If `halts` were allowed to loop, `paradox` could loop too and there is no contradiction.

## Key takeaways
- TMs (and programs) are countable; languages are uncountable, so most languages have no recogniser at all.
- Diagonalisation builds an object that differs from every item in a list at the diagonal, so it can't be in the list.
- A_TM and HALT_TM are recognisable but undecidable: a hypothetical decider can be turned against itself.
- L is decidable iff L and L̄ are both recognisable (proof by dovetailing). So Ā_TM and the complement of HALT_TM are not recognisable.
- In practice: no perfect loop detector, so systems use timeouts, resource bounds and conservative termination checkers.

## Further reading
- [Halting problem (Wikipedia)](https://en.wikipedia.org/wiki/Halting_problem)
- [Cantor's diagonal argument (Wikipedia)](https://en.wikipedia.org/wiki/Cantor%27s_diagonal_argument)
- [Computability and Complexity (Stanford Encyclopedia of Philosophy)](https://plato.stanford.edu/entries/computability/)
- [Kleene's recursion theorem (Wikipedia)](https://en.wikipedia.org/wiki/Kleene%27s_recursion_theorem)
- [Recursively enumerable language (Wikipedia)](https://en.wikipedia.org/wiki/Recursively_enumerable_language)
