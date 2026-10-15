---
id: para-polymorphic-dispatch
title: Polymorphism and dispatch choices
level: basic
minutes: 3
sourceLesson: para-oop
summary: Java overload selection uses static types; overriding uses the receiver at runtime.
---

One interface can have several implementations. Distinguish the language rule that selects an implementation from the runtime machinery that makes the call efficient.

## Polymorphism

Polymorphism ("many forms") means one piece of code works with values of different types. There are three main kinds:

- **Subtype polymorphism**: code written for `Animal` works on any subclass. This is what OOP usually means.
- **Ad hoc polymorphism**: the same name has different implementations per type, such as overloading `print(int)` and `print(String)`.
- **Parametric polymorphism**: type-parameterised definitions, like `List<T>`, that reuse a common implementation across element types. Actual language features can permit type-dependent behavior; Java generics are not a guarantee of mathematical parametricity (covered in the types module).

**Duck typing** accepts objects according to the operations actually used, without requiring declared inheritance. It resembles structural interface compatibility, but a matching method name alone does not guarantee the right behavioral contract. Python does not care whether an object inherits from anything; if it has a `.read()` method, you can pass it where a file is expected. "If it walks like a duck and quacks like a duck..."

## How dispatch works

**Dispatch** is how the language picks which method body runs for `obj.speak()`.

## Static vs dynamic dispatch

With **dynamic dispatch**, the choice depends on the object's runtime class. A common implementation technique is a **virtual method table** (vtable). The diagram is a simplified model: actual Java, C# and C++ runtimes/ABIs differ in object layout, interface dispatch and optimization; language semantics do not mandate one table layout.

```
 a (static type Animal)
 |
 v
 [Dog object]
 | vptr --> Dog vtable
 | ...       [0] speak -> Dog.speak
             [1] greet -> Animal.greet
```

In this simplified model, `a.speak()` loads the table and target before an indirect call; exact instruction and load counts vary, and JIT compilers like HotSpot often remove even that by **inlining** when they see only one class at a call site.

**Static dispatch** picks the method at compile time from the *declared* type. In Java, **overloading** is resolved statically, while **overriding** is resolved dynamically. That catches people out:

```java
// Overload choice uses declared types.
static String f(Object o) {
  return "obj";
}
static String f(String s) {
  return "str";
}

Object x = "hello";
f(x);  // "obj"
```

`x` holds a `String` at runtime, but its static type is `Object`, so the compiler picks `f(Object)`.

## Single, double and multiple dispatch

Ordinary Java and Python method selection uses **single dispatch**: the receiver (`obj` in `obj.m(arg)`) chooses the method. Languages such as Common Lisp (CLOS) and **Julia** use **multiple dispatch**, choosing on the runtime types of *all* arguments, which suits operations like `collide(asteroid, ship)`. In single-dispatch languages the **visitor pattern** fakes double dispatch with two virtual calls.

## Key takeaways
- Java overload selection uses static types; overriding uses the receiver at runtime.
- Dispatch semantics and concrete vtable layouts are separate concerns.

## Further reading
- [Java: method invocation](https://docs.oracle.com/javase/specs/jls/se21/html/jls-15.html)
- [Julia: methods and multiple dispatch](https://docs.julialang.org/en/v1/manual/methods/)
