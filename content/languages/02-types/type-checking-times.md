---
id: type-checking-times
title: When type checking happens
level: basic
minutes: 4
sourceLesson: type-static-dynamic
summary: Static checking analyses a program before execution; dynamic typing checks operations on runtime values.
---

Every value in a running program is just bits. The bit pattern `0x41` could be the integer 65, the character `A`, or part of a pointer. A **type** is the extra knowledge that tells you which interpretation is meant, and therefore which operations make sense.

Think of a type as **a set of values plus the operations allowed on them**. `int` is a set of whole numbers that you can add and compare. `str` is a set of character sequences that you can concatenate and slice. A **type error** is an attempt to apply an operation to a value outside its set: dividing a string, calling a number as if it were a function.

A **type system** is the set of rules a language uses to detect (or prevent) those errors. Languages differ on two separate questions:

1. **When** are types checked? Before the program runs (**static**) or while it runs (**dynamic**)?
2. **Which coercions are permitted**? One informal use of **strong/weak** distinguishes fewer implicit conversions from more permissive conversions; these labels have no universal definition.

People often blur these, saying "Python is weakly typed" when they mean "dynamically typed". The absence of annotations does not establish which conversions Python permits; keep the two questions separate.

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
// No annotation: integer default is i32.
let total = 40 + 2;
```

Writing types explicitly is called **manifest typing**. Working out types without explicit annotations uses **type inference**, covered in the following inference units.

## Dynamic typing: check while running

In a **dynamically typed** language, the rules of an operation depend on the types of its runtime values, rather than requiring every operation to pass a static type checker. Rebinding rules are a separate language choice. Tagged values are a common implementation model, but optimizers can prove checks unnecessary or use other representations.

```python
def add_one(x):
    # The same operation runs for each call.
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

## Key takeaways
- Static checking analyses a program before execution; dynamic typing checks operations on runtime values.
- Inference can make static code concise; runtime tags are an implementation technique, not the definition of dynamic typing.

## Further reading
- [Luca Cardelli: Type systems](https://lucacardelli.name/Papers/TypeSystems.pdf)
- [Python built-in numeric types](https://docs.python.org/3/library/stdtypes.html)
- [Java Language Specification: Conversions](https://docs.oracle.com/javase/specs/jls/se21/html/jls-5.html)
