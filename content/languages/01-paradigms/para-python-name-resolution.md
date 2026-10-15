---
id: para-python-name-resolution
title: Python name resolution and local bindings
level: advanced
minutes: 3
sourceLesson: para-scope-closures
summary: A function binding normally makes the name local throughout that function.
---

Python usually resolves an ordinary name through local, enclosing-function, module and built-in namespaces. A binding anywhere in a function can change how every use of that name is classified.

## Python's scope rules

Python resolves names in the **LEGB** order: Local, Enclosing function, Global (module), Built-in.

```python
# inner reads the enclosing x binding.
x = "global"

def outer():
    x = "enclosing"
    def inner():
        return x      # finds enclosing
    return inner()
```

The key subtlety: Python decides a name's scope at compile time, for the whole function. Unless a `global` or `nonlocal` declaration applies, binding a name anywhere in a function makes it local throughout that function:

```python
# The later assignment makes x local.
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

- Ordinary `for` and `if` suites do not create scopes. A variable assigned in a `for` or `if` is visible after it. After `for k in range(3): pass`, `k` is `2`.
- The ordinary class namespace does not enclose methods. A method can't see class-level names directly; it must write `self.y` or `ClassName.y`. Comprehensions in a class body can't see them either, except in the outermost `for ... in` expression.

JavaScript had the block problem with `var`, which is function-scoped. ES2015's `let` and `const` are block-scoped, which is one reason style guides ban `var`.

## Key takeaways
- A function binding normally makes the name local throughout that function.
- Class namespace lookup differs from the enclosing-function rule.

## Further reading
- [Python: naming and binding](https://docs.python.org/3.12/reference/executionmodel.html)
