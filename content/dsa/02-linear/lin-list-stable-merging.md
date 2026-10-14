---
id: lin-list-stable-merging
title: Stable destructive merging and merge schedules
level: intermediate
minutes: 3
sourceLesson: lin-list-techniques
summary: Relink node-disjoint sorted inputs and attach an untouched suffix.
---

Use the Node class from the reversal unit. A dummy node provides an initial attachment point, and the current output tail tells you where to append the next selected node. The inputs below must not share nodes: rewiring intersecting inputs can create a cycle.

## Merging two sorted lists

Assume two sorted, acyclic, node-disjoint lists and constant-time value comparison. This destructive merge repeatedly takes the smaller head and attaches it to the result. A dummy head gives you somewhere to attach the first node.

```python
def merge(a, b):
    dummy = tail = Node(0)
    while a and b:
        if a.val <= b.val:
            # Attach A before advancing its
            # input.
            tail.next, a = a, a.next
        else:
            # Attach B before advancing its
            # input.
            tail.next, b = b, b.next
        tail = tail.next
    tail.next = a or b   # leftovers
    return dummy.next
```

```
a: 1 -> 4 -> 6
b: 2 -> 3 -> 7
take 1(a) 2(b) 3(b) 4(a) 6(a)
a empty: attach rest of b (7)
result: 1 2 3 4 6 7
```

For lists of n and m nodes, this is O(n + m) time and O(1) extra space: it relinks existing nodes rather than creating new ones. Using `<=` keeps equal elements in their original order (a **stable merge**), which matters for merge sort.

Merge is the core of **merge sort on linked lists**, which is the standard way to sort an n-node list in O(n log n) without random access (log n is log₂ n, the number of times n can be halved before reaching 1; it is how many levels of splitting there are): find the middle with fast/slow pointers, split, sort each half, merge.

### Several sorted lists

Sequentially merging each new list into the whole accumulated result repeatedly revisits earlier nodes. Balanced pairwise rounds instead roughly halve the number of lists per round. With equal-length lists, the total merge-input sizes have the following costs:


```formula
W_seq ≈ kN / 2
W_pair = N log_2(k)
where
W_seq: cumulative merge-input size in a sequential schedule, in nodes
W_pair: cumulative merge-input size for balanced pairwise rounds, in nodes; the equality assumes a power-of-two list count
N: total nodes across all lists
k: number of lists, at least two
log_2: base-two logarithm, giving the halving-round count
≈: approximate equality omitting lower-order terms
In words: Sequential merging scales with the list count times the total input, while balanced rounds scale with the number of halving rounds.
```

For eight lists of one thousand nodes each, sequential merge-input sizes total thirty-five thousand nodes; three balanced rounds total twenty-four thousand. Actual comparisons can be fewer because merge attaches an untouched suffix. For non-power-of-two list counts, balanced round counts are rounded up and some lists sit out a round. A heap of current heads also gives O(N log k), with N and k as defined above, but its mechanics belong to the later heaps module.

## Key takeaways
- Relink node-disjoint sorted inputs and attach an untouched suffix.
- Balanced pairwise rounds avoid repeatedly scanning an ever-growing result.

## Further reading
- [Linked list — Wikipedia](https://en.wikipedia.org/wiki/Linked_list)
- [Merge sort — Wikipedia](https://en.wikipedia.org/wiki/Merge_sort)
