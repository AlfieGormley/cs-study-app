---
id: fp-composition-order
title: Composing functions in execution order
level: basic
minutes: 3
sourceLesson: fp-higher-order
summary: Composition feeds the inner function result to the outer function.
---

Composition feeds the inner function result to the outer function. This unit develops that mechanism using the earlier units as prerequisites.

## Composition

**Function composition** builds a new function by feeding one function's output into another. Maths writes it with a small circle, ∘ (Haskell uses a full stop, `.`):

```formula
(f ∘ g)(x) = f(g(x))
where
∘: function composition, read "after": f ∘ g means "f after g"
f: the function applied second
g: the function applied first
x: the input value
In words: composing f with g makes a new function that runs g on x, then runs f on g's result, so a chain of compositions is read right to left.
```

For example, let the inner function add one and the outer function double. Starting from five gives twelve. Reversing their order gives eleven: the order matters.

```haskell
-- Composition feeds each result leftward.
-- read right to left: words, then
-- length, then show
countWords :: String -> String
countWords = show . length . words
```

```python
# Reverse fs to apply the rightmost first.
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

## Key takeaways
- Composition feeds the inner function result to the outer function.
- The rightmost function runs first in conventional composition.

## Further reading
- [Haskell 2010 report: Prelude definitions](https://www.haskell.org/onlinereport/haskell2010/haskellch9.html)
- [Python Fp](https://docs.python.org/3/howto/functional.html)
