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

The numbers are invented additive cost units for this exercise, not measured difficulty or ordinal 1-to-10 ratings. Assume costs do not overlap, all steps are feasible and attackers choose the cheapest route. Under those assumptions:

- **OR node**: the attacker picks the cheapest child, so take the **minimum**.
- **AND node**: the attacker must do every child, so take the **sum**.

For any non-leaf node with at least one child, the exercise uses these rules:

```formula
C_OR = min(c_1, c_2, …, c_k)
C_AND = c_1 + c_2 + … + c_k
where
C_OR: the cost of an OR node, in the exercise's invented cost units
C_AND: the cost of an AND node, in the same units
min: the minimum: the smallest of the values in the brackets
c_1: the cost of the node's first child (a leaf's number, or a cost already worked out lower down)
c_2: the cost of the second child
c_k: the cost of the last child
k: the number of children the node has
…: "and so on" for every child in between
In words: an attacker who may choose pays only for the cheapest option; an attacker who must do every step pays for all of them.
```

Work from the leaves up to the root:

```formula
C_phish = 2 + 4 = 6
C_takeover = min(3, C_phish) = 3
C_backup = 5 + 9 = 14
C_root = min(2, C_takeover, C_backup)
C_root = min(2, 3, 14) = 2
where
C_phish: cost of the AND node "Phish password AND OTP": phishing page (2) plus real-time OTP relay (4), in cost units
C_takeover: cost of the OR node "Take over their account": the cheaper of credential stuffing (3) and the phishing route
C_backup: cost of the AND node "Steal DB backup": find the public bucket (5) plus decrypt the backup (9)
C_root: cost of the root goal, the cheapest of its three children: guessing the invoice URL (2), account takeover and backup theft
min: the minimum: the smallest of the values in the brackets
In words: the cheapest way to read another customer's invoice costs 2 units, by guessing the invoice URL (the IDOR).
```

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
