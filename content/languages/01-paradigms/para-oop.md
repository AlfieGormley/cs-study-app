---
id: para-oop
title: Object-oriented programming
level: basic
minutes: 13
summary: Encapsulation, inheritance versus composition, polymorphism, and how method dispatch actually works in Java, Python and JavaScript.
---

**Object-oriented programming (OOP)** organises a program around **objects**: bundles of state (fields) and the behaviour (methods) that operates on it. Instead of free-floating data passed to free-floating procedures, each piece of data comes with the operations allowed on it.

The ideas came from **Simula 67** (built for simulations, where "objects" were ships and customers) and **Smalltalk** (Alan Kay and colleagues at Xerox PARC in the 1970s). Kay has said the core idea was **messaging**: objects are like little computers that communicate only by sending each other messages. C++, Java, C#, Python and JavaScript all inherited some version of this.

OOP is often combined with imperative code, but objects may be immutable and their methods may be pure. What it adds is a way to **structure** that state. Four ideas carry most of the weight: encapsulation, inheritance, composition and polymorphism.

## Encapsulation

**Encapsulation** means an object hides its internal state and exposes only operations that keep that state valid. The rules that must always hold ("balance is never negative") are called **invariants**, and encapsulation is how you protect them.

```python
class Account:
    def __init__(self):
        self._balance = 0

    def deposit(self, amount):
        if type(amount) is not int:
            raise TypeError("integer pence")
        if amount <= 0:
            raise ValueError("must be > 0")
        self._balance += amount

    def withdraw(self, amount):
        if type(amount) is not int:
            raise TypeError("integer pence")
        if amount <= 0:
            raise ValueError("must be > 0")
        if amount > self._balance:
            raise ValueError("insufficient")
        self._balance -= amount

    @property
    def balance(self):
        return self._balance
```

This educational account uses integer pence and rejects nonpositive amounts. Callers respecting the public API use these methods, so validation is centralized. Python’s underscore convention does not prevent direct mutation of `_balance`; this is not a concurrent or production banking implementation.

How strictly languages enforce this varies:

| Language | Mechanism | Enforced? |
|---|---|---|
| Java, C# | `private`, `protected` | By compiler |
| Python | `_name` convention | No |
| Python | `__name` mangling | Weakly |
| JavaScript | `#field` | By runtime |

In Python, `self.__balance` inside class `Account` is renamed to `self._Account__balance`. That avoids accidental clashes in subclasses but is not real privacy. Python's culture is "we are all consenting adults".

## Inheritance

**Inheritance** lets a class reuse and extend another. A `Dog` *is an* `Animal`: it gets the parent's fields and methods and can **override** some of them.

```java
class Animal {
  String speak() { return "..."; }
  String greet() {
    return "I say " + speak();
  }
}

class Dog extends Animal {
  @Override
  String speak() { return "Woof"; }
}
```

`new Dog().greet()` returns `"I say Woof"`. The inherited `greet` calls `speak`, and because the object is a `Dog`, the overridden version runs.

Inheritance does two separate jobs at once:

1. **Code reuse**: the subclass gets the parent's implementation.
2. **Subtyping**: a `Dog` can be used wherever an `Animal` is expected.

Mixing these two jobs is where trouble starts.

### The fragile base class problem

Because subclasses depend on *how* the parent is implemented, not just on what it promises, changes in the parent can break them. Joshua Bloch's *Effective Java* has the classic example: a set that counts attempted insertions, including duplicates.

```java
class CountingSet<E>
    extends HashSet<E> {
  int added = 0;

  @Override
  public boolean add(E e) {
    added++;
    return super.add(e);
  }

  @Override
  public boolean addAll(
      Collection<? extends E> c) {
    added += c.size();
    return super.addAll(c);
  }
}
```

Calling `addAll(List.of("a", "b", "c"))` leaves `added` at **6**, not 3. `HashSet` inherits `addAll` from `AbstractCollection`, which calls `add` once per element, and that call dispatches to the overridden `add`. Nothing in `HashSet`'s public contract tells you this; you had to know its internals.

### Liskov substitution

The **Liskov substitution principle** (Barbara Liskov, 1987) says a subtype must be usable anywhere its parent is, without surprising the caller. The famous violation is `Square extends Rectangle`. A rectangle lets you set width and height independently; a square cannot. Code that does `r.setWidth(5); r.setHeight(2)` and expects area 10 breaks when handed a `Square`. In geometry a square *is a* rectangle, but in code a *mutable* square does not behave like a mutable rectangle.

## Composition

**Composition** builds objects out of other objects: a `Car` *has an* `Engine`. Instead of inheriting behaviour, an object holds a reference to a helper and **delegates** to it.

```java
class CountingSet<E> {
  private final Set<E> inner =
      new HashSet<>();
  int added = 0;

  boolean add(E e) {
    added++;
    return inner.add(e);
  }

  boolean addAll(Collection<E> c) {
    added += c.size();
    return inner.addAll(c);
  }
}
```

Now `inner.addAll` calls `inner`'s own `add`, not ours, so the count is correct. The wrapper depends only on `Set`'s public behaviour. You may substitute another Set implementation only if its contract suits callers: TreeSet requires an ordering and has different null and equality/ordering considerations. (In practice you would also `implements Set<E>` and forward the remaining methods, which is the **decorator** pattern.)

The *Design Patterns* book (Gamma, Helm, Johnson and Vlissides, 1994) summed it up as "favour object composition over class inheritance". The rule of thumb:

- Use inheritance for a genuine **is-a** relationship where the subtype honours the parent's contract, ideally when the parent was designed for extension.
- Use composition for **has-a** or **uses-a** relationships, and whenever you just want to reuse code.

Many newer languages lean this way. **Go** has no inheritance at all: it offers struct embedding (automatic delegation) and interfaces. **Rust** has traits but no inheritance between structs.

## Polymorphism

**Polymorphism** ("many forms") means one piece of code works with values of different types. There are three main kinds:

- **Subtype polymorphism**: code written for `Animal` works on any subclass. This is what OOP usually means.
- **Ad hoc polymorphism**: the same name has different implementations per type, such as overloading `print(int)` and `print(String)`.
- **Parametric polymorphism**: generics, like `List<T>`, which work identically for any `T` (covered in the types module).

**Duck typing** is subtype polymorphism without declared types. Python does not care whether an object inherits from anything; if it has a `.read()` method, you can pass it where a file is expected. "If it walks like a duck and quacks like a duck..."

## How dispatch works

**Dispatch** is how the language picks which method body runs for `obj.speak()`.

### Static vs dynamic dispatch

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

### Single, double and multiple dispatch

Java and Python use **single dispatch**: only the receiver (`obj` in `obj.m(arg)`) chooses the method. Languages such as Common Lisp (CLOS) and **Julia** use **multiple dispatch**, choosing on the runtime types of *all* arguments, which suits operations like `collide(asteroid, ship)`. In single-dispatch languages the **visitor pattern** fakes double dispatch with two virtual calls.

### Python and JavaScript

Python dispatch is a runtime lookup. With ordinary `object.__getattribute__`, lookup gives data descriptors found through the class MRO precedence over the instance dictionary, then considers non-data descriptors and other class attributes. Functions implement non-data descriptors, which bind ordinary methods. Custom attribute hooks can change lookup behavior. With multiple inheritance, the MRO is computed by **C3 linearisation**:

```python
class A: pass
class B(A): pass
class C(A): pass
class D(B, C): pass

print([k.__name__ for k in D.__mro__])
# ['D', 'B', 'C', 'A', 'object']
```

In the "diamond", A comes after both B and C, so B and C get a chance to override A's methods. `super()` follows this MRO, not just "the parent".

JavaScript is **prototype-based**: objects inherit directly from other objects. A property lookup walks the prototype chain. The `class` keyword (ES2015) is mostly syntax over that: `class Dog extends Animal` sets `Dog.prototype`'s prototype to `Animal.prototype`.

## Pitfalls

- **Deep hierarchies**: five levels of inheritance means reading five files to know what a method does.
- **God objects**: one class that knows everything defeats encapsulation.
- **Getters and setters for every field**: if every field is exposed, you have a struct with ceremony and no invariants.
- **Inheritance for reuse only**: if you never use the subclass *as* the parent type, composition is almost certainly better.

## Key takeaways
- OOP bundles state with the operations allowed on it; encapsulation protects invariants.
- Inheritance mixes code reuse with subtyping. Subclasses that depend on parent internals break when the parent changes (fragile base class).
- Prefer composition and delegation for reuse; reserve inheritance for true, contract-honouring is-a relationships (Liskov).
- Polymorphism comes in subtype, ad hoc (overloading) and parametric (generics) forms; duck typing is subtyping without declarations.
- Java selects overriding implementations at runtime and resolves overloads at compile time from static types; vtables are an implementation technique.
- Python looks methods up along the C3 MRO at runtime; JavaScript walks a prototype chain.

## Further reading
- [Object-oriented programming — Wikipedia](https://en.wikipedia.org/wiki/Object-oriented_programming)
- [Composition over inheritance — Wikipedia](https://en.wikipedia.org/wiki/Composition_over_inheritance)
- [Liskov substitution principle — Wikipedia](https://en.wikipedia.org/wiki/Liskov_substitution_principle)
- [The Python 2.3 Method Resolution Order — Python docs](https://docs.python.org/3/howto/mro.html)
- [Inheritance and the prototype chain — MDN](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Inheritance_and_the_prototype_chain)
- [Virtual method table — Wikipedia](https://en.wikipedia.org/wiki/Virtual_method_table)
