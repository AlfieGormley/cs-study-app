---
id: auto-dfa
title: Deterministic finite automata
level: basic
minutes: 13
summary: The simplest model of a computer, a machine with a fixed number of states and no memory beyond them, and how it decides which strings belong to a language.
---

A simplified vending-machine controller can track bounded credit, and a simplified traffic light can track its current phase. Real controllers may also track timers, sensors and historical data. Both are **finite-state machines**: at any moment they are in one of a fixed, finite set of states, and each input moves them to another state.

A **deterministic finite automaton** (DFA) is the mathematical version of that idea, stripped down to its core. It reads a string one symbol at a time, changes state on each symbol, and at the end says yes or no. It is the simplest model of computation that is still useful, and it sits underneath lexers, regex engines, network protocol parsers and hardware controllers.

## Strings and languages

First, some vocabulary used for the rest of this module.

- An **alphabet** Σ is a finite set of symbols, for example Σ = {0, 1} or Σ = {a, b}.
- A **string** is a finite sequence of symbols. `0110` is a string over {0, 1}.
- The **empty string**, written ε, has length 0.
- Σ* is the set of all strings over Σ, including ε.
- A **language** is any set of strings, so any subset of Σ*. It can be finite or infinite.

"Binary strings with an even number of 1s" is a language. So is "valid Python identifiers" and "binary numbers divisible by 3". The question a DFA answers is **membership**: is this string in the language?

## The formal definition

A DFA is a 5-tuple (Q, Σ, δ, q₀, F):

- Q: a finite set of **states**.
- Σ: the input **alphabet**.
- δ: the **transition function**, δ : Q × Σ → Q. Given a state and a symbol, it names exactly one next state.
- q₀ ∈ Q: the **start state**.
- F ⊆ Q: the **accepting** (final) states.

To run it on a string, start in q₀ and follow δ once per symbol. If you finish in a state in F, the DFA **accepts**; otherwise it **rejects**. The language of the DFA, L(M), is the set of strings it accepts.

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

Read a binary number left to right. If the value so far is v and you read bit b, the new value is 2v + b. We only care about v mod 3, and

```
(2v + b) mod 3 = (2(v mod 3) + b) mod 3
```

so three states, one per remainder, are enough.

| Remainder | on 0 | on 1 |
|---|---|---|
| → 0 (accept) | 0 | 1 |
| 1 | 2 | 0 |
| 2 | 1 | 2 |

Trace `1001` (which is 9):

```
start  0
  1 -> (2*0+1)%3 = 1
  0 -> (2*1+0)%3 = 2
  0 -> (2*2+0)%3 = 1
  1 -> (2*1+1)%3 = 0   accept
```

And `101` (5) goes 0 → 1 → 2 → 2, ending in 2: reject. The same trick builds a DFA for "divisible by k" with k states, in any base.

> [!note] What about the empty string?
> This DFA accepts ε, because the start state is accepting. Whether ε "is divisible by 3" is a design decision. If you want to reject it, add a separate start state. Edge cases like this are where hand-built automata most often go wrong.

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

Strictly, δ must be defined for every (state, symbol) pair. In practice people draw **partial** DFAs and leave missing arrows implied. A missing arrow means "go to a **dead state**" (also called a trap or sink): a non-accepting state that loops to itself on every symbol. Once you fall in, you can never accept.

Here is a DFA for unsigned decimals such as `42` and `3.14`: one or more digits, optionally followed by a dot and one or more digits. `d` stands for an ASCII digit, 0 through 9.

| State | on d | on . |
|---|---|---|
| → S | INT | dead |
| INT (accept) | INT | DOT |
| DOT | FRAC | dead |
| FRAC (accept) | FRAC | dead |

- `3.14`: S → INT → DOT → FRAC → FRAC. Accept.
- `3.`: ends in DOT, which is not accepting. Reject.
- `.5`: S on `.` goes to dead. Reject.
- `1.2.3`: FRAC on `.` goes to dead. Reject.

This is exactly the regex `[0-9]+(\.[0-9]+)?`, and lexers for programming languages are built from automata like this one for every token type.

## Combining DFAs

Languages recognised by DFAs are called **regular languages**. They are closed under the usual set operations, and the proofs are constructions you can actually run.

### Complement

To recognise everything a complete DFA rejects, swap accepting and non-accepting states. The DFA for "odd number of 1s" is Example 1 with O accepting instead of E.

> [!warning] Complete the DFA first
> Swapping only works if δ is total. In a partial DFA, strings that "fall off" are rejected both before and after the swap. Add the dead state explicitly, then swap, and the dead state becomes accepting.

### Intersection and union: the product construction

For complete DFAs over the same alphabet, to recognise strings in both L(M₁) and L(M₂), run the two machines **in parallel**. A state of the product machine is a pair (p, q): where M₁ is and where M₂ is.

- States: Q₁ × Q₂.
- δ((p, q), c) = (δ₁(p, c), δ₂(q, c)).
- Start: (q₁, q₂).
- Accept for intersection: both components accepting. For union: at least one.

The product for even parity and divisibility by 3 has 2 × 3 = 6 states before minimisation. It accepts 0 and other all-zero strings; positive-value examples without leading zeroes include 11 (3), 110 (6), 1001 (9) and 1100 (12). Each has an even number of 1s and a value divisible by 3.

The product has |Q₁| × |Q₂| states, so intersecting k machines multiplies their sizes. This blow-up is real and shows up in model checking and in regex engines that support intersection.

## Where DFAs are used

- **Lexers.** Tools such as lex and flex compile token patterns to automata. One DFA membership scan is linear; longest-match tokenization, backup, rescanning and actions need separate complexity analysis.
- **Regex engines** such as RE2 and Rust's regex can combine DFA and NFA strategies; supported searches have input-linear bounds for a fixed pattern. GNU grep also uses other strategies depending on pattern and mode. Lesson 6 covers this.
- **Protocols and parsers.** HTTP parsers, UTF-8 validators and network packet filters are frequently hand-written state machines.
- **Hardware.** A synchronous digital circuit with bounded discrete internal state can be modelled as a finite-state machine; this abstraction omits analog timing effects. Controllers are designed as state diagrams and then synthesised.
- **Game AI and UI flows.** Enemy behaviour (patrol, chase, attack) and multi-step forms are often modelled as state machines, though these usually carry extra data so they are not pure DFAs.

## What a DFA cannot do

A DFA has a fixed number of states, so it can only remember a bounded amount of information. It cannot count without limit. "Equal numbers of a's and b's" or "balanced brackets" need unbounded memory, and no DFA recognises them. Lesson 4 proves this with the pumping lemma.

That limitation is also the strength: because memory is bounded, a fixed-machine membership scan takes O(n) transitions and O(1) auxiliary space, and many questions about DFAs (is the language empty? are two DFAs equivalent?) are decidable and fast. For more powerful machines those same questions become hard or impossible.

## Key takeaways
- A DFA is (Q, Σ, δ, q₀, F): finite states, one move per (state, symbol), accept if the run ends in F.
- Design by asking what minimum information must be remembered: parity needs 2 states, the remainder construction uses k states but can sometimes be minimised further.
- Running a DFA is O(n) time and O(1) memory, with no backtracking.
- Missing transitions mean a dead state; make the DFA total before complementing.
- Regular languages are closed under complement (swap F) and intersection and union (product construction, |Q₁| × |Q₂| states).
- DFAs cannot count without bound, so languages like balanced brackets are not regular.

## Further reading
- [Deterministic finite automaton — Wikipedia](https://en.wikipedia.org/wiki/Deterministic_finite_automaton)
- [Regular language — Wikipedia](https://en.wikipedia.org/wiki/Regular_language)
- [Finite-state machine — Wikipedia](https://en.wikipedia.org/wiki/Finite-state_machine)
- [Introduction to Automata Theory, Languages, and Computation — Ullman book page](http://infolab.stanford.edu/~ullman/ialc.html)
