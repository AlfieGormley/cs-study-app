---
id: para-scope-closures
title: Scope, binding, closures and evaluation strategies
level: advanced
minutes: 15
summary: How languages decide what a name refers to, how closures capture variables, and when and how function arguments get evaluated.
---

Every paradigm in this module rests on the same few questions. When you write `x`, *which* `x` do you mean? When a function is created inside another function, what happens to the variables it uses after the outer function returns? And when you call `f(g())`, does `g()` run before `f`, inside `f`, or maybe never?

The answers are **scope**, **binding**, **closures** and **evaluation strategy**. Get them wrong and you get some of the most confusing bugs in programming: loops that capture the wrong value, defaults that remember old calls, and functions that mutate their caller's data "by accident".

## Binding and binding time

A **binding** is an association between a name and something: a value, a memory location, a type, a function. Languages differ in *when* bindings are fixed:

| When | Example |
|---|---|
| Language design | `+` means addition |
| Compile time | A C local's type and stack slot |
| Link/load time | A call to `printf` resolved to an address |
| Run time | A Python name bound by `x = 5` |

Earlier binding generally means faster code and more errors caught early. Later binding means more flexibility: Python can rebind any name, add methods to a class at run time, or swap a module during a test.

The **scope** of a binding is the region of program text where the name refers to it. The **lifetime** is how long the thing exists. They aren't the same: a C `static` local has block scope but lives for the whole program, and a closure variable (below) outlives the function that created it.

## Lexical vs dynamic scope

With **lexical** (static) scope, a name refers to the binding in the nearest enclosing block *in the source code*. You can work it out by reading the program. Almost every modern language works this way: C, Java, Python, JavaScript, Rust, Haskell.

With **dynamic** scope, a name refers to the most recent binding *on the call stack* at run time. Early Lisps worked this way, Emacs Lisp did by default for decades, and so does Bash:

```bash
x=global
show() { echo "$x"; }
f() { local x=local; show; }

f      # prints: local
show   # prints: global
```

`show` has no `x` of its own. Under dynamic scope it sees whichever `x` its *caller* had. Under lexical scope it would always print `global`, because that's the `x` visible where `show` was written.

Dynamic scope is occasionally handy (a "current output stream" every function picks up), but it makes code hard to reason about: a function's behaviour depends on who called it. Scheme (1975) showed lexical scope could work in Lisp, and the industry followed. Languages that want the dynamic behaviour now opt in explicitly: Common Lisp's special variables, Perl's `local`, Python's `contextvars`, React's context.

## Python's scope rules

Python resolves names in the **LEGB** order: Local, Enclosing function, Global (module), Built-in.

```python
x = "global"

def outer():
    x = "enclosing"
    def inner():
        return x      # finds enclosing
    return inner()
```

The key subtlety: Python decides a name's scope **at compile time, for the whole function**. Unless a `global` or `nonlocal` declaration applies, binding a name anywhere in a function makes it local throughout that function:

```python
x = 10
def f():
    print(x)   # UnboundLocalError
    x = 5
```

Because of `x = 5`, `x` is local to `f`. The `print` runs before that local has a value, so Python raises `UnboundLocalError` rather than reading the global.

To assign to an outer name, declare it:

- `global x` rebinds the module-level `x`.
- `nonlocal x` rebinds `x` in the nearest enclosing function.

Two more rules trip people up:

- **Blocks don't create scopes.** A variable assigned in a `for` or `if` is visible after it. After `for k in range(3): pass`, `k` is `2`.
- **Class bodies don't enclose methods.** A method can't see class-level names directly; it must write `self.y` or `ClassName.y`. Comprehensions in a class body can't see them either, except in the outermost `for ... in` expression.

JavaScript had the block problem with `var`, which is function-scoped. ES2015's `let` and `const` are block-scoped, which is one reason style guides ban `var`.

## Closures

A **closure** is a function together with the environment it was created in. It can use variables from enclosing scopes even after those scopes have returned:

```python
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

### Python closures capture bindings

In Python and ordinary JavaScript closures, references to lexical bindings persist; other languages offer capture by value or reference. This distinction is and the source of a famous bug:

```python
fs = [lambda: i for i in range(3)]
print([f() for f in fs])   # [2, 2, 2]
```

All three lambdas close over the **same variable** `i`. They don't look it up until they're called, by which time the loop has finished and `i` is `2`. This is **late binding**.

The usual fix is to bind the current value at creation time, using a default argument (defaults are evaluated when the function is defined):

```python
fs = [lambda i=i: i for i in range(3)]
print([f() for f in fs])   # [0, 1, 2]
```

`functools.partial` does the same job more explicitly.

JavaScript shows the same issue and a language-level fix:

```javascript
for (var i = 0; i < 3; i++)
  setTimeout(() => console.log(i));
// 3 3 3   (one shared i)

for (let j = 0; j < 3; j++)
  setTimeout(() => console.log(j));
// 0 1 2   (fresh j per iteration)
```

With `let`, the spec creates a new binding for each loop iteration, so each closure captures a different variable.

### How closures are implemented

A plain C-style function can keep its locals on the stack, because they die when it returns. A closure breaks that: an inner function may be *returned* and called later, after the outer frame is gone. This is the **upward funarg problem**, and it's why closures need captured variables to live somewhere longer-lived, usually the heap.

```
counter() frame (gone)
         |
inc --> [code] + [env] --> cell: n = 3
                           (on the heap)
```

- **CPython** stores captured variables in *cell* objects. You can see them: `c.__closure__[0].cell_contents` is `3`. Both the outer function and every closure share the same cell, which is how `nonlocal` writes are visible.
- **Lua** uses *upvalues*: they point into the stack while the outer function runs and are moved ("closed") to the heap when it returns.
- **C** has no closures. Callbacks take a function pointer plus a `void *` context argument, which is a closure built by hand.
- **Rust** and **C++** make capture explicit. A C++ lambda says `[x]` (copy) or `[&x]` (reference); a reference that outlives `x` is undefined behaviour. Safe Rust rejects escaping borrows that outlive their referents. A `move` closure captures by value, moving or copying its captures; moving a borrowed reference does not extend the referent’s lifetime.

Closures also keep their environment alive. In JavaScript, an event listener that closes over a large object keeps that object from being garbage collected while the listener and captured object remain reachable. Removing the listener helps only if no other live reference retains the closure or object.

## Evaluation strategies

When you call `f(expr)`, an **evaluation strategy** decides when `expr` is evaluated and what `f` receives.

### Strict: evaluate arguments first

Most languages are **strict** (applicative order): argument expressions are evaluated to values before the call; this does not recursively force lazy objects or traverse referenced data. Within strict languages, the question is what gets passed:

- **Call by value** (C and Java, including Java reference values): the function gets a copy. Assigning to the parameter can't affect the caller.
- **Call by reference** (C++ `int&`, C# `ref`, Pascal `var`): the parameter is an alias for the caller's variable. Assigning to it changes the caller's variable.
- **Call by sharing** (a useful description of Python, JavaScript, Ruby and Java object-reference behavior): the function gets a copy of a *reference* to the object. The term comes from Barbara Liskov's CLU.

Call by sharing confuses people because it behaves like reference for mutation and like value for assignment:

```python
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
> Python evaluates default values **once**, when `def` runs. So `def add(v, acc=[])` shares one list across every call: `add(1)` returns `[1]`, then `add(2)` returns `[1, 2]`. Use `acc=None` and create the list inside the function.

### Non-strict: evaluate arguments only when needed

- **Call by name** (Algol 60's default; Scala's `x: => Int` parameters): the argument expression is passed unevaluated and re-evaluated *every time* the parameter is used.
- **Call by need** (Haskell): like call by name, but the result is cached after the first evaluation. This is **lazy evaluation**. R's function arguments are also lazy "promises".

The difference matters when an argument is expensive, has side effects, or never terminates:

```
def first(a, b): return a

first(1, loop_forever())
```

| Strategy | Result |
|---|---|
| Call by value | Hangs: `b` is evaluated first |
| Call by name | Returns 1: `b` never used |
| Call by need | Returns 1: `b` never used |

If a parameter is used three times, call by name evaluates the argument three times; call by need evaluates it once. With side effects, call by name can even give different values each time, which Algol programmers exploited in a trick called Jensen's device.

Even strict languages have non-strict corners. `and`, `or` and the ternary `a if c else b` short-circuit: in `x is not None and x.ok`, the right side only runs if needed. Python generators and iterators are lazy too, as the functional basics lesson showed.

Laziness has costs. Unevaluated expressions ("thunks") use memory, and it's hard to predict when work happens. Haskell programs sometimes leak memory by building long chains of thunks, which is why it offers strictness annotations and functions like `foldl'`.

## Pitfalls checklist

- **Late-binding closures in loops**: bind the value with a default argument, `partial` or `let`.
- **`UnboundLocalError`**: an assignment later in the function made the name local. Add `global`/`nonlocal` or rename.
- **Mutable defaults**: use `None` and create inside.
- **Surprise mutation**: under call by sharing, functions can mutate arguments. Copy defensively or use immutable types.
- **Dangling captures** in C++: capturing by reference in a lambda that outlives the scope.
- **Leaky closures**: long-lived callbacks keep their whole environment alive.

## Key takeaways
- A binding links a name to something; binding time ranges from language design to run time, trading speed for flexibility.
- Lexical scope resolves names from the source text; dynamic scope from the call stack. Almost all modern languages are lexical, and opt into dynamic behaviour explicitly.
- Python uses LEGB and decides scope per function at compile time, so a later assignment makes a name local everywhere in that function.
- Capture rules depend on language: Python shares cells, while C++ and Rust also capture by value. Escaping environments often use heap storage, but storage and lifetime depend on implementation and ownership.
- Python and JavaScript share object references; Java is pass-by-value, including copied reference values. Mutating a shared object can be visible, but rebinding a parameter does not rebind the caller’s variable.
- Strict evaluation evaluates arguments first; call by name re-evaluates on each use; call by need (laziness) evaluates at most once.

## Further reading
- [Scope (computer science) — Wikipedia](https://en.wikipedia.org/wiki/Scope_(computer_science))
- [Closure (computer programming) — Wikipedia](https://en.wikipedia.org/wiki/Closure_(computer_programming))
- [Evaluation strategy — Wikipedia](https://en.wikipedia.org/wiki/Evaluation_strategy)
- [Execution model: naming and binding — Python docs](https://docs.python.org/3/reference/executionmodel.html)
- [Closures — MDN](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Closures)
- [Funarg problem — Wikipedia](https://en.wikipedia.org/wiki/Funarg_problem)
