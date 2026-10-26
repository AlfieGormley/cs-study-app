---
id: cplx-reduction-rules
title: "Reading and composing reductions"
level: intermediate
minutes: 5
summary: "A many-one reduction preserves yes and no answers through one polynomial-time translation."
sourceLesson: cplx-np-completeness
---

Thousands of problems in NP have resisted polynomial-time algorithms: scheduling, routing, packing, colouring, satisfiability. Cook’s 1971 theorem began a way to relate such problems: an efficient algorithm for any NP-complete problem would give one for every problem in NP.

The tool that ties them together is the **polynomial-time reduction**, and the problems at the top of the pile are called **NP-complete**.

## Reductions: "B is at least as hard as A"

A **polynomial-time (many-one, or Karp) reduction** from problem A to problem B is a function f such that:

- f is computable in polynomial time, and
- for every input x: x is a yes-instance of A **if and only if** f(x) is a yes-instance of B.

In symbols:

```formula essential
A ≤_p B
x ∈ A  iff  f(x) ∈ B   for every x
where
A, B: decision problems, each viewed as the set of inputs whose answer is yes
≤_p: "polynomial-time reduces to": A ≤_p B means a polynomial-time translation maps every instance of A to an instance of B with the same yes/no answer, so B is at least as hard as A
x: any input (instance) of problem A, written as a string of bits
f: the reduction: a function, computable in polynomial time, that turns an instance of A into an instance of B
f(x): the instance of B that f produces from x
∈: "is a member of": x ∈ A means x is a yes-instance of A
In words: A reduces to B when a fast translation f turns every question about A into a question about B with exactly the same answer.
```

Read the reduction notation as "A is no harder than B", because any algorithm for B gives one for A: compute f(x), then ask B.

For example, Hamiltonian cycle (is there a cycle visiting every vertex exactly once?) reduces to TSP (is there a tour of tour cost at most some budget?). Given a graph with 10 vertices, f gives every edge weight 1, every missing edge weight 2, and sets the budget to 10. A tour of cost 10 must use only weight-1 edges, so the TSP answer is yes exactly when the graph has a Hamiltonian cycle.

```
 x --[ f: poly time ]--> f(x)
 f(x) --[ solver for B ]--> yes/no
 together: an algorithm for A
```

Two properties do most of the work:

- **Transitive**: if A reduces to B and B reduces to C, then A reduces to C. Compose the two translations; a polynomial of a polynomial is a polynomial.
- **Downward closure of P**: if A reduces to B and B can be solved in polynomial time, so can A.

Why composition stays polynomial: the first translation cannot write more output than it has time to write. The second therefore receives only polynomially many bits; a polynomial in that length is still a polynomial in the original length.

> [!analogy] Real-world analogy: Translating an application form
> An office accepts only its own form. A translator copies your request into that format without changing what is being requested, then the office decides it.
>
> **How it maps:** The translation is the reduction, the office is the target solver, and its decision answers the original question. A better office procedure would therefore help everyone whose forms can be translated.
>
> **Where it stops:** A mathematical reduction must preserve both yes and no answers for every input and run in polynomial time. Ordinary paperwork does not guarantee either property.

## Key takeaways

- A many-one reduction preserves yes and no answers through one polynomial-time translation.
- An algorithm for the target solves the source problem.
- Polynomial output length makes composition stay polynomial.

## Further reading

- [Computational Complexity — Arora and Barak](https://theory.cs.princeton.edu/complexity/book.pdf)
- [Theory of Computation — MIT OpenCourseWare](https://ocw.mit.edu/courses/18-404j-theory-of-computation-fall-2020/)
