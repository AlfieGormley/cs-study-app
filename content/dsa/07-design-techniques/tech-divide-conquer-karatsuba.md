---
id: tech-divide-conquer-karatsuba
title: Karatsuba and fewer products
level: intermediate
minutes: 5
sourceLesson: tech-divide-conquer
summary: Three recursive half-products replace the four products of schoolbook splitting.
---

## Karatsuba multiplication

Schoolbook multiplication of two n-digit numbers multiplies every digit of one by every digit of the other: O(n²) digit products. In 1960 Anatoly Karatsuba found a faster way, published with Ofman in 1962.

Split each number into a high half and a low half around a power of ten. Their product then has three parts: the two high halves multiplied together, the two low halves multiplied together, and a middle part made of the two cross products. The trick is that the middle part can be had with **one** extra multiplication instead of two:

```formula essential
x = a 10^m + b
y = c 10^m + d
xy = ac × 10^{2m} + (ad + bc) × 10^m + bd
ad + bc = (a + b)(c + d) − ac − bd
where
x: the first number to multiply, with n digits
y: the second number to multiply, with n digits
n: the number of digits in each number
m: the split point, about half the number of digits (n / 2)
10^m: 10 raised to the power m, a 1 followed by m zeros
10^{2m}: 10 raised to the power 2m
a: the high half of x (its leading digits)
b: the low half of x (its last m digits)
c: the high half of y
d: the low half of y
In words: the product is "high × high" shifted left by 2m digits, plus the cross terms shifted by m digits, plus "low × low". Multiply the two half-sums once and subtract the high and low products you already have: what remains is exactly the sum of the cross terms.
```

So Karatsuba computes only three half-size products: ac, bd and the product of the half-sums. Additions, subtractions and shifts are cheap, linear-time operations.

### Why one product matters

- **Four half-size products** (ac, ad, bc and bd separately) with linear extra work is the master theorem's "leaves dominate" case with a critical exponent of 2: quadratic, no better than schoolbook.
- **Three half-size products** lower the critical exponent to log₂3, about 1.585. The cost grows like n to that power.

Dropping one product is not a constant-factor saving: it changes the growth rate. Each time the digit count doubles, Karatsuba's work roughly triples while schoolbook's quadruples. For 1000-digit numbers the scale expressions are about 57,000 against a million. Those are growth-model figures, not exact digit-product counts: rounding, base cases and carries in the half-sums all matter.

```formula reference
T(n) = 3T(n / 2) + O(n)
T(n) = Θ(n^{log_2(3)})
where
T(n): the number of digit operations to multiply two n-digit numbers
n: the number of digits in each number
O(n): linear work for the additions, subtractions and shifts
log_2(3): the base-2 logarithm of 3, about 1.585
Θ: Big-Theta, grows at exactly this rate up to constant factors
In words: three half-size products plus linear work put the algorithm in the "leaves dominate" case, with about n^1.585 work instead of n^2.
```

A worked example on 1234 × 5678, splitting after two digits: the high halves are 12 and 56, the low halves 34 and 78. Three two-digit products are needed: 12 × 56 = 672, 34 × 78 = 2652, and the half-sums 46 × 134 = 6164. The middle part is 6164 − 672 − 2652 = 2840. Shifting and adding gives 6,720,000 + 284,000 + 2,652 = 7,006,652, the correct product.

> [!analogy] Real-world analogy: measuring a room by subtraction
> A rectangular room is divided by one line across and one line down into four rectangular zones. A carpet fitter already knows the areas of two diagonally opposite zones and needs the combined area of the other two. Instead of measuring each of those, they measure the whole room once and subtract the two areas they already have.
>
> **How it maps:** the room's sides are the half-sums (a + b) and (c + d), so its area is their product, which contains all four zones ac, ad, bc and bd. The two known zones are ac and bd. Subtracting them leaves the other two together, ad + bc, at the cost of one measurement instead of two.
>
> **Where it stops:** for a carpet fitter, one saved measurement is a small convenience. In Karatsuba the saving repeats at every level of the recursion, which is what changes the growth rate; and the subtraction only gives the two zones' total, never each one separately, which is all the product needs.

## Key takeaways
- Three recursive half-products replace the four products of schoolbook splitting.
- Arithmetic-operation counts, bit costs and real implementation cutoffs are different claims.

## Further reading
- [Karatsuba algorithm](https://en.wikipedia.org/wiki/Karatsuba_algorithm)
- [GMP multiplication algorithms](https://gmplib.org/manual/Multiplication-Algorithms)
