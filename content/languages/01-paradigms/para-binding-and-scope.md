---
id: para-binding-and-scope
title: Binding times and lexical or dynamic scope
level: advanced
minutes: 3
sourceLesson: para-scope-closures
summary: Scope describes name resolution; lifetime describes existence during execution.
---

Every paradigm in this module rests on the same few questions. When you write `x`, *which* `x` do you mean? When a function is created inside another function, what happens to the variables it uses after the outer function returns? And when you call `f(g())`, does `g()` run before `f`, inside `f`, or maybe never?

The answers are **scope**, **binding**, closures and **evaluation strategy**. Get them wrong and you get some of the most confusing bugs in programming: loops that capture the wrong value, defaults that remember old calls, and functions that mutate their caller's data "by accident".

## Binding and binding time

A **binding** is an association between a name and something: a value, a memory location, a type, a function. Languages differ in *when* bindings are fixed:

| When | Example |
|---|---|
| Language design | `+` means addition |
| Compile time | A C declaration's type (storage placement can vary) |
| Link/load time | A call to `printf` resolved to an address |
| Run time | A Python name bound by `x = 5` |

Earlier binding can enable optimisation and earlier diagnostics, but does not guarantee faster execution. Later binding can support more flexibility: Python can rebind any name, add methods to a class at run time, or swap a module during a test.

The **scope** of a binding is the region of program text where the name refers to it. The **lifetime** is how long the thing exists. They aren't the same: a C `static` local has block scope but lives for the whole program, and a closure variable (below) outlives the function that created it.

## Lexical vs dynamic scope

With **lexical scope** (also called static scope), a name refers to the binding in the nearest enclosing block *in the source code*. You can work it out by reading the program. Almost every modern language works this way: C, Java, Python, JavaScript, Rust, Haskell.

With **dynamic scope**, a name refers to the most recent binding *on the call stack* at run time. Early Lisps worked this way, Emacs Lisp did by default for decades, and so does Bash:

```bash
x=global
show() { echo "$x"; }
f() { local x=local; show; }

f      # prints: local
show   # prints: global
```

`show` has no `x` of its own. Under dynamic scope it sees whichever `x` its *caller* had. Under lexical scope it would always print `global`, because that's the `x` visible where `show` was written.

Dynamic scope is occasionally handy (a "current output stream" every function picks up), but it makes code hard to reason about: a function's behaviour depends on who called it. Scheme (1975) showed lexical scope could work in Lisp, and the industry followed. Languages that want the dynamic behaviour now ask for it explicitly: Common Lisp's special variables and Perl's `local`. Python's `contextvars` explicitly propagates values through execution contexts, and React context through a component tree; neither changes those languages' lexical variable lookup.

## Key takeaways
- Scope describes name resolution; lifetime describes existence during execution.
- Dynamic scope follows active callers; lexical scope follows source nesting.

## Further reading
- [Python: naming and binding](https://docs.python.org/3.12/reference/executionmodel.html)
- [Bash: shell functions](https://www.gnu.org/software/bash/manual/html_node/Shell-Functions.html)
