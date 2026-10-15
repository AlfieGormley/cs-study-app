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

Assume independent uniform draws and a sample size no bigger than the stream. Follow one item: it must first enter the sample, then survive every later step, where it is evicted only if the draw picks exactly its slot. Multiplying those chances, most factors cancel (the product telescopes):

```formula
P_enter = k / (i + 1)
P_survive(t) = t / (t + 1)
P = k/(i+1) × (i+1)/(i+2) × … × (n−1)/n
P = k / n
P = 10 / 1000 = 0.01
where
k: the sample size, 10 in the last line
n: the positive total number of stream items, 1,000 in the last line; k ≤ n
i: the position of the item we follow, counting from 0, with i ≥ k
t: a later step, i < t ≤ n − 1
P_enter: the probability the item gets into the sample when it arrives
P_survive(t): the probability it is not evicted at step t (one minus 1/(t + 1))
P: the probability it is in the final sample
…: and so on, one factor per later step
≤: is at most
In words: each item's chance of getting in shrinks exactly as fast as later items' chances of knocking it out, so every item ends with the same chance, the sample size divided by the total item count.
```

The first k items start in with probability 1, and the same telescoping gives k/n: with 10 slots and 1,000 lines, every line has a 1 % chance. If the stream is shorter than k, the code returns everything it saw; a negative k is outside its contract.

Equal inclusion probabilities alone do not prove uniform subsets. Algorithm R additionally gives every possible sample the same probability, by induction over each replacement step:

```formula
P(S) = 1 / C(n, k)
C(n, k) = n! / (k! × (n − k)!)
C(5, 2) = 120 / (2 × 6) = 10
where
S: one particular set of k items
P(S): the probability that the final sample is exactly S
C(n, k): "n choose k", the number of different k-item sets you can pick from n items
n!: n factorial, 1 × 2 × … × n
k: the sample size
n: the stream length
In words: every possible sample of k items is equally likely; from 5 items with 2 slots there are 10 possible pairs, each with probability 1/10.
```

## Key takeaways

- A later item enters a size-k reservoir with k divided by the number of items seen.
- Uniform subsets need a replacement induction as well as equal item-inclusion probabilities.

## Further reading
- [Skip list — Wikipedia](https://en.wikipedia.org/wiki/Skip_list)
- [Treap — Wikipedia](https://en.wikipedia.org/wiki/Treap)
- [Treap (Cartesian tree) — cp-algorithms](https://cp-algorithms.com/data_structures/treap.html)
- [Reservoir sampling — Wikipedia](https://en.wikipedia.org/wiki/Reservoir_sampling)
- [Fisher–Yates shuffle — Wikipedia](https://en.wikipedia.org/wiki/Fisher%E2%80%93Yates_shuffle)
- [Vitter’s reservoir-sampling paper](https://www.cs.umd.edu/~samir/498/vitter.pdf)
