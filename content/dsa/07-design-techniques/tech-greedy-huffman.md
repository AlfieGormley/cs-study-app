---
id: tech-greedy-huffman
title: Building Huffman prefix codes
level: intermediate
minutes: 4
sourceLesson: tech-greedy
summary: Merge the two lowest-frequency trees until one remains.
---

## Huffman coding

Text is stored as bits. A **fixed-length code** gives every symbol the same length, enough bits to give each symbol a different pattern. Six symbols need 3 bits each: 2 bits give only 4 patterns, too few, while 3 bits give 8, leaving 2 unused.

If some symbols are much more common, a **variable-length code** can do better by giving them shorter codewords.

For immediate symbol-by-symbol decoding without separators, a **prefix code** is sufficient: no codeword is a prefix of another. Prefix codes correspond to binary trees with symbols at the leaves; the code for a symbol is its path (0 = left, 1 = right).

> [!analogy] Real-world analogy: Morse code
> Morse code gives the most common English letter, E, a single dot and T a single dash, while rare letters such as Q get four symbols. Operators send common letters quickly and pay extra only for rare ones.
>
> **How it maps:** letters are symbols, dots and dashes are bits, and "brief codewords for frequent letters" is exactly what a variable-length code like Huffman's exploits to lower the average length.
>
> **Where it stops:** Morse is not a prefix code: E (one dot) is the start of I (two dots), so operators need a pause between letters to tell them apart. Huffman codes need no separator, and Huffman's algorithm chooses lengths that are provably optimal for the given frequencies rather than by hand.

### The greedy algorithm

David Huffman's 1952 algorithm:

1. Make a leaf for each symbol, weighted by its frequency.
2. Repeatedly remove the **two lowest-weight** trees and merge them under a new node whose weight is their sum.
3. Stop when one tree remains.

```python
import heapq, itertools

def huffman(freq):
    if not freq:
        return {}
    if any(not isinstance(sym, str)
           or type(f) is not int or f <= 0
           for sym, f in freq.items()):
        raise ValueError("frequencies")
    # Break equal weights without comparing
    # nodes.
    tie = itertools.count()  # tie-breaker
    heap = [(f, next(tie), sym)
            for sym, f in freq.items()]
    heapq.heapify(heap)
    while len(heap) > 1:
        f1, _, a = heapq.heappop(heap)
        f2, _, b = heapq.heappop(heap)
        node = (f1 + f2, next(tie), (a, b))
        heapq.heappush(heap, node)
    codes = {}
    # Traverse the final tree to assign
    # codewords.
    pending = [(heap[0][2], "")]
    while pending:
        node, code = pending.pop()
        if isinstance(node, tuple):
            pending.append(
                (node[1], code + "1"))
            pending.append(
                (node[0], code + "0"))
        else:
            # Give a lone symbol a non-empty
            # code.
            codes[node] = code or "0"
    return codes
```

The function accepts string symbols with positive integer frequencies and returns an empty mapping for an empty alphabet. For one symbol it uses the non-empty code "0"; a format with a known message length could instead use an empty codeword. Tree construction uses O(k) heap operations for k symbols, each costing O(log k), so O(k log k) time; materialising all code strings adds their total length, which can be Θ(k²). Integer arithmetic and string costs are additional to unit-cost heap analysis.

The tie counter matters: without it, two entries with equal frequency make `heapq` compare the third elements, and comparing a string with a tuple raises `TypeError`.

> [!example] Six symbols per 100 characters
> Frequencies: a 45, b 13, c 12, d 16, e 9, f 5.
> 1. Merge f 5 + e 9 = 14.
> 2. Merge c 12 + b 13 = 25.
> 3. Merge 14 + d 16 = 30.
> 4. Merge 25 + 30 = 55.
> 5. Merge a 45 + 55 = 100.
>
> Code lengths: a 1, b 3, c 3, d 3, e 4, f 4.

The resulting tree (0 = left branch, 1 = right branch):

```
            (100)
           0/   \1
          a45   (55)
              0/    \1
            (25)    (30)
            / \     /  \
          c12 b13 (14) d16
                  / \
                f5   e9
```

The cost of a code is each symbol's frequency times its code length, added up. Here the Huffman code needs 224 bits for the 100 characters, against 300 bits for a fixed 3-bit code: about a quarter fewer payload bits, excluding codebook and framing overhead. The saving comes from giving `a`, almost half the text, a 1-bit code.

```formula reference
B = Σ f_i ℓ_i
where
B: the total payload bits to encode the text with a given code
Σ: sum: add up the term for every symbol i
i: one symbol of the alphabet
f_i: how many times symbol i occurs (its frequency)
ℓ_i: the length of symbol i's codeword, in bits
In words: the encoded size is every symbol's count times its code length, added up; Huffman's tree makes this total as small as any prefix code can.
```

## Key takeaways
- Merge the two lowest-frequency trees until one remains.
- Tie counters prevent mixed node types being compared, and payload bits exclude format overhead.

## Further reading
- [Greedy algorithms and Huffman codes — Erickson](https://jeffe.cs.illinois.edu/teaching/algorithms/book/04-greedy.pdf)
- [Python heapq](https://docs.python.org/3/library/heapq.html)
