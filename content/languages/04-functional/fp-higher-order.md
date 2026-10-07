---
id: fp-higher-order
title: Higher-order functions, map, filter and reduce
level: basic
minutes: 10
summary: Functions as values, the map/filter/reduce trio, closures, currying and composition, with the gotchas that bite in Python and JavaScript.
---

In a functional language, functions are **first-class values**. You can store them in variables, put them in lists, pass them as arguments and return them from other functions, exactly like numbers or strings.

A **higher-order function** is one that takes a function as an argument, returns a function, or both. Once you have them, a huge amount of repetitive looping code collapses into a few reusable patterns.

## Spotting the pattern

Look at these three loops:

```python
def doubled(xs):
    out = []
    for x in xs:
        out.append(x * 2)
    return out

def names(users):
    out = []
    for u in users:
        out.append(u.name)
    return out

def lengths(words):
    out = []
    for w in words:
        out.append(len(w))
    return out
```

They are the same loop with one line different. Pull the varying part out as a parameter and you get `map`:

```python
def my_map(f, xs):
    out = []
    for x in xs:
        out.append(f(x))
    return out

my_map(lambda x: x * 2, [1, 2, 3])
# [2, 4, 6]
```

The loop is written once. Callers say *what* to do to each element, not *how* to iterate.

## The big three

### map: transform every element

`map(f, xs)` applies `f` to each element and returns the results. For a finite, unchanged input and a total callback, there is one result per input element. Python returns an iterator; JavaScript array map preserves array length, including holes.

```
[1,  2,  3]
 |   |   |   f = x * 10
[10, 20, 30]
```

### filter: keep some elements

`filter(p, xs)` keeps the elements for which the predicate `p` returns true. The output is the **same length or shorter**, and elements are unchanged.

### reduce (fold): combine into one value

`reduce(f, xs, init)` walks the list carrying an **accumulator**. At each step it computes `acc = f(acc, x)`. The result can be anything: a number, a string, a dict, even another list.

```
reduce(add, [1, 2, 3, 4], 0)

acc=0  -> add(0,1)=1
acc=1  -> add(1,2)=3
acc=3  -> add(3,3)=6
acc=6  -> add(6,4)=10
result: 10
```

`map` and `filter` are both special cases of `reduce`: you can write either as a fold that builds a list. That makes `reduce` the most general and also the hardest to read, so reach for it last.

### In three languages

```python
from functools import reduce
xs = [1, 2, 3, 4, 5]

evens = list(filter(lambda x: x % 2 == 0,
                    xs))
squares = list(map(lambda x: x * x, xs))
total = reduce(lambda a, x: a + x, xs, 0)
```

```javascript
const xs = [1, 2, 3, 4, 5];
const evens = xs.filter(x => x % 2 === 0);
const squares = xs.map(x => x * x);
const total = xs.reduce((a, x) => a + x, 0);
```

```haskell
xs = [1 .. 5]
evens   = filter even xs
squares = map (\x -> x * x) xs
total   = foldl (+) 0 xs
```

Chained together they read as a pipeline: "the sum of the squares of the even numbers".

```javascript
xs.filter(x => x % 2 === 0)
  .map(x => x * x)
  .reduce((a, x) => a + x, 0);   // 20
```

> [!tip] Pythonic style
> In Python, list comprehensions are usually preferred over `map` and `filter` with a lambda. `[x * x for x in xs if x % 2 == 0]` does both in one readable line. `map` is still neat with a named function: `map(str.upper, words)`. Guido van Rossum moved `reduce` into `functools` in Python 3 because explicit loops are usually clearer.

### Left and right folds

A fold can associate from the left or the right. With subtraction the difference shows:

```
foldl (-) 0 [1,2,3] = ((0-1)-2)-3 = -6
foldr (-) 0 [1,2,3] = 1-(2-(3-0)) =  2
```

JavaScript reduce visits left to right and reduceRight right to left, but both call the callback with the accumulator first. Haskell foldr instead calls f(element, accumulator); for subtraction these conventions produce different results. In Haskell, `foldr` is the natural fold for building lists and for lazy, possibly infinite input; `foldl'` (strict left fold) is the right choice for summing large finite lists.

## Returning functions: closures

A function defined inside another function can use the outer function's variables, even after the outer function has returned. The inner function plus the variables it captured is a **closure**.

```python
def make_multiplier(n):
    def times(x):
        return x * n   # captures n
    return times

triple = make_multiplier(3)
triple(10)   # 30
```

Closures are how you build specialised functions from general ones, and how callbacks carry context in JavaScript event handlers.

### Partial application and currying

**Partial application** fixes some arguments of a function and returns a function of the rest:

```python
from functools import partial
def power(base, exp):
    return base ** exp

square = partial(power, exp=2)
square(7)   # 49
```

**Currying** transforms a function of several arguments into a chain of one-argument functions: `f(a, b, c)` becomes `f(a)(b)(c)`.

```javascript
const add = a => b => a + b;
const inc = add(1);
inc(41);   // 42
```

Haskell function arrows are right-associative, so ordinary multi-argument definitions are curried. A function can instead take a tuple as its single argument. `add :: Int -> Int -> Int` really means `Int -> (Int -> Int)`: a function that takes an `Int` and returns a function. So `map (add 1) xs` works with no extra syntax.

## Composition

**Composition** builds a new function by feeding one function's output into another. In maths, `(f . g)(x) = f(g(x))`.

```haskell
-- read right to left: words, then
-- length, then show
countWords :: String -> String
countWords = show . length . words
```

```python
def compose(*fs):
    def run(x):
        for f in reversed(fs):
            x = f(x)
        return x
    return run

count_words = compose(str, len, str.split)
count_words("to be or not")   # '4'
```

Composition is why small, pure, single-purpose functions are valuable: they snap together like Lego. Unix pipes (`cat log | grep ERR | wc -l`) are the same idea at the shell level.

## Gotchas

### Python's map and filter are lazy

In Python 3, `map` and `filter` return **iterators**, not lists. They defer per-item mapping/filtering until consumed and are one-shot; construction still evaluates arguments and obtains iterators.

```python
m = map(lambda x: x * 2, [1, 2, 3])
list(m)   # [2, 4, 6]
list(m)   # []  already exhausted
```

### JavaScript's map passes three arguments

`Array.prototype.map` calls the callback with `(element, index, array)`. Functions with optional second parameters misbehave:

```javascript
["1", "2", "3"].map(parseInt);
// [1, NaN, NaN]
```

`parseInt("2", 1)` treats 1 as the radix, which is invalid, giving `NaN`. `parseInt("3", 2)` fails because 3 isn't a binary digit. Write `.map(s => parseInt(s, 10))` or `.map(Number)`.

### reduce on an empty array

With no initial value, JavaScript's `reduce` uses the first element as the accumulator. On an empty array that throws `TypeError: Reduce of empty array with no initial value`. Python's `functools.reduce` raises a `TypeError` too. Always pass an initial value.

### Late-binding closures

Python closures capture **variables**, not values:

```python
fs = [lambda: i for i in range(3)]
[f() for f in fs]   # [2, 2, 2]
```

All three lambdas share one `i`, which is 2 by the time they run. Bind the value at definition time with a default argument: `lambda i=i: i`. JavaScript's `let` in a `for` loop creates a fresh binding per iteration, so the equivalent JS gives `[0, 1, 2]`; with `var` it gives `[3, 3, 3]`.

## Trade-offs

- **Readability.** Short pipelines of `map`/`filter` are clearer than loops. Deeply nested `reduce` calls with clever accumulators are usually worse. If you need a comment to explain the fold, write a loop.
- **Performance.** In JavaScript, `xs.filter(...).map(...)` builds an intermediate array per step. Whether allocation matters depends on the workload; a single loop or lazy pipeline can avoid intermediate arrays. Haskell's GHC can often *fuse* such pipelines into one loop.
- **Early exit.** Fully consumed finite eager maps and strict folds normally process all eligible elements; Python map can be partially consumed and lazy Haskell folds can short-circuit. Use `any`/`all` (Python), `some`/`every`/`find` (JS) when you can stop early.

## Key takeaways
- Higher-order functions take or return functions, letting you write a loop pattern once and reuse it.
- `map` transforms each element, `filter` keeps some, `reduce` folds everything into one value; map and filter are special cases of reduce.
- Closures capture variables from their defining scope; currying and partial application build specialised functions from general ones.
- Composition chains small pure functions into pipelines.
- Watch for Python's one-shot lazy iterators, JavaScript's extra `map` arguments, empty `reduce` and late-binding closures.

## Further reading
- [Higher-order function — Wikipedia](https://en.wikipedia.org/wiki/Higher-order_function)
- [Array.prototype.reduce() — MDN](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array/reduce)
- [functools — Python docs](https://docs.python.org/3/library/functools.html)
- [Fold (higher-order function) — Wikipedia](https://en.wikipedia.org/wiki/Fold_(higher-order_function))
- [Closures — MDN](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Closures)
- [Primary verification source 2](https://docs.python.org/3/library/functions.html)
- [Primary verification source 3](https://tc39.es/ecma262/multipage/indexed-collections.html)
- [Primary verification source 4](https://hackage.haskell.org/package/base/docs/Data-List.html)
