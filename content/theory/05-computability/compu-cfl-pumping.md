---
id: compu-cfl-pumping
title: Why context-free strings can be pumped
level: intermediate
minutes: 5
summary: The language supplies a pumping length, you choose a long string, and the decomposition may then be chosen to suit that string.
sourceLesson: compu-pda-pumping
---

## The pumping lemma for context-free languages

Is every language context-free? No. To prove it, you need a property every CFL has, then show some language lacks it.

**Lemma.** If a language L is context-free, there is a whole number p, the **CFL pumping length**, such that every string s in L at least p characters long can be cut into five consecutive pieces u, v, x, y, z meeting all of these conditions:

```formula
p ≥ 1     s ∈ L     |s| ≥ p
s = u v x y z
|v y| ≥ 1
|v x y| ≤ p
u v^i x y^i z ∈ L   for every i ≥ 0
where
L: a context-free language (a set of strings)
p: the CFL pumping length, a whole number that depends only on L
s: any string in L with at least p characters
u, v, x, y, z: five consecutive pieces of s, written side by side to mean "joined in order" (not multiplied); any of them may be empty, subject to the conditions
|s|: the length of s, in characters; |v y| is the combined length of v and y
v^i: the piece v repeated i times in a row (v^0 is empty, v^2 is v twice)
i: the pump count, any whole number 0, 1, 2, …
∈: is a member of
≥, ≤: is at least, is at most
|v x y|: the combined length of the enclosed string pieces, in symbols
|v y|: the combined length of the enclosed string pieces, in symbols
In words: in a context-free language, every long string has two pieces v and y, close together and not both empty, that can be repeated any number of times, or deleted, in step, and the result stays in the language.
```

The three conditions say: at least one of v, y is non-empty; the window vxy is at most p long; and pumping v and y together never leaves L. For example, the language { aⁿbⁿ } works with a CFL pumping length of two. For `aabb`, take the first and last pieces to be a and b, the two pumped pieces also a and b, and the middle piece empty. Deleting the pumped pieces gives `ab`; doubling them gives `aaabbb`. Both stay in the language.

**Why it holds.** Take a Chomsky normal form grammar with k variables. A parse tree in Chomsky normal form branches into at most two at each variable, which bounds how many leaves a short tree can have:

```formula
N ≤ 2^{h − 1}
p = 2^k
k = 3:   p = 2^3 = 8
h ≤ 3  ⇒  N ≤ 2^2 = 4 < 8
where
N: the number of terminal leaves (characters) in a Chomsky normal form parse tree
h: the largest number of variable nodes on any path from the root down to a terminal
k: the number of variables in the grammar
p: the CFL pumping length chosen for this grammar
⇒: implies
≤: is at most
<: is less than
In words: a tree whose paths are short can only produce a short string, so a string of length 2^k forces some path to contain more than k variables.
```

With three variables, any string of 8 or more characters needs a path with at least 4 variable nodes. A path with more than k variables must use some variable twice (the pigeonhole principle). Call the repeated variable R:

```
          S
         / \
        u   R          the upper R
           /|\         derives v x y
          v R y        the lower R
            |          derives x
            x
```

The drawing is schematic: it suppresses intervening nodes and the unchanged suffix z after the upper R subtree; it is not a complete Chomsky normal form parse tree. The pieces before and after that subtree remain fixed when pumping.

Both R nodes can derive anything the other can. Replacing the lower R subtree with a copy of the upper one doubles both pumped pieces. Replacing the upper subtree with the lower one deletes both pumped pieces. Choose a longest root-to-leaf path and a repeated variable among its lowest one-more-than-k variable nodes. The upper selected subtree yields at most the pumping length in terminals, so the displayed window bound holds. Chomsky normal form, without empty or unit rules inside this nonempty derivation, guarantees that the two pumped pieces are not both empty.

Compared with the regular pumping lemma, there are now **two** pumped pieces, v and y, which pump in step. That is precisely how `aⁿbⁿ` survives pumping: v takes a's and y takes b's.

## Key takeaways

- The language supplies a pumping length, you choose a long string, and the decomposition may then be chosen to suit that string.
- The two pumped pieces are close and not both empty; every nonnegative pump count must work.
- A repeated variable along a deep Chomsky normal form parse-tree path supplies the pumping construction.

## Further reading

- [Sipser: CFL pumping lemma and Turing machines](https://ocw.mit.edu/courses/18-404j-theory-of-computation-fall-2020/resources/mit18_404f20_lec5-1/)
