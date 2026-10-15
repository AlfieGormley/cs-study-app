---
id: type-parametric-reasoning
title: What parametricity lets you prove
level: intermediate
minutes: 3
sourceLesson: type-generics
summary: Total parametric functions cannot inspect or invent values of an unknown element type.
---

A generic type signature relates inputs to outputs. Stronger reasoning requires genuinely uniform behaviour, with the totality and observation restrictions below.

## Parametricity: types as theorems

Under total parametric semantics (excluding nontermination, exceptions, `seq` and unsafe inspection), because a parametric function cannot inspect its `T`, its type alone tells you a surprising amount about what it does. Philip Wadler called this **theorems for free** (1989).

- `f :: a -> a`. Under the stated total parametric assumptions, the only available result is the input itself, so `f` must be the identity. Nontermination is excluded by those assumptions.
- `g :: [a] -> [a]`. `g` cannot invent new `a` values or look at them. It can only drop, duplicate and reorder elements based on the list's **shape**. For finite lists, `reverse` and `take 3` fit; `cycle` is a partial, potentially infinite example outside this total finite-list statement; `sort` does not (it needs `Ord a`).

A consequence is the free theorem for `g`. Because `g` only moves elements by position, it doesn't matter whether you transform the elements before or after calling it:

```formula
map h (g xs) = g (map h xs)   for all h, xs
where
g: a total parametric function, uniformly of type [a] → [a] for every element type a, used at both a and b; such as reverse on finite, fully defined lists
h: a total function from a to some other type b
xs: any finite list whose elements have type a
map h: the list you get by applying h to every element, keeping the order
[a]: a list whose elements have type a
a, b: type variables (any types)
→: the function-type arrow: [a] → [a] takes a list of a and returns a list of a
In words: transforming every element and then rearranging gives the same list as rearranging first and transforming afterwards.
```

For example, with `g = reverse` and `h` adding 1: reversing `[1, 2, 3]` gives `[3, 2, 1]` and adding 1 gives `[4, 3, 2]`; adding 1 first gives `[2, 3, 4]` and reversing gives `[4, 3, 2]`. The theorem assumes total functions on finite, fully defined lists.

This only holds if the language really is uniform. Java breaks it: a generic method can call `instanceof`, `getClass()` or `hashCode()` on a `T`. TypeScript can use `typeof`; Python can use `type` or `isinstance`. Haskell supports useful parametric reasoning subject to those caveats. Rust generics also permit observations such as `size_of::<T>()`, so merely avoiding `Any` is not a parametricity guarantee.

## Key takeaways
- Total parametric functions cannot inspect or invent values of an unknown element type.
- The list free theorem requires its totality and uniformity assumptions; mainstream generic syntax alone does not establish them.

## Further reading
- [Wadler: Theorems for free](https://people.mpi-sws.org/~dreyer/tor/papers/wadler.pdf)
- [Wadler: Parametricity papers](https://homepages.inf.ed.ac.uk/wadler/topics/parametricity.html)
