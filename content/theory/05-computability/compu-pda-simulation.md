---
id: compu-pda-simulation
title: Simulating pushdown choices and deterministic limits
level: intermediate
minutes: 4
summary: Breadth-first simulation explores configurations; the example stack cap is specific to the displayed machines.
sourceLesson: compu-pda-pumping
---

## Simulating a PDA in Python

Because the PDA is nondeterministic, the simulator explores every reachable **PDA configuration** (state, input position, stack) by breadth-first search. The stack is a string with the top on the left.

```python
from collections import deque

def run(delta, start, accept, w):
    q = deque([(start, 0, "$")])
    seen = set()
    while q:
        s, i, st = q.popleft()
        # Input position and stack
        # distinguish runs.
        cfg = (s, i, st)
        # prune repeats and runaway stacks
        too_tall = len(st) > len(w) + 3
        if cfg in seen or too_tall:
            continue
        seen.add(cfg)
        if i == len(w) and s in accept:
            return True
        for key, moves in delta.items():
            ss, a, p = key
            if ss != s:
                continue
            if a and w[i:i+1] != a:
                continue
            if p and not st.startswith(p):
                continue
            j = i + (1 if a else 0)
            # Pop before pushing.
            rest = st[len(p):]
            for r, push in moves:
                q.append((r, j, push+rest))
    return False
```

A palindrome reads the same backwards. The even-length ones are a string followed by its own reverse:

```formula
L_pal = { w w^R : w ∈ {a, b}* }
w = "ab"   w^R = "ba"   w w^R = "abba"
where
L_pal: the language of even-length palindromes over a and b
w: any finite string of a's and b's
w^R: the reverse of w, the same characters in the opposite order
{a, b}*: every finite string made of a's and b's, including the empty string
∈: is a member of
In words: take any string of a's and b's and append its mirror image; every even-length palindrome arises this way.
```

These even-length palindromes over the two-symbol alphabet {a,b} need nondeterminism in the PDA model, because the machine cannot see where the middle is. It *guesses*: some branch jumps to the popping state at exactly the right spot.

```python
PAL = {
  ("p", "a", ""): [("p", "a")],
  ("p", "b", ""): [("p", "b")],
  ("p", "", ""):  [("q", "")],  # guess
  ("q", "a", "a"): [("q", "")],
  ("q", "b", "b"): [("q", "")],
  ("q", "", "$"): [("f", "")],
}
for w in ["abba", "abab", "baab", "ab"]:
    print(w, run(PAL, "p", {"f"}, w))
# abba True / abab False
# baab True / ab False
```

> [!note] The length cap
> A PDA can loop forever pushing on epsilon-moves. The cap `len(st) > len(w)+3` is safe for the equal-block and palindrome machines, whose useful stacks need at most one symbol per input character plus the bottom marker. It may falsely reject other PDAs that require taller stacks. A general simulator would first convert the PDA to a grammar, or use CYK.

## Determinism matters here

For finite automata, nondeterminism adds no power (subset construction). For PDAs it does. A **deterministic PDA** (DPDA) has at most one enabled move in each configuration, including no choice between an enabled epsilon move and a move consuming the next symbol, and DPDAs recognise a strictly smaller class: the **deterministic context-free languages** (DCFLs).

The displayed even-palindrome language over a and b is context-free but not deterministic context-free: a DPDA has no way to know when the middle has arrived. Add a centre marker, `w c wᴿ`, and a DPDA can do it, because the `c` tells it when to switch.

Explicit delimiters can make deterministic parsing easier; they are not sufficient by themselves to make every grammar deterministic. Knuth showed in 1965 that the DCFLs are exactly the languages with LR(k) grammars, under the usual end-of-input convention. Practical LR/LALR generator modes accept particular grammar subclasses; Bison’s GLR mode has different guarantees.

## Key takeaways

- Breadth-first simulation explores state, input position and stack configurations.
- The stack cap is safe for the displayed machines and is not a general PDA decision procedure.
- An unmarked even palindrome requires nondeterminism; a centre marker permits deterministic switching.

## Further reading

- [Sipser: grammars, parse trees and pushdown automata](https://ocw.mit.edu/courses/18-404j-theory-of-computation-fall-2020/resources/mit18_404f20_lec4-1/)
- [Context-free language closure properties — further reference](https://en.wikipedia.org/wiki/Context-free_language)
