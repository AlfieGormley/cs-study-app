---
id: pattern-why
title: Why patterns
level: basic
minutes: 10
summary: What a design pattern is, where the idea came from, the two principles behind the Gang of Four catalogue, and why many patterns shrink or vanish in a language like Python.
---

Every experienced engineer has a mental library of shapes that keep coming back. "Wrap this object so it looks like that interface." "Let callers plug in their own rule." "Tell everyone who cares when this changes." A **design pattern** is one of those shapes, written down and given a name.

A pattern is not a library you import, and it is not finished code. It is a *recurring solution to a recurring problem in a context*, described well enough that you can adapt it to your own situation.

## Where the idea came from

The word comes from architecture. In *A Pattern Language* (1977), Christopher Alexander and colleagues described 253 patterns for towns and buildings, such as "Light on two sides of every room". Each one named a problem, the forces pulling against each other, and a solution you could apply "a million times over, without ever doing it the same way twice".

Software borrowed the idea in the late 1980s. The breakthrough was the 1994 book *Design Patterns: Elements of Reusable Object-Oriented Software* by Erich Gamma, Richard Helm, Ralph Johnson and John Vlissides, known as the **Gang of Four (GoF)**. It catalogued 23 patterns, with examples in C++ and Smalltalk.

## What a pattern description contains

The GoF book describes each pattern with the same template. The four essential parts are:

1. **Name.** A word or two that becomes shared vocabulary.
2. **Problem.** When to apply it, including the conditions that must hold.
3. **Solution.** The elements, their roles and how they collaborate. It is a template, not code.
4. **Consequences.** The costs and benefits: what gets easier, what gets harder.

The consequences matter as much as the solution. A pattern that makes one kind of change easy nearly always makes another kind harder. That is the trade you are choosing to make.

## The catalogue at a glance

The GoF split their 23 patterns by purpose:

| Purpose | Concerned with | Examples |
|---|---|---|
| Creational | How objects are made | Factory method, builder |
| Structural | How objects are composed | Adapter, decorator, proxy |
| Behavioural | How objects share work | Strategy, observer, visitor |

The full list:

- **Creational (5):** abstract factory, builder, factory method, prototype, singleton.
- **Structural (7):** adapter, bridge, composite, decorator, facade, flyweight, proxy.
- **Behavioural (11):** chain of responsibility, command, interpreter, iterator, mediator, memento, observer, state, strategy, template method, visitor.

This module covers the ones you will meet most often in real code and in interviews.

## The two principles underneath

Almost every GoF pattern is an application of two principles stated in the book's introduction.

### Program to an interface, not an implementation

Code should depend on *what an object can do*, not *which class it is*. If a report generator accepts "anything with a `write(text)` method", you can hand it a text file, a socket adapter exposing that contract, an in-memory text buffer or a test fake. A raw socket does not provide write(text).

In Python this is **duck typing**. You can make it explicit with an abstract base class or a `typing.Protocol`, but the idea is the same.

### Favour object composition over class inheritance

Inheritance fixes behaviour at class-definition time and couples the subclass to its parent's internals. Composition lets you assemble behaviour from parts at run time.

Here is the classic way inheritance goes wrong:

```
         Notifier
        /    |    \
    Email   SMS   Slack
     /  \
 Email+  Email+
 Retry   Log      ... and so on
```

Every combination of feature and channel needs its own subclass. With three channels and three optional features, that is up to 3 × 2³ = 24 classes. With composition you write 3 channels and 3 wrappers, and combine them as needed:

```python
class Email:
    def send(self, msg):
        print(f"email: {msg}")

class Retry:
    def __init__(self, inner, tries=3):
        valid = type(tries) is int
        if not valid or tries < 1:
            raise ValueError("tries > 0")
        self.inner = inner
        self.tries = tries

    def send(self, msg):
        for n in range(self.tries):
            try:
                return self.inner.send(msg)
            except ConnectionError:
                if n == self.tries - 1:
                    raise

notifier = Retry(Email())
notifier.send("deploy finished")
# prints: email: deploy finished
```

`Retry` works with any object that has `send`, so one class serves every channel. That is the decorator pattern, which you will meet properly in lesson 3.

## Why bother naming them?

> [!tip] The real value is vocabulary
> "Put an adapter in front of the legacy client" conveys succinctly what would otherwise take a paragraph and a whiteboard. Reviewers immediately know the shape, the trade-offs and the usual pitfalls.

Patterns also help you:

- **Recognise designs in other people's code.** When you see `ast.NodeVisitor` or `BufferedReader(FileIO(...))`, knowing the pattern tells you how the pieces are meant to fit.
- **Spot the forces in a problem.** "This needs to vary independently of that" is a sign that a pattern such as strategy or bridge may help.
- **Avoid reinventing a worse version.** Many hand-rolled designs are half a pattern with the important consequence missing (an observer with no way to unsubscribe, say).

## Patterns and language features

The GoF wrote for C++ and Smalltalk in the early 1990s. Several of their patterns exist to work around missing language features.

In a 1996 talk, Peter Norvig argued that **16 of the 23** patterns have qualitatively simpler implementations in dynamic languages such as Lisp and Dylan, at least for some of their uses. Some become invisible altogether. The same is largely true of Python:

| Pattern | What Python gives you |
|---|---|
| Strategy | Pass a function |
| Command | Pass a function or closure |
| Iterator | `__iter__`, `__next__`, generators |
| Singleton | A module-level object |
| Factory method | Classes are callables |
| Template method | Often just pass a hook |

Older Java examples often use an interface and explicit classes; Java 8 and later also support lambdas and method references for functional-interface strategies. In Python, `sorted` takes a `key` function, and that *is* the strategy pattern:

```python
words = ["pear", "Fig", "apple"]
print(sorted(words))
# ['Fig', 'apple', 'pear']
print(sorted(words, key=str.lower))
# ['apple', 'Fig', 'pear']
```

(For the ASCII letters here, uppercase F precedes lowercase a and p in code-point order. This is not a universal ordering rule for all Unicode upper- and lowercase letters.)

The pattern has not disappeared. The *problem* (let the caller choose the rule) is still there; the language just makes the *solution* a one-liner. Knowing the pattern still tells you the consequences, for instance that every strategy must accept the same arguments.

## When patterns hurt

Patterns are a means, not a goal. Common ways they go wrong:

- **Pattern-first design.** Starting with "let's use the abstract factory" and then looking for a problem. Start from the change you expect, then pick the shape that makes it cheap.
- **Speculative flexibility.** Adding a strategy interface for a rule that has only ever had one implementation. That is a YAGNI violation: you pay the indirection now for flexibility you may never need.
- **Java in Python.** Writing `AbstractShapeFactoryInterface` classes in a language where a dictionary of functions would do.
- **Cargo-culting the diagram.** Copying the GoF structure exactly when only part of it applies.

> [!warning] Indirection has a price
> Each pattern adds a layer between "what happens" and "where it is written". That layer is worth it when it absorbs real change. When it does not, it is just harder code to read and debug.

A good rule: **refactor towards a pattern** when the second or third variation shows up, rather than designing for it on day one. Joshua Kerievsky's book *Refactoring to Patterns* (2004) is built on this idea.

## Patterns beyond the GoF

The GoF catalogue is about designing *classes and objects*. Other catalogues work at different scales:

- **Enterprise application patterns** (Martin Fowler, 2002): repository, unit of work, data mapper, active record.
- **Integration patterns** (Hohpe and Woolf, 2003): message channel, publish-subscribe, dead letter channel.
- **Concurrency patterns:** producer-consumer, thread pool, reactor.
- **Architectural patterns:** layered, hexagonal, microservices, event sourcing.

The idea is the same at every scale: a named problem, a reusable solution and an honest list of consequences.

## Key takeaways
- A design pattern is a named, reusable solution to a recurring problem in a context, with known consequences. It is a template, not code.
- The 1994 Gang of Four book catalogued 23 patterns in three groups: creational, structural and behavioural.
- Two principles drive most of them: program to an interface, and favour composition over inheritance.
- The main payoff is shared vocabulary and recognising designs in existing code.
- Many patterns become trivial in Python because functions are first-class and iteration is built in, but the problem and its trade-offs remain.
- Introduce a pattern when real variation appears; speculative patterns add indirection with no payoff.

## Further reading
- [Design Patterns (the GoF book) — Wikipedia](https://en.wikipedia.org/wiki/Design_Patterns)
- [Software design pattern — Wikipedia](https://en.wikipedia.org/wiki/Software_design_pattern)
- [A Pattern Language — Wikipedia](https://en.wikipedia.org/wiki/A_Pattern_Language)
- [Design Patterns in Dynamic Languages — Peter Norvig](https://norvig.com/design-patterns/)
- [Composition over inheritance — Python Design Patterns guide](https://python-patterns.guide/gang-of-four/composition-over-inheritance/)
- [Design patterns catalogue — Refactoring.Guru](https://refactoring.guru/design-patterns/catalog)
