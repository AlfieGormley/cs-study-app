---
id: sep-solid-responsibility
title: Single responsibility: whose change is this?
level: intermediate
minutes: 3
summary: SOLID offers questions about change pressure rather than unconditional rules.
sourceLesson: sep-solid
---

**SOLID** is an acronym for five object-oriented design principles widely presented by Robert C. Martin. They are less rules than *questions to ask* when a design starts to hurt:

| Letter | Principle | Question it asks |
|---|---|---|
| S | Single responsibility | Who asks for this to change? |
| O | Open/closed | Can I add a case without editing old code? |
| L | Liskov substitution | Can a subtype stand in for its parent? |
| I | Interface segregation | Do clients depend on what they don't use? |
| D | Dependency inversion | Does policy depend on detail? |

All five are really about the previous lesson's themes: put things that change together in one place (cohesion), and keep the connections between places narrow (coupling).

## S: Single responsibility principle

The popular version, "a class should do one thing", is vague. Martin's sharper version is: **a module should be responsible to one, and only one, actor**. An SRP actor is a group of people who might request a change.

```python
# Shared helpers can entangle these actors.
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
# These are responsibility sketches.
# After: one reason to change each
class PayCalculator:
    def pay(self, emp): ...

class HoursReporter:
    def report(self, emp): ...

class EmployeeRepository:
    def save(self, emp): ...
```

`Employee` becomes plain data. Each class now changes for one group's reasons.

> [!tip] The "and" test
> If describing a class needs "and" ("it parses the file *and* emails the result"), it probably serves more than one actor.

## Key takeaways
- SOLID offers questions about change pressure rather than unconditional rules.
- Single responsibility groups code by the actor requesting a change.
- Sharing a helper across unrelated actors can couple their business rules.

## Further reading
- [Martin: Design Principles and Design Patterns](https://objectmentor.com/resources/articles/Principles_and_Patterns.pdf)
- [SingleReponsibilityPrinciple](https://blog.cleancoder.com/uncle-bob/2014/05/08/SingleReponsibilityPrinciple.html)
