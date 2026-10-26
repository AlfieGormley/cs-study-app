---
id: compu-mapping-reductions
title: Total mappings and the direction of hardness
level: advanced
minutes: 5
summary: A mapping reduction is a total computable transformation preserving yes and no answers.
sourceLesson: compu-reductions-rice
---

The halting problem took a clever self-referential argument. You don't want to invent a new paradox for every problem. Instead, you use a **computable reduction**: show that if you could solve the new problem B, you could use it to solve a problem A that is already known to be impossible.

The pay-off is Rice's theorem, one of the most practically important results in computer science. It limits exact, terminating analysis of non-trivial extensional properties for arbitrary programs. This does not mean every analysis task or formal type-checking judgement is undecidable.

## The idea

"A reduces to B" means: **A is no harder than B**. If you had an algorithm for B, you could build an algorithm for A by translating each A-question into a B-question.

The logic is a contrapositive: if a solver for the target would solve an impossible source problem, the target cannot have a solver either. For example, machine acceptance reduces to halting, so a halting decider would contradict the already-proved impossibility of an acceptance decider.

> [!analogy] Real-world analogy: A plug adaptor
> An adaptor lets an appliance use an outlet with a different shape. The appliance works only when the adaptor and a working outlet are both available.
>
> **How it maps:** The reduction adapts a source question into a target question. A working target solver plus that terminating adaptation supplies a source solver.
>
> **Where it stops:** Reductions must preserve both yes and no answers exactly. Physical compatibility alone does not establish that logical guarantee or a bound on running time.

> [!warning] The direction is everything
> To prove B undecidable, reduce a **known undecidable** problem A **to** B. Reducing B to A shows only that B is no harder than A, which alone does not prove B undecidable. Getting this backwards is the most common mistake in computability proofs.

## Mapping reductions

A is **mapping reducible** to B when a total computable function transforms every source input while preserving its yes/no answer. The notation and condition are:

```formula essential
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

The machine examples below describe well-formed encodings. To make each map total on all strings, detect malformed encodings and send them to a fixed no-instance of the target, taking malformed strings as non-members of the source. Complement arguments use complements in that same universe, including malformed strings. When complementing a displayed map, keep its malformed-input branch unchanged; it then maps source-complement yes-instances to target-complement yes-instances.

Useful properties, all following from the definition:

- A target decider or recogniser supplies one for the source.
- The same map works when both languages are complemented.
- Maps compose, so mapping reducibility is transitive.

```formula reference
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

## Key takeaways

- A mapping reduction is a total computable transformation preserving yes and no answers.
- To prove a new target hard, reduce a known hard source to it.
- Decidability and recognisability pass backwards along the mapping.

## Further reading

- [Lynch: mapping reductions and Rice’s theorem](https://ocw.mit.edu/courses/6-045j-automata-computability-and-complexity-spring-2011/resources/mit6_045js11_lec09/)
