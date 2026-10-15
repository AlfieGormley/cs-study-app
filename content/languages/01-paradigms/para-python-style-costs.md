---
id: para-python-style-costs
title: Python style, copying and shallow freezing
level: intermediate
minutes: 3
sourceLesson: para-multi-paradigm
summary: Python recursion and repeated list joining have practical limits.
---

Python supports functional techniques, but its recursion, containers and copying rules still apply. Trace allocation and mutation before choosing an apparently concise expression.

## Work with the language, not against it

A multi-paradigm language still has a *grain*: styles it supports well and styles it only tolerates. Fighting the grain costs performance and readability.

## Python

Python supports functional style but isn't built around it:

- No tail-call optimisation. Guido van Rossum rejected it deliberately, partly to keep full stack traces. A standard tested CPython configuration reports a limit of 1,000 (configurable), so a recursive sum over a 10,000-item list raises `RecursionError`. Use a loop or `sum()`.
- Lambdas are single expressions. Anything longer should be a named `def`.
- Immutability is shallow, and you must ask for it. A `frozen=True` dataclass blocks ordinary field assignment, but a list stored in a field can still be mutated. Use tuples and `frozenset` for the contents and ensure their nested contents are immutable too.
- Copying is not free. `sum(list_of_lists, [])` looks elegant but builds a new list at every step, which is quadratic for n single-element lists; more generally cost depends on both the number and lengths of the lists. `itertools.chain.from_iterable` is linear.

Where the quadratic cost comes from: `sum` starts from `[]` and does `acc = acc + item` once per list. Each `+` builds a brand-new list and copies everything gathered so far, so with n lists of one item each, step k copies k items.

```formula
copies = 1 + 2 + … + n
copies = n(n + 1) / 2 ≈ n^2 / 2
where
copies: the total number of element copies made by all the + steps
n: the number of single-item lists being joined
…: "and so on", continuing the pattern up to n
n^2: n × n, n squared
≈: approximately equal to; for large n the n^2 / 2 part dominates
In words: every step re-copies all the earlier items, so the total work grows with the square of the number of lists.
```

For 10,000 lists that is 50,005,000 copies, about 50 million, against 10,000 for `chain.from_iterable`. Ten times more lists means about a hundred times more copying. This is what **quadratic time** means: cost growing with n squared, written O(n²). **Linear time** means cost growing in direct proportion to n, written O(n).

## Key takeaways
- Python recursion and repeated list joining have practical limits.
- A frozen dataclass can still contain mutable objects.

## Further reading
- [Guido van Rossum: tail recursion elimination](https://neopythonic.blogspot.com/2009/04/tail-recursion-elimination.html)
- [Python: frozen dataclasses](https://docs.python.org/3/library/dataclasses.html)
