---
id: fp-recursion-tail-calls
title: Recursion and tail calls
level: intermediate
minutes: 11
summary: How recursion replaces loops, what it costs on the call stack, why tail calls can run in constant space, and which languages actually optimise them.
---

Pure code can use local mutation if it stays unobservable. In a purely functional style, repetition is commonly expressed without mutable loop counters. Instead, repetition comes from **recursion**: a function that calls itself on a smaller problem until it reaches a case it can answer directly.

Recursion is not just a substitute for loops. For recursive data (trees, nested lists, JSON, abstract syntax trees) it's the most natural way to write code, because the shape of the function mirrors the shape of the data.

## Anatomy of a recursive function

A terminating recursion over finite input commonly has two parts:

1. **Base case**: an input simple enough to answer without recursing.
2. **Recursive case**: break the input into a smaller piece, call yourself on it, and combine the result.

```python
def length(xs):
    if not xs:                 # base
        return 0
    return 1 + length(xs[1:])  # recursive
```

In Haskell, pattern matching makes the two cases explicit:

```haskell
length' :: [a] -> Int
length' []     = 0
length' (_:xs) = 1 + length' xs
```

To prove termination, identify a well-founded measure that decreases towards a base case. The raw input need not shrink on every call; a countdown measure or another ordering may suffice.

> [!note] Structural recursion
> When you recurse on the *parts* of a value (the tail of a list, the children of a tree node), termination is guaranteed because the data is finite. This is called **structural recursion**, and it's the safest kind.

## What it costs: the call stack

In a conventional non-tail-recursive execution, each active call retains a frame or continuation for its pending work. Compilers and runtimes may optimize that representation.

Look at `1 + length(xs[1:])`. After the recursive call returns, there's still work to do: add 1. So every frame must stay alive until the bottom is reached:

```
length([a,b,c])
= 1 + length([b,c])
= 1 + (1 + length([c]))
= 1 + (1 + (1 + length([])))
= 1 + (1 + (1 + 0))
= 3
```

The expression grows wider as it goes down, then collapses on the way back. A list of *n* items needs *n* frames: O(n) stack space.

CPython commonly defaults to a recursion limit of **1,000**; inspect sys.getrecursionlimit() in the actual process. Node.js also has a finite recursion limit, but no universal frame count is provided here because it depends on engine, flags and frame shape. Deep list recursion is therefore not portable.

> [!warning] Don't just raise the limit
> `sys.setrecursionlimit(10**6)` lets Python try deeper recursion, but memory remains finite and platform-specific calls may still consume C stack. Since CPython 3.11 many Python-to-Python calls avoid recursive C calls, so Python recursion depth and native-stack depth are not identical. Raising the limit can still risk exhaustion or crashes.

## Tail calls

A call is a **tail call** if it's the very last thing a function does: its result is returned directly, with nothing left to compute.

```python
def f(n):
    return g(n) + 1   # NOT a tail call

def f(n):
    return g(n + 1)   # tail call
```

When a call is in tail position, the current frame has nothing left to do. A language can **reuse** the frame for the callee instead of pushing a new one. This is **tail call optimisation** (TCO), or more precisely **proper tail calls** when the language guarantees it. A tail-recursive function then runs in O(1) stack, exactly like a loop.

### The accumulator pattern

To make a function tail-recursive, carry the partial result in an extra parameter, the **accumulator**, instead of leaving work for after the call returns:

```python
def length(xs, acc=0):
    if not xs:
        return acc
    return length(xs[1:], acc + 1)
```

```
length([a,b,c], 0)
= length([b,c], 1)
= length([c], 2)
= length([], 3)
= 3
```

The pending expression stays the same width; a runtime with TCO can discard the caller. CPython retains the calls, and Python list slicing still copies data.

```haskell
sumTo :: Int -> Int -> Int
sumTo acc 0 = acc
sumTo acc n = sumTo (acc + n) (n - 1)
```

The same trick turns factorial, sum, reverse and many folds into loops.

## Which languages actually do it?

| Language | Tail calls eliminated? |
|---|---|
| Scheme | Yes, required by the standard |
| Haskell, OCaml, Erlang | Yes |
| Scala, Kotlin | Direct self-recursion only |
| Clojure | Only via explicit `recur` |
| JavaScript | Specified for eligible strict-mode calls; engine-dependent |
| Python | No, by design |
| Java, C# | Not guaranteed |
| C, C++ | Often at `-O2`; not guaranteed |

- **Scheme** made proper tail calls part of the language definition, so a tail-recursive loop is *guaranteed* constant space. Erlang and Elixir servers run forever as tail-recursive loops.
- **JavaScript** added proper tail calls in ES2015 (strict mode only). WebKit documents JavaScriptCore support. Do not assume portable engine support: verify your target runtime. An exhaustive current engine-support matrix is omitted because it was not reliably established in this review.
- **Python** deliberately does not. Guido van Rossum argued that TCO loses stack traces, and that Python programmers should write loops.
- **The JVM** has no general tail-call instruction, so Scala and Kotlin compile self-recursive tail calls into loops at compile time. Scala does this automatically (`@tailrec` makes the compiler fail if it can't); Kotlin needs the `tailrec` modifier. Clojure makes you write `recur` so the compiler can check it.

## Working without TCO

When the language won't help, you have three options.

### 1. Write the loop

A tail-recursive function translates mechanically into a loop: the parameters become loop variables and the tail call becomes "update and go round again".

```python
def length(xs):
    acc = 0
    while xs:
        xs, acc = xs[1:], acc + 1
    return acc
```

(Aside: `xs[1:]` copies the list, so this is O(n²) overall. Real code would index or iterate. Python lists are arrays, not linked lists.)

### 2. Use an explicit stack

For tree recursion that isn't tail-recursive, keep your own stack on the heap, which can grow far larger than the call stack:

```python
def tree_sum(root):
    total, stack = 0, [root]
    while stack:
        node = stack.pop()
        total += node.value
        stack.extend(node.children)
    return total
```

### 3. Trampolines

A **trampoline** turns each recursive call into a returned *thunk* (a zero-argument function), and a driver loop keeps calling thunks until it gets a real value. The driver keeps call depth bounded independently of the number of steps, though the exact number of frames depends on the implementation.

```javascript
const trampoline = f => (...args) => {
  let r = f(...args);
  while (typeof r === "function") r = r();
  return r;
};

const count = trampoline(
  function go(n, acc = 0) {
    return n === 0
      ? acc
      : () => go(n - 1, acc + 1);
  });

count(1_000_000);   // 1000000, no overflow
```

It introduces closure/call overhead relative to a direct loop; measure the actual implementation. It's most useful for **mutual recursion** (`isEven` calls `isOdd` calls `isEven`), which a simple loop can't express as neatly.

## Recursion that branches

Some recursion calls itself more than once. Naive Fibonacci is the classic warning:

```python
def fib(n):
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)
```

The call tree branches twice at every level:

```
            fib(4)
          /        \
      fib(3)       fib(2)
     /     \       /    \
  fib(2) fib(1) fib(1) fib(0)
  /   \
fib(1) fib(0)
```

`fib(2)` is computed twice, `fib(1)` three times. The number of calls grows like φⁿ (φ ≈ 1.618): `fib(30)` makes about 2.7 million calls. Stack depth is only O(n), but time is exponential.

Two fixes:

- **Memoisation**: cache results (`@functools.cache`), so each body computes a distinct fib(k) once: O(n) additions and cached entries in a unit-cost arithmetic model.
- **Accumulators**: a loop carries two Fibonacci values with O(n) additions and O(1) numeric variables. Exact integers grow with n, so bit costs are larger; tail recursion also needs TCO for constant call space.

```python
def fib(n, a=0, b=1):
    if n == 0:
        return a
    return fib(n - 1, b, a + b)
```

## Haskell's twist: laziness and space leaks

In a lazy language, the accumulator can betray you. This sum looks tail-recursive:

```haskell
mySum acc []     = acc
mySum acc (x:xs) = mySum (acc + x) xs
```

But Haskell doesn't evaluate `acc + x` until something needs it. The accumulator becomes a growing chain of unevaluated additions (**thunks**): `((0 + 1) + 2) + 3 ...`. Evaluating that chain at the end can itself overflow the stack.

The fix is to force the accumulator at each step: `foldl'` from `Data.List`, a bang pattern (`!acc`), or `seq`. For strict finite reductions such as numeric sums, foldl' is commonly the appropriate choice; lazy foldl still has uses and WHNF forcing is not deep evaluation. The next lesson covers laziness in depth.

## Key takeaways
- Terminating recursion needs progress in a well-founded measure towards a terminating case.
- Ordinary recursion uses O(n) stack; CPython stops at about 1,000 frames by default.
- A tail call is the last action of a function; with tail call optimisation it runs in constant stack, like a loop.
- Accumulators turn many recursive functions into tail-recursive ones.
- Tail-call guarantees vary by runtime; Python has no language guarantee and CPython retains recursive Python calls. Verify engine behavior or use loops, explicit stacks or trampolines.
- Branching recursion like naive Fibonacci is exponential; memoise or carry state forward.

## Further reading
- [Tail call — Wikipedia](https://en.wikipedia.org/wiki/Tail_call)
- [Tail Recursion Elimination — Guido van Rossum](https://neopythonic.blogspot.com/2009/04/tail-recursion-elimination.html)
- [Recursion — Learn You a Haskell](https://learnyouahaskell.github.io/recursion.html)
- [Trampoline (computing) — Wikipedia](https://en.wikipedia.org/wiki/Trampoline_(computing))
- [Foldr Foldl Foldl' — Haskell Wiki](https://wiki.haskell.org/Foldr_Foldl_Foldl%27)
- [Primary verification source 1](https://docs.python.org/3/whatsnew/3.11.html#inlined-python-function-calls)
- [Primary verification source 2](https://docs.python.org/3/library/sys.html#sys.setrecursionlimit)
- [Primary verification source 3](https://webkit.org/blog/6240/ecmascript-6-proper-tail-calls-in-webkit/)
- [Primary verification source 4](https://clojure.org/reference/special_forms#recur)
- [Primary verification source 5](https://kotlinlang.org/docs/functions.html#tail-recursive-functions)
- [Primary verification source 6](https://www.erlang.org/doc/system/eff_guide_functions.html)
- [Primary verification source 7](https://standards.scheme.org/corrected-r7rs/r7rs-Z-H-5.html)
- [Primary verification source 8](https://hackage.haskell.org/package/base/docs/Data-List.html)
