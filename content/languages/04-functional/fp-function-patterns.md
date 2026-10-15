---
id: fp-function-patterns
title: Function values, map and filter
level: basic
minutes: 4
sourceLesson: fp-higher-order
summary: Higher-order functions take or return functions.
---

In a functional language, functions are **first-class values**. You can store them in variables, put them in lists, pass them as arguments and return them from other functions, exactly like numbers or strings.

A **higher-order function** is one that takes a function as an argument, returns a function, or both. Once you have them, a huge amount of repetitive looping code collapses into a few reusable patterns.

## Spotting the pattern

Look at these three loops:

```python
# Only the per-element operation varies.
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
# Apply the supplied operation per item.
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

## map: transform every element

`map(f, xs)` applies `f` to each element and returns the results. For a finite, unchanged input and a total callback, there is one result per input element. Python returns an iterator; JavaScript array map preserves array length, including holes.

```formula
map(f, [x_1, x_2, ..., x_n])
  = [f(x_1), f(x_2), ..., f(x_n)]
where
map: the higher-order function that applies another function to every element of a list
f: the function applied to each element
x_1, x_2, x_n: the list's elements in order: x_1 is the first, x_n the last
n: the number of elements in the list
...: "and so on" for every element in between
In words: map builds a new list of the same length, whose element at each position is f applied to the input element at that position.
```

With f multiplying by 10, the list [1, 2, 3] becomes [10, 20, 30]:

```
[1,  2,  3]
 |   |   |   f multiplies by 10
[10, 20, 30]
```

## filter: keep some elements

`filter(p, xs)` keeps the elements for which the **predicate** `p` (a function that answers true or false) returns true. The output is the same length or shorter, and elements are unchanged.

```formula
filter(p, xs) = [x ∈ xs | p(x)]
len(filter(p, xs)) ≤ len(xs)
where
filter: the higher-order function that keeps only the elements that pass a test
p: the predicate, a function returning true or false for each element
xs: the input list (read "exes": the plural of x)
x: one element of xs
∈: "is an element of"
|: "such that": keep x only when the condition after the bar holds
p(x): the predicate's answer for x; x is kept when it is true
len: the length (number of elements) of a list
≤: less than or equal to
In words: filter keeps, in their original order, exactly the elements for which p says true, so the output is never longer than the input.
```

For example, with p testing "is even", filter turns [1, 2, 3, 4, 5] into [2, 4]: five elements in, two out.

A fold, introduced next, carries an accumulator and may return a number, a dictionary or another list. Unlike map and filter, its result does not need to be a list.

## Key takeaways
- Higher-order functions take or return functions.
- Map transforms positions; filter keeps selected original elements.

## Further reading
- [Python Fp](https://docs.python.org/3/howto/functional.html)
- [Python Functions](https://docs.python.org/3/library/functions.html)
- [ECMAScript: indexed collections](https://tc39.es/ecma262/multipage/indexed-collections.html)
