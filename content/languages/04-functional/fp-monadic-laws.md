---
id: fp-monadic-laws
title: Monad laws and safe regrouping
level: intermediate
minutes: 3
sourceLesson: fp-functors-monads
summary: Left and right identity say wrapping adds no extra behaviour.
---

Left and right identity say wrapping adds no extra behaviour. This unit develops that mechanism using the earlier units as prerequisites.

## The rules, in plain words

There are three "monad laws". You'll rarely write them down, but they're what make refactoring chains safe:

1. **Wrapping then chaining does nothing extra.** `Some(x).flat_map(f)` is the same as `f(x)`.
2. Chaining with wrap does nothing. `m.flat_map(Some)` is the same as `m`.
3. Grouping doesn't matter. `m.flat_map(f).flat_map(g)` equals `m.flat_map(lambda x: f(x).flat_map(g))`.

These are usually called **left identity**, **right identity** and **associativity**. In the standard notation:

```formula
wrap(x) >>= f = f(x)
m >>= wrap = m
(m >>= f) >>= g = m >>= (λx. f(x) >>= g)
where
>>=: "bind", Haskell's symbol for flat_map: m >>= f means m.flat_map(f)
wrap: put a plain value into a box (Some, Ok or a singleton list; Haskell calls it return or pure)
x: any plain value
m: any box value (a monadic value)
f, g: functions that take a plain value and return a box
λ: lambda, the Greek letter that marks an anonymous function: λx. e is the function that takes x and returns e, written lambda x: e in Python
In words: wrapping a value and then binding f is the same as calling f; binding wrap changes nothing; and binding f then g is the same as binding the single combined step "f, then g".
```

For example, with the earlier `Maybe` and the callback `lambda x: Some(x + 1)`: `Some(2).flat_map(f)` is `Some(3)`, which is exactly `f(2)`, as the first law requires.

Rule 3 is the useful one in practice: it says you can pull a few steps out into a helper function, or inline one, without changing behaviour. It justifies regrouping lawful chains. Refactoring real async code must also preserve cancellation, exception boundaries and observable microtask scheduling.

## Key takeaways
- Left and right identity say wrapping adds no extra behaviour.
- Associativity permits regrouping lawful compatible chains.

## Further reading
- [Haskell base: functor and monad laws](https://hackage.haskell.org/package/base/docs/Control-Monad.html)
- [Wadler: Monads for functional programming](https://homepages.inf.ed.ac.uk/wadler/papers/marktoberdorf/baastad.pdf)
