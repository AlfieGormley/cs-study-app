---
id: lin-list-combining-patterns
title: Combine pointer patterns and preserve caller state
level: intermediate
minutes: 3
sourceLesson: lin-list-techniques
summary: Split, reverse and compare can test a palindrome with fixed extra space.
---

The previous units established reversal, middle finding, fixed gaps and merging. Combine these patterns without changing their assumptions: ordinary traversal and intersection search below require finite, acyclic inputs. In the complexity bounds n is the number of nodes being processed.

## Combining patterns

Harder problems chain these together.

- **Is the list a palindrome, in O(1) space?** Find the middle (fast/slow), reverse the second half, compare the two halves node by node, then reverse it back to restore the list.
- **Reorder `1,2,3,4,5` to `1,5,2,4,3`?** Find the middle, reverse the second half, then interleave the halves.
- **Where do two lists intersect?** Walk pointer A along list A then list B, and pointer B along B then A. Both travel the same total distance, so they arrive at the shared node together (or both reach `None`).

> [!warning] Common bugs
> - Losing the rest of the list by overwriting `next` before saving it.
> - Checking `fast.next.next` without first checking `fast.next`, causing an AttributeError on short lists.
> - Comparing values (`==`) when you mean identity (`is`).
> - Forgetting to restore a list you mutated (for example in the palindrome check), surprising the caller.

### Intersection by switching routes

Use node identity and finite acyclic inputs. Each pointer traverses its own list, then switches to the other head on the iteration after it reaches None. Equal total routes cancel out the difference between the two unshared prefixes. If there is no shared node, both eventually reach None together.

```python
def intersection(a, b):
    p, q = a, b
    while p is not q:
        # Switch heads after the null state.
        p = p.next if p else b
        q = q.next if q else a
    # Shared node, or None for no junction.
    return p
```

For distinct prefixes of three and five nodes followed by four shared nodes, the pointers meet after thirteen loop iterations. One pointer traverses seven links to None, spends one iteration switching, then traverses the other five-node prefix. The other traverses nine links, switches, and takes three more. Equal-length inputs can meet earlier; count the extra iteration spent on None when tracing this exact loop.

For the palindrome pattern, split so the second half excludes an odd middle node, reverse that second half, compare corresponding values, and reverse it back even after a mismatch. Restoring the original links is part of the function’s contract, rather than an optional cosmetic step. An implementation must also reconnect any link it detached during splitting.

## Key takeaways
- Split, reverse and compare can test a palindrome with fixed extra space.
- Switching to the other list's head equalises the two intersection-search routes, including the step through None.

## Further reading
- [Cycle detection — Wikipedia](https://en.wikipedia.org/wiki/Cycle_detection)
- [Linked list — Wikipedia](https://en.wikipedia.org/wiki/Linked_list)
