---
id: pattern-tangled-responsibilities
title: Untangling overloaded responsibilities
level: advanced
minutes: 3
sourceLesson: pattern-anti-patterns
summary: An anti-pattern is an attractive recurring solution with harmful consequences and a better alternative.
---

A pattern is a recurring *good* solution. An **anti-pattern** is a recurring *bad* one: a response to a real problem that looks reasonable at the time, keeps getting used, and produces worse consequences than it solves.

That second part matters. An anti-pattern isn't just a mistake. It's an attractive mistake, which is why it recurs, and it usually has a known better alternative.

The term is commonly attributed to Andrew Koenig’s 1995 writing and popularised by the 1998 book *AntiPatterns* by Brown, Malveau, McCormick and Mowbray. Closely related are Martin Fowler and Kent Beck's **code smells** from *Refactoring* (1999): surface symptoms that often point to a deeper problem.

## Why good teams produce bad structure

Anti-patterns rarely come from ignorance. They come from **local decisions that are each reasonable**:

- "Just add it to `OrderService` for now; we'll split it later."
- "Copy this function and tweak it; the deadline is Friday."
- "Nobody knows what this does, so don't touch it."

Each step saves time today and adds a little cost to every future change. The costs compound, which is why Ward Cunningham's **technical debt** metaphor fits so well.

## God object

### What it looks like

One class knows and does far too much. `OrderManager` validates input, calculates prices, talks to the database, sends emails, formats PDFs and holds global caches. The *AntiPatterns* book names it the **Blob anti-pattern**.

```
          +--------------+
 UI ----> |              | ----> DB
 API ---> | OrderManager | ----> Email
 Jobs --> |  4,000 lines | ----> PDF
 Tests -> |  90 methods  | ----> Cache
          +--------------+
```

### Why it happens

There's always one obvious place to put the next feature, and adding a method there is faster than designing a new class.

### Why it hurts

- Every change risks breaking an unrelated feature.
- It's a merge-conflict magnet, since everyone edits the same file.
- It's hard to test: constructing one needs every dependency.
- Low cohesion and high coupling at the same time.

### The way out

Extract classes along responsibility lines (pricing, notification, persistence), one at a time, with tests around each extraction. The **single responsibility principle** is the test: how many unrelated reasons does this class have to change?

## Big ball of mud

Brian Foote and Joseph Yoder named it in 1997: a system that is "haphazardly structured, sprawling, sloppy, duct-tape and bailing wire, spaghetti code jungle". It's the god object at the scale of a whole system: no discernible architecture, everything depending on everything.

Their paper is unusually sympathetic. It calls the big ball of mud the de facto standard software architecture, because it is what you get from deadlines, staff turnover and growth without investment in structure. Sometimes it's even the right economic choice for throwaway code.

### The way out

Rewriting from scratch is tempting but high-risk: the rewrite has to rediscover years of edge cases while the old system keeps changing, and it delivers little until cut-over. The usual alternative is the **strangler fig** approach (named by Martin Fowler): put a routing layer in front, build new functionality beside the old system, move features across one at a time, and retire the old code as it empties.

## Key takeaways
- An anti-pattern is an attractive recurring solution with harmful consequences and a better alternative.
- God objects accumulate unrelated reasons to change.
- Tests and gradual extraction or replacement preserve discovered behaviour during a refactor.

## Further reading
- [AntiPattern — Martin Fowler](https://martinfowler.com/bliki/AntiPattern.html)
- [Big Ball of Mud — Brian Foote and Joseph Yoder](https://www.laputan.org/mud/)
- [Strangler Fig Application — Martin Fowler](https://martinfowler.com/bliki/StranglerFigApplication.html)
