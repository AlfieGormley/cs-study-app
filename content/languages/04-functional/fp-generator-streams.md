---
id: fp-generator-streams
title: Generators and streaming pipelines
level: intermediate
minutes: 3
sourceLesson: fp-laziness
summary: Generators pause between requested values.
---

Generators pause between requested values. This unit develops that mechanism using the earlier units as prerequisites.

## Laziness in Python and JavaScript

Neither language is lazy by default, but both have opt-in laziness through **iterators** and **generator functions** (generators for short).

## Python generators

A function containing `yield` returns a generator. Its body runs only as values are requested, pausing at each `yield`:

```python
# Yield suspends before the next increment.
def naturals():
    n = 1
    while True:      # infinite, but fine
        yield n
        n += 1

from itertools import islice
list(islice(naturals(), 5))
# [1, 2, 3, 4, 5]
```

Generator **expressions** look like list comprehensions with round brackets:

```python
# Only the first expression stores results.
squares = [x * x for x in range(10**6)]
# list: stores a million results now

squares = (x * x for x in range(10**6))
# generator: defers per-item squares
```

Many Python iterators defer per-item work. This does not guarantee bounded memory: itertools.product pools its inputs, cycle caches values, and tee buffers when consumers diverge. A streaming filter/map pipeline can avoid materializing the whole input:

```python
# Consume while the file remains open.
with open("access.log") as f:
    errors = (l for l in f if " 500 " in l)
    ips = (l.split()[0] for l in errors)
    first = list(islice(ips, 10))
```

This avoids storing the whole file and stops requesting lines after 10 matches. Memory still depends on the longest line, I/O buffers and the 10 collected results; the file reader may read ahead internally.

## JavaScript generators and iterators

```javascript
// Stop after the requested number of
// yields.
function* naturals() {
  let n = 1;
  while (true) yield n++;
}

function* take(n, it) {
  if (n <= 0) return;
  for (const x of it) {
    yield x;
    if (--n === 0) return;
  }
}

[...take(5, naturals())];  // [1,2,3,4,5]
```

The ES2025 standard specifies lazy iterator helper methods (`.map`, `.filter`, `.take`, `.drop`) via `Iterator.prototype`, so a runtime implementing these helpers can avoid a hand-written `take`. Check the actual runtime; standards inclusion does not establish support in every installed engine. Array methods, by contrast, are eager: `arr.map(f)` builds a whole new array immediately.

## Elsewhere

The same idea shows up across the industry, usually under the name *deferred execution*:

- **Apache Spark**: transformations (`map`, `filter`) build a plan; nothing runs until an action (`count`, `collect`).
- **C# LINQ** and **Java Streams**: queries run when enumerated or when a terminal operation is called.
- **Django ORM**: QuerySets defer evaluation, but iteration is only one trigger; list(), len(), bool(), repr() and some other operations can execute queries.
- **Polars** lazy frames: the whole query is optimised before execution.

Deferring lets the system see the whole pipeline first and optimise it (push filters down, skip unused columns).

## Key takeaways
- Generators pause between requested values.
- Deferred work does not by itself guarantee bounded memory.

## Further reading
- [Python Expressions](https://docs.python.org/3/reference/expressions.html)
- [Python Itertools](https://docs.python.org/3/library/itertools.html)
- [Ecma Control](https://tc39.es/ecma262/multipage/control-abstraction-objects.html)
- [Spark](https://spark.apache.org/docs/latest/rdd-programming-guide.html)
- [Django](https://docs.djangoproject.com/en/5.2/ref/models/querysets/)
- [Java Stream](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/stream/package-summary.html)
- [Linq](https://learn.microsoft.com/en-us/dotnet/standard/linq/deferred-execution-lazy-evaluation)
- [Polars](https://docs.pola.rs/user-guide/lazy/using/)
