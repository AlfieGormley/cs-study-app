---
id: logp-invariants-hoare
title: Hoare triples and invariants across systems
level: intermediate
minutes: 3
sourceLesson: logp-invariants
summary: A partial-correctness Hoare triple promises a postcondition only if execution terminates.
---

## Hoare logic in one paragraph

Tony Hoare (1969) wrote correctness claims as **Hoare triples** {P} S {Q}: if **precondition** P holds before running statement S, and S terminates, then postcondition Q holds after. The rule for loops is the recipe above:

```formula
{I ∧ B} S {I}
gives   {I} W {I ∧ ¬B}
where
{P} S {Q}: a Hoare triple: if P holds before S runs and S terminates, Q holds afterwards
I: the loop invariant
B: the loop condition
S: the loop body, the statements run each iteration
W: the whole loop, `while B: S`
∧: AND
¬: NOT; ¬B means the loop condition is false
In words: if one run of the body, started with I and B true, ends with I true, then the whole loop, started with I true, ends (if it ends) with I true and B false.
```

Textbooks draw the rule as a fraction: the premise above a line, the conclusion below:

```
       {I ∧ B}  body  {I}
------------------------------
{I}  while B: body  {I ∧ ¬B}
```

If the body preserves I whenever the condition B is true, then the loop as a whole preserves I and exits with not B. Tools such as **Dafny** ask you to write invariants and then check these obligations automatically with an SMT solver.


## Invariants beyond loops

The same idea scales up from loops to whole systems.

- **Data structure (representation) invariants**: a binary min-heap's parent is no greater than either child; a red-black tree's equal black height on every path; a chained hash table's "key k is in bucket hash(k) mod m" (the bucket number is the key's hash value, modulo the number of buckets m). Every public method must restore them before returning.
- **Class invariants**: a bank `Account` with balance is at least 0. Constructors establish it; methods preserve it.
- **Database constraints** enforce their defined conditions at specified checking points. Deferrable constraints may be checked at commit; PostgreSQL CHECK accepts TRUE or NULL, and default UNIQUE handling permits multiple NULLs. Add NOT NULL when required.
- **Distributed systems**: "at most one leader per term" in Raft. Amazon engineers used TLA+ to model-check invariants like these and reported finding subtle bugs in systems including DynamoDB that testing had missed.

> [!tip] Put the invariant in the code
> Write the invariant as a comment, and in debug builds as an `assert`. An assertion detects a violation when execution reaches that check; the underlying bug may have occurred earlier. Python can disable assert statements under optimisation, so do not use them as mandatory input validation.


## Finding invariants

There is no algorithm for this in general, but a few heuristics cover most loops:

1. **Replace a constant with a variable** in the postcondition (sum(a) becomes sum(a[:i])).
2. **Describe the regions** of the array the loop has partitioned (binary search, partition in quicksort, Dutch national flag).
3. **Find the conserved quantity**: something that stays fixed while the variables change (result times base to the power e, gcd(a, b)).
4. **Strengthen if stuck**: if maintenance can't be proved, the invariant is usually missing a fact, just like strengthening an induction hypothesis.


## Key takeaways
- A partial-correctness Hoare triple promises a postcondition only if execution terminates.
- Representation and class invariants need defined checking boundaries; assertions check executions rather than prove all executions.

## Further reading
- [MIT Mathematics for Computer Science](https://ocw.mit.edu/courses/6-042j-mathematics-for-computer-science-spring-2015/mit6_042js15_textbook.pdf)
- [Dafny](https://dafny.org/)
