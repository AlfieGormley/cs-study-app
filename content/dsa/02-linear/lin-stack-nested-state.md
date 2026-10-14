---
id: lin-stack-nested-state
title: Call frames and balanced nesting
level: intermediate
minutes: 3
sourceLesson: lin-stacks
summary: A call frame retains the state needed after a nested call returns.
---

A stack serves the last added item first. Nested function calls and nested bracket pairs both require the most recent unfinished task to finish first. For the bracket checker n is the input character count; for call frames depth is the number of active nested calls.

## The call stack

In the ordinary unoptimised call-stack model, each active call has a **stack frame** retaining its arguments, local state and a **return address** (where to continue when it finishes). Returning releases that frame. Registers, inlining, tail calls and runtime-managed frames can change the physical layout.

```python
def a(): return b() + 1
def b(): return c() * 2
def c(): return 5
a()
```

```
call a     call b     call c     c returns 5
+-----+    +-----+    +-----+    +-----+
|     |    |     |    |  c  |    |     |
|     |    |  b  |    |  b  |    |  b  |
|  a  |    |  a  |    |  a  |    |  a  |
+-----+    +-----+    +-----+    +-----+
```

This is why recursion uses O(depth) memory, and why unbounded recursion fails:

- Native thread stacks have implementation- and configuration-dependent limits. Excessive native recursion can exhaust them, often causing a fault; Java can raise StackOverflowError. Compiler optimizations and runtime-managed frames can change this simple model.
- CPython guards itself with a recursion limit (commonly **1,000** at startup), raising `RecursionError`; inspect `sys.getrecursionlimit()` for the actual process setting.

Any recursive algorithm can be rewritten with an **explicit stack** on the heap, which can grow to gigabytes. Depth-first search on a large graph is the usual example (see the graphs module).

## Balanced brackets

Is `{[()()]}` balanced? Is `([)]`? Nesting means the most recently opened bracket must be the first one closed: a stack.

```python
def balanced(s):
    pairs = {")": "(", "]": "[", "}": "{"}
    stack = []
    for ch in s:
        if ch in "([{":
            # Remember the latest unmatched
            # opener.
            stack.append(ch)
        elif ch in pairs:
            if not stack:
                return False
            # A closer must match that
            # newest opener.
            if stack.pop() != pairs[ch]:
                return False
    return not stack
```

Three ways to fail:

1. A closer that doesn't match the top: `([)]` fails at `)`, because the top is `[`.
2. A closer with an empty stack: `())`.
3. Openers left over at the end: `((`.

For a string of n characters, that is O(n) time, and O(n) space in the worst case (a string of nothing but openers). Compilers, linters, JSON and XML parsers and your editor's bracket matching all use this idea.

> [!tip] One bracket type?
> If there's only `(` and `)`, you don't need the stack itself, just a counter: +1 for `(`, −1 for `)`, fail if it goes negative, and require 0 at the end.

## Key takeaways
- A call frame retains the state needed after a nested call returns.
- Each closer must match the newest unfinished opener.

## Further reading
- [Call stack — Wikipedia](https://en.wikipedia.org/wiki/Call_stack)
- [Using lists as stacks — Python tutorial](https://docs.python.org/3/tutorial/datastructures.html)
