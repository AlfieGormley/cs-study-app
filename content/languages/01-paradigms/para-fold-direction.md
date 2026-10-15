---
id: para-fold-direction
title: Folds, seeds and grouping
level: intermediate
minutes: 4
sourceLesson: para-functional-basics
summary: A fold combines a seed with each element.
---

A fold records how an accumulated result combines with the next value. Its seed and grouping determine the answer when the operation is sensitive to order.

## Folds

A **fold** walks a list, combining each element with an **accumulator**. It is the general pattern behind `sum`, `max`, `len` and even `map` itself.

```python
# Shift the accumulator before each digit.
from functools import reduce
digits = [1, 2, 3]
n = reduce(lambda acc, d: acc * 10 + d,
           digits, 0)
# 123
```

Each step applies the same rule to the accumulator:

```formula
acc_new = acc × 10 + d
((0 × 10 + 1) × 10 + 2) × 10 + 3
= (1 × 10 + 2) × 10 + 3 = 123
where
acc: the accumulator: the number built so far, starting from the seed 0
acc_new: the accumulator after the next digit has been added
d: the next digit taken from the list
10: the base of decimal numbers; multiplying by 10 shifts the number one place left to make room for the new digit
In words: shift the number so far one decimal place left, then put the new digit on the end.
```

Haskell distinguishes the direction:

- `foldl f z [a, b, c]` = `f (f (f z a) b) c`: groups from the left.
- `foldr f z [a, b, c]` = `f a (f b (f c z))`: groups from the right.

For a finite list, the two directions give the same mathematical result when the operation is **associative** and the seed is a two-sided **identity element** for it:

```formula
(a ⊕ b) ⊕ c = a ⊕ (b ⊕ c)
z ⊕ a = a ⊕ z = a
where
⊕: the combining operation the fold uses, such as + or −
a: any value the fold combines
b: any value the fold combines
c: any value the fold combines
z: the seed (starting value) passed to the fold
In words: the first line (associativity) says moving the brackets never changes the answer; the second (identity) says combining with the seed changes nothing. With both, folding from the left and from the right agree.
```

Integer addition with seed 0 has both properties. Floating-point addition is not associative, because each step rounds. Subtraction is not associative either, so the direction matters:

```formula
((z − a) − b) − c
((0 − 1) − 2) − 3 = −6
a − (b − (c − z))
1 − (2 − (3 − 0)) = 2
where
z: the seed, here 0
a: the first list element, here 1
b: the second list element, here 2
c: the third list element, here 3
−: subtraction, which is not associative
In words: foldl (first two lines) brackets from the left and gives −6; foldr (last two lines) brackets from the right and gives 2.
```

In Haskell those are `foldl (-) 0 [1,2,3]` and `foldr (-) 0 [1,2,3]`.

## Key takeaways
- A fold combines a seed with each element.
- Associativity and a two-sided identity allow left/right agreement on finite values.

## Further reading
- [Haskell: standard Prelude definitions](https://www.haskell.org/onlinereport/haskell2010/haskellch9.html)
- [Python: functools.reduce](https://docs.python.org/3/library/functools.html)
