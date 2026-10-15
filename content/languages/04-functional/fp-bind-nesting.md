---
id: fp-bind-nesting
title: Flattening nested effects with bind
level: intermediate
minutes: 4
sourceLesson: fp-functors-monads
summary: Map nests a wrapper returned by its callback.
---

Map nests a wrapper returned by its callback. This unit develops that mechanism using the earlier units as prerequisites.

## Where map runs out

Now try the staircase. `find_team` itself returns a `Maybe`, because a user might have no team:

```python
# map wraps the callback result again.
find_user(1).map(find_team)
# Some(Some({'lead': 2}))
```

A box inside a box. `map` boxes whatever `f` returns, and `f` already returned a box. Chain a third step and you'd have three layers, each needing its own unwrap.

The same nesting appears with every box type:

| Box | `map` with a box-returning `f` |
|---|---|
| list | list of lists |
| Optional | Optional of Optional |
| Result | Result of Result |
| Promise-like wrapper with a separate map | nested wrapper; JavaScript then instead auto-flattens |

What we want is "map, then squash the two layers into one". That operation has many names: `flat_map`, `flatMap`, `and_then`, `bind`, `SelectMany`, `>>=`, and in JavaScript, `then`.

## Monads: boxes you can chain

Add `flat_map` to the class:

```python
# Bind returns the compatible box directly.
    def flat_map(self, f):
        if not self.ok:
            return self
        # f already returns a box
        return f(self.value)
```

The only difference from `map` is the last line: `f` returns a box, so we return it as-is instead of wrapping it again. Now the staircase is flat:

```python
# An absent intermediate skips later steps.
(find_user(uid)
    .flat_map(find_team)
    .flat_map(find_lead)
    .map(lambda u: u.email))
```

Each step runs only if the previous one produced a value. The first `Nothing` short-circuits the rest of the chain, exactly like the nested `if`s, but the checking lives in one place.

A **monad** provides two operations satisfying the laws below; a box is an intuition, since state and continuation monads need not be containers:

1. **monadic wrap**: put a plain value into a box (`Some(x)`, `[x]`, `Ok(x)`, a lawful abstract wrap operation). Haskell calls it `return` or `pure`.
2. **flat_map**: run a box-returning function on the contents and keep a single layer of box.

That's it. Every monad is a functor too, because `map(f)` is just `flat_map` followed by wrapping `f`'s result:

```formula
map(f, m) = m >>= (wrap ∘ f)
where
map: the functor operation: apply f to the contents and keep the box
f: a function that returns a plain value
m: any box value
>>=: "bind", Haskell's symbol for flat_map: m >>= g means m.flat_map(g)
wrap: the monad's operation that puts a plain value into a box (Some, Ok or a singleton list)
∘: function composition: (wrap ∘ f)(x) = wrap(f(x))
In words: to map f, flat_map a function that runs f and then boxes its result, so flat_map never sees a nested box.
```

For example, `Some(3).flat_map(lambda x: Some(x + 1))` gives `Some(4)`, exactly what `Some(3).map(lambda x: x + 1)` gives.

> [!tip] The one-sentence version
> A monad lets you write a sequence of steps that each return a boxed value, and the box type decides what "and then" means: stop on missing, stop on error, try every option, or wait.

## Key takeaways
- Map nests a wrapper returned by its callback.
- Bind chains a compatible wrapper-returning callback without adding a layer.

## Further reading
- [Haskell base: functor and monad laws](https://hackage.haskell.org/package/base/docs/Control-Monad.html)
- [Wadler: Monads for functional programming](https://homepages.inf.ed.ac.uk/wadler/papers/marktoberdorf/baastad.pdf)
