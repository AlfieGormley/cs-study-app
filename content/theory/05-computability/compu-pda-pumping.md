---
id: compu-pda-pumping
title: Pushdown automata and the CFL pumping lemma
level: intermediate
minutes: 13
summary: A finite automaton plus a stack recognises exactly the context-free languages; the pumping lemma proves that some languages, like aⁿbⁿcⁿ, are beyond them.
---

A grammar *generates* strings. To *recognise* them you want a machine. For regular languages that machine is a finite automaton. For context-free languages it is a finite automaton with one extra piece of memory: an unbounded **stack**.

This lesson builds that machine, the **pushdown automaton** (PDA), then proves where its power runs out.

## Intuition: a stack is exactly enough for nesting

To check `aⁿbⁿ`, push a token for each `a`, then pop one for each `b`. Accept if the stack empties exactly when the input ends.

```
input:  a  a  b  b
stack: A$ AA$ A$ $   (after each symbol)
push A, push A, pop, pop -> empty: accept
```

The stack gives unbounded memory, but with a strict restriction: you may only look at the top. That is exactly what nesting needs, because the most recently opened bracket is the first one that must close. It is also exactly how your program's call stack works.

## The formal definition

One PDA convention is a 6-tuple (a list of six parts in a fixed order), starting with an empty stack. The examples abbreviate an initial epsilon move that pushes the bottom marker $, and the simulator starts after that move:

```formula
P = (Q, Σ, Γ, δ, q_0, F)
q_0 ∈ Q     F ⊆ Q
δ(q, a, X) = { (r, Y), … }
a, X → Y
where
P: the pushdown automaton
Q: a finite set of states
Σ: sigma, the input alphabet: the characters the input string may contain
Γ: gamma, the stack alphabet: the symbols that may be pushed (it may differ from Σ)
δ: delta, the transition function: given the current situation, it lists the allowed moves
q_0: the start state
F: the set of accepting states
∈: is a member of
⊆: is a subset of: every member of F is also in Q
q, r: states, the current one and the next one
a: the input character read on this move, or ε to read nothing
X: the symbol popped from the top of the stack, or ε to leave the stack alone
Y: the string pushed in its place, or ε to push nothing
ε: epsilon, the empty string: "nothing" on that side of the move
{ (r, Y), … }: a set of possible moves, each a pair of next state and string to push
→: on the diagram label, separates what is read and popped (left) from what is pushed (right)
In words: a PDA is a finite set of states plus a stack; each move reads an input character (or nothing), pops a stack symbol (or nothing), pushes a string and changes state.
```

So δ(q, a, X) means "in state q, reading input a with X on top of the stack, the machine may move to r and replace X with Y". On a diagram the same move is labelled `a, X → Y`: read a, pop X, push Y. For example, the label `a,ε→A` below means "read an a, pop nothing, push an A".

The standard PDA is **nondeterministic**: δ returns a *set* of moves, and the PDA accepts if *any* sequence of choices ends in an accepting state with all input read.

A PDA for `aⁿbⁿ` uses a bottom marker `$`:

```
     a,ε→A        b,A→ε
      ┌─┐          ┌─┐
      ▼ │          ▼ │
  ──▶ p ── ε,ε→ε ─▶ q ── ε,$→ε ─▶ (f)
```

Start with `$` on the stack. In state p, push an A per `a`. Jump (nondeterministically) to q, pop an A per `b`. When `$` is on top, move to accepting state f.

## Simulating a PDA in Python

Because the PDA is nondeterministic, the simulator explores every reachable **PDA configuration** (state, input position, stack) by breadth-first search. The stack is a string with the top on the left.

```python
from collections import deque

def run(delta, start, accept, w):
    q = deque([(start, 0, "$")])
    seen = set()
    while q:
        s, i, st = q.popleft()
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
> A PDA can loop forever pushing on ε-moves. The cap `len(st) > len(w)+3` is safe for these two machines, whose useful stacks need at most one symbol per input character plus the bottom marker. It may falsely reject other PDAs that require taller stacks. A general simulator would first convert the PDA to a grammar, or use CYK.

## PDAs and CFGs are equivalent

**Theorem.** A language is context-free if and only if some PDA recognises it.

- **CFG → PDA.** Push the start variable. Repeatedly: if the top is a variable A, nondeterministically replace it with the right-hand side of some rule `A → w`; if the top is a terminal, pop it while reading the same input character. Accept on an empty stack only after all input has been consumed. The stack holds the not-yet-matched part of a leftmost derivation.
- **PDA → CFG.** First normalise the PDA so acceptance occurs with an empty stack and moves push or pop one symbol. Variables A_pq then describe computations from state p with an empty stack to state q with an empty stack. Pair matching pushes and pops and concatenate such balanced subcomputations. This sketch omits the full normalisation and rule construction.

So grammars and stack machines are two views of the same class, the way regular expressions and DFAs are.

## Determinism matters here

For finite automata, nondeterminism adds no power (subset construction). For PDAs it does. A **deterministic PDA** (DPDA) has at most one enabled move in each configuration, including no choice between an enabled epsilon move and a move consuming the next symbol, and DPDAs recognise a strictly smaller class: the **deterministic context-free languages** (DCFLs).

Even palindromes `w wᴿ` with w ∈ {a,b}* are context-free but not deterministic context-free: a DPDA has no way to know when the middle has arrived. Add a centre marker, `w c wᴿ`, and a DPDA can do it, because the `c` tells it when to switch.

Explicit delimiters can make deterministic parsing easier; they are not sufficient by themselves to make every grammar deterministic. Knuth showed in 1965 that the DCFLs are exactly the languages with LR(k) grammars, under the usual end-of-input convention. Practical LR/LALR generator modes accept particular grammar subclasses; Bison’s GLR mode has different guarantees.

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
In words: in a context-free language, every long string has two pieces v and y, close together and not both empty, that can be repeated any number of times, or deleted, in step, and the result stays in the language.
```

The three conditions say: at least one of v, y is non-empty; the window vxy is at most p long; and pumping v and y together never leaves L. For example, the language { aⁿbⁿ } works with a CFL pumping length of p = 2. Take s = aabb with u = a, v = a, x = ε (empty), y = b, z = b. Pumping with i = 0 gives ab, i = 2 gives aaabbb: both stay in the language.

**Why it holds.** Take a CNF grammar with k variables. A parse tree in Chomsky normal form branches into at most two at each variable, which bounds how many leaves a short tree can have:

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
In words: a tree whose paths are short can only produce a short string, so a string of length 2^k forces some path to contain more than k variables.
```

With k = 3 variables, any string of 8 or more characters needs a path with at least 4 variable nodes. A path with more than k variables must use some variable twice (the pigeonhole principle). Call the repeated variable R:

```
          S
         / \
        u   R          the upper R
           /|\         derives v x y
          v R y        the lower R
            |          derives x
            x
```

Both R nodes can derive anything the other can. Replace the lower R's subtree with a copy of the upper one, and you get uv²xy²z. Replace the upper subtree with the lower one, and you get uxz (i = 0). Choose a longest root-to-leaf path and a repeated variable among its lowest k + 1 variable nodes; the upper selected subtree then yields at most 2ᵏ = p terminals. This keeps |vxy| ≤ p, and Chomsky normal form (no ε or unit rules) guarantees v and y are not both empty.

Compared with the regular pumping lemma, there are now **two** pumped pieces, v and y, which pump in step. That is precisely how `aⁿbⁿ` survives pumping: v takes a's and y takes b's.

## Proof: aⁿbⁿcⁿ is not context-free

**Claim.** The language of equal blocks of a's, b's and c's is not context-free.

**Proof.** Suppose L is context-free with CFL pumping length p. Choose the string s below:

```formula
L = { a^n b^n c^n : n ≥ 0 }
s = a^p b^p c^p
|s| = 3 × p ≥ p
where
L: the language of a's, then b's, then c's, all three blocks the same length
n: the shared block length, any whole number 0, 1, 2, …
a, b, c: the three letters of the alphabet
a^n: the letter a written n times in a row (likewise b^n, c^n)
p: the CFL pumping length the lemma promises, if L were context-free
s: the string we choose to attack, which is in L
|s|: the length of s, in characters
≥: is at least
In words: pick the string with p a's, p b's and p c's; it is in L and is long enough for the lemma to apply.
```

The lemma says s = uvxyz with |vxy| ≤ p and |vy| ≥ 1 (the five pieces u, v, x, y, z as in the lemma above). Since vxy spans at most p characters, it cannot contain both an a and a c: there are p b's between them. So vxy lies within aᵖbᵖ or within bᵖcᵖ.

- **Case 1: vxy has no c.** Pump to i = 2. The string gains at least one a or b, but the number of c's stays p. The counts are no longer equal, so uv²xy²z ∉ L.
- **Case 2: vxy has no a.** Pump to i = 2. It gains at least one b or c, but still has p a's. Again uv²xy²z ∉ L.

Every allowed split fails, contradicting the lemma. So L is not context-free. ∎

The same style of proof shows that the "copy" language is not context-free:

```formula
L_copy = { w w : w ∈ {a, b}* }
s = a^p b^p a^p b^p
where
L_copy: every string that is some string w written twice
w: any finite string of a's and b's
{a, b}*: every finite string of a's and b's, including the empty string
∈: is a member of
s: the string to pump, which is w w for w = a^p b^p
a^p: the letter a written p times (likewise b^p)
p: the CFL pumping length
In words: strings made of a block repeated exactly, such as abab or aabbaabb, are beyond any PDA; the proof pumps s = a^p b^p a^p b^p.
```

Contrast this with palindromes `w wᴿ`, which are. A stack reverses order naturally; copying in the same order needs a queue, and a PDA has none.

> [!warning] How pumping proofs go wrong
> - You choose s; the adversary chooses the split. You must defeat **every** split satisfying the conditions, not one convenient split.
> - The lemma is a necessary condition only. Some non-CFLs pass it. Ogden's lemma, which lets you mark which positions get pumped, is stronger.
> - Picking a weak s (like `abc` repeated) often makes the proof impossible. Choose s so the |vxy| ≤ p window cannot reach everything.

## Closure properties

| Operation | Regular | CFL |
|---|---|---|
| Union | yes | yes |
| Concatenation, star | yes | yes |
| Intersection | yes | no |
| Complement | yes | no |
| ∩ with a regular language | yes | yes |

"Closed under" an operation means that applying it to CFLs always gives another CFL.

```formula
L_1 = { a^n b^n c^m : n, m ≥ 0 }
L_2 = { a^m b^n c^n : n, m ≥ 0 }
L_1 ∩ L_2 = { a^n b^n c^n : n ≥ 0 }
A ∩ B = Σ* − (Ā ∪ B̄)
where
L_1: strings a…b…c… with as many a's as b's (any number of c's)
L_2: strings a…b…c… with as many b's as c's (any number of a's)
n, m: whole numbers 0, 1, 2, … giving block lengths
a, b, c: the three letters of the alphabet
a^n: the letter a written n times (likewise b^n, c^m)
∩: intersection: the strings in both languages
∪: union: the strings in either language
A, B: any two languages over the same alphabet
Ā: the complement of A: every string over the alphabet that is outside A (likewise B̄)
Σ*: every finite string over the alphabet Σ (sigma)
−: set difference: everything on the left except what is on the right
In words: the two context-free languages overlap exactly in a^n b^n c^n, which is not context-free; and intersection can be built from union and complement, so complement cannot always work either.
```

**Intersection fails:** L₁ and L₂ are both context-free, but their intersection is aⁿbⁿcⁿ. **Complement fails** as a consequence: CFLs are closed under union, so if they were closed under complement, De Morgan's law (the last line) would make them closed under intersection too.

Intersection with a *regular* language does work: run the PDA and a DFA side by side, since only one of them needs the stack. This is a handy proof tool. To show L is not context-free, intersect it with a regular language to get something you already know is not context-free.

## Where this shows up

- **Nested syntax** in JSON, XML and programming languages motivates stack parsing; complete language rules may require further checks. For a deterministic context-free grammar, an LR parser is a DPDA whose stack holds states and symbols.
- **Not everything in a language is context-free.** "Every variable is declared before use" resembles { w c w }, which is not context-free. Compilers check it in a separate semantic pass with a symbol table. C's `typedef` makes even *parsing* context-dependent (`a * b;` is a declaration if `a` is a type name), which motivates techniques such as the "lexer hack" to supply symbol-table information during parsing; not every C compiler uses the same technique.
- **Static analysis** of recursive programs uses pushdown models, because matching calls with returns is a nesting problem.

## Key takeaways
- A PDA is a finite automaton plus a stack. Nondeterministic PDAs recognise exactly the context-free languages.
- Unlike for finite automata, determinism costs power: `w wᴿ` over a two-symbol alphabet needs nondeterminism in the PDA model; DCFLs are exactly the LR(k) languages.
- The CFL pumping lemma: long strings split as uvxyz with |vxy| ≤ p and |vy| ≥ 1, and uvⁱxyⁱz stays in L.
- aⁿbⁿcⁿ and { ww } are not context-free. You choose s; you must beat every split.
- CFLs are closed under union, concatenation and star, and intersection with regular languages, but not under intersection or complement.

## Further reading
- [Pushdown automaton (Wikipedia)](https://en.wikipedia.org/wiki/Pushdown_automaton)
- [Pumping lemma for context-free languages (Wikipedia)](https://en.wikipedia.org/wiki/Pumping_lemma_for_context-free_languages)
- [Deterministic context-free language (Wikipedia)](https://en.wikipedia.org/wiki/Deterministic_context-free_language)
- [Ogden's lemma (Wikipedia)](https://en.wikipedia.org/wiki/Ogden%27s_lemma)
- [LR parser (Wikipedia)](https://en.wikipedia.org/wiki/LR_parser)
