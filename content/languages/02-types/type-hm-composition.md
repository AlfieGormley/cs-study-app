---
id: type-hm-composition
title: Inferring composed functions
level: intermediate
minutes: 5
sourceLesson: type-inference
summary: Hindley–Milner infers the core calculus using constraints, unification and let generalisation.
---

The previous unit used language-specific local inference. This unit studies the simpler Hindley–Milner core: ordinary functions, application and let bindings, before extensions such as overloading or subtyping.

## Global inference: Hindley–Milner

ML, OCaml, Haskell, F# and Elm go much further. Their HM-style cores can infer principal types without annotations. Real languages add features and restrictions, so this is not a guarantee for every program in each language. The system behind this is **Hindley–Milner** (HM), discovered by Roger Hindley (1969) and independently by Robin Milner (1978). Milner's inference procedure is called **Algorithm W**; Luis Damas and Milner proved in 1982 that it always finds the most general type.

HM works in three steps:

1. **Assign** a fresh type variable to every unknown.
2. **Generate constraints** from how things are used.
3. **Solve** the constraints by **unification**, then **generalise** eligible variables not free in the typing environment at a let binding.

### Worked example: compose

```haskell
-- Feed g's result into f.
compose f g x = f (g x)
```

Type-theory papers use a compact notation for this, and the next three steps use it. A colon means "has type", and an arrow builds a function type.

Steps 1 and 2: give each unknown a type variable, then read off one constraint per function call. `g x` applies `g` to `x`, so `g` must be a function from `t3` to some new type `t4`. `f (g x)` then applies `f` to that `t4`, giving another new type `t5`:

```formula
f : t1    g : t2    x : t3
t2 = t3 → t4
g x : t4
t1 = t4 → t5
f (g x) : t5
where
f, g, x: the three parameters of compose, whose types are not known yet
t1, t2, t3: type variables: placeholder types for f, g and x, still to be worked out
t4, t5: fresh type variables invented for the results of the calls g x and f (g x)
:: "has type": f : t1 means "f has type t1"
→: the function-type arrow: t3 → t4 is the type of a function that takes a t3 and returns a t4
=: a constraint: the two sides must turn out to be the same type
g x: function application: g called with the argument x (Haskell puts no brackets round arguments)
In words: calling g on x forces g to be a function from x's type to something; calling f on that result forces f to be a function from that something to the final result.
```

Step 3: substitute the solved `t1` and `t2` back into the type of `compose`, which takes `f`, then `g`, then `x`, and returns `t5`:

```formula
compose : t1 → t2 → t3 → t5
compose : (t4 → t5) → (t3 → t4) → t3 → t5
where
compose: the function being typed
t1, t2, t3, t4, t5: the type variables from steps 1 and 2; t1 = t4 → t5 and t2 = t3 → t4
:: "has type"
→: the function-type arrow. Arrows group to the right, so A → B → C means A → (B → C): take an A, then a B, and return a C. This is how Haskell writes a function of several arguments (currying)
In words: compose takes a function from t4 to t5, then a function from t3 to t4, then a t3, and returns a t5.
```

Nothing constrains `t3`, `t4` or `t5`, so they become **universally quantified**: the caller may choose any types for them. Renamed tidily (`a` for `t3`, `b` for `t4`, `c` for `t5`):

```formula
compose : ∀a b c. (b → c) → (a → b) → a → c
where
compose: the function being typed
a, b, c: type variables, renamed from t3, t4 and t5
∀a b c.: "for all types a, b and c": the type is polymorphic, and each use of compose may pick its own a, b and c
:: "has type"
→: the function-type arrow, grouping to the right
In words: for any three types, compose turns a function from b to c and a function from a to b into a function from a to c.
```

In Haskell's own syntax, `::` means "has type", `->` is the arrow, and the "for all" is left implicit:

```haskell
compose :: (b -> c) -> (a -> b) -> a -> c
```

That is exactly the type of Haskell's built-in `(.)`. The compiler found it with zero annotations, and it is the **principal type**: every other valid type for `compose`, such as `(Int -> Bool) -> (String -> Int) -> String -> Bool`, is an instance of it.

## Key takeaways
- Hindley–Milner infers the core calculus using constraints, unification and let generalisation.
- A principal type contains every valid instance without adding unnecessary equalities.

## Further reading
- [Milner: A theory of type polymorphism](https://homepages.inf.ed.ac.uk/wadler/papers/papers-we-love/milner-type-polymorphism.pdf)
- [Damas and Milner: Principal type schemes](https://steshaw.org/hm/milner-damas.pdf)
- [Haskell 2010: Declarations and types](https://www.haskell.org/onlinereport/haskell2010/haskellch4.html)
