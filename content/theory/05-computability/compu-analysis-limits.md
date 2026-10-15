---
id: compu-analysis-limits
title: Conservative analysis and other undecidable problems
level: advanced
minutes: 4
summary: Exact total analysis of an undecidable property cannot cover every arbitrary program.
sourceLesson: compu-reductions-rice
---

## Living with Rice: approximation

For these non-trivial extensional properties of arbitrary programs, Rice says no analyser can be all three of: **automatic**, **always terminating**, and **exactly correct** on every program. Real tools pick which to give up:

| Approach | Gives up | Example |
|---|---|---|
| Sound over-approximation | completeness: false alarms | type checkers, Astrée |
| Unsound bug finding | soundness: missed bugs | linters, many SAST tools |
| Bounded checking | coverage beyond a bound | CBMC, fuzzing |
| Interactive proof | automation | Coq/Rocq, Isabelle |

Java rejects `int x = flag ? 1 : "a";` even if `flag` is always true: the reference conditional expression must satisfy the target assignment type for both branches, and the string branch is not compatible with `int`. This is a particular language rule, not a restriction uniquely forced by Rice. A different sound language could accept some statically known constant-branch cases.

A terminating type checker can decide a formal typing judgement exactly. The harder question is whether arbitrary programs in a model that permits dynamic typing faults can ever reach such a fault. In a sufficiently expressive model this is undecidable, by a computable reduction from the halting problem, so an always-terminating sound safety analyser must be conservative. Languages that exclude an error by construction need separate treatment. **Abstract interpretation** (Cousot and Cousot, 1977) provides a framework for sound approximation.

Compiler optimisation is the same story. Perfect dead-code elimination would decide whether code is reachable, which is undecidable, so compilers remove only code they can *prove* is dead.

## Other famous undecidable problems

Computable reductions spread undecidability far beyond machines:

- **Post correspondence problem** (Post, 1946): given dominoes with a top and bottom string, is there a non-empty finite sequence of dominoes, allowing repetitions, whose top and bottom concatenations match? Undecidable, by a computable reduction from A_TM.
- **CFG problems**: whether a CFG is ambiguous, whether it generates every string, and whether two CFGs are equivalent are all undecidable (via PCP or computation histories).
- **Hilbert's tenth problem**: does a polynomial equation with integer coefficients have an integer solution? Undecidable (Matiyasevich, building on Davis, Putnam and Robinson, 1970).
- **Typability and type checking for Curry-style System F**, where pure λ-terms lack explicit type annotations, are undecidable (Wells, 1994). Do not confuse this with decidable checking of fully annotated Church-style System F. Practical languages use restricted inference and/or annotations, with details depending on their type systems.

## Pitfalls

- **Reducing in the wrong direction.** To show a target problem is hard, reduce a known hard source to that target.
- **f must be computable and total.** These mapping reductions construct M′ without running an unbounded simulation of M. Other computable reductions may use bounded simulation or other terminating computations; "never run a machine" is not a general rule.
- **Rice is about languages, not machines.** "Does M run for more than n steps on w" or "does M have a useless state" are about the machine, so Rice says nothing about them (even if some are undecidable for other reasons).
- **Undecidable in general is not hopeless in practice.** Termination provers, model checkers and type systems solve huge numbers of real instances. They just can't solve all of them.

## Key takeaways

- Exact total analysis of an undecidable property cannot cover every arbitrary program.
- Formal type checking can be decidable even when general event reachability for runtime faults is not.
- The model and precise question matter: CFG membership is decidable, but CFG ambiguity and the question of generating every string are not.

## Further reading

- [Java Language Specification: the conditional operator](https://docs.oracle.com/javase/specs/jls/se25/html/jls-15.html#jls-15.25)
- [Cousot and Cousot: abstract interpretation](https://www.di.ens.fr/~cousot/COUSOTpapers/POPL77.shtml)
- [Wells: Curry-style System F undecidability](https://lics.siglog.org/archive/1994/Wells-Typabilityandtypech.html)
