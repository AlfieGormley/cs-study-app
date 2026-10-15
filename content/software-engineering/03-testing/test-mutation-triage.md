---
id: test-mutation-triage
sourceLesson: test-flaky-coverage-mutation
title: Triage equivalent mutants and measure suite health
level: advanced
minutes: 3
summary: Equivalence depends on the observed contract and input domain.
---

The previous unit showed mutants that missing boundary tests could kill. Some survivors cannot be killed under the intended contract; others are too costly to analyse across an entire codebase. Triage turns the result into useful work.

## Equivalent mutants and cost

Some mutants don't change behaviour at all, so no test can kill them. These are **equivalent mutants**:

```python
def larger(a, b):
    # Equal ints differ in source, not
    # value.
    if a > b:     # mutant: a >= b
        return a
    return b
```

For ordinary integer inputs under a value-only maximum contract, equal inputs give equal output values. The mutant is equivalent under that contract, but not universally in Python: callers can observe object identity, and equal-valued floats such as -0.0 and 0.0 have distinguishable signs. Deciding equivalence is undecidable in general, so a human has to judge surviving mutants, which takes time.

Mutation testing is also expensive: each mutant means re-running (part of) the suite, and a large codebase has hundreds of thousands of potential mutants. Tools reduce the cost by running only the tests that cover each mutated line, and by mutating only changed code.

Google's approach, described in *State of Mutation Testing at Google* (2018), mutates only lines changed in a code review, skips "arid" lines unlikely to matter (such as logging), and shows a few surviving mutants to the author and reviewer as review comments. That turns an expensive batch metric into targeted, actionable feedback.

Tools: **mutmut** and **Cosmic Ray** for Python, **PIT** (Pitest) for the JVM, **Stryker** for JavaScript, C# and Scala.

## Putting it together

```
 coverage   -> what never runs?
 mutation   -> what runs but is
               never really checked?
 flake rate -> can we trust red?
```

A healthy team watches all three, uses them to find weak spots, and never turns any of them into a target to game.

## Key takeaways
- Equivalence depends on the observed contract and input domain.
- Changed-line mutation analysis makes expensive test-strength checks more actionable.
- Read coverage, mutation results and flake rates together without gaming a target.

## Further reading
- [Code Coverage Best Practices — Google Testing Blog](https://testing.googleblog.com/2020/08/code-coverage-best-practices.html)
- [Mutation testing basics — PIT](https://pitest.org/quickstart/basic_concepts/)
- [State of Mutation Testing at Google — Google Research](https://research.google/pubs/state-of-mutation-testing-at-google/)
- [mutmut documentation](https://mutmut.readthedocs.io/)
