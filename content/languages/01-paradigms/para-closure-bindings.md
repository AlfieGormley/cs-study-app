---
id: para-closure-bindings
title: Closures and late-bound loop variables
level: advanced
minutes: 3
sourceLesson: para-scope-closures
summary: Each counter invocation creates a distinct captured binding.
---

Returning an inner function can keep an enclosing binding available after its creator returns. Separate that lifetime behavior from the time when each callback reads its binding.

## Closures

A closure is a function together with the environment it was created in. It can use variables from enclosing scopes even after those scopes have returned:

```python
# Returned inc keeps this call's n alive.
def counter():
    n = 0
    def inc():
        nonlocal n
        n += 1
        return n
    return inc

c = counter()
c(); c()
print(c())   # 3
```

`counter` returned long ago, yet `n` lives on. Each call to `counter()` creates a fresh `n`, so two counters don't interfere. A closure is a little object with private state; the old saying goes "closures are a poor man's objects, and objects are a poor man's closures".

## Python closures capture bindings

In Python and ordinary JavaScript closures, references to lexical bindings persist; other languages offer capture by value or reference. This distinction is the source of a famous bug:

```python
# All lambdas read the same later binding.
fs = [lambda: i for i in range(3)]
print([f() for f in fs])   # [2, 2, 2]
```

All three lambdas close over the same variable `i`. They don't look it up until they're called, by which time the loop has finished and `i` is `2`. This is **late binding**.

The usual fix is to bind the current value at creation time, using a default argument (defaults are evaluated when the function is defined):

```python
# Defaults save each current loop value.
fs = [lambda i=i: i for i in range(3)]
print([f() for f in fs])   # [0, 1, 2]
```

`functools.partial` does the same job more explicitly.

JavaScript shows the same issue and a language-level fix:

```javascript
// var shares i; let creates a binding.
for (var i = 0; i < 3; i++)
  setTimeout(() => console.log(i));
// 3 3 3   (one shared i)

for (let j = 0; j < 3; j++)
  setTimeout(() => console.log(j));
// 0 1 2   (fresh j per iteration)
```

With `let`, the spec creates a new binding for each loop iteration, so each closure captures a different variable.

## Key takeaways
- Each counter invocation creates a distinct captured binding.
- Defaults or per-iteration bindings can preserve each loop value.

## Further reading
- [Python: closures and cells](https://docs.python.org/3.12/reference/datamodel.html)
- [ECMAScript language specification](https://tc39.es/ecma262/2023/)
