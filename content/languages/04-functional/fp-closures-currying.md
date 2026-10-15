---
id: fp-closures-currying
title: Closures, partial application and currying
level: basic
minutes: 3
sourceLesson: fp-higher-order
summary: A closure retains access to captured bindings.
---

A closure retains access to captured bindings. This unit develops that mechanism using the earlier units as prerequisites.

## Returning functions: closures

A function defined inside another function can use the outer function's variables, even after the outer function has returned. The inner function plus the variables it captured is a **closure**.

```python
# The inner function keeps access to n.
def make_multiplier(n):
    def times(x):
        return x * n   # captures n
    return times

triple = make_multiplier(3)
triple(10)   # 30
```

Closures are how you build specialised functions from general ones, and how callbacks carry context in JavaScript event handlers.

## Partial application and currying

**Partial application** fixes some arguments of a function and returns a function of the rest:

```python
# Fix the exponent; leave base unsupplied.
from functools import partial
def power(base, exp):
    return base ** exp

square = partial(power, exp=2)
square(7)   # 49
```

**Currying** transforms a function of several arguments into a chain of one-argument functions:

```formula
f(a, b, c) = f_c(a)(b)(c)
add(a, b) = a + b
add_c(1)(41) = 1 + 41 = 42
where
f: a function that takes three arguments at once
f_c: the curried form of f: give it a and it returns a function waiting for b; that returns a function waiting for c, which finally returns the same result as f(a, b, c)
a, b, c: the arguments, supplied one at a time to f_c
add: an ordinary two-argument addition function
add_c: the curried form of add, written in JavaScript as a => b => a + b
In words: currying turns one call with several arguments into a chain of one-argument calls; supplying only the first argument, as in add_c(1), gives a reusable "add one" function.
```

In JavaScript, the curried form is just nested arrow functions:

```javascript
// The first call returns another function.
const add = a => b => a + b;
const inc = add(1);
inc(41);   // 42
```

Haskell function arrows are right-associative, so ordinary multi-argument definitions are curried. A function can instead take a tuple as its single argument. `add :: Int -> Int -> Int` really means `Int -> (Int -> Int)`: a function that takes an `Int` and returns a function. So `map (add 1) xs` works with no extra syntax.

## Key takeaways
- A closure retains access to captured bindings.
- Currying and fixing some arguments are related but distinct operations.

## Further reading
- [Python Expressions](https://docs.python.org/3/reference/expressions.html)
- [Python Functools](https://docs.python.org/3/library/functools.html)
- [Haskell3](https://www.haskell.org/onlinereport/haskell2010/haskellch3.html)
