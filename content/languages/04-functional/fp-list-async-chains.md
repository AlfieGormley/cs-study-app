---
id: fp-list-async-chains
title: List, Promise and do-notation chains
level: intermediate
minutes: 3
sourceLesson: fp-functors-monads
summary: List bind concatenates each callback result in iteration order.
---

List bind concatenates each callback result in iteration order. This unit develops that mechanism using the earlier units as prerequisites.

## List: try every possibility

For lists, `flat_map` means "for each item, produce zero or more results, and collect them all in one flat list":

```python
# Concatenate each returned sequence.
def flat_map(xs, f):
    return [y for x in xs for y in f(x)]

flat_map([1, 2, 3], lambda x: [x, x * 10])
# [1, 10, 2, 20, 3, 30]
```

Returning `[]` drops an item, returning `[x]` keeps it, returning several items fans out. A list comprehension with two `for` clauses is chained `flat_map`:

```python
# The inner loop runs for each outer item.
[(x, y) for x in [1, 2] for y in "ab"]
# [(1,'a'), (1,'b'), (2,'a'), (2,'b')]
```

JavaScript has `Array.prototype.flatMap`; C# LINQ calls it `SelectMany`; Spark has `rdd.flatMap`.

## Promise: wait, then continue

`then` is `flat_map` for "not here yet". If the callback returns another Promise, `then` waits for it and you get a flat `Promise<T>`, not a Promise of a Promise:

```javascript
// Each callback consumes the prior result.
fetch(url)
  .then(r => r.json())  // returns Promise
  .then(data => data.items.length);
```

And `async`/`await` is the same chain written as straight-line code. Each `await` is "flat_map the rest of the function onto this Promise".

```javascript
// Await exposes each fulfilled result.
const r = await fetch(url);
const data = await r.json();
return data.items.length;
```

## Haskell's do-notation

Haskell generalises that trick to every monad. `do` blocks (**do-notation**) are syntactic sugar for a chain of `>>=` (bind, i.e. `flat_map`):

```haskell
-- Bind the result of each prior action.
leadEmail uid = do
  user <- findUser uid
  team <- findTeam user
  lead <- findLead team
  return (email lead)
```

The same chaining shape works when all three functions use a compatible monad: Maybe, Either String, list or IO. The box type decides what each `<-` does. Scala's `for` comprehensions express related map/flatMap sequencing. F# computation expressions use builder-defined operations and can express monadic sequencing as well as other abstractions.

## Key takeaways
- List bind concatenates each callback result in iteration order.
- Promise and do-notation analogies require their own sequencing and effect assumptions.

## Further reading
- [Haskell3](https://www.haskell.org/onlinereport/haskell2010/haskellch3.html)
- [Ecma Control](https://tc39.es/ecma262/multipage/control-abstraction-objects.html)
- [ECMAScript: indexed collections](https://tc39.es/ecma262/multipage/indexed-collections.html)
- [Linq Selectmany](https://learn.microsoft.com/en-us/dotnet/api/system.linq.enumerable.selectmany)
- [Fsharp](https://learn.microsoft.com/en-us/dotnet/fsharp/language-reference/computation-expressions)
- [Scala For](https://docs.scala-lang.org/scala3/book/control-structures.html)
