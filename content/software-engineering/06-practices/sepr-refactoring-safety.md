---
id: sepr-refactoring-safety
title: Refactoring without changing behaviour
level: basic
minutes: 4
summary: Build a safety net and separate structural changes from feature and bug fixes.
sourceLesson: sepr-refactoring
---

**Refactoring** is changing the structure of code without changing what it does. Martin Fowler's definition has two parts: a refactoring is a small change that makes code easier to understand and cheaper to modify, *without changing its observable behaviour*; and *refactoring* (the activity) is applying a series of those small changes.

The key word is *behaviour-preserving*. If you rename a function and fix a bug in the same commit, you have done two things, and when something breaks you will not know which one caused it. Kent Beck's image is the **two hats**: when you add a feature you wear one hat, when you refactor you wear the other, and you swap often but never wear both at once.

## Why bother?
Code is read far more than it is written. Every feature you add lands in the shape the code already has. If that shape is awkward, the feature is slow to add and easy to get wrong.

Beck's advice sums up the workflow: "make the change easy (warning: this may be hard), then make the easy change." Refactoring is the first half. You reshape the code so the new feature fits naturally, then add it.

There are a few common moments to refactor:

- **Preparatory**: just before a feature, to make room for it.
- **Comprehension**: while reading confusing code, rename and extract until it makes sense, so the next reader gets your understanding for free.
- **Litter-pickup**: small improvements as you pass through (the "boy scout rule": leave the code a bit better than you found it).
- **Planned**: a dedicated chunk of work when neglect has made an area painful. Healthy teams need this less, because the other three keep it in check.

Prioritise restructuring where code changes frequently and those changes cause regressions or slow reviews. A stable, rarely changed module may offer little change-related return, while still needing assessment for security, operational and knowledge risks.

## The safety net: tests
You cannot claim behaviour is unchanged unless something checks it. Before refactoring, you need tests that cover the code you are about to touch, and they should be fast enough to run after every small step.

If the code has no tests, write **characterisation tests** first (Michael Feathers' term from *Working Effectively with Legacy Code*). You do not assert what the code *should* do; you record what it *currently* does, bugs included.

```python
def price(qty, item):
    # Keep current pricing, even quirks.
    total = qty * item
    if qty >= 500:
        return total - 100
    return total

def test_price_characterisation():
    # Whatever it returns today is "right"
    # for the purposes of refactoring.
    assert price(qty=0, item=10) == 0
    assert price(qty=3, item=10) == 30
    assert price(qty=600, item=10) == 5900
```

If a refactoring changes one of these outputs, you have changed behaviour, deliberately or not. Fix bugs afterwards, as a separate, visible change.

> [!tip] Commit at every green
> Make one small move, run the tests, commit. If the next step goes wrong you can discard the intended tracked-file edits with `git restore <paths>` after checking the diff (unrelated uncommitted work must be preserved) instead of debugging a half-finished restructure.

## Key takeaways
- Refactoring preserves observable behaviour; bug fixes and new features are separate changes.
- Use tests around the affected code, and characterisation tests when intended legacy behaviour is unclear.
- Prefer small green steps and prioritise areas where structure causes real cost.

## Further reading
- [Definition of Refactoring — Martin Fowler](https://martinfowler.com/bliki/DefinitionOfRefactoring.html)
- [Workflows of Refactoring — Martin Fowler](https://martinfowler.com/articles/workflowsOfRefactoring/)
