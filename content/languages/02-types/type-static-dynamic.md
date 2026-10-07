---
id: type-static-dynamic
title: Static vs dynamic, strong vs weak
level: basic
minutes: 10
summary: What a type actually is, when it gets checked (compile time or run time), how much a language coerces behind your back, and why these are two separate questions.
---

Every value in a running program is just bits. The bit pattern `0x41` could be the integer 65, the character `A`, or part of a pointer. A **type** is the extra knowledge that tells you which interpretation is meant, and therefore which operations make sense.

Think of a type as **a set of values plus the operations allowed on them**. `int` is a set of whole numbers that you can add and compare. `str` is a set of character sequences that you can concatenate and slice. A **type error** is an attempt to apply an operation to a value outside its set: dividing a string, calling a number as if it were a function.

A **type system** is the set of rules a language uses to detect (or prevent) those errors. Languages differ on two separate questions:

1. **When** are types checked? Before the program runs (**static**) or while it runs (**dynamic**)?
2. **Which coercions are permitted**? One informal use of **strong/weak** distinguishes fewer implicit conversions from more permissive conversions; these labels have no universal definition.

People often blur these, saying "Python is weakly typed" when they mean "dynamically typed". It is neither weak nor static, and it helps to keep the axes apart.

## Static typing: check before running

A **statically typed** language checks types by analysing the source code, usually at compile time. A checker assigns static types and reports violations of its rules before execution. Some tools still emit executable code despite errors, and runtime checks or escape hatches may remain.

```java
// Java
int n = 5;
String s = n;  // compile error:
// incompatible types: int cannot be
// converted to String
```

Java, C, C++, C#, Go, Rust, Haskell, OCaml, Kotlin, Swift and TypeScript are all statically typed.

Static does **not** mean you must write the types. Haskell and OCaml infer almost everything, and Rust and modern Java infer local variable types:

```rust
// Rust: the compiler infers i32
let total = 40 + 2;
```

Writing types explicitly is called **manifest** typing. Static checking with little or no annotation is called **type inference** (the subject of the next lesson).

## Dynamic typing: check while running

In a **dynamically typed** language, variables have no fixed type. Operations are resolved or checked using runtime value types. Tagged values are a common implementation model, but optimizers can prove checks unnecessary or use other representations.

```python
def add_one(x):
    return x + 1

add_one(41)     # 42
add_one("41")   # TypeError at run time
```

The second call fails only when that line actually executes. Python's message is `can only concatenate str (not "int") to str`. A bug on a code path your tests never run will sit there silently until a user hits it.

Python, JavaScript, Ruby, PHP, Lua, Erlang, Clojure and Lisp are dynamically typed.

> [!note] Dynamic does not mean untyped
> Python enforces operation rules at runtime. Lower-level untyped models lack comparable high-level guarantees; assembly instructions still have operand and representation requirements.

### Duck typing

Dynamic languages usually care whether a value **supports the operation**, not what class it is. If it has a `.read()` method, you can read from it. This is **duck typing**: "if it walks like a duck and quacks like a duck, it is a duck". It is flexible, and it is also why a typo in a method name can go unnoticed until run time.

## Strong and weak: how much coercion?

The second axis is about **implicit conversions** (coercions). When you combine mismatched types, does the language refuse, or does it convert one of them for you?

Unlike static/dynamic, "strong" and "weak" have no single formal definition. They describe a spectrum. JavaScript sits near the weak end:

```js
"5" + 2      // "52"  (number -> string)
"5" - 2      // 3     (string -> number)
"3" * "4"    // 12
[] + {}      // "[object Object]"
0 == ""      // true
1 + undefined // NaN
```

Python sits near the strong end. `"5" + 2` raises `TypeError` rather than guessing. Python still has a few deliberate coercions: `1 + 2.5` widens the int to a float, and `1 + True` is `2` because `bool` is a subclass of `int`.

C is statically typed but weak in an important sense. It converts freely between numeric types (`int x = 3.9;` silently truncates to 3), and pointer casts can bypass useful static checks. A cast alone need not be erroneous, but invalid alignment or accessing an object through an incompatible type can cause undefined behaviour.

Rust is at the strict end even for numbers. It will not widen an `i32` to an `i64` without being asked:

```rust
let a: i32 = 5;
let b: i64 = a;        // error: mismatched
let c: i64 = a.into(); // ok, explicit
```

Java, by contrast, widens `int` to `long` silently, and `"a" + 1` is `"a1"` because `+` with a String converts the other side.

## The two axes together

| | Strong-ish | Weak-ish |
|---|---|---|
| **Static** | Rust, Haskell, Java | C, C++ |
| **Dynamic** | Python, Ruby | JavaScript, PHP |

Treat this as a rough map, not a ranking. Every language makes some coercions and forbids others.

A more precise idea than "strong" is **type safety** (or soundness): the guarantee that a program which passes the checks can never perform an operation on a value of the wrong type in a way that corrupts memory or gets "stuck". Robin Milner summarised it in 1978 as **"well-typed programs cannot go wrong"**. Safe languages may still raise run-time errors (a Java `ClassCastException`, a Python `TypeError`), but they fail *cleanly*. C does not promise even that.

## Static languages still check at run time

Static checking cannot prove everything, so static languages keep some dynamic checks:

- **Downcasts**: in Java, `(String) obj` is checked at run time and may throw `ClassCastException`.
- **Array bounds**: Java, Rust and C# check indices at run time.
- **Covariant array stores**: Java requires reference-array store compatibility checks (the JIT may eliminate checks it proves unnecessary) (lesson 4 explains why).

And dynamic languages can be checked statically: TypeScript adds a static checker on top of JavaScript, and mypy or Pyright check Python type hints. That hybrid is **gradual typing** (lesson 6).

## Static checkers are conservative

A static checker must decide *without running the program*. Deciding exactly which programs will hit a type error is undecidable in general (it would solve the halting problem), so a checker has to approximate. Sound checkers err on the safe side and **reject some programs that would actually run fine**:

```java
Object o = "hi";
// Fine at run time, rejected statically:
int n = o.length(); // Object has no length
```

The programmer knows `o` holds a String; the checker only knows its declared type is `Object`. You fix this with a cast or a better declared type. Every static system has this cost: occasionally you have to persuade the checker of something you already know.

## Trade-offs

| | Static | Dynamic |
|---|---|---|
| Type checks | Static constraints before execution; runtime checks may remain | Operation rules checked during execution |
| Tooling | Declared/inferred types can guide tooling | Inference, annotations and runtime knowledge can guide tooling |
| Speed | Depends on representation and implementation | Depends on representation and implementation |
| Flexibility | Must satisfy checked constraints | Runtime operation rules still apply |
| Feedback loop | REPLs and incremental checkers are possible | REPLs and compilation are possible |

What does this buy in practice? A 2017 study, *To Type or Not to Type* (Gao, Bird and Barr), examined a sample of fixed bugs in public JavaScript projects, added annotations, and found that TypeScript 2.0 and Flow 0.30 each detected about **15%**. This historical sample does not estimate every project or current checker; undetected bugs were not all established to be inherently beyond type checking.

> [!tip] A useful way to think about it
> A sound type system can prove specified properties about all executions within its model and assumptions. Practical checkers may intentionally be unsound. Tests are **evidence about some executions**, but can check anything. They complement each other.

## Common pitfalls

- **Confusing the axes.** "Python is weakly typed" is wrong: Python is dynamic and fairly strong. "C is strongly typed because it is static" is also wrong.
- **Assuming static means safe.** C and C++ are static but allow memory-unsafe casts and undefined behaviour.
- **Assuming annotations are enforced.** Python type hints can be checked by separate tools and remain available as annotation metadata (with deferred evaluation in Python 3.14); Python does not enforce them by itself. TypeScript type annotations are erased during compilation. `def f(x: int)` will happily accept a string at run time.
- **Relying on coercion.** JavaScript's `==` converts operands; use `===`, which never coerces.

## Key takeaways
- A type is a set of values plus the operations allowed on them; a type error applies an operation outside that set.
- Static vs dynamic is about **when** types are checked: before running (Java, Rust, Haskell) or as each operation runs (Python, JavaScript).
- Strong vs weak is an informal spectrum of **how much implicit coercion** a language does: JavaScript and C coerce freely; Python and Rust mostly refuse.
- Static does not require annotations (inference), and dynamic does not mean untyped (values carry tags).
- Static checkers must be conservative, so they sometimes reject correct programs; static languages still need some run-time checks.

## Further reading
- [Type system — Wikipedia](https://en.wikipedia.org/wiki/Type_system)
- [Strong and weak typing — Wikipedia](https://en.wikipedia.org/wiki/Strong_and_weak_typing)
- [Type safety — Wikipedia](https://en.wikipedia.org/wiki/Type_safety)
- [Luca Cardelli, Type Systems (PDF)](https://lucacardelli.name/Papers/TypeSystems.pdf)
- [To Type or Not to Type: Quantifying Detectable Bugs in JavaScript (PDF)](https://earlbarr.com/publications/typestudy.pdf)
- [Duck typing — Wikipedia](https://en.wikipedia.org/wiki/Duck_typing)
- [Primary verification source 1](https://docs.python.org/3/library/annotationlib.html)
- [Primary verification source 3](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1570.pdf)
- [Primary verification source 4](https://docs.oracle.com/javase/specs/jls/se21/html/jls-5.html)
