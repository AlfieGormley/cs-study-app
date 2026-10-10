---
id: compu-reductions-rice
title: Reductions and Rice's theorem
level: advanced
minutes: 15
summary: How to prove a new problem undecidable by transforming a known one into it, and Rice's theorem, which says every non-trivial question about what a program computes is undecidable.
---

The halting problem took a clever self-referential argument. You don't want to invent a new paradox for every problem. Instead, you use a **computable reduction**: show that if you could solve the new problem B, you could use it to solve a problem A that is already known to be impossible.

The pay-off is Rice's theorem, one of the most practically important results in computer science. It limits exact, terminating analysis of non-trivial extensional properties for arbitrary programs. This does not mean every analysis task or formal type-checking judgement is undecidable.

## The idea

"A reduces to B" means: **A is no harder than B**. If you had an algorithm for B, you could build an algorithm for A by translating each A-question into a B-question.

The logic you use to prove undecidability is the contrapositive:

```formula
A ≤ B  and  B ∈ R   ⇒   A ∈ R
A ≤ B  and  A ∉ R   ⇒   B ∉ R
where
A, B: two decision problems, each written as a language: the set of inputs whose answer is "yes"
≤: "reduces to": an algorithm for B can be turned into an algorithm for A, so A is no harder than B
R: the class of decidable languages: those some always-halting Turing machine decides
∈, ∉: is a member of, is not a member of
⇒: implies
In words: if B can be decided, so can anything that reduces to it; so if A cannot be decided, nothing that A reduces to can be decided either.
```

The second line is the first one turned round (its contrapositive). For example, A_TM (does machine M accept input w?) is undecidable and reduces to HALT_TM (does M halt on w?), so HALT_TM is undecidable too, as Example 1 shows.

> [!warning] The direction is everything
> To prove B undecidable, reduce a **known undecidable** problem A **to** B. Reducing B to A shows only that B is no harder than A, which alone does not prove B undecidable. Getting this backwards is the most common mistake in computability proofs.

## Mapping reductions

A is **mapping reducible** to B, written A ≤ₘ B, if there is a computable function f such that for every input x:

```formula
x ∈ A   ⇔   f(x) ∈ B
where
A, B: two languages (decision problems as sets of yes-instances)
x: any input string for problem A
f: the mapping reduction: a total computable function, a procedure that always halts, turning each A-input into a B-input
f(x): the B-input that x is translated into
∈: is a member of
⇔: if and only if: each side implies the other
In words: f sends yes-instances of A to yes-instances of B and no-instances of A to no-instances of B.
```

f must be total (always halt). It need not decide A or B: it translates instances. It may perform arbitrary terminating computation, not only textual rewriting. Given a decider for B, the decider for A is "compute f(x), then ask B".

The machine examples below describe well-formed encodings. To make each map total on all strings, detect malformed encodings and send them to a fixed no-instance of the target, taking malformed strings as non-members of the source. Complement arguments use complements in that same universe.

Useful properties, all following from the definition:

- If A ≤ₘ B and B is decidable (or recognisable), so is A.
- A ≤ₘ B if and only if Ā ≤ₘ B̄ (the same f works for the complements).
- ≤ₘ is transitive: A ≤ₘ B and B ≤ₘ C give A ≤ₘ C.

```formula
A ≤_m B  and  B ∈ R   ⇒  A ∈ R
A ≤_m B  and  B ∈ RE  ⇒  A ∈ RE
A ≤_m B  ⇔  Ā ≤_m B̄
A ≤_m B  and  B ≤_m C  ⇒  A ≤_m C
where
A, B, C: languages (decision problems)
≤_m: is mapping reducible to (also called many-one reducible)
R: the class of decidable languages
RE: the class of Turing-recognisable languages
Ā: the complement of A: every string outside A (likewise B̄)
∈: is a member of
⇒: implies
⇔: if and only if
In words: decidability and recognisability both pass backwards along a mapping reduction, the same map works for complements, and mapping reductions chain.
```

A more general notion is a **Turing reduction**: A is decidable using a B-oracle that you can query many times and whose answers you can post-process (for example, negate). Every language is Turing reducible to its complement, but A_TM is not mapping reducible to its complement. Mapping reductions are finer, which is why they can separate recognisable from unrecognisable.

## Example 1: A_TM ≤ₘ HALT_TM

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

```formula
f(⟨M, w⟩) = ⟨M′, w⟩
⟨M, w⟩ ∈ A_TM  ⇔  ⟨M′, w⟩ ∈ HALT_TM
where
f: the mapping reduction, a total computable function on encodings
M: any Turing machine
M′: M-prime, the edited copy of M built by the mapping reduction
w: any input string
⟨M, w⟩: angle brackets: one string encoding a machine and an input
A_TM: the acceptance problem: pairs where M accepts w
HALT_TM: the halting problem: pairs where the machine halts on w
∈: is a member of
⇔: if and only if
In words: M accepts w exactly when the edited machine M′ halts on w, so a halting decider would decide acceptance.
```

The function f is computable: it just edits a transition table, it never *runs* M. Programs that build programs are the whole technique. In Python, with a "machine" as a function that returns True (accept), False (reject) or never returns:

```python
def f(M, w):
    # A_TM ≤ₘ HALT_TM
    def M2(x):
        if M(x):        # may never return
            return True # accepted: halt
        while True:     # rejected: hang
            pass
    return M2, w        # build, don't run
```

## Example 2: the blank-tape halting problem

```formula
HALT_ε = { ⟨M⟩ : M(ε)↓ }
f(⟨M, w⟩) = ⟨M_w⟩
where
HALT_ε: the blank-tape halting problem
M: any Turing machine
⟨M⟩: angle brackets: the encoding of M as a string
ε: epsilon, the empty input, so the tape starts blank
M(ε)↓: M, started on a blank tape, eventually halts
f: the mapping reduction from HALT_TM, a total computable function
w: any input string
M_w: a new machine that erases its input, writes w, then runs M
In words: HALT_ε holds the machines that halt when started on a blank tape; the map f sends ⟨M, w⟩ to ⟨M_w⟩, and M_w halts on blank input exactly when M halts on w.
```

Reduce HALT_TM to it. Given ⟨M, w⟩, build M_w, which erases its input, writes w on the tape, then runs M. M_w halts on blank input (indeed on any input) iff M halts on w. In Python: `lambda _: M(w)`.

This is the problem the busy beaver function would solve, which is why S(n) is uncomputable.

## Example 3: emptiness, E_TM

```formula
E_TM = { ⟨M⟩ : L(M) = ∅ }
where
E_TM: the emptiness problem for Turing machines
M: any Turing machine
⟨M⟩: angle brackets: the encoding of M as a string
L(M): the language of M: the set of strings it accepts
∅: the empty set, with no members
In words: E_TM holds the machines that accept no string at all.
```

**Theorem.** E_TM is undecidable.

**Proof.** Reduce A_TM to the complement Ē_TM. Given ⟨M, w⟩, build

```
M₁(x):
  if x ≠ w: reject
  run M on w; accept if it accepts
```

```formula
L(M_1) = {w}   if w ∈ L(M)
L(M_1) = ∅     if w ∉ L(M)
w ∈ L(M)  ⇔  ⟨M_1⟩ ∈ Ē_TM
where
M: the given Turing machine
w: the given input
M_1: the new machine built from M and w
L(M): the language of M: the strings it accepts
{w}: the set containing just w
∅: the empty set
Ē_TM: the complement of E_TM: the machines whose language is not empty
∈, ∉: is a member of, is not a member of
⇔: if and only if
In words: M₁ accepts only w, and only if M accepts w, so M₁ has a non-empty language exactly when M accepts w.
```

So M accepts w ⇔ L(M₁) ≠ ∅ ⇔ ⟨M₁⟩ ∈ Ē_TM. Hence A_TM ≤ₘ Ē_TM, so Ē_TM is undecidable. A language is decidable iff its complement is, so E_TM is undecidable. ∎

(Ē_TM is recognisable: dovetail M on all strings and accept if any is accepted. So E_TM itself is co-recognisable but not recognisable.)

## Example 4: equivalence is neither

```formula
EQ_TM = { ⟨M, N⟩ : L(M) = L(N) }
where
EQ_TM: the equivalence problem for Turing machines
M, N: any two Turing machines
⟨M, N⟩: angle brackets: one string encoding both machines
L(M): the language of M: the strings it accepts (likewise L(N))
In words: EQ_TM holds every pair of machines that accept exactly the same strings.
```

Both proofs below use the machine N(x) = "ignore x, run M on w; accept if it accepts". So N accepts every string (L(N) = Σ*, the set of all strings) if M accepts w, and nothing (∅) otherwise.

**Not recognisable.** Map ⟨M, w⟩ to ⟨M_rej, N⟩ where M_rej rejects everything. So M accepts w ⇔ L(N) ≠ L(M_rej). That is A_TM ≤ₘ EQ̄_TM, hence Ā_TM ≤ₘ EQ_TM. Ā_TM is unrecognisable, so EQ_TM is too.

**Not co-recognisable.** Same N, but compare with a machine M_all that accepts everything: M accepts w ⇔ L(N) = L(M_all). That is A_TM ≤ₘ EQ_TM, hence Ā_TM ≤ₘ EQ̄_TM, so EQ̄_TM is unrecognisable.

```formula
f_1(⟨M, w⟩) = ⟨M_rej, N⟩
f_2(⟨M, w⟩) = ⟨M_all, N⟩
A_TM ≤_m EQ̄_TM   so   Ā_TM ≤_m EQ_TM
A_TM ≤_m EQ_TM   so   Ā_TM ≤_m EQ̄_TM
where
f_1, f_2: the two mapping reductions, total computable functions on encodings
M: the given machine
w: the given input
N: the machine that ignores its input and accepts iff M accepts w
M_rej: a machine that rejects every input, so L(M_rej) = ∅
M_all: a machine that accepts every input, so L(M_all) = Σ*
A_TM: the acceptance problem: pairs where M accepts w
Ā_TM: the complement of A_TM: pairs where M does not accept w; it is not recognisable
EQ_TM: the equivalence problem: pairs of machines with the same language
EQ̄_TM: the complement of EQ_TM: pairs of machines whose languages differ
≤_m: is mapping reducible to
In words: one map turns "M accepts w" into "these two machines differ", the other into "these two machines agree", so neither EQ_TM nor its complement can be recognised.
```

This is why "are these two programs equivalent?" has no general algorithm, neither a complete recogniser for equivalence nor a complete recogniser for inequivalence. Sound tools can still settle particular instances.

## Rice's theorem

Language emptiness and fixed-language equality exemplify a broader theorem due to Rice (1953). Halting itself is not determined solely by the accepted language: rejection and divergence can recognise the same language.

A **semantic property** of TMs is a set P of TM descriptions that depends only on the language: if L(M) = L(N), then either both are in P or neither is. P is a **non-trivial property** if some TM is in P and some TM is not.

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

1. Assume the machines with empty language lie outside P. (If they are, run this argument on the complement of P, which is also non-trivial and semantic; P is decidable iff its complement is.)
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
6. So ⟨M, w⟩ ∈ A_TM ⇔ ⟨M′⟩ ∈ P. That is A_TM ≤ₘ P, and A_TM is undecidable, so P is undecidable. ∎

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

## Living with Rice: approximation

For these non-trivial extensional properties of arbitrary programs, Rice says no analyser can be all three of: **automatic**, **always terminating**, and **exactly correct** on every program. Real tools pick which to give up:

| Approach | Gives up | Example |
|---|---|---|
| Sound over-approximation | completeness: false alarms | type checkers, Astrée |
| Unsound bug finding | soundness: missed bugs | linters, many SAST tools |
| Bounded checking | coverage beyond a bound | CBMC, fuzzing |
| Interactive proof | automation | Coq/Rocq, Isabelle |

Java rejects `int x = flag ? 1 : "a";` even if `flag` is always true: the reference conditional expression must satisfy the target assignment type for both branches, and the string branch is not compatible with `int`. This is a particular language rule, not a restriction uniquely forced by Rice. A different sound language could accept some statically known constant-branch cases.

A terminating type checker can decide a formal typing judgement exactly. The harder question is whether arbitrary programs in a model that permits runtime type faults can ever reach such a fault. In a sufficiently expressive model this is undecidable, by a computable reduction from the halting problem, so an always-terminating sound safety analyser must be conservative. Languages that exclude an error by construction need separate treatment. **Abstract interpretation** (Cousot and Cousot, 1977) provides a framework for sound approximation.

Compiler optimisation is the same story. Perfect dead-code elimination would decide whether code is reachable, which is undecidable, so compilers remove only code they can *prove* is dead.

## Other famous undecidable problems

Computable reductions spread undecidability far beyond machines:

- **Post correspondence problem** (Post, 1946): given dominoes with a top and bottom string, is there a non-empty finite sequence of dominoes, allowing repetitions, whose top and bottom concatenations match? Undecidable, by a computable reduction from A_TM.
- **CFG problems**: whether a CFG is ambiguous, whether it generates every string, and whether two CFGs are equivalent are all undecidable (via PCP or computation histories).
- **Hilbert's tenth problem**: does a polynomial equation with integer coefficients have an integer solution? Undecidable (Matiyasevich, building on Davis, Putnam and Robinson, 1970).
- **Typability and type checking for Curry-style System F**, where pure λ-terms lack explicit type annotations, are undecidable (Wells, 1994). Do not confuse this with decidable checking of fully annotated Church-style System F. Practical languages use restricted inference and/or annotations, with details depending on their type systems.

## Pitfalls

- **Reducing in the wrong direction.** To show B is hard: known-hard A ≤ B.
- **f must be computable and total.** These mapping reductions construct M′ without running an unbounded simulation of M. Other computable reductions may use bounded simulation or other terminating computations; "never run a machine" is not a general rule.
- **Rice is about languages, not machines.** "Does M run for more than n steps on w" or "does M have a useless state" are about the machine, so Rice says nothing about them (even if some are undecidable for other reasons).
- **Undecidable in general is not hopeless in practice.** Termination provers, model checkers and type systems solve huge numbers of real instances. They just can't solve all of them.

## Key takeaways
- A ≤ₘ B means a computable f with x ∈ A ⇔ f(x) ∈ B. To prove B undecidable, reduce a known undecidable A to B.
- The constructions here emit new machines without waiting for M to halt. A_TM ≤ₘ HALT_TM; E_TM is undecidable, and EQ_TM is neither recognisable nor co-recognisable.
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
