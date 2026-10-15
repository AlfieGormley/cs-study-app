---
id: type-let-polymorphism
title: Let-polymorphism and higher ranks
level: intermediate
minutes: 3
sourceLesson: type-inference
summary: Each use of a generalised let-bound definition gets a fresh type instance.
---

Hindley–Milner generalisation makes a reusable identity function different from an unknown function parameter. The earlier composition and unification lessons supply the constraint-solving background.

## Let-polymorphism

HM generalises at `let` bindings, but **not** at lambda parameters. This difference is subtle and important:

```haskell
-- Each ident call chooses its own type.
ok = let ident x = x
     in (ident 1, ident True)

-- Both uses must share one input type.
bad f = (f 1, f True)
```

In `ok`, `ident` is let-bound, so after inferring that its argument and result share a type, HM generalises that type variable. Each use then gets a fresh copy of `t`: one at a number type, one at `Bool`:

```formula
ident : ∀t. t → t
ident 1 : n        with t := n
ident True : Bool  with t := Bool
where
ident: the let-bound identity function in ok
t: a type variable
∀t.: "for all types t": the type has been generalised, so each use may choose its own t
n: the type of the literal 1, which can be any number type (Haskell writes this as the constraint Num n)
True: one of the two values of Bool
Bool: the type with the two values True and False
:: "has type"
→: the function-type arrow
:=: "is replaced by", for that one use only
In words: because ident is generalised, the call on 1 and the call on True each pick their own t, so they don't conflict.
```

In `bad`, `f` is a parameter. Its type is a single unknown `t`, with no "for all", shared across both uses:

```formula
f : t
t = n → r1
t = Bool → r2
n = Bool
where
f: the parameter of bad; a lambda parameter gets one type, not a generalised one
t: f's single type
n: the type of the literal 1, which must be a number type (Num n)
r1, r2: the unknown result types of f 1 and f True
Bool: the type with the two values True and False
:: "has type"
→: the function-type arrow
=: a constraint: both sides must be the same type
In words: both calls constrain the same t, which forces the number type n to be Bool; Bool is not a number type, so inference fails.
```

GHC reports this as `No instance for (Num Bool)`. Allowing `f` to be polymorphic would need **rank-2 types**, which go beyond ordinary HM let-polymorphism. Rank-2 inference is decidable in the corresponding System F fragment; rank-3 and higher inference is undecidable. GHC requires annotations for higher-rank polymorphic arguments.

## Key takeaways
- Each use of a generalised let-bound definition gets a fresh type instance.
- Ordinary lambda parameters remain monomorphic; explicitly polymorphic arguments need richer types.

## Further reading
- [Haskell 2010: Declarations and types](https://www.haskell.org/onlinereport/haskell2010/haskellch4.html)
- [Damas and Milner: Principal type schemes](https://steshaw.org/hm/milner-damas.pdf)
- [GHC: Higher-rank polymorphism](https://downloads.haskell.org/ghc/latest/docs/users_guide/exts/rank_polymorphism.html)
- [Kfoury and Wells: Rank-2 type inference](https://3e8.org/pub/scheme/doc/lisp-pointers/v7i3/p196-kfoury.pdf)
