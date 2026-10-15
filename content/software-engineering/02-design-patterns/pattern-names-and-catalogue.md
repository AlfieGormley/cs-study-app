---
id: pattern-names-and-catalogue
title: Named patterns and their consequences
level: basic
minutes: 3
sourceLesson: pattern-why
summary: A pattern describes a recurring problem, a reusable collaboration and its consequences.
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
- **Behavioural (11):** chain of responsibility, command, Interpreter pattern, iterator, mediator, Memento pattern, observer, state, strategy, template method, visitor.

This module covers the ones you will meet most often in real code and in interviews.

## Why bother naming them?

> [!tip] The real value is vocabulary
> "Put an adapter in front of the legacy client" conveys succinctly what would otherwise take a paragraph and a whiteboard. Reviewers immediately know the shape, the trade-offs and the usual pitfalls.

Patterns also help you:

- **Recognise designs in other people's code.** When you see `ast.NodeVisitor` or `BufferedReader(FileIO(...))`, knowing the pattern tells you how the pieces are meant to fit.
- **Spot the forces in a problem.** "This needs to vary independently of that" is a sign that a pattern such as strategy or bridge may help.
- **Avoid reinventing a worse version.** Many hand-rolled designs are half a pattern with the important consequence missing (an observer with no way to unsubscribe, say).

## Key takeaways
- A pattern describes a recurring problem, a reusable collaboration and its consequences.
- The GoF catalogue has five creational, seven structural and eleven behavioural patterns.
- Shared names help engineers recognise designs and discuss the trade-offs.

## Further reading
- [Design Patterns — publisher catalogue](https://www.informit.com/store/design-patterns-elements-of-reusable-object-oriented-software-9780201633610)
- [Design Patterns in Dynamic Languages — Peter Norvig](https://www.norvig.com/design-patterns/)
