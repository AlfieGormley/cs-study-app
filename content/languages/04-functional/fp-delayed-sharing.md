---
id: fp-delayed-sharing
title: Thunks and shared demand
level: intermediate
minutes: 3
sourceLesson: fp-laziness
summary: A thunk represents work that has not yet been demanded.
---

Most languages use **strict evaluation** (also called *eager evaluation*): when you call `f(g(x))`, they compute `g(x)` first, then pass the result to `f`. If `f` never uses its argument, the work was wasted.

**Lazy evaluation** flips this. An expression isn't computed when it's written, only when its value is actually needed. If it's never needed, it's never computed.

You already use laziness every day without thinking of it that way:

```python
# The second lookup needs a non-null user.
if user is not None and user.is_admin:
    ...
```

`and` doesn't evaluate `user.is_admin` if `user is not None` is false. That short-circuit is laziness on a small scale. Haskell uses non-strict evaluation by default, with explicit strictness operations and compiler analysis that can evaluate known-needed work eagerly.

## Thunks: delaying work

A delayed computation is stored as a **thunk**: a small object that remembers *how* to compute a value without having computed it yet. In Python, the simplest thunk is a zero-argument function:

```python
# Calling expensive is what starts work.
expensive = lambda: slow_query()
# slow_query has not run yet
if need_it:
    result = expensive()
```

Haskell builds thunks automatically. In Haskell expression syntax, the binding `let y = slowSum xs` delays that work until demanded; a compiler may eliminate or evaluate the thunk when semantics allow.

## Call-by-need: compute once, share

There are two flavours of non-strict evaluation:

| Strategy | Evaluates argument |
|---|---|
| Call-by-value (strict) | Once, before the call |
| Call-by-name | Every time it's used |
| Call-by-need (lazy) | At most once, on first use |

Call-by-name re-runs the expression on each use, which can be very wasteful. **Call-by-need** evaluates a thunk the first time it's forced, then **overwrites the thunk with its value** so later uses reuse the result instead of repeating that computation. This is what Haskell does, and it's what people usually mean by "lazy".

```haskell
-- Both uses demand the same binding.
let y = expensive 42
in y + y   -- expensive runs once
```

## Key takeaways
- A thunk represents work that has not yet been demanded.
- Call by need shares one evaluation, while call by name can repeat it.

## Further reading
- [Haskell6](https://www.haskell.org/onlinereport/haskell2010/haskellch6.html)
- [Hughes](https://www.cse.chalmers.se/~rjmh/Papers/whyfp.html)
- [Python Expressions](https://docs.python.org/3/reference/expressions.html)
