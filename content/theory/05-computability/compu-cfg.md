---
id: compu-cfg
title: Context-free grammars
level: basic
minutes: 11
summary: Grammars that can count and nest, how derivations and parse trees work, ambiguity, Chomsky normal form and the CYK parsing algorithm.
---

Finite automata have a fixed, finite memory. That is why no DFA can recognise `aⁿbⁿ` (some number of a's followed by the same number of b's): to check the b's, it would have to remember an unbounded count of a's.

Yet the languages programmers care about are full of exactly this kind of matching. Every `(` needs a `)`. Every `{` needs a `}`. Nested block structures can have arbitrarily many pending delimiters in the mathematical model; concrete language and markup rules add their own exceptions and constraints. **Context-free grammars** (CFGs) are the next step up the ladder. They can describe nesting, and they are the formal basis of almost every programming-language parser.

## The idea: rewrite rules

A grammar is a set of rewrite rules. You start from a start symbol and keep replacing symbols until only real characters remain.

First, the notation `aⁿbⁿ`. A superscript on a letter means "repeat it that many times", and a **formal language** is just a set of strings. So `aⁿbⁿ` names this language:

```formula
L = { a^n b^n : n ≥ 0 }
L = { ε, "ab", "aabb", "aaabbb", … }
where
L: the language being described: a set of strings
a, b: the two characters (letters) the strings are made of
n: a whole number 0, 1, 2, … saying how many copies
a^n: the letter a written n times in a row, so a^3 is "aaa" and a^0 is the empty string
ε: epsilon, the empty string: a string with no characters at all
{ … : … }: set-builder notation: the set of everything of the form before the colon, for every value allowed by the condition after it
≥: is greater than or equal to
…: and so on, following the same pattern
In words: L is every string made of some number of a's followed by exactly the same number of b's, including the empty string.
```

Here is a grammar for that language, as two rewrite rules, and a derivation that uses them:

```formula
S → a S b
S → ε
S ⇒ a S b ⇒ a a S b b ⇒ a a b b
where
S: the start variable: a placeholder that must eventually be rewritten away
a, b: terminals: real characters that appear in the final string
ε: epsilon, the empty string (rewriting S to ε just deletes it)
→: "may be rewritten as": the left side may be replaced by the right side
⇒: one rewriting step, applying one rule to the current string
In words: S may be replaced by a S b or deleted; using the first rule twice and then the second turns S into aabb.
```

Read the rules as: "an S is either an `a`, then another S, then a `b`; or it is the empty string ε". Writing both on one line with a bar `|` (meaning "or") is the usual shorthand: `S → aSb | ε`. Inside a grammar, letters written side by side (`aSb`) simply follow each other; nothing is multiplied.

Each `⇒` in the derivation is one rule application, called a **derivation step**. For `aabb` that is three steps: two uses of `S → aSb`, then one of `S → ε`. In general `aⁿbⁿ` takes n + 1 steps.

Every time an `a` is added, a matching `b` is added on the other side. The grammar never has to count; the structure of the rule does the matching for it.

## The formal definition

A context-free grammar is a 4-tuple (a list of four parts in a fixed order):

```formula
G = (V, Σ, R, S)
A → w   with A ∈ V
L(G) = { w ∈ Σ* : S ⇒* w }
where
G: the grammar
V: a finite set of variables (non-terminals), such as S, E, T
Σ: sigma, the alphabet: a finite set of terminals (the actual characters), sharing nothing with V
R: a finite set of rules, each of the form A → w
S: the start variable, one particular member of V
A: the single variable on the left of a rule
w: any string of variables and terminals on the right of a rule (possibly the empty string ε); in L(G), a string of terminals only
→: "may be rewritten as"
∈: is a member of
Σ*: sigma-star: every finite string of terminals, including the empty string ε
⇒*: derives in zero or more rewriting steps
L(G): the language of G: the set of terminal strings that S can be rewritten into
{ … : … }: set-builder notation: the set of all w that satisfy the condition after the colon
In words: a grammar has variables, terminals, rules that each rewrite one variable, and a start variable; its language is every all-terminal string you can reach from the start.
```

The **variables** (non-terminals) are placeholders that still need rewriting. The **terminals** are the real characters of the finished string. Each **rule** rewrites one variable. For the grammar above, V = {S}, Σ = {a, b}, R holds the two rules and S is the start. A language is **context-free** if some CFG generates it.

> [!note] Why "context-free"?
> The left-hand side of every rule is a single variable. So you may rewrite A no matter what surrounds it: its context is irrelevant. *Context-sensitive* grammars permit rules like `aAb → aXb`, where A may only be rewritten between an a and a b. Those are strictly more powerful.

Every regular language is context-free (a DFA translates directly into a grammar with rules like `A → 0B`), but not the other way round: `aⁿbⁿ` is context-free and not regular.

## Simulating a grammar in Python

For the balanced-parentheses grammar below, breadth-first search over **sentential forms** (partly rewritten strings), always expanding the leftmost variable, enumerates all strings up to the bound. Terminals are single characters, and all variables must be keys of G. This routine is not a terminating enumerator for arbitrary CFGs: a rule such as S → SS can grow variables indefinitely without exceeding a terminal-count bound. For general CFGs, enumerate the finitely many candidate terminal strings and decide membership with a parser.

```python
from collections import deque

def generate(G, start, maxlen):
    out, seen = set(), set()
    q = deque([(start,)])
    while q:
        f = q.popleft()
        if f in seen:
            continue
        seen.add(f)
        terms = [x for x in f if x not in G]
        if len(terms) > maxlen:
            continue
        i = next((k for k, x in enumerate(f)
                  if x in G), None)
        if i is None:   # all terminals
            out.add("".join(f))
            continue
        for rhs in G[f[i]]:
            q.append(f[:i] + rhs + f[i+1:])
    return sorted(out, key=lambda s:
                  (len(s), s))

P = {"S": [("(", "S", ")", "S"), ()]}
print(generate(P, "S", 6))
```

The grammar `S → (S)S | ε` describes balanced parentheses. The output lists all 9 balanced strings of length at most 6: `''`, `()`, `(())`, `()()`, and the five of length 6. (The counts 1, 1, 2, 5 for lengths 0, 2, 4, 6 are the Catalan numbers, which turn up all over grammar theory.)

## Parse trees

A derivation is a sequence; a **parse tree** shows the structure. Each internal node is a variable, its children are the right-hand side of the rule used, and reading the leaves left to right gives the string.

For arithmetic, a classic grammar is:

```
E → E + T | T
T → T * F | F
F → ( E ) | id
```

The parse tree for `id + id * id` is:

```
          E
        / | \
       E  +  T
       |   / | \
       T  T  *  F
       |  |     |
       F  F     id
       |  |
       id id
```

The tree puts `id * id` lower down, so it is grouped first. That is operator precedence, encoded purely by the shape of the grammar: `*` lives at the T level, beneath `+` at the E level. Left recursion (`E → E + T`) makes `+` left-associative, so `a + b + c` means `(a + b) + c`.

A **leftmost derivation** always rewrites the leftmost variable. There is a one-to-one match between parse trees and leftmost derivations, so "how many parse trees" and "how many leftmost derivations" are the same question.

## Ambiguous grammars

An **ambiguous grammar** is one in which some string has two or more different parse trees. The tempting short grammar for arithmetic is ambiguous:

```
E → E + E | E * E | id
```

`id + id * id` now has two trees: one groups `(id + id) * id`, the other `id + (id * id)`. The grammar alone leaves grouping unspecified; a parser needs an additional disambiguation policy or an unambiguous grammar.

The problem gets worse with length. Each parse tree picks one operator as the root; the operands to its left and to its right are then grouped independently. That gives a recurrence (a formula defined in terms of smaller cases of itself):

```formula
T(1) = 1
T(n) = Σ T(k) × T(n − k)
       for k = 1, …, n − 1
T(n) = C(n − 1)
C(m) = (2 × m)! / ((m + 1)! × m!)
where
T(n): the number of parse trees for an expression with n operands (the ids)
n: the number of operands, 1 or more
k: how many operands sit left of the root operator, from 1 to n − 1
Σ: capital sigma: add up the term after it for every listed value of k
C(m): the m-th Catalan number, a famous counting sequence 1, 1, 2, 5, 14, 42, …
m: the position in the Catalan sequence, starting at 0
!: factorial: the product of all whole numbers from 1 up to that number, so 4! = 24 (and 0! = 1)
In words: count the trees by trying every operator as the root and multiplying the ways to group each side; the totals are the Catalan numbers.
```

For n = 4 operands: T(4) = T(1) × T(3) + T(2) × T(2) + T(3) × T(1) = 2 + 1 + 2 = 5, and the closed form agrees: C(3) = 6! / (4! × 3!) = 720 / 144 = 5. The sequence runs 1, 1, 2, 5, 14, 42, 132 for n = 1 to 7, and the ratio between neighbouring terms creeps up towards 4 as n grows (132 / 42 is already about 3.1). This short recursive count confirms it:

```python
from functools import lru_cache

@lru_cache(None)
def trees(n):          # n operands
    if n == 1:
        return 1
    # split into left k and right n-k
    return sum(trees(k) * trees(n - k)
               for k in range(1, n))

print([trees(n) for n in range(1, 8)])
# [1, 1, 2, 5, 14, 42, 132]
```

The famous real-world case is the **dangling else**:

```
S → if C then S
  | if C then S else S
  | other
```

In `if a then if b then x else y`, does `else y` belong to the inner or the outer `if`? C, C++ and Java all resolve it by convention: the `else` binds to the nearest eligible unmatched `if`. Parser generators such as yacc and Bison report this as a *shift/reduce conflict* and resolve it by shifting, which gives the same answer.

> [!warning] Ambiguous grammars versus ambiguous languages
> You can usually remove grammar ambiguity by rewriting the grammar (as the E/T/F grammar does). But some context-free *languages* are **inherently ambiguous**: every grammar for them is ambiguous. A standard example is { aⁱbʲcᵏ : i = j or j = k }. In the obvious union grammar, strings with i = j = k have two derivations. That observation alone does not prove inherent ambiguity: the theorem rules out every equivalent unambiguous CFG, not just this construction. Deciding whether an arbitrary CFG is ambiguous is also undecidable; a full proof of these results is beyond this lesson.

## Chomsky normal form and CYK

A grammar is in **Chomsky normal form** if every rule is one of:

- `A → B C` (exactly two variables), or
- `A → a` (exactly one terminal),
- plus optionally `S → ε` if the empty string is in the language. If this exception is used, S cannot appear on any right-hand side, so the empty production cannot occur inside a nonempty derivation.

Every CFG can be converted to Chomsky normal form mechanically: add a fresh start variable, remove ε-rules, remove unit rules like `A → B`, replace terminals in mixed/long right-hand sides with fresh variables, and break long right-hand sides into chains of pairs. For `aⁿbⁿ` with n ≥ 1:

```
S → A T | A B
T → S B
A → a
B → b
```

Chomsky normal form matters because it makes parsing a clean dynamic programme. In Chomsky normal form, every derivation of a nonempty string has the same, predictable length:

```formula
D(n) = (n − 1) + n = 2 × n − 1   for n ≥ 1
where
D(n): the number of derivation steps (rule applications) needed for a string of length n in a CNF grammar
n: the length of the string, in characters
In words: you need n − 1 two-variable rules to grow one variable into n of them, then n one-terminal rules to turn each into a character.
```

For `aabb` (n = 4) with the grammar above: S ⇒ AT ⇒ ASB ⇒ AABB uses 3 binary rules, then 4 terminal rules make aabb, so 7 steps = 2 × 4 − 1. The variable skeleton is a full binary tree; terminal-production nodes still have one terminal child in the complete parse tree. The count only holds for strict Chomsky normal form; the ε-exception for the start variable is the one derivation of length 1 that produces no characters.

The **CYK algorithm** (Cocke–Younger–Kasami) fills a table where `t[i][j]` holds every variable that can derive the substring from position i to j:

```python
RULES = [("S", "A", "T"), ("S", "A", "B"),
         ("T", "S", "B")]
TERM = {"a": {"A"}, "b": {"B"}}

def cyk(w):
    n = len(w)
    t = [[set() for _ in range(n)]
         for _ in range(n)]
    for i, c in enumerate(w):
        t[i][i] = set(TERM.get(c, ()))
    for L in range(2, n + 1):     # span
        for i in range(n - L + 1):
            j = i + L - 1
            for k in range(i, j):  # split
                for A, B, C in RULES:
                    if (B in t[i][k] and
                        C in t[k+1][j]):
                        t[i][j].add(A)
    return n > 0 and "S" in t[0][n-1]

for w in ["ab", "aabb", "aab", "abab"]:
    print(w, cyk(w))
# ab True / aabb True
# aab False / abab False
```

The three nested loops over span, start and split point, each running up to n times, plus a loop over the rules, give the running time:

```formula
T_CYK(n) = O(n^3 × |G|)
where
T_CYK(n): the number of basic steps CYK takes on an input string
n: the length of the input string, in tokens (characters here)
|G|: the size of the grammar, roughly its number of rules
O(…): big-O: grows no faster than the expression inside, up to a constant factor, for large n
In words: CYK's work grows with the cube of the input length, times the size of the grammar.
```

So for a fixed grammar, a 10 times longer input costs about 10³ = 1,000 times as much: 100 tokens needs on the order of 10⁶ inner steps per rule, 1,000 tokens about 10⁹. That proves every CFL (context-free language) can be parsed in polynomial time, but it is too slow for compilers handling large files.

## Real-world use

- **Language specifications** are written as grammars, usually in BNF or EBNF notation. The JSON specification at json.org is a short grammar; Python's full grammar is published in its reference manual.
- **Parser generators** take grammars and produce parsers. Deterministic LL(k) and LR(k) parsers have linear input-time bounds for a fixed suitable grammar. Bison also offers GLR parsing, and ANTLR uses adaptive prediction; it is wrong to describe all these capabilities as fixed-k deterministic parsing with the same guarantee.
- **Python 3.9+** replaced its LL(1) parser with a PEG parser (PEP 617). PEGs look like CFGs but use *ordered choice* (`A / B` tries A first and commits), so they are never ambiguous by construction.
- **Natural language processing** used probabilistic CFGs and CYK-style chart parsing for decades before neural parsers.

## Pitfalls

- Formal regular expressions cannot recognise arbitrary balanced nesting. Some practical regex engines add recursion or other non-regular features; HTML parsing also has rules beyond simple balanced tags.
- Left recursion (`E → E + T`) is fine for LR parsers but sends a naive recursive-descent (LL) parser into infinite recursion. Hand-written parsers rewrite it as a loop.
- A grammar that accepts the right strings can still give the wrong trees. Precedence and operator associativity live in the shape of the grammar, and tests must check the tree, not just acceptance.

## Key takeaways
- A CFG is (V, Σ, R, S) with rules `A → w`; one variable on the left means rewriting ignores context.
- CFGs can express nesting and matching, such as `aⁿbⁿ` and balanced brackets, which no finite automaton can.
- Parse trees capture structure; a grammar is ambiguous if some string has two trees. Some CFLs are inherently ambiguous.
- Grammar shape encodes precedence (layers E/T/F) and operator associativity (left or right recursion).
- Any CFG converts to Chomsky normal form, and CYK then decides membership in O(n³) time for a string of length n. Fixed-grammar deterministic LL/LR parsers can run in linear input time; other practical parsing methods have different guarantees.

## Further reading
- [Context-free grammar (Wikipedia)](https://en.wikipedia.org/wiki/Context-free_grammar)
- [CYK algorithm (Wikipedia)](https://en.wikipedia.org/wiki/CYK_algorithm)
- [Ambiguous grammar (Wikipedia)](https://en.wikipedia.org/wiki/Ambiguous_grammar)
- [Dangling else (Wikipedia)](https://en.wikipedia.org/wiki/Dangling_else)
- [Introducing JSON, with its full grammar (json.org)](https://www.json.org/json-en.html)
- [PEP 617: New PEG parser for CPython](https://peps.python.org/pep-0617/)
