---
id: para-runtime-object-lookup
title: Python MRO and JavaScript prototypes
level: basic
minutes: 3
sourceLesson: para-oop
summary: Python super follows the MRO rather than a fixed parent.
---

Python and JavaScript both select methods at runtime, but they follow different lookup structures. Trace Python's class order first, then compare JavaScript's chain of prototypes.

## Python and JavaScript

Python dispatch is a runtime lookup. With ordinary `object.__getattribute__`, lookup gives data descriptors found through the class MRO precedence over the instance dictionary, then considers non-data descriptors and other class attributes. Functions implement non-data descriptors, which bind ordinary methods. Custom attribute hooks can change lookup behavior. With multiple inheritance, the MRO is computed by **C3 linearisation**:

```python
# The full MRO guides super calls.
class A: pass
class B(A): pass
class C(A): pass
class D(B, C): pass

print([k.__name__ for k in D.__mro__])
# ['D', 'B', 'C', 'A', 'object']
```

In the "diamond", A comes after both B and C, so B and C get a chance to override A's methods. `super()` follows this MRO, not just "the parent".

JavaScript is **prototype-based**: objects can inherit properties from other objects. To interpret the Python question, follow `D`, then `B`, then `C`, then `A`; cooperative `super()` calls continue along this full order. A property lookup walks the prototype chain. The `class` keyword (ES2015) is mostly syntax over that: `class Dog extends Animal` sets `Dog.prototype`'s prototype to `Animal.prototype`.

## Pitfalls

- Deep hierarchies: five levels of inheritance means reading five files to know what a method does.
- **God objects**: one class that knows everything defeats encapsulation.
- Getters and setters for every field: if every field is exposed, you have a struct with ceremony and no invariants.
- Inheritance for reuse only: if you never use the subclass *as* the parent type, composition is almost certainly better.

## Key takeaways
- Python super follows the MRO rather than a fixed parent.
- JavaScript property lookup follows the prototype chain.

## Further reading
- [Python: method resolution order](https://docs.python.org/3/howto/mro.html)
- [ECMAScript language specification](https://tc39.es/ecma262/2023/)
