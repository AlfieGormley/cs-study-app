---
id: type-inference
title: Type inference (Hindley–Milner intuition)
level: intermediate
minutes: 12
summary: How compilers work out types you never wrote, from local inference in Java, Rust and TypeScript to the constraint-and-unification engine of Hindley–Milner in Haskell and OCaml.
---

Some statically typed APIs require repetitive annotations: `ArrayList<String> names = new ArrayList<String>();`. The compiler already knew the right-hand side was an `ArrayList<String>`, so the annotation was pure ceremony.

**Type inference** lets the compiler work types out from how values are used. You get the safety of static checking without most of the typing. How much a language can infer varies enormously, from "the type of this one variable" to "every type in the whole program".

## Local inference: from the right-hand side

The simplest form looks at an initialiser and copies its type to the variable:

```java
// Java 10+
var names = new ArrayList<String>();
var n = names.size(); // int
```

C++ `auto`, C# `var`, Go `:=`, Kotlin `val` and Swift `let` can similarly infer a local from its initialiser. This example does not describe each language’s full inference rules: contextual and bidirectional inference can also contribute.

It has limits. In Java, `var list = new ArrayList<>();` infers `ArrayList<Object>`, because the diamond has nothing to go on. Method parameters and fields must still be annotated.

### TypeScript: local plus contextual

TypeScript infers variable and return types, and also flows types *inwards* from context (**contextual typing**):

```ts
let l = "hi";      // string (widened)
const c = "hi";    // "hi" (literal type)
let xs = [1, "a"]; // (string | number)[]

// x inferred from the array's type:
[1, 2].map(x => x * 2);

function f(x) { return x * 2; }
// error under strict: Parameter 'x'
// implicitly has an 'any' type
```

TypeScript does **not** infer parameter types from how a function body uses them. That last line is the key difference from Hindley–Milner.

### Rust: inference within a function

Rust requires full signatures on functions but infers many local types inside the body, including from **later** uses:

```rust
let mut v = Vec::new(); // Vec<?>
v.push(1u8);            // now Vec<u8>
```

Sometimes nothing pins a type down, and you must help:

```rust
let nums: Vec<i32> = "1 2 3"
    .split(' ')
    .map(|s| s.parse().unwrap())
    .collect();
```

Without the `Vec<i32>` annotation, neither `parse` nor `collect` knows what to produce, and the compiler reports that type annotations are needed (the diagnostic code depends on the unresolved constraint).

Python's mypy does something similar. `x = []` followed by `x.append(1)` in the same scope infers `list[int]`; a bare `x = []` with no later clue is an error: `Need type annotation for "x"`.

## Global inference: Hindley–Milner

ML, OCaml, Haskell, F# and Elm go much further. Their HM-style cores can infer principal types without annotations. Real languages add features and restrictions, so this is not a guarantee for every program in each language. The system behind this is **Hindley–Milner** (HM), discovered by Roger Hindley (1969) and independently by Robin Milner (1978). Milner's inference procedure is called **Algorithm W**; Luis Damas and Milner proved in 1982 that it always finds the most general type.

HM works in three steps:

1. **Assign** a fresh type variable to every unknown.
2. **Generate constraints** from how things are used.
3. **Solve** the constraints by **unification**, then **generalise** eligible variables not free in the typing environment at a let binding.

### Worked example: compose

```haskell
compose f g x = f (g x)
```

Step 1: give the unknowns type variables: `f : t1`, `g : t2`, `x : t3`.

Step 2: read off constraints.

- `g x` applies `g` to `x`, so `g` is a function from `t3` to something new: `t2 = t3 -> t4`, and `g x : t4`.
- `f (g x)` applies `f` to a `t4`: `t1 = t4 -> t5`, and the result is `t5`.

Step 3: substitute back.

```
compose : t1 -> t2 -> t3 -> t5
        = (t4 -> t5) -> (t3 -> t4)
          -> t3 -> t5
```

Nothing constrains `t3`, `t4` or `t5`, so they become universally quantified. Renamed tidily:

```haskell
compose :: (b -> c) -> (a -> b) -> a -> c
```

That is exactly the type of Haskell's built-in `(.)`. The compiler found it with zero annotations, and it is the **principal type**: every other valid type for `compose`, such as `(Int -> Bool) -> (String -> Int) -> String -> Bool`, is an instance of it.

## Unification

Unification asks: what substitution for the type variables makes these two types identical?

| Unify | Result |
|---|---|
| `a` with `Int` | `a := Int` |
| `a -> Int` with `Bool -> b` | `a := Bool, b := Int` |
| `Int` with `Bool` | type error |
| `a` with `a -> b` | infinite type: error |

Here is a small unifier in Python, not a complete Algorithm W implementation. It assumes finite, well-formed type terms and an acyclic substitution. Type variables are strings; other types are tuples like `("->", arg, result)` or `("Int",)`.

```python
def resolve(t, s):
    while isinstance(t, str) and t in s:
        t = s[t]
    return t

def occurs(v, t, s):
    t = resolve(t, s)
    if t == v:
        return True
    if isinstance(t, tuple):
        return any(occurs(v, x, s)
                   for x in t[1:])
    return False

def unify(a, b, s):
    a, b = resolve(a, s), resolve(b, s)
    if a == b:
        return s
    if isinstance(a, str):
        if occurs(a, b, s):
            raise TypeError("infinite type")
        return {**s, a: b}
    if isinstance(b, str):
        return unify(b, a, s)
    if a[0] != b[0] or len(a) != len(b):
        raise TypeError(f"{a} vs {b}")
    for x, y in zip(a[1:], b[1:]):
        s = unify(x, y, s)
    return s
```

Unifying `("->", "a", ("Int",))` with `("->", ("Bool",), "b")` returns `{'a': ('Bool',), 'b': ('Int',)}`.

### The occurs check

What is the type of `self_apply x = x x`? `x : a`, and applying `x` to itself needs `a = a -> b`. Substituting gives `a = (a -> b) -> b = ((a -> b) -> b) -> b`, forever. The **occurs check** (does `a` appear inside the type we're binding it to?) catches this. GHC reports "Occurs check: cannot construct the infinite type".

## Let-polymorphism

HM generalises at `let` bindings, but **not** at lambda parameters. This difference is subtle and important:

```haskell
ok = let ident x = x
     in (ident 1, ident True)

bad f = (f 1, f True)
```

In `ok`, `ident` is let-bound, so after inferring `t -> t` HM generalises it to `forall t. t -> t`. Each use gets a fresh copy: one at a number, one at `Bool`.

In `bad`, `f` is a parameter. Its type is a single unknown `t`, shared across both uses. Unifying "argument is a number" with "argument is `Bool`" fails (GHC says `No instance for (Num Bool)`). Allowing `f` to be polymorphic would need **rank-2 types**, which go beyond ordinary HM let-polymorphism. Rank-2 inference is decidable in the corresponding System F fragment; rank-3 and higher inference is undecidable. GHC requires annotations for higher-rank polymorphic arguments.

## Cost and limits

- **Speed.** In practice HM runs in close to linear time. In theory, deciding ML typability is DEXPTIME-complete (Mairson; Kfoury, Tiuryn and Urzyczyn, 1990): nested `let`s can produce types that double in size at each level. This worst case is not a prediction of typical application performance.
- **Extensions break completeness.** Rich combinations of subtyping, higher-rank types, GADTs and type-level computation can lose principal types, require annotations or make inference undecidable; no such result follows merely from adding any one feature in any form. That is one reason Java, TypeScript and Scala don't use HM: subtyping and overloading don't mix well with it.
- **Type classes add constraints.** Haskell infers `square x = x * x` as `Num a => a -> a`. Sometimes a constraint can't be resolved: `f = show . read` fails with "ambiguous type variable", because nothing says which type to read.
- **Error messages.** The error is reported where unification fails, which can be far from the real mistake. A wrong argument on line 10 may be blamed on line 40.

> [!tip] Annotate the boundaries
> Idiomatic Haskell and OCaml code still writes type signatures on top-level functions, even though they could be inferred. Signatures document intent, give better error locality, and stop a mistake in the body silently changing the inferred type that callers see. Rust requires function signatures; TypeScript can infer exported return types, so explicit exported signatures are a documentation policy rather than a universal compiler requirement.

## Comparison

| Language | Infers | Needs annotations on |
|---|---|---|
| Java, C# | Locals from initialiser | Params, fields, returns |
| TypeScript | Locals, returns, lambdas in context | Function params |
| Rust | Many local types, including later constraints | Function signatures, ambiguous locals |
| Haskell, OCaml | HM-style core expressions | Higher-rank uses, restricted or ambiguous extensions |

## Key takeaways
- Type inference lets a compiler deduce types from use, so static checking needn't mean verbose code.
- Local inference (Java `var`, C++ `auto`) copies an initialiser's type; Rust and TypeScript also use later uses and context within a function.
- Hindley–Milner assigns type variables, collects equality constraints, solves them by unification, and generalises eligible let-bound variables; the HM core has principal types.
- The occurs check rejects infinite types like the one `x x` would need.
- HM generalises at `let`, not at lambda parameters; polymorphic parameters need rank-N types and annotations.
- Even where inference is total, annotating top-level functions improves documentation and error messages.

## Further reading
- [Hindley–Milner type system — Wikipedia](https://en.wikipedia.org/wiki/Hindley%E2%80%93Milner_type_system)
- [Type inference — Wikipedia](https://en.wikipedia.org/wiki/Type_inference)
- [Unification (computer science) — Wikipedia](https://en.wikipedia.org/wiki/Unification_(computer_science))
- [Type inference — TypeScript handbook](https://www.typescriptlang.org/docs/handbook/type-inference.html)
- [Inference — Rust by Example](https://doc.rust-lang.org/rust-by-example/types/inference.html)
- [Local variable type inference style guide — OpenJDK](https://openjdk.org/projects/amber/guides/lvti-style-guide)
- [Efficient and insightful generalization (Oleg Kiselyov)](https://okmij.org/ftp/ML/generalization.html)
- [Primary verification source 1](https://3e8.org/pub/scheme/doc/lisp-pointers/v7i3/p196-kfoury.pdf)
- [Primary verification source 3](https://www.haskell.org/onlinereport/haskell2010/haskellch4.html)
- [Primary verification source 4](https://mypy.readthedocs.io/en/stable/common_issues.html)
