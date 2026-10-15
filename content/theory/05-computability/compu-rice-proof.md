---
id: compu-rice-proof
title: Proving Rice’s theorem for semantic properties
level: advanced
minutes: 5
summary: A semantic property depends only on the accepted language; a non-trivial property separates some two machines.
sourceLesson: compu-reductions-rice
---

## Rice's theorem

Language emptiness and fixed-language equality exemplify a broader theorem due to Rice (1953). Halting itself is not determined solely by the accepted language: rejection and divergence can recognise the same language.

A **semantic property** of TMs is a set P of TM descriptions that depends only on the language: machines accepting the same language must either both have the property or both lack it. P is a **non-trivial property** if some TM is in P and some TM is not.

```formula
L(M) = L(N)  ⇒  (⟨M⟩ ∈ P ⇔ ⟨N⟩ ∈ P)
⟨T⟩ ∈ P   and   ⟨T′⟩ ∉ P
where
P: the property, written as the set of encodings of machines that have it
M, N: any two Turing machines
L(M): the language of M: the strings it accepts (likewise L(N))
⟨M⟩: angle brackets: the encoding of M as a string
T, T′: some machine that has the property and some machine that does not (both must exist)
∈, ∉: is a member of, is not a member of
⇒: implies
⇔: if and only if
In words: the first line says P is semantic (machines with the same language agree on P); the second says P is non-trivial (it is neither true of all machines nor of none).
```

For example, "L(M) contains the string hello" is semantic and non-trivial. "M has more than 5 states" is not semantic: two machines with the same language can have 3 and 50 states.

**Theorem (Rice).** Every non-trivial semantic property of Turing machines is undecidable.

**Proof.** Let P be non-trivial and semantic.

1. Assume the machines with empty language lie outside P. (If instead they lie inside P, run this argument on the complement of P, which is also non-trivial and semantic; P is decidable iff its complement is.)
2. Since P is non-trivial, pick a machine T whose encoding has the property. Its language is nonempty, because empty-language machines were assumed not to have the property.
3. Given ⟨M, w⟩, build:

```
M′(x):
  run M on w
  if M accepts w: run T on x,
                  answer as T does
  if M rejects w: reject
  # If M loops, the simulation loops.
```

4. If M accepts w, the constructed machine behaves like T on every input. It has the same language as T and therefore has the property.
5. If M does not accept w, the constructed machine accepts nothing. Its empty language means it lacks the property.
6. Thus the original machine accepts its given input exactly when the constructed machine has the property. This total computable mapping reduces the undecidable acceptance problem to the property, proving it undecidable. ∎

```formula
w ∈ L(M)  ⇒  L(M′) = L(T)  ⇒  ⟨M′⟩ ∈ P
w ∉ L(M)  ⇒  L(M′) = ∅  ⇒  ⟨M′⟩ ∉ P
where
M: the given machine
w: the given input
M′: the new machine built in step 3
T: a machine whose encoding is in P
L(M): the language of M: the strings it accepts
∅: the empty set
P: the semantic, non-trivial property, assumed not to contain machines with empty language
∈, ∉: is a member of, is not a member of
⇒: implies
In words: M′ copies T when M accepts w and accepts nothing otherwise, so asking whether M′ has the property answers whether M accepts w.
```

```python
def rice_map(M, w, T):
    # Emit a gated recogniser without
    # running M.
    def M2(x):
        if M(w):          # may never return
            return T(x)   # behave like T
        return False      # accept nothing
    return M2
```

### What Rice's theorem covers

For the language version stated here, examples include:

- Does M accept the fixed string `hello`?
- Is L(M) regular, finite or empty?
- Is L(M) equal to a fixed recognisable reference language?

Each property depends only on L(M), and some TMs have it while others do not. A corresponding partial-function version of Rice covers non-trivial properties of the computed function, such as returning 0 on every input.

Printing, division by zero and null dereferences are **not automatically properties of the recognised language**: two machines can accept the same language but differ in these events. Event reachability is also undecidable in general when the model can simulate an arbitrary TM and trigger the event only after it halts. That is a separate computable reduction, or can be phrased using an instrumented recogniser. A vague label such as "malware" needs a precise non-trivial property before any theorem applies.

**Not** covered (decidable, or at least not ruled out by Rice):

- **Syntactic or structural questions**: does M have more than 5 states? Does the source contain `eval`? These depend on the description, not the language.
- **Resource-bounded questions**: does it halt within 10⁶ steps on input x?
- **Trivial properties**: "L(M) is recognisable" is true of every TM.

## Key takeaways

- A semantic property depends only on the accepted language; a non-trivial property separates some two machines.
- The proof gates a reference recogniser behind one acceptance computation.
- Structural, bounded and trivial questions do not satisfy the theorem’s hypotheses.

## Further reading

- [Lynch: mapping reductions and Rice’s theorem](https://ocw.mit.edu/courses/6-045j-automata-computability-and-complexity-spring-2011/resources/mit6_045js11_lec09/)
