---
id: auto-dfa
title: Deterministic finite automata
level: basic
minutes: 13
summary: The simplest model of a computer, a machine with a fixed number of states and no memory beyond them, and how it decides which strings belong to a language.
---

A simplified vending-machine controller can track bounded credit, and a simplified traffic light can track its current phase. Real controllers may also track timers, sensors and historical data. Both are **finite-state machines**: at any moment they are in one of a fixed, finite set of states, and each input moves them to another state.

A **deterministic finite automaton** (DFA) is the mathematical version of that idea, stripped down to its essentials. It reads a string one symbol at a time, changes state on each symbol, and at the end says yes or no. It is the simplest model of computation that is still useful, and it sits underneath lexers, regex engines, network protocol parsers and hardware controllers.

## Strings and languages

First, some vocabulary used for the rest of this module. Automata theory writes it in a compact notation borrowed from set theory, so here is every symbol you will meet, spelled out once:

```formula
Σ = {0, 1}   or   Σ = {a, b}
w = 0110   so   |w| = 4
|ε| = 0
Σ* = {ε, 0, 1, 00, 01, 10, 11, 000, …}
L ⊆ Σ*
where
Σ: capital Greek sigma: the input alphabet, a finite set of symbols the machine can read
{ }: curly braces: the set containing exactly the items listed inside, in any order
a, b: two example symbols, used as the letters of an alphabet
w: an example string: a finite sequence of symbols from Σ, here the four symbols 0, 1, 1, 0 in that order
| |: vertical bars around a string mean its length: how many symbols it contains
ε: Greek epsilon: the empty string, the string with no symbols at all (in Python, "")
*: the Kleene star: Σ* is the set of every finite string you can build from the symbols of Σ, including ε. It is infinite, but each string in it is finite
…: and so on without end
L: a formal language: any set of strings over Σ
⊆: is a subset of: every element of the left-hand set is also in the right-hand set
In words: an alphabet is a finite set of symbols; a string is a finite row of them (0110 has length 4, ε has length 0); Σ* collects every possible string; and a language is any collection of those strings, so it is a subset of Σ*.
```

The same ideas in words:

- An **input alphabet** (usually just called the alphabet) is a finite set of symbols, such as the two bits 0 and 1, or the letters a and b.
- A **string over an alphabet** is a finite sequence of its symbols. `0110` is a string over {0, 1}.
- The **empty string** has no symbols and length 0.
- A **formal language** (in this module, just "a language") is any set of strings over the alphabet. It can be finite or infinite.

"Binary strings with an even number of 1s" is a language. So is "valid Python identifiers" and "binary numbers divisible by 3". The question a DFA answers is the **membership problem**: is this string in the language?

## The formal definition

Mathematicians describe a DFA by listing its five ingredients in a fixed order, a 5-tuple. Any DFA, however big, is fully pinned down by these five things:

```formula
M = (Q, Σ, δ, q₀, F)
δ : Q × Σ → Q
q₀ ∈ Q
F ⊆ Q
where
M: the machine, the DFA being described
( , , , , ): round brackets with commas: an ordered list of components (a tuple); here there are five, so it is a 5-tuple
Q: the finite set of automaton states
Σ: capital Greek sigma: the input alphabet, the finite set of symbols the DFA can read
δ: Greek delta: the transition function. δ(q, c) is the one state to move to from state q on reading symbol c
×: the Cartesian product: Q × Σ is the set of every (state, symbol) pair
→: maps to: δ takes a pair from the set on the left and returns one element of the set on the right
q₀: "q nought": the start state, where every run begins
∈: is an element of
F: the set of accepting states (also called final states)
⊆: is a subset of: every element of F is also in Q; F may be empty or all of Q
In words: a DFA has a finite set of states, an alphabet, a rule giving exactly one next state for every state and symbol, one start state, and a chosen set of accepting states.
```

For the even-parity machine in Example 1 below, the five parts are:

```formula
Q = {E, O}     Σ = {0, 1}
q₀ = E         F = {E}
δ(E, 1) = O    δ(O, 1) = E
δ(E, 0) = E    δ(O, 0) = O
where
Q: the set of automaton states
E: the state meaning "an even number of 1s so far"
O: the state meaning "an odd number of 1s so far"
Σ: the input alphabet, here the two bits
q₀: the start state
F: the set of accepting states
δ: the transition function: δ(state, symbol) is the next state
{ }: the set of the items listed inside
In words: two states, E and O; a 1 swaps between them and a 0 leaves the state alone; start in E, and accept if you end in E.
```

In words, the five parts of any DFA are:

- a finite set of **automaton states**;
- the **input alphabet**;
- the **transition function**, which, given a state and a symbol, names exactly one next state;
- the **start state**;
- the **accepting states** (final states).

To run it on a string, begin in the start state and apply the transition function once per symbol. If you finish in an accepting state, the DFA **accepts**; otherwise it **rejects**. The set of strings it accepts is called the language of M:

```formula
L(M) = { w ∈ Σ* : δ̂(q₀, w) ∈ F }
where
L(M): the language recognised by the machine M: the set of strings it accepts
M: the DFA
{ w ∈ Σ* : … }: set-builder notation: the set of all strings w in Σ* that make the condition after the colon true. The colon reads "such that"
w: any string over the alphabet
Σ*: every finite string over the alphabet Σ, including the empty string
δ̂: "delta hat": the extended transition function. δ̂(q, w) is the state you end in after starting at q and applying δ once per symbol of w, left to right. For the empty string it stays put
q₀: the start state
∈: is an element of
F: the set of accepting states
In words: the language of M is exactly the set of strings that, read from the start state, leave the machine in an accepting state.
```

For example, the even-parity machine reads 1011 and finishes in O (traced in Example 1 below). O is not accepting, so 1011 is not in the machine's language.

"Deterministic" means there is never a choice: for every state and every symbol there is exactly one move. So a DFA's run on a given string is a single path, and it takes exactly n steps for a string of length n.

## Example 1: an even number of 1s

The language is binary strings with an even number of 1s. The only thing the machine needs to remember is the **parity** so far: even or odd. That is two states.

```
        0                0
       +-+              +-+
       v |              v |
 --> ((E)) ----1----> ( O )
         <----1------
```

The double brackets mark E as accepting. The arrow from nowhere marks it as the start. As a **transition table**, which is how you would store it in code:

| State | on 0 | on 1 |
|---|---|---|
| → E (accept) | E | O |
| O | O | E |

Trace `1011`:

```
start  E
  1 -> O
  0 -> O
  1 -> E
  1 -> O    end in O: reject
```

Three 1s is odd, so rejecting is right. Notice the DFA never counts the 1s. It only tracks the one bit of information that matters. Designing a DFA is mostly the art of asking "what is the least I need to remember?"

## Example 2: binary numbers divisible by 3

Read a binary number left to right, most significant bit first. Appending a bit to the right of a binary number doubles its value and adds the new bit, just as appending a digit in decimal multiplies by 10 and adds it. The machine cannot store the whole value, which grows without limit, but it does not need to: the remainder after dividing by 3 can be updated from the old remainder alone.

```formula
v′ = 2 × v + b
(2 × v + b) mod 3
  = (2 × (v mod 3) + b) mod 3
where
v: the value of the binary number read so far (a whole number, 0 for the empty string)
b: the next bit read, 0 or 1
v′: "v prime": the value after appending b
mod: the remainder after whole-number division, so 7 mod 3 = 1 and 9 mod 3 = 0
In words: the new remainder depends only on the old remainder and the new bit, never on the full value. So three states, one per possible remainder (0, 1 or 2), are enough.
```

For example, after reading `100` the value is 4 and the remainder is 1. Reading a 1 gives the value 2 × 4 + 1 = 9, and from the remainder alone, (2 × 1 + 1) mod 3 = 0: the same answer, because 9 is divisible by 3. This works because multiples of 3 contribute nothing to a remainder after doubling, so they can be thrown away at every step.

| Remainder | on 0 | on 1 |
|---|---|---|
| → 0 (accept) | 0 | 1 |
| 1 | 2 | 0 |
| 2 | 1 | 2 |

Trace `1001` (which is 9), applying the update once per bit:

```formula
r_0 = 0
r_1 = (2 × 0 + 1) mod 3 = 1
r_2 = (2 × 1 + 0) mod 3 = 2
r_3 = (2 × 2 + 0) mod 3 = 1
r_4 = (2 × 1 + 1) mod 3 = 0
where
r_0, r_1, r_2, r_3, r_4: the state (the remainder) after reading the first 0, 1, 2, 3 and 4 bits of 1001
mod: the remainder after whole-number division, so 4 mod 3 = 1
In words: the remainders go 0, 1, 2, 1, 0. The run ends in state 0, which is accepting, so 1001 (nine) is accepted as divisible by 3.
```

And `101` (5) goes 0 → 1 → 2 → 2, ending in 2: reject. The same trick builds a DFA for "divisible by k" with k states, in any base.

> [!note] What about the empty string?
> This DFA accepts the empty string, because the start state is accepting. Whether the empty string "is divisible by 3" is a design decision. If you want to reject it, add a separate start state. Edge cases like this are where hand-built automata most often go wrong.

## Running a DFA in Python

A DFA is just a lookup table and a loop. This is the whole simulator:

```python
def run_dfa(delta, start, accept, w):
    q = start
    for c in w:
        if (q, c) not in delta:
            return False   # no move: reject
        q = delta[(q, c)]
    return q in accept

D3 = {(r, b): (2 * r + int(b)) % 3
      for r in range(3) for b in "01"}

print(run_dfa(D3, 0, {0}, "1001"))  # True
print(run_dfa(D3, 0, {0}, "101"))   # False
```

The cost is O(n) time for a string of length n, for a fixed machine with constant-time transition lookup, using constant auxiliary state storage beyond the stored machine and input. That is the defining property of finite automata and the reason they are used for high-throughput scanning: they never need to look back, buffer or backtrack.

## Dead states and partial DFAs

Strictly, the transition function must be defined for every (state, symbol) pair: it must be **total**. A DFA where that holds is a **complete DFA**. In practice people draw **partial** DFAs and leave missing arrows implied. A missing arrow means "go to a **dead state**" (also called a trap or sink): a non-accepting state that loops to itself on every symbol. Once you fall in, you can never accept.

Here is a DFA for unsigned decimals such as `42` and `3.14`: one or more digits, optionally followed by a dot and one or more digits. `d` stands for an ASCII digit, 0 through 9.

| State | on d | on . |
|---|---|---|
| → S | WHOLE | dead |
| WHOLE (accept) | WHOLE | DOT |
| DOT | FRAC | dead |
| FRAC (accept) | FRAC | dead |

- `3.14`: S → WHOLE → DOT → FRAC → FRAC. Accept.
- `3.`: ends in DOT, which is not accepting. Reject.
- `.5`: S on `.` goes to dead. Reject.
- `1.2.3`: FRAC on `.` goes to dead. Reject.

This is exactly the regex `[0-9]+(\.[0-9]+)?`, and lexers for programming languages are built from automata like this one for every token type.

## Combining DFAs

Languages recognised by DFAs are called **regular languages**. They are closed under the usual set operations, and the proofs are constructions you can actually run.

### Complement

To recognise everything a complete DFA rejects, swap accepting and non-accepting states. The DFA for "odd number of 1s" is Example 1 with O accepting instead of E.

> [!warning] Complete the DFA first
> Swapping only works if the transition function is total. In a partial DFA, strings that "fall off" are rejected both before and after the swap. Add the dead state explicitly, then swap, and the dead state becomes accepting.

### Intersection and union: the product construction

Take two complete DFAs over the same alphabet. To recognise the strings both of them accept, run the two machines **in parallel**. A state of the product machine is a pair: where the first machine is, and where the second machine is. This is the **product construction**:

```formula
Q = Q₁ × Q₂
δ((p, q), c) = (δ₁(p, c), δ₂(q, c))
q₀ = (q₁, q₂)
F_{∩} = { (p, q) : p ∈ F₁ and q ∈ F₂ }
F_{∪} = { (p, q) : p ∈ F₁ or q ∈ F₂ }
where
Q₁, Q₂: the state sets of the first machine M₁ and the second machine M₂
Q: the state set of the product machine
×: the Cartesian product: Q₁ × Q₂ is the set of all pairs (p, q) with p from Q₁ and q from Q₂
p: a state of the first machine
q: a state of the second machine
( , ): an ordered pair: first component from M₁, second from M₂
c: one input symbol
δ₁, δ₂: the transition functions of the two machines
δ: the transition function of the product: it moves both components at once on the same symbol
q₁, q₂: the start states of the two machines
q₀: the start state of the product, the pair of the two start states
F₁, F₂: the accepting-state sets of the two machines
F_{∩}: the accepting states for intersection (strings both machines accept)
F_{∪}: the accepting states for union (strings at least one machine accepts)
∈: is an element of
{ (p, q) : … }: the set of all pairs that make the condition after the colon true
In words: the product machine tracks both machines at once. It moves each one on every symbol, and it accepts according to a rule: both accept for intersection, at least one accepts for union.
```

Its number of states is the product of the two sizes, which is where the name comes from:

```formula
|Q| = |Q₁| × |Q₂|
|Q| = 2 × 3 = 6
where
| |: vertical bars around a set mean its cardinality, the number of elements it has
Q: the state set of the product machine
Q₁: the state set of the first machine, here even parity with 2 states
Q₂: the state set of the second machine, here divisibility by 3 with 3 states
In words: the product of the parity machine and the divisible-by-3 machine has 2 × 3 = 6 states before minimisation.
```

It accepts 0 and other all-zero strings; positive-value examples without leading zeroes include 11 (3), 110 (6), 1001 (9) and 1100 (12). Each has an even number of 1s and a value divisible by 3.

Because the sizes multiply, intersecting k machines multiplies all k of their sizes together. This blow-up is real and shows up in model checking and in regex engines that support intersection.

## Where DFAs are used

- **Lexers.** Tools such as lex and flex compile token patterns to automata. One DFA membership scan is linear; longest-match tokenization, backup, rescanning and actions need separate complexity analysis.
- **Regex engines** such as RE2 and Rust's regex can combine DFA and NFA strategies; supported searches have input-linear bounds for a fixed pattern. GNU grep also uses other strategies depending on pattern and mode. Lesson 6 covers this.
- **Protocols and parsers.** HTTP parsers, UTF-8 validators and network packet filters are frequently hand-written state machines.
- **Hardware.** A synchronous digital circuit with bounded discrete internal state can be modelled as a finite-state machine; this abstraction omits analog timing effects. Controllers are designed as state diagrams and then synthesised.
- **Game AI and UI flows.** Enemy behaviour (patrol, chase, attack) and multi-step forms are often modelled as state machines, though these usually carry extra data so they are not pure DFAs.

## What a DFA cannot do

A DFA has a fixed number of states, so it can only remember a bounded amount of information. It cannot count without limit. "Equal numbers of a's and b's" or "balanced brackets" need unbounded memory, and no DFA recognises them. Lesson 4 proves this with the pumping lemma for regular languages.

That limitation is also the strength: because memory is bounded, a fixed-machine membership scan of a string of length n takes O(n) transitions and O(1) auxiliary space (a constant amount, however long the input), and many questions about DFAs (is the language empty? are two DFAs equivalent?) are decidable and fast. For more powerful machines those same questions become hard or impossible.

## Key takeaways
- A DFA is a 5-tuple: a finite set of states, an alphabet, a transition function with exactly one move per (state, symbol) pair, a start state and a set of accepting states. It accepts if the run ends in an accepting state.
- Design by asking what minimum information must be remembered: parity needs 2 states, the remainder construction uses k states but can sometimes be minimised further.
- Running a DFA on a string of length n is O(n) time and O(1) memory, with no backtracking.
- Missing transitions mean a dead state; make the DFA total before complementing.
- Regular languages are closed under complement (swap accepting and non-accepting states) and intersection and union (product construction, whose state count is the product of the two machines' state counts).
- DFAs cannot count without bound, so languages like balanced brackets are not regular.

## Further reading
- [Deterministic finite automaton — Wikipedia](https://en.wikipedia.org/wiki/Deterministic_finite_automaton)
- [Regular language — Wikipedia](https://en.wikipedia.org/wiki/Regular_language)
- [Finite-state machine — Wikipedia](https://en.wikipedia.org/wiki/Finite-state_machine)
- [Introduction to Automata Theory, Languages, and Computation — Ullman book page](http://infolab.stanford.edu/~ullman/ialc.html)
