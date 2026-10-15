---
id: type-unification-occurs
title: Unification and the occurs check
level: intermediate
minutes: 4
sourceLesson: type-inference
summary: Unification matches type constructors and solves variable substitutions.
---

The preceding composition example generated equality constraints between types. Unification now solves those constraints by matching structure and recording replacements for unknown type variables.

## Unification

Unification asks: what **substitution** (a rule replacing each type variable with a type) makes two types identical? Take one function type with an unknown input and integer result, and another with Boolean input and unknown result. Matching argument with argument and result with result gives:

```formula
S(a → Int) = S(Bool → b)
S = {a := Bool, b := Int}
S(a → Int) = Bool → Int
S(Bool → b) = Bool → Int
where
S: the substitution being searched for
S(T): the type T with every type variable replaced as S says
a, b: type variables (types not yet known)
Int: the fixed-width signed integer base type used in this example
Bool: the type with the two values True and False
→: the function-type arrow: Bool → Int is a function from Bool to Int
:=: "is replaced by": every a becomes Bool, and every b becomes Int
{ }: the set of replacements that makes up S
In words: replacing a by Bool and b by Int turns both types into Bool → Int, so they unify.
```

Unification fails when two different concrete types meet, or when a variable would have to contain itself:

| Unify | Result |
|---|---|
| Type variable with Int | Replace the variable by Int |
| `a -> Int` with `Bool -> b` | Replace a by Bool and b by Int |
| `Int` with `Bool` | type error |
| `a` with `a -> b` | Infinite type; error |

Here is a small unifier in Python, not a complete Algorithm W implementation. It assumes finite, well-formed type terms and an acyclic substitution. Type variables are strings; other types are tuples like `("->", arg, result)` or `("Int",)`.

```python
def resolve(t, s):
    # Follow variable-to-type replacements.
    while isinstance(t, str) and t in s:
        t = s[t]
    return t

def occurs(v, t, s):
    t = resolve(t, s)
    if t == v:
        return True
    # Search children, not constructor tags.
    if isinstance(t, tuple):
        return any(occurs(v, x, s)
                   for x in t[1:])
    return False

def unify(a, b, s):
    a, b = resolve(a, s), resolve(b, s)
    if a == b:
        return s
    if isinstance(a, str):
        # Do not construct a cyclic type.
        if occurs(a, b, s):
            raise TypeError("infinite type")
        return {**s, a: b}
    if isinstance(b, str):
        return unify(b, a, s)
    if a[0] != b[0] or len(a) != len(b):
        raise TypeError(f"{a} vs {b}")
    # Match corresponding type arguments.
    for x, y in zip(a[1:], b[1:]):
        s = unify(x, y, s)
    return s
```

Unifying `("->", "a", ("Int",))` with `("->", ("Bool",), "b")` returns `{'a': ('Bool',), 'b': ('Int',)}`.

### The occurs check

What is the type of `self_apply x = x x`? Give `x` the type `a`. Applying `x` to an argument means `a` must be a function type, and the argument is `x` itself:

```formula
x : a
a = a → b
a = (a → b) → b
a = ((a → b) → b) → b
where
x: the parameter of self_apply
a: the unknown type of x
b: the unknown result type of the call x x
:: "has type"
→: the function-type arrow: a → b is a function from a to b
=: a constraint: both sides must be the same type
In words: x is called with itself, so its type a must be "a function from a to b"; substituting that definition into itself makes the type grow forever, so no finite type works.
```

The **occurs check** (does `a` appear inside the type we're binding it to?) catches this. Compilers reject this finite-type constraint; exact diagnostic wording varies. GHC 9.6.6 reports a mismatch between a type variable and a function type containing that variable.

## Key takeaways
- Unification matches type constructors and solves variable substitutions.
- The occurs check rejects a variable containing itself in a finite type.

## Further reading
- [Damas and Milner: Principal type schemes](https://steshaw.org/hm/milner-damas.pdf)
- [Milner: A theory of type polymorphism](https://homepages.inf.ed.ac.uk/wadler/papers/papers-we-love/milner-type-polymorphism.pdf)
- [GHC: Higher-rank polymorphism](https://downloads.haskell.org/ghc/latest/docs/users_guide/exts/rank_polymorphism.html)
