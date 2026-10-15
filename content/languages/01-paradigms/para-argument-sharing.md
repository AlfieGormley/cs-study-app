---
id: para-argument-sharing
title: Strict arguments, sharing and mutable defaults
level: advanced
minutes: 3
sourceLesson: para-scope-closures
summary: Mutating a shared object differs from rebinding a local parameter.
---

Evaluating an argument and passing its value does not imply copying the whole object. Separate a mutation of shared data from a reassignment of a local parameter.

## Evaluation strategies

When you call `f(expr)`, an **evaluation strategy** decides when `expr` is evaluated and what `f` receives.

## Strict: evaluate arguments first

Most languages use **strict evaluation** (applicative order): argument expressions are evaluated to values before the call; this does not recursively force lazy objects or traverse referenced data. Within strict languages, the question is what gets passed:

- **Call by value** (C and Java, including Java reference values): the function gets a copy. Assigning to the parameter can't affect the caller.
- **Call by reference** (C++ `int&`, C# `ref`, Pascal `var`): the parameter is an alias for the caller's variable. Assigning to it changes the caller's variable.
- **Call by sharing** (a useful description of Python, JavaScript, Ruby and Java object-reference behavior): the function gets a copy of a *reference* to the object. The term comes from Barbara Liskov's CLU.

Call by sharing confuses people because it behaves like reference for mutation and like value for assignment:

```python
# Mutation reaches the shared list object.
def mutate(lst):
    lst.append(1)     # caller sees it

def rebind(lst):
    lst = lst + [2]   # caller doesn't

def extend(lst):
    lst += [3]        # caller sees it!

L = [0]
mutate(L); rebind(L); extend(L)
print(L)   # [0, 1, 3]
```

`rebind` creates a new list and points the *local* name at it; the caller's `L` is untouched. `extend` looks like `rebind`, but `+=` on a list calls `__iadd__`, which extends the list in place. On an immutable type like a tuple or `int`, `+=` would rebind instead.

> [!warning] Mutable default arguments
> Python evaluates default values once, when `def` runs. So `def add(v, acc=[])` shares one list across every call: `add(1)` returns `[1]`, then `add(2)` returns `[1, 2]`. Use `acc=None` and create the list inside the function.

## Key takeaways
- Mutating a shared object differs from rebinding a local parameter.
- Python evaluates default argument expressions when def executes.

## Further reading
- [Python: calls and argument values](https://docs.python.org/3/tutorial/controlflow.html#default-argument-values)
- [Python: assignment statements](https://docs.python.org/3/reference/simple_stmts.html)
