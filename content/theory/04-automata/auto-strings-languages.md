---
id: auto-strings-languages
title: Strings, alphabets and languages
level: basic
minutes: 4
sourceLesson: auto-dfa
summary: An alphabet supplies symbols; a language selects finite strings over it.
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
*: the Kleene star: Σ* is the set of every finite string you can build from the symbols of Σ, including ε. It is infinite for a non-empty alphabet; for the empty alphabet it contains only ε. Each string is finite
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

Some textbooks require an alphabet to be non-empty; if the empty alphabet is permitted, its only finite string is the empty string. Neither convention makes the empty language the same thing as the language containing only the empty string.

## Key takeaways
- An alphabet supplies symbols; a language selects finite strings over it.
- The empty string is a string of length zero, distinct from an empty language.

## Further reading
- [MIT: finite automata and regular expressions](https://ocw.mit.edu/courses/18-404j-theory-of-computation-fall-2020/resources/lecture-1-introduction-finite-automata-regular-expressions/)
