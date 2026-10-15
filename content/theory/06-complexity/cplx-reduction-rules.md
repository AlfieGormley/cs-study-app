---
id: cplx-reduction-rules
title: "Reading and composing reductions"
level: intermediate
minutes: 5
summary: "A many-one reduction preserves yes and no answers through one polynomial-time translation."
sourceLesson: cplx-np-completeness
---

Thousands of problems in NP have resisted polynomial-time algorithms: scheduling, routing, packing, colouring, satisfiability. In 1971 Stephen Cook found that many of them are secretly the same problem. Solve one efficiently and you have solved them all.

The tool that ties them together is the **polynomial-time reduction**, and the problems at the top of the pile are called **NP-complete**.

## Reductions: "B is at least as hard as A"

A **polynomial-time (many-one, or Karp) reduction** from problem A to problem B is a function f such that:

- f is computable in polynomial time, and
- for every input x: x is a yes-instance of A **if and only if** f(x) is a yes-instance of B.

In symbols:

```formula
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

```formula
A ≤_p B and B ≤_p C  gives  A ≤_p C
A ≤_p B and B ∈ P  gives  A ∈ P
where
A, B, C: decision problems
≤_p: "polynomial-time reduces to": A ≤_p B means a polynomial-time translation maps every instance of A to an instance of B with the same yes/no answer
∈: "is a member of" (belongs to the class)
P: the complexity class P: decision problems a deterministic algorithm solves in polynomial time (at most about n^k steps on an n-bit input, for some fixed k)
In words: reductions chain together, and anything that reduces to an efficiently solvable problem is itself efficiently solvable.
```

Why the composition stays polynomial: the first translation f cannot write more output than it has time to write, so the second translation g runs on an input that is at most polynomially long.

```formula
t_total ≤ p(n) + q(p(n))
t_total ≤ n^2 + (n^2)^3 = n^2 + n^6
where
t_total: the number of steps to compute g(f(x)), the composed translation from A to C
n: the length of the input x, in bits
p(n): the polynomial step bound of f on an n-bit input; here n^2
q(m): the polynomial step bound of g on an m-bit input; here m^3
In words: f takes at most p(n) steps and so outputs at most p(n) bits; g then takes at most q(p(n)) steps. With bounds n^2 and m^3 the total is about n^6, still a polynomial.
```

## Key takeaways

- A many-one reduction preserves yes and no answers through one polynomial-time translation.
- An algorithm for the target solves the source problem.
- Polynomial output length makes composition stay polynomial.

## Further reading

- [Computational Complexity — Arora and Barak](https://theory.cs.princeton.edu/complexity/book.pdf)
- [Theory of Computation — MIT OpenCourseWare](https://ocw.mit.edu/courses/18-404j-theory-of-computation-fall-2020/)
