---
id: auto-dfa-uses-limits
title: Finite memory: uses and limits
level: basic
minutes: 3
sourceLesson: auto-dfa
summary: Counters restricted to a finite range and fixed nesting limits can be represented by finitely many states.
---

A DFA has finitely many states and one transition per input symbol. In the cost discussion below, n is the input length in symbols. Any fixed finite language can be recognised by a trie of its strings plus a rejecting dead state.

## Where DFAs are used

- **Lexers.** Tools such as lex and flex compile token patterns to automata. One DFA membership scan is linear; longest-match tokenization, backup, rescanning and actions need separate complexity analysis.
- **Regex engines** such as RE2 and Rust's regex can combine DFA and NFA strategies; supported searches have input-linear bounds for a fixed pattern. GNU grep also uses other strategies depending on pattern and mode. The practical regex units cover this.
- **Protocols and parsers.** HTTP parsers, UTF-8 validators and network packet filters are frequently hand-written state machines.
- **Hardware.** A synchronous digital circuit with bounded discrete internal state can be modelled as a finite-state machine; this abstraction omits analog timing effects. Controllers are designed as state diagrams and then synthesised.
- **Game AI and UI flows.** Enemy behaviour (patrol, chase, attack) and multi-step forms are often modelled as state machines, though these usually carry extra data so they are not pure DFAs.

## What a DFA cannot do

A DFA has a fixed number of states, so it can only remember a bounded amount of information. It cannot count without limit. "Equal numbers of a's and b's" or "balanced brackets" need unbounded memory, and no DFA recognises them. The pumping-lemma units proves this with the pumping lemma for regular languages.

That limitation is also the strength: because memory is bounded, a fixed-machine membership scan of a string of length n takes O(n) transitions and O(1) auxiliary space (a constant amount, however long the input), and many questions about DFAs (is the language empty? are two DFAs equivalent?) are decidable and fast. For more powerful machines those same questions become hard or impossible.

## Key takeaways
- Counters restricted to a finite range and fixed nesting limits can be represented by finitely many states.
- Unbounded matching counts and unrestricted balanced brackets need more memory than a DFA supplies.

## Further reading
- [MIT: finite automata and regular expressions](https://ocw.mit.edu/courses/18-404j-theory-of-computation-fall-2020/resources/lecture-1-introduction-finite-automata-regular-expressions/)
