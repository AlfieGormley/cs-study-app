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

One PDA convention is a 6-tuple (Q, Σ, Γ, δ, q₀, F), starting with an empty stack. The examples abbreviate an initial epsilon move that pushes the bottom marker $, and the simulator starts after that move:

- **Q**: a finite set of states, with start state q₀ and accepting states F ⊆ Q.
- **Σ**: the input alphabet.
- **Γ**: the stack alphabet (may differ from Σ).
- **δ**: the transition function. δ(q, a, X) is a set of pairs (r, Y): "in state q, reading input a (or ε) with X on top of the stack (or ε, meaning don't look), move to r and replace X with Y".

Transitions are written `a, X → Y`: read a, pop X, push Y. Either side may be ε. The standard PDA is **nondeterministic**: δ returns a *set* of moves, and the PDA accepts if *any* sequence of choices ends in an accepting state with all input read.

A PDA for `aⁿbⁿ` uses a bottom marker `$`:

```
     a,ε→A        b,A→ε
      ┌─┐          ┌─┐
      ▼ │          ▼ │
  ──▶ p ── ε,ε→ε ─▶ q ── ε,$→ε ─▶ (f)
```

Start with `$` on the stack. In state p, push an A per `a`. Jump (nondeterministically) to q, pop an A per `b`. When `$` is on top, move to accepting state f.

## Simulating a PDA in Python

Because the PDA is nondeterministic, the simulator explores every reachable **configuration** (state, input position, stack) by breadth-first search. The stack is a string with the top on the left.

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

Even-length palindromes `w wᴿ` over the two-symbol alphabet {a,b} need nondeterminism in the PDA model, because the machine cannot see where the middle is. It *guesses*: some branch jumps to the popping state at exactly the right spot.

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

> [!note] The length guard
> A PDA can loop forever pushing on ε-moves. The guard `len(st) > len(w)+3` is safe for these two machines, whose useful stacks need at most one symbol per input character plus the bottom marker. It may falsely reject other PDAs that require taller stacks. A general simulator would first convert the PDA to a grammar, or use CYK.

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

**Lemma.** If L is context-free, there is a number p ≥ 1 (the pumping length) such that every s ∈ L with |s| ≥ p can be split as s = uvxyz where:

1. |vy| ≥ 1 (at least one of v, y is non-empty),
2. |vxy| ≤ p,
3. uvⁱxyⁱz ∈ L for every i ≥ 0.

**Why it holds.** Take a CNF grammar with k variables. If every root-to-terminal path has at most h variable nodes, a nonempty CNF parse has at most 2^(h−1) terminal leaves. So a long enough string (choose p = 2ᵏ) forces a root-to-leaf path with more than k variables on it. By the pigeonhole principle some variable R repeats on that path:

```
          S
         / \
        u   R          the upper R
           /|\         derives v x y
          v R y        the lower R
            |          derives x
            x
```

Both R nodes can derive anything the other can. Replace the lower R's subtree with a copy of the upper one, and you get uv²xy²z. Replace the upper subtree with the lower one, and you get uxz (i = 0). Choose a longest root-to-leaf path and a repeated variable among its lowest k + 1 variable nodes; the upper selected subtree then yields at most 2ᵏ = p terminals. This keeps |vxy| ≤ p, and CNF (no ε or unit rules) guarantees v and y are not both empty.

Compared with the regular pumping lemma, there are now **two** pumped pieces, v and y, which pump in step. That is precisely how `aⁿbⁿ` survives pumping: v takes a's and y takes b's.

## Proof: aⁿbⁿcⁿ is not context-free

**Claim.** L = { aⁿbⁿcⁿ : n ≥ 0 } is not context-free.

**Proof.** Suppose L is context-free with pumping length p. Choose

```
s = aᵖ bᵖ cᵖ    (|s| = 3p ≥ p)
```

The lemma says s = uvxyz with |vxy| ≤ p and |vy| ≥ 1. Since vxy spans at most p characters, it cannot contain both an a and a c: there are p b's between them. So vxy lies within aᵖbᵖ or within bᵖcᵖ.

- **Case 1: vxy has no c.** Pump to i = 2. The string gains at least one a or b, but the number of c's stays p. The counts are no longer equal, so uv²xy²z ∉ L.
- **Case 2: vxy has no a.** Pump to i = 2. It gains at least one b or c, but still has p a's. Again uv²xy²z ∉ L.

Every allowed split fails, contradicting the lemma. So L is not context-free. ∎

The same style of proof shows { ww : w ∈ {a,b}* } is not context-free (use s = aᵖbᵖaᵖbᵖ). Contrast this with palindromes `w wᴿ`, which are. A stack reverses order naturally; copying in the same order needs a queue, and a PDA has none.

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

**Intersection fails:** { aⁿbⁿcᵐ } and { aᵐbⁿcⁿ } are both context-free, but their intersection is aⁿbⁿcⁿ. **Complement fails** as a consequence: if CFLs were closed under complement, De Morgan's law A ∩ B = complement(Ā ∪ B̄) would make them closed under intersection too.

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
