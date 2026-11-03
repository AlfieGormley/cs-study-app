---
id: adv-reservoir-uniformity
title: Reservoir sampling and uniform subsets
level: advanced
minutes: 3
summary: A later item enters a size-k reservoir with k divided by the number of items seen.
sourceLesson: adv-randomised-structures
---

Here n is the number of keys or stream items, and k is the requested sample size when sampling. Random draws are assumed independent and uniform under the stated model.

## Reservoir sampling

You are reading a log stream of unknown length and want a uniform random sample of k lines, using O(k) memory. You cannot store the stream, and you cannot know n in advance.

**Algorithm R** keeps the first k items. Then, for each later item `i` (counting from 0), it draws `j = randint(0, i)`; if `j < k`, the new item replaces `sample[j]`.

```python
import random

def reservoir(stream, k):
    sample = []
    for i, x in enumerate(stream):
        if i < k:
            sample.append(x)
        else:
            # randint is inclusive of i
            # Draw uniformly among all items
            # seen.
            j = random.randint(0, i)
            if j < k:
                # Replace a slot only when j
                # is in it.
                sample[j] = x
    return sample
```

### Why it is uniform

Assume independent uniform draws and a non-negative sample size. Every later item gets one draw over all positions seen so far. It enters only when that draw selects one of the sample slots; if it enters, each slot is equally likely to be replaced. As the stream grows, the chance of admission shrinks.

An early item starts with an advantage because it enters automatically, but must survive more opportunities for replacement. A later item has a smaller admission chance but fewer later replacements to survive. These effects balance: every stream position has the same final inclusion chance. Duplicate values still represent distinct stream positions.

```formula reference
P_enter = k / (i + 1)
P_survive(t) = t / (t + 1)
P = k/(i+1) × (i+1)/(i+2) × … × (n−1)/n
P = k / n
where
k: positive sample size, no greater than the stream length
n: total number of stream items
i: zero-based position of a later item, at least k
t: a subsequent zero-based position
P_enter: probability the item enters on arrival
P_survive(t): probability an admitted item survives the later draw at position t
P: probability the item appears in the final sample
…: one survival factor for each later position
In words: earlier items face more replacement attempts; later items are harder to admit. The factors cancel, leaving the same final inclusion chance for every position.
```

Equal inclusion chances alone do not prove that every possible subset is equally likely. Algorithm R has that stronger property too. Inductively, assume the old reservoir is a uniform subset. A new subset excluding the arriving item comes from retaining its old subset; one including the arriving item can come from any old subset that differs by the replaced item. Uniform admission and uniform slot selection make these routes balance.

If the stream is shorter than the requested sample, the code returns everything it saw. A zero-sized sample remains empty. A negative size is outside this example's contract.

## Key takeaways

- A later item enters a size-k reservoir with k divided by the number of items seen.
- Uniform subsets need a replacement induction as well as equal item-inclusion probabilities.

## Further reading
- [Random Sampling with a Reservoir — Jeffrey Vitter](https://www.cs.umd.edu/~samir/498/vitter.pdf)
