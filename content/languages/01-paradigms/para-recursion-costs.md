---
id: para-recursion-costs
title: Recursion and tail-call limits
level: intermediate
minutes: 3
sourceLesson: para-functional-basics
summary: A tail call has no remaining work after its result.
---

A recursive definition can follow the shape of a list directly. Its mathematical clarity does not by itself guarantee bounded stack use in the chosen runtime.

## Recursion instead of loops

Pure functional code avoids mutable loop counters, so repetition is expressed by recursion, often with **pattern matching** on the shape of the data:

```haskell
-- The second case consumes one list cell.
len :: [a] -> Int
len []     = 0
len (_:xs) = 1 + len xs
```

Read it as two equations: the length of an empty list is 0; the length of a list with a head and a tail `xs` is one more than the length of `xs`.

Deep recursion needs care. Each call normally uses a stack frame. Many functional-language implementations support tail-call optimisation (TCO): when the recursive call is the very last thing a function does, the frame is reused, so the tail-call stack can stay bounded. This does not guarantee constant total memory: lazy accumulators, retained data or allocation can still grow. Mainstream languages differ:

- **CPython** does not eliminate Python-function tail calls. A standard tested CPython interpreter reports a recursion limit of 1,000 via `sys.getrecursionlimit()`; this value is configurable and is not a Python-language guarantee. Recursing over a 10,000-element list raises `RecursionError`.
- **JavaScript**: ES2015 specified proper tail calls, but in practice JavaScriptCore (used by Safari) implements them; V8 (Chrome, Node) does not.
- **Java**: ordinary JVM bytecode provides no general proper-tail-call guarantee; Scala and Kotlin offer `@tailrec` / `tailrec` for self-recursion, compiled into loops.

In practice, use `map`, `filter` and folds where you can; they express intent, but their space behavior still depends on language, implementation and strictness.

## Key takeaways
- A tail call has no remaining work after its result.
- Stack and total memory depend on the runtime and evaluation strategy.

## Further reading
- [Guido van Rossum: tail recursion elimination](https://neopythonic.blogspot.com/2009/04/tail-recursion-elimination.html)
- [WebKit: proper tail calls](https://webkit.org/blog/6240/ecmascript-6-proper-tail-calls-in-webkit/)
