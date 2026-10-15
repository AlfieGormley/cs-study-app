---
id: git-trunk-feature-flags
title: Trunk-based development and unfinished work
level: intermediate
minutes: 4
sourceLesson: git-workflows
summary: Integrate small changes at least daily rather than parking a whole feature on a long branch.
---

A workflow helps only if integration is frequent enough to reveal incompatible work. Trunk-based development turns that into a daily practice, including while a large feature remains unfinished.

## Trunk-based development

In **trunk-based development** (TBD), everyone integrates into one trunk at least daily. There are two styles:

- **Commit straight to trunk**: common in small teams with strong tests and pairing.
- **Short-lived feature branches**: a branch lives hours to a day or two, is reviewed in a small pull request, and merged. This is the usual style in companies that require review.

The rule is not "no branches"; it is "no long-lived development branches apart from trunk; maintained release branches are a separate case".

DORA's research (from its 2016 and 2017 data) found that teams with higher delivery performance tended to have **three or fewer active branches**, **merge into trunk at least daily**, and have **no code freezes or integration phases**.

### Shipping unfinished work safely

If you merge daily, half-built features reach trunk. Two techniques keep that safe:

**Feature flags.** New code paths ship switched off and are enabled when ready, possibly for a percentage of users first.

This application sketch assumes a flag service, both pricing implementations and a charging function. It shows routing, not a complete checkout system. A disabled flag does not make incompatible initialisation or data changes safe.

```python
def checkout(cart, user):
    # Choose one pricing path per user.
    if flags.enabled("new_pricing", user):
        total = new_pricing(cart)
    else:
        total = legacy_pricing(cart)
    # Both totals fit the charge contract.
    return charge(user, total)
```

**Branch by abstraction.** To replace a large component (say, an ORM), introduce an interface in front of it, move callers onto the interface, build the new implementation behind it step by step, switch over, then delete the old one. Every step is a small, releasable commit on trunk.

Every flag is a fork in the code's behaviour, and forks multiply. With independent on/off flags, each extra flag can double the number of combinations the code might run in:

```formula
N = 2^n
N = 2^10 = 1024
where
N: the most on/off combinations (configurations) the flags allow
n: the number of independent Boolean (on/off) feature flags affecting the same behaviour
2: the two states of each flag, on and off; each state of one flag can pair with every combination of the others
^: raise to a power: 2^n means n copies of 2 multiplied together
In words: every extra flag doubles the possible configurations, so 10 flags already allow 1,024 and 20 allow over a million.
```

This is an upper bound: constraints and paths that can never be on together reduce the combinations that can actually happen, and teams test the ones that matter rather than all of them. But the trend is why old flags must go.

> [!warning] Flags are debt
> Give each flag an owner and an expiry date, and delete it once the feature is fully launched. Stale flags cause real incidents: The SEC's account of Knight Capital's 2012 incident reports losses exceeding $460 million and describes a repurposed old flag that reactivated dead code on one server.



## Key takeaways

- Integrate small changes at least daily rather than parking a whole feature on a long branch.
- Feature flags and branch by abstraction let incomplete work integrate safely when compatibility is maintained.
- Independent flags multiply configurations; assign owners and remove completed release flags.

## Further reading

- [Trunk Based Development](https://trunkbaseddevelopment.com/)
- [Trunk-based development — DORA capabilities](https://dora.dev/capabilities/trunk-based-development/)
- [Branch by abstraction — Martin Fowler](https://martinfowler.com/bliki/BranchByAbstraction.html)
- [Feature Toggles — Pete Hodgson on martinfowler.com](https://martinfowler.com/articles/feature-toggles.html)
