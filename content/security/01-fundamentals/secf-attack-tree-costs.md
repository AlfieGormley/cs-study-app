---
id: secf-attack-tree-costs
title: Attack trees and their cost assumptions
level: basic
minutes: 4
sourceLesson: secf-threat-modelling
summary: OR chooses a feasible alternative; AND needs every required step.
---

## Attack trees

STRIDE is good at breadth: finding many threats. **Attack trees**, popularised by Bruce Schneier in 1999, are good at depth: analysing one goal in detail.

The root is the attacker's goal. Children are ways to achieve it. An **OR** node succeeds if any child does; an **AND** node needs all children.

```
Read another customer's invoice (OR)
+- Guess invoice URL (IDOR)       2
+- Take over their account (OR)
|  +- Credential stuffing         3
|  +- Phish password AND OTP (AND)
|     +- Phishing page             2
|     +- Real-time OTP relay       4
+- Steal DB backup (AND)
   +- Find public bucket           5
   +- Decrypt backup               9
```

The numbers are invented additive costs for this exercise, not measured difficulty or ordinal 1-to-10 ratings. Assume costs do not overlap, all steps are feasible and attackers choose the cheapest route. Under those assumptions:

- **OR node**: the attacker picks the cheapest child, so take the **minimum**.
- **AND node**: the attacker must do every child, so take the **sum**.

> [!analogy] Real-world analogy: a burglar choosing a way in
> A burglar can climb through an unlocked back window, or use the front door, which means both picking the lock and disabling the alarm.
>
> **How it maps:** "Window or front door" is an OR node: the burglar uses whichever is easier. "Pick the lock and disable the alarm" is an AND node: both are needed, so their difficulty adds up. Fitting a better front lock leaves the window as the cheapest way in.
>
> **Where it stops:** Real burglars do not have exact costs, may not know every route and can change plans part-way. Attack-tree numbers are likewise judgements under stated assumptions, not measurements.

Working from the leaves up: the phishing route is an AND, so it costs 2 plus 4, which is 6. Account takeover is an OR, so it costs the cheaper of credential stuffing (3) and phishing (6), which is 3. Backup theft is an AND costing 5 plus 9, which is 14. The root is an OR, so the attacker's cheapest route is the invoice-URL guess at 2.

In this model, removing the IDOR path leaves the root at the cheaper of 3 and 14, so the minimum rises from 2 to 3. Strengthening a cost-14 path alone leaves that minimum unchanged. Real prioritisation also needs impact, likelihood, mitigation cost and interactions between paths; these invented numbers cannot rank a real deployment.

```python
def cost(node):
    kids = node.get("children")
    # Leaves carry the exercise cost.
    if not kids:
        return node["cost"]
    # Resolve descendants before the parent.
    costs = [cost(c) for c in kids]
    if node["type"] == "AND":
        # AND requires paying for every
        # step.
        return sum(costs)
    return min(costs)  # OR
```

Other annotations need their own aggregation rules. For these additive costs use minimum/sum; for "requires special equipment?", OR requires it only when every feasible alternative does, while AND requires it when any required step does. Probabilities require explicit dependence assumptions and mustn't simply be added like costs.

> [!warning] Trees are only as good as their leaves
> An attack tree can't show a path nobody thought of. Use STRIDE (breadth) to populate the tree, and the tree (depth) to prioritise.

## Key takeaways
- OR chooses a feasible alternative; AND needs every required step.
- Minimum and sum apply only to this additive cost model.
- Boolean requirements and probabilities need different aggregation rules.

## Further reading
- [Attack Trees — Bruce Schneier](https://www.schneier.com/academic/archives/1999/12/attack_trees.html)
