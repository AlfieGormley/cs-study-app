---
id: auto-dfa-parity-cycles
title: Designing parity and length cycles
level: basic
minutes: 3
sourceLesson: auto-dfa
summary: Parity needs only the distinction between even and odd, rather than a full counter.
---

The earlier definition specifies a start state, a set of accepting states and exactly one next state per symbol. Here E means an even number of 1s so far and O means an odd number; start and accept in E.

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

A four-state cycle can similarly track the input length modulo four: each input symbol advances one position, and only the starting position accepts. Four prefixes of lengths zero through three need distinct futures: append enough symbols to bring one chosen length to a multiple of four, and the others still have different remainders.

## Key takeaways
- Parity needs only the distinction between even and odd, rather than a full counter.
- A length-divisibility cycle stores a fixed remainder; distinguishable futures justify the state count.

## Further reading
- [MIT: finite automata and regular expressions](https://ocw.mit.edu/courses/18-404j-theory-of-computation-fall-2020/resources/lecture-1-introduction-finite-automata-regular-expressions/)
