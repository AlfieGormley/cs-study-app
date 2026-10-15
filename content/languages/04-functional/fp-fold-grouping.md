---
id: fp-fold-grouping
title: Left and right fold grouping
level: basic
minutes: 3
sourceLesson: fp-higher-order
summary: Left and right folds nest applications in different directions.
---

Left and right folds nest applications in different directions. This unit develops that mechanism using the earlier units as prerequisites.

## Left and right folds

A fold can associate from the left or the right, meaning it can bracket the steps starting from the left end or from the right end of the list:

```formula
foldl(f, z, [x_1, x_2, x_3])
  = f(f(f(z, x_1), x_2), x_3)
foldr(f, z, [x_1, x_2, x_3])
  = f(x_1, f(x_2, f(x_3, z)))
where
foldl: the left fold: starts from the initial value and combines elements from the left
foldr: the right fold: brackets from the right, with the initial value at the far right (the deepest application combines it with the last element; lazy evaluation need not execute in this order)
f: the two-argument combining function
z: the initial value (the seed)
x_1, x_2, x_3: the list's three elements, in order
In words: foldl puts the seed at the far left and brackets to the left; foldr puts the seed at the far right and brackets to the right.
```

With subtraction the difference shows:

```formula
foldl(−, 0, [1, 2, 3]) = ((0 − 1) − 2) − 3
                       = −6
foldr(−, 0, [1, 2, 3]) = 1 − (2 − (3 − 0))
                       = 2
where
foldl: the left fold, bracketing from the left
foldr: the right fold, bracketing from the right
−: subtraction, used here as the combining function
In words: subtraction gives different answers depending on the bracketing, so the left fold gives −6 and the right fold gives 2.
```

With exact integer addition and zero as the seed, both folds give six: addition is associative and zero is its identity. Floating-point addition is not generally associative, and associativity alone does not make arbitrary seeds interchangeable between left and right folds.

JavaScript reduce visits left to right and reduceRight right to left, but both call the callback with the accumulator first. Haskell foldr instead calls f(element, accumulator); for subtraction these conventions produce different results. In Haskell, `foldr` is the natural fold for building lists and for lazy, possibly infinite input; `foldl'` (strict left fold) is the right choice for summing large finite lists.

## Key takeaways
- Left and right folds nest applications in different directions.
- Haskell foldr and JavaScript reduceRight use different callback argument conventions.

## Further reading
- [Haskell List](https://hackage.haskell.org/package/base/docs/Data-List.html)
- [ECMAScript: indexed collections](https://tc39.es/ecma262/multipage/indexed-collections.html)
