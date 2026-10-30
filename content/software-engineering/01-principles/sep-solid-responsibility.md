---
id: sep-solid-responsibility
title: Single responsibility: whose change is this?
level: intermediate
minutes: 4
summary: SOLID offers questions about change pressure rather than unconditional rules.
sourceLesson: sep-solid
---

**SOLID** is an acronym for five object-oriented design principles. Robert C. Martin gathered most of them in his 2000 paper *Design Principles and Design Patterns*, and Michael Feathers coined the acronym around 2004. Two are older than Martin's versions: open/closed comes from Bertrand Meyer (1988) and Liskov substitution from Barbara Liskov (1987).

They are less rules than *questions to ask* when a design starts to hurt:

| Letter | Principle | Question it asks |
|---|---|---|
| S | Single responsibility | Who asks for this to change? |
| O | Open/closed | Can I add a case without editing old code? |
| L | Liskov substitution | Can a subtype stand in for its parent? |
| I | Interface segregation | Do clients depend on what they don't use? |
| D | Dependency inversion | Does policy depend on detail? |

All five come back to the coupling and cohesion lessons: put things that change together in one place (cohesion), and keep the connections between places narrow (coupling).

## S: Single responsibility principle

The popular version, "a class should do one thing", is vague. Martin's own wording is that a module should have **one, and only one, reason to change**, and his 2014 essay explains that the reasons are *people*: the group who would ask for the change. His book *Clean Architecture* (2017) states it as **a module should be responsible to one, and only one, actor**, where an actor is such a group. He traces the underlying idea to Parnas's information hiding and Dijkstra's separation of concerns.

```python
# Before: three actors, one class
class Employee:
    # asked for by finance
    def calculate_pay(self): ...
    # asked for by operations
    def report_hours(self): ...
    # asked for by IT / DBAs
    def save(self): ...
```

Imagine `calculate_pay` and `report_hours` share a helper `regular_hours()`. Finance asks for a change to how overtime is counted; a developer edits the helper; the operations report silently changes too. Two actors were coupled through one class.

```python
# After: one reason to change each
class PayCalculator:
    def pay(self, emp): ...

class HoursReporter:
    def report(self, emp): ...

class EmployeeRepository:
    def save(self, emp): ...
```

`Employee` becomes plain data. Each class now changes for one group's reasons.

The split has a price: three classes to find instead of one, and `Employee` data passed between them. It pays off when the groups' changes really do collide. A small class that one team owns may be clearer left whole.

> [!tip] The "and" test
> If describing a class needs "and" ("it parses the file *and* emails the result"), it may serve more than one actor. Check who actually asks for each part to change before splitting.

## Key takeaways
- SOLID offers questions about change pressure rather than unconditional rules.
- Single responsibility groups code by the actor requesting a change.
- Sharing a helper across unrelated actors can couple their business rules.

## Further reading
- [Martin: Design Principles and Design Patterns (2000)](https://objectmentor.com/resources/articles/Principles_and_Patterns.pdf)
- [Martin: The Single Responsibility Principle (2014)](https://blog.cleancoder.com/uncle-bob/2014/05/08/SingleReponsibilityPrinciple.html)
- [SOLID (history of the acronym)](https://en.wikipedia.org/wiki/SOLID)
