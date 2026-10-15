---
id: para-nonstrict-arguments
title: Call by name, call by need and short circuiting
level: advanced
minutes: 3
sourceLesson: para-scope-closures
summary: Call by name repeats demand; call by need shares an evaluated result.
---

Some languages defer an argument expression until its value is needed. The distinction between repeating a deferred computation and sharing its result affects both work and memory.

## Non-strict: evaluate arguments only when needed

- **Call by name** (Algol 60's default; Scala's `x: => Int` parameters): the argument expression is passed unevaluated and re-evaluated *every time* the parameter is used.
- **Call by need** (Haskell): like call by name, but the result is cached after the first evaluation. This is **lazy evaluation**. R's function arguments are also lazy "promises".

The difference matters when an argument is expensive, has side effects, or never terminates. In this pseudocode, `loop_forever()` stands for a nonterminating expression; it is deliberately not supplied as a runnable function:

```
def first(a, b): return a

first(1, loop_forever())
```

| Strategy | Result |
|---|---|
| Call by value | Hangs: `b` is evaluated first |
| Call by name | Returns 1: `b` never used |
| Call by need | Returns 1: `b` never used |

In the abstract strategies, if all three uses demand the argument value, call by name evaluates the expression on each demand, while call by need shares the result after the first evaluation. A real compiler may optimise pure expressions while preserving language semantics. With side effects, call by name can even give different values each time, which Algol programmers exploited in a trick called Jensen's device.

Even strict languages have non-strict corners. `and`, `or` and the ternary `a if c else b` short-circuit: in `x is not None and x.ok`, the right side only runs if needed. Python generators and iterators are lazy too, as the functional basics lesson showed.

Laziness has costs. Unevaluated expressions ("thunks") use memory, and it's hard to predict when work happens. Haskell programs sometimes leak memory by building long chains of thunks, which is why it offers strictness annotations and functions like `foldl'`.

## Pitfalls checklist

- Late-binding closures in loops: bind the value with a default argument, `partial` or `let`.
- `UnboundLocalError`: an assignment later in the function made the name local. Add `global`/`nonlocal` or rename.
- **Mutable defaults**: use `None` and create inside.
- Surprise mutation: under call by sharing, functions can mutate arguments. Copy defensively or use immutable types.
- **Dangling captures** in C++: capturing by reference in a lambda that outlives the scope.
- Leaky closures: long-lived callbacks can retain the captured objects they need; implementations may omit unused bindings.

## Key takeaways
- Call by name repeats demand; call by need shares an evaluated result.
- Laziness changes work and space behavior and does not force every nested value.

## Further reading
- [Haskell: non-strict expression semantics](https://www.haskell.org/onlinereport/haskell2010/haskellch3.html)
- [ALGOL 60 revised report](https://www.softwarepreservation.org/projects/ALGOL/report/Algol60_revised_report_CACM.pdf)
