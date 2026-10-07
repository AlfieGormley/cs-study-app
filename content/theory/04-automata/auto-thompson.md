---
id: auto-thompson
title: From regular expressions to NFAs (Thompson)
level: intermediate
minutes: 15
summary: What a regular expression formally is, Thompson's construction for compiling one into an ε-NFA piece by piece, a working Python version, and the reverse trip from automaton back to regex.
---

A tool such as grep -E can compile (a|b)*abb and scan input using the resulting matcher. Throughput depends on the tool, data, hardware and I/O. Between the pattern and the scan is a compiler. It parses the regex into a tree, turns the tree into an automaton, and runs the automaton over the text.

A standard first step of that compiler is **Thompson's construction**, published by Ken Thompson in 1968. It is short enough to write from memory, it produces an NFA linear in the size of the regex, and every piece of it is one of the three operations that define regular expressions.

## What a regular expression is, formally

Strip away the syntax sugar and a regular expression over Σ is built from six rules:

| Regex | Language |
|---|---|
| ∅ | no strings at all |
| ε | just the empty string |
| a (for a ∈ Σ) | just the string "a" |
| R \| S | union: L(R) ∪ L(S) |
| RS | concatenation: xy, x ∈ L(R), y ∈ L(S) |
| R* | Kleene star: zero or more copies of L(R) |

Everything else in everyday regex syntax is shorthand, as long as it stays regular:

- `R+` is `RR*`.
- `R?` is `R|ε`.
- `[a-c]` is `a|b|c`.
- `R{2,3}` is `RR|RRR`.
- In a formal wildcard notation, . can denote the union of the alphabet. Real regex engines commonly exclude newline unless a dot-all option is enabled.

General backreferences can express non-regular languages, such as (a+)b\1 matching aⁿbaⁿ for n ≥ 1. Some individual backreference patterns are still regular: (a+)\1 matches positive even-length runs of a, equivalent to (aa)+. Engines such as RE2 reject the feature syntactically rather than proving regularity separately for each pattern.

Precedence, highest first: star, then concatenation, then union. So `ab|c*` means `(ab)|(c*)`, not `a(b|c)*`.

### Kleene's theorem

Stephen Kleene proved in 1956 that regular expressions and finite automata describe exactly the same languages:

- Every regex has an NFA (and hence a DFA) recognising its language. Thompson's construction is one proof.
- Every DFA has an equivalent regex. State elimination, at the end of this lesson, is one proof.

That equivalence is why the languages are called *regular*: the regex view and the machine view are two descriptions of one class.

## Thompson's construction

The idea is structural induction. Build a small NFA **fragment** for each part of the regex, then glue fragments together. Every fragment keeps two promises:

1. It has exactly **one start state** with no arrows coming in.
2. It has exactly **one accepting state** with no arrows going out.

Those promises make gluing safe, because you never accidentally create a path into the middle of another fragment.

### Base case: a single symbol

```
--> (s) --a--> (f)
```

For ε, use an ε-arrow instead of a. For ∅, use two states and no arrow.

### Concatenation RS

Link R's accept state to S's start with an ε-arrow. R's accept stops being accepting.

```
--> [R: r0 ... r1] -ε-> [S: s0 ... s1]
```

The new fragment starts at r0 and accepts at s1.

### Union R|S

Add a new start with ε-arrows into both fragments and a new accept with ε-arrows out of both.

```
         ε                   ε
     +-----> (r0) ~R~> (r1) -----+
     |                           v
--> (s)                         (f)
     |   ε                   ε   ^
     +-----> (s0) ~S~> (s1) -----+
```

### Star R*

Add a new start and accept. From the new start you can skip R entirely or enter it. From R's accept you can loop back or leave.

```
                 ε (repeat)
            +-------------+
            v             |
--> (s) -ε-> (r0) ~R~> (r1) -ε-> (f)
     |                            ^
     +------------- ε ------------+
                 (skip)
```

`R+` is the same without the skip arrow. `R?` is the same without the repeat arrow.

### How big is the result?

Each symbol, `|` and `*` adds exactly two states, and concatenation adds none (just an ε-arrow). So a regex with k symbols and operators gives at most 2k states, and each state has at most two outgoing arrows. The NFA is **linear in the size of the regex**, which is the property everything else relies on.

> [!note] Textbook variant
> Many textbooks, including the Dragon Book (Aho, Lam, Sethi and Ullman), merge R's accept state with S's start state during concatenation instead of adding an ε-arrow. That saves one state per concatenation. Both versions accept the same language.

## Parsing first: postfix

Building fragments needs a stack, and stacks work best on **postfix** notation. Two steps convert `(a|b)*abb`:

1. Insert an explicit concatenation operator `.` wherever two items sit next to each other: `(a|b)*.a.b.b`.
2. Run the shunting-yard algorithm with precedence `*` > `.` > `|`: the result is `ab|*a.b.b.`.

Read the postfix left to right. A symbol pushes a new fragment. `*` pops one fragment and pushes its star. `.` and `|` pop two and push the combination.

## Thompson's construction in Python

This compact compiler accepts validated postfix expressions of literal characters and the operators ., | and *. It omits parsing, escaping, character classes and explicit ε/∅ tokens. Its global state accumulates across calls; reset delta and n before comparing independent machine sizes.

```python
from collections import defaultdict

delta = defaultdict(set)  # (q, c) -> set
n = 0

def new():
    global n
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
            arc(e1, "", s2)
            st.append((s1, e2))
        elif c == "|":
            s2, e2 = st.pop()
            s1, e1 = st.pop()
            s, e = new(), new()
            arc(s, "", s1); arc(s, "", s2)
            arc(e1, "", e); arc(e2, "", e)
            st.append((s, e))
        elif c == "*":
            s1, e1 = st.pop()
            s, e = new(), new()
            arc(s, "", s1); arc(s, "", e)
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
print(n)  # 14
```

The result plugs straight into `run_nfa` from the previous lesson. `run_nfa(delta, start, {acc}, "babb")` is `True` and `"abba"` gives `False`. The audit compares this NFA with re.fullmatch on all strings over {a, b} up to length 10; that finite check supports the example but is not the general equivalence proof.

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

Now apply the subset construction. The start is ε-closure({0}) = {0, 1, 2, 4, 7}.

| DFA | NFA states | on a | on b |
|---|---|---|---|
| → A | {0,1,2,4,7} | B | C |
| B | {1,2,3,4,6,7,8} | B | D |
| C | {1,2,4,5,6,7} | B | C |
| D | {1,2,4,5,6,7,9} | B | E |
| E (accept) | {1,2,4,5,6,7,10} | B | C |

Five DFA states from 11 NFA states. Read them as "how much of abb have I just seen": A and C mean none, B means a, D means ab, E means abb. A and C behave identically, so the minimal DFA (lesson 5) has 4 states.

## The other direction: automaton to regex

To show every DFA has a regex, use **state elimination**:

1. Add a new start state with an ε-arrow to the old start, and a new single accept state with ε-arrows from the old accepting states.
2. Allow arrows to be labelled with regexes, not just symbols.
3. Remove the other states one by one. When you remove state q, for every path p → q → r, add an arrow p → r labelled (p→q)(q→q)*(q→r), and union it with any existing p → r arrow.
4. When only the new start and accept remain, the label between them is the regex.

For the "even number of 1s" DFA from lesson 1 (E loops on 0, 1 goes to O, O loops on 0, 1 goes back to E), eliminate O: the path E → O → E becomes `10*1`. With E's own `0` loop the answer is `(0|10*1)*`.

Regexes produced this way can be exponentially longer than the DFA, and different elimination orders give different (equivalent) regexes. That is why tools go regex → automaton all the time and rarely the other way.

## Where this shows up

- **lex and flex** compile token patterns into an NFA in this way, then determinise it ahead of time into a table-driven DFA. GNU grep may select DFA, literal-search or other matching strategies depending on options and pattern features.
- **RE2, Go's `regexp` and Rust's `regex`** compile into an NFA-like program of instructions (match a byte, split into two threads, jump) that is Thompson's NFA in a different notation. Russ Cox's articles show this "Pike VM" view.
- **Alternatives** exist. The Glushkov (or position) automaton has no ε-arrows and one state per symbol occurrence plus a start, which suits bit-parallel matching. Brzozowski **derivatives** build a DFA directly from the regex by repeatedly asking "what is left to match after reading this symbol?"

## Pitfalls

- **Precedence bugs.** `^ab|cd$` means `(^ab)|(cd$)`, not `^(ab|cd)$`. Many real validation bugs come from this.
- **Counted repetition is expansion.** `(a|b){1000}` becomes a thousand copies of the fragment, and `x{1,1000}` likewise. RE2 limits counted repetitions for this reason: its syntax rejects `{n}` when n exceeds 1000. Other engines have different limits and representations.
- **Star of something that matches ε.** `(a*)*` is legal, but the NFA has ε-cycles. Set simulation handles that fine because ε-closure visits each state once. A naive recursive backtracker without a zero-progress guard may loop; practical engines commonly detect empty repetitions, although other patterns can still cause excessive backtracking.

## Key takeaways
- Formal regexes use union, concatenation and star over ∅, ε and single symbols. Many practical features are shorthand, while general backreferences add expressive power.
- Kleene's theorem: regexes and finite automata describe exactly the regular languages.
- Thompson's construction builds an ε-NFA with one start and one accept per fragment, at most 2 states per symbol or operator.
- Parse to postfix first, then build fragments with a stack.
- (a|b)*abb gives an 11 to 14 state NFA, a 5-state DFA, and a 4-state minimal DFA.
- State elimination turns a DFA back into a regex, but the regex can be exponentially larger.

> [!note] Evidence gap
> A previous fixed grep throughput figure is omitted because no reproducible hardware, input and tool configuration was available.

## Further reading
- [Thompson's construction — Wikipedia](https://en.wikipedia.org/wiki/Thompson%27s_construction)
- [Regular Expression Matching Can Be Simple And Fast — Russ Cox](https://swtch.com/~rsc/regexp/regexp1.html)
- [Regular expression — Wikipedia](https://en.wikipedia.org/wiki/Regular_expression)
- [Kleene's algorithm — Wikipedia](https://en.wikipedia.org/wiki/Kleene%27s_algorithm)
- [Shunting yard algorithm — Wikipedia](https://en.wikipedia.org/wiki/Shunting_yard_algorithm)
