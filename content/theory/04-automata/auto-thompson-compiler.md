---
id: auto-thompson-compiler
title: A postfix compiler and its resulting DFA
level: intermediate
minutes: 4
sourceLesson: auto-thompson
summary: This postfix compiler combines fragments without changing their accepted language.
---

## Thompson's construction in Python

This compact compiler accepts validated postfix expressions of plain characters and the operators ., | and *. It omits parsing, escaping, character classes and explicit ε/∅ tokens. Its global state accumulates across calls; reset delta and n before comparing independent machine sizes.

```python
from collections import defaultdict

delta = defaultdict(set)  # (q, c) -> set
n = 0

def new():
    global n
    # Allocate a fresh state for each
    # fragment.
    n += 1
    return n - 1

def arc(a, c, b):
    delta[(a, c)].add(b)

def build(postfix):
    st = []   # stack of (start, accept)
    for c in postfix:
        if c == ".":
            s2, e2 = st.pop()
            s1, e1 = st.pop()
            # Concatenate without consuming
            # input.
            arc(e1, "", s2)
            st.append((s1, e2))
        elif c == "|":
            s2, e2 = st.pop()
            s1, e1 = st.pop()
            s, e = new(), new()
            # Branch into either
            # alternative.
            arc(s, "", s1); arc(s, "", s2)
            arc(e1, "", e); arc(e2, "", e)
            st.append((s, e))
        elif c == "*":
            s1, e1 = st.pop()
            s, e = new(), new()
            # Enter the body or skip zero
            # copies.
            arc(s, "", s1); arc(s, "", e)
            # Repeat the body or leave the
            # star.
            arc(e1, "", s1); arc(e1, "", e)
            st.append((s, e))
        else:                 # a symbol
            s, e = new(), new()
            arc(s, c, e)
            st.append((s, e))
    if len(st) != 1:
        raise ValueError("invalid postfix")
    return st.pop()

start, acc = build("ab|*a.b.b.")
# Five symbols, union and star: 14 states.
print(n)  # 14
```

The result plugs straight into `run_nfa` from the earlier epsilon-closure unit. `run_nfa(delta, start, {acc}, "babb")` is `True` and `"abba"` gives `False`. The audit compares this NFA with re.fullmatch on all strings over {a, b} up to length 10; that finite check supports the example but is not the general equivalence proof.

Fourteen states matches the formula: five symbols, one `|` and one `*` is seven items, times two.

## Worked example: (a|b)*abb to a DFA

Here is the classic Dragon Book version of the NFA, with concatenation states merged, so it has 11 states numbered 0 to 10:

```
0 -ε-> 1, 7
1 -ε-> 2, 4
2 -a-> 3      4 -b-> 5
3 -ε-> 6      5 -ε-> 6
6 -ε-> 1, 7
7 -a-> 8 -b-> 9 -b-> 10 (accept)
```

States 0 to 7 implement `(a|b)*`, including its exit at 7: 1 to 6 is the union, and 0, 6 → 1 and the arrows to 7 are the star. States 7 to 10 spell abb.

Now apply the subset construction. The start state is the ε-closure of state 0: everything reachable from 0 by ε-arrows alone.

```formula
E({0}) = {0, 1, 2, 4, 7}
where
E: the ε-closure: a set of NFA states plus every state reachable from them by following only ε-arrows, which read no input
{ }: the set of the states listed inside
0, 1, 2, 4, 7: NFA states from the listing above
In words: from 0 you can reach 1 and 7 for free, and from 1 you can reach 2 and 4. States 2, 4 and 7 are where the next symbol is read.
```

| DFA | NFA states | on a | on b |
|---|---|---|---|
| → A | {0,1,2,4,7} | B | C |
| B | {1,2,3,4,6,7,8} | B | D |
| C | {1,2,4,5,6,7} | B | C |
| D | {1,2,4,5,6,7,9} | B | E |
| E (accept) | {1,2,4,5,6,7,10} | B | C |

Five DFA states from 11 NFA states. Read them as "how much of abb have I just seen": A and C mean none, B means a, D means ab, E means abb. A and C behave identically, so the minimal DFA (the minimisation units) has 4 states.

## Key takeaways
- This postfix compiler combines fragments without changing their accepted language.
- Subset construction can leave equivalent DFA states to merge later.

## Further reading
- [Russ Cox: simple and fast regular-expression matching](https://swtch.com/~rsc/regexp/regexp1.html)
- [MIT: regexes to finite automata](https://ocw.mit.edu/courses/18-404j-theory-of-computation-fall-2020/resources/mit18_404f20_lec2-1/)
