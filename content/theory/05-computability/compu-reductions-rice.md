---
id: compu-reductions-rice
title: Reductions and Rice's theorem
level: advanced
minutes: 15
summary: How to prove a new problem undecidable by transforming a known one into it, and Rice's theorem, which says every non-trivial question about what a program computes is undecidable.
---

The halting problem took a clever self-referential argument. You don't want to invent a new paradox for every problem. Instead, you use a **reduction**: show that if you could solve the new problem B, you could use it to solve a problem A that is already known to be impossible.

The pay-off is Rice's theorem, one of the most practically important results in computer science. It limits exact, terminating analysis of non-trivial extensional properties for arbitrary programs. This does not mean every analysis task or formal type-checking judgement is undecidable.

## The idea

"A reduces to B" means: **A is no harder than B**. If you had a solver for B, you could build a solver for A by translating each A-question into a B-question.

The logic you use to prove undecidability is the contrapositive:

```
  A ≤ B  and  B decidable
        ⇒ A decidable

  A ≤ B  and  A undecidable
        ⇒ B undecidable
```

> [!warning] The direction is everything
> To prove B undecidable, reduce a **known undecidable** problem A **to** B. Reducing B to A shows only that B is no harder than A, which alone does not prove B undecidable. Getting this backwards is the most common mistake in computability proofs.

## Mapping reductions

A is **mapping reducible** to B, written A ≤m B, if there is a computable function f such that for every input x:

```
  x ∈ A   ⇔   f(x) ∈ B
```

f must be total (always halt). It need not decide A or B: it translates instances. It may perform arbitrary terminating computation, not only textual rewriting. Given a decider for B, the decider for A is "compute f(x), then ask B".

The machine examples below describe well-formed encodings. To make each map total on all strings, detect malformed encodings and send them to a fixed no-instance of the target, taking malformed strings as non-members of the source. Complement arguments use complements in that same universe.

Useful properties, all following from the definition:

- If A ≤m B and B is decidable (or recognisable), so is A.
- A ≤m B if and only if Ā ≤m B̄ (the same f works for the complements).
- ≤m is transitive: A ≤m B and B ≤m C give A ≤m C.

A more general notion is a **Turing reduction**: A is decidable using a B-oracle that you can query many times and whose answers you can post-process (for example, negate). Every language is Turing reducible to its complement, but A_TM is not mapping reducible to its complement. Mapping reductions are finer, which is why they can separate recognisable from unrecognisable.

## Example 1: A_TM ≤m HALT_TM

The input is ⟨M, w⟩. Build a machine M′ that halts exactly when M accepts w:

```
M′(x):
  run M on x
  if M accepts: accept (halt)
  if M rejects: loop forever
```

Map ⟨M, w⟩ to ⟨M′, w⟩. Then:

- M accepts w ⇒ M′ halts on w.
- M rejects w ⇒ M′ loops on w.
- M loops on w ⇒ M′ loops on w.

So ⟨M, w⟩ ∈ A_TM ⇔ ⟨M′, w⟩ ∈ HALT_TM. The function f is computable: it just edits a transition table, it never *runs* M. Programs that build programs are the whole technique. In Python, with a "machine" as a function that returns True (accept), False (reject) or never returns:

```python
def f(M, w):
    # A_TM ≤m HALT_TM
    def M2(x):
        if M(x):        # may never return
            return True # accepted: halt
        while True:     # rejected: hang
            pass
    return M2, w        # build, don't run
```

## Example 2: the blank-tape halting problem

```
HALT_ε = { ⟨M⟩ : M halts on blank input }
```

Reduce HALT_TM to it. Given ⟨M, w⟩, build M_w, which erases its input, writes w on the tape, then runs M. M_w halts on blank input (indeed on any input) iff M halts on w. In Python: `lambda _: M(w)`.

This is the problem the busy beaver function would solve, which is why S(n) is uncomputable.

## Example 3: emptiness, E_TM

```
E_TM = { ⟨M⟩ : L(M) = ∅ }
```

**Theorem.** E_TM is undecidable.

**Proof.** Reduce A_TM to the complement Ē_TM. Given ⟨M, w⟩, build

```
M₁(x):
  if x ≠ w: reject
  run M on w; accept if it accepts
```

L(M₁) is {w} if M accepts w, and ∅ otherwise. So M accepts w ⇔ L(M₁) ≠ ∅ ⇔ ⟨M₁⟩ ∈ Ē_TM. Hence A_TM ≤m Ē_TM, so Ē_TM is undecidable. A language is decidable iff its complement is, so E_TM is undecidable. ∎

(Ē_TM is recognisable: dovetail M on all strings and accept if any is accepted. So E_TM itself is co-recognisable but not recognisable.)

## Example 4: equivalence is neither

```
EQ_TM = { ⟨M, N⟩ : L(M) = L(N) }
```

**Not recognisable.** Map ⟨M, w⟩ to ⟨R, N⟩ where R rejects everything and N(x) = "run M on w; accept if it accepts". L(N) is Σ* if M accepts w, ∅ otherwise. So M accepts w ⇔ L(N) ≠ L(R). That is A_TM ≤m EQ̄_TM, hence Ā_TM ≤m EQ_TM. Ā_TM is unrecognisable, so EQ_TM is too.

**Not co-recognisable.** Same N, but compare with a machine A that accepts everything: M accepts w ⇔ L(N) = L(A). That is A_TM ≤m EQ_TM, hence Ā_TM ≤m EQ̄_TM, so EQ̄_TM is unrecognisable.

This is why "are these two programs equivalent?" has no general algorithm, neither a complete recogniser for equivalence nor a complete recogniser for inequivalence. Sound tools can still settle particular instances.

## Rice's theorem

Language emptiness and fixed-language equality exemplify a broader theorem due to Rice (1953). Halting itself is not determined solely by the accepted language: rejection and divergence can recognise the same language.

A **semantic property** of TMs is a set P of TM descriptions that depends only on the language: if L(M) = L(N), then either both are in P or neither is. P is **non-trivial** if some TM is in P and some TM is not.

**Theorem (Rice).** Every non-trivial semantic property of Turing machines is undecidable.

**Proof.** Let P be non-trivial and semantic.

1. Assume the machines with empty language are not in P. (If they are, run this argument on the complement of P, which is also non-trivial and semantic; P is decidable iff its complement is.)
2. Since P is non-trivial, pick some TM T with ⟨T⟩ ∈ P. Then L(T) ≠ ∅.
3. Given ⟨M, w⟩, build:

```
M′(x):
  run M on w
  if M accepts w: run T on x,
                  answer as T does
  if M rejects w: reject
  # If M loops, the simulation loops.
```

4. If M accepts w, then M′ behaves like T on every x, so L(M′) = L(T) and ⟨M′⟩ ∈ P.
5. If M does not accept w, M′ accepts nothing, so L(M′) = ∅ and ⟨M′⟩ ∉ P.
6. So ⟨M, w⟩ ∈ A_TM ⇔ ⟨M′⟩ ∈ P. That is A_TM ≤m P, and A_TM is undecidable, so P is undecidable. ∎

```python
def rice_map(M, w, T):
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

Printing, division by zero and null dereferences are **not automatically properties of the recognised language**: two machines can accept the same language but differ in these events. Event reachability is also undecidable in general when the model can simulate an arbitrary TM and trigger the event only after it halts. That is a separate reduction, or can be phrased using an instrumented recogniser. A vague label such as "malware" needs a precise non-trivial property before any theorem applies.

**Not** covered (decidable, or at least not ruled out by Rice):

- **Syntactic or structural questions**: does M have more than 5 states? Does the source contain `eval`? These depend on the description, not the language.
- **Resource-bounded questions**: does it halt within 10⁶ steps on input x?
- **Trivial properties**: "L(M) is recognisable" is true of every TM.

## Living with Rice: approximation

For these non-trivial extensional properties of arbitrary programs, Rice says no analyser can be all three of: **automatic**, **always terminating**, and **exactly correct** on every program. Real tools pick which to give up:

| Approach | Gives up | Example |
|---|---|---|
| Sound over-approximation | completeness: false alarms | type checkers, Astrée |
| Unsound bug finding | soundness: missed bugs | linters, many SAST tools |
| Bounded checking | coverage beyond a bound | CBMC, fuzzing |
| Interactive proof | automation | Coq/Rocq, Isabelle |

Java rejects `int x = flag ? 1 : "a";` even if `flag` is always true: the reference conditional expression must satisfy the target assignment type for both branches, and the string branch is not compatible with `int`. This is a particular language rule, not a restriction uniquely forced by Rice. A different sound language could accept some statically known constant-branch cases.

A terminating type checker can decide a formal typing judgement exactly. The harder question is whether arbitrary programs in a model that permits runtime type faults can ever reach such a fault. In a sufficiently expressive model this is undecidable by a reachability reduction, so an always-terminating sound safety analyser must be conservative. Languages that exclude an error by construction need separate treatment. **Abstract interpretation** (Cousot and Cousot, 1977) provides a framework for sound approximation.

Compiler optimisation is the same story. Perfect dead-code elimination would decide whether code is reachable, which is undecidable, so compilers remove only code they can *prove* is dead.

## Other famous undecidable problems

Reductions spread undecidability far beyond machines:

- **Post correspondence problem** (Post, 1946): given dominoes with a top and bottom string, is there a non-empty finite sequence of dominoes, allowing repetitions, whose top and bottom concatenations match? Undecidable, by reduction from A_TM.
- **CFG problems**: whether a CFG is ambiguous, whether it generates every string, and whether two CFGs are equivalent are all undecidable (via PCP or computation histories).
- **Hilbert's tenth problem**: does a polynomial equation with integer coefficients have an integer solution? Undecidable (Matiyasevich, building on Davis, Putnam and Robinson, 1970).
- **Typability and type checking for Curry-style System F**, where pure λ-terms lack explicit type annotations, are undecidable (Wells, 1994). This must not be confused with decidable checking of fully annotated Church-style System F. Practical languages use restricted inference and/or annotations, with details depending on their type systems.

## Pitfalls

- **Reducing in the wrong direction.** To show B is hard: known-hard A ≤ B.
- **f must be computable and total.** These reductions construct M′ without running an unbounded simulation of M. Other reductions may use bounded simulation or other terminating computations; "never run a machine" is not a general rule.
- **Rice is about languages, not machines.** "Does M run for more than n steps on w" or "does M have a useless state" are about the machine, so Rice says nothing about them (even if some are undecidable for other reasons).
- **Undecidable in general is not hopeless in practice.** Termination provers, model checkers and type systems solve huge numbers of real instances. They just can't solve all of them.

## Key takeaways
- A ≤m B means a computable f with x ∈ A ⇔ f(x) ∈ B. To prove B undecidable, reduce a known undecidable A to B.
- The constructions here emit new machines without waiting for M to halt. A_TM ≤m HALT_TM; E_TM is undecidable, and EQ_TM is neither recognisable nor co-recognisable.
- Rice's theorem: every non-trivial property of the language a program computes is undecidable.
- Syntactic, resource-bounded and trivial properties escape Rice.
- Exact total analysis of an undecidable property is impossible on all inputs. Particular instances, restricted languages and formal type judgements may still be decidable.

## Further reading
- [Rice's theorem (Wikipedia)](https://en.wikipedia.org/wiki/Rice%27s_theorem)
- [Many-one reduction (Wikipedia)](https://en.wikipedia.org/wiki/Many-one_reduction)
- [Turing reduction (Wikipedia)](https://en.wikipedia.org/wiki/Turing_reduction)
- [Post correspondence problem (Wikipedia)](https://en.wikipedia.org/wiki/Post_correspondence_problem)
- [Hilbert's tenth problem (Wikipedia)](https://en.wikipedia.org/wiki/Hilbert%27s_tenth_problem)
- [Abstract interpretation (Wikipedia)](https://en.wikipedia.org/wiki/Abstract_interpretation)
- [Undecidable problem (Wikipedia)](https://en.wikipedia.org/wiki/Undecidable_problem)

- [Wells, LICS 1994: Curry-style System F](https://lics.siglog.org/archive/1994/Wells-Typabilityandtypech.html)
- [Java Language Specification: conditional operator](https://docs.oracle.com/javase/specs/jls/se25/html/jls-15.html#jls-15.25)
