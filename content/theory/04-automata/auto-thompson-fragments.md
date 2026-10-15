---
id: auto-thompson-fragments
title: Composing Thompson fragments
level: intermediate
minutes: 4
sourceLesson: auto-thompson
summary: Each fragment has one entry and one accepting exit.
---

## Thompson's construction

The idea is structural induction. Build a small **NFA fragment** for each part of the regex, then glue fragments together. Every fragment keeps two promises:

1. It has exactly one **start state**, with no arrows coming in.
2. It has exactly one **accepting state**, with no arrows going out.

Those promises make gluing safe, because you never accidentally create a path into the middle of another fragment.

### Base case: a single symbol

```
--> (s) --a--> (f)
```

For the empty-string regex ε (Greek epsilon), use an ε-arrow, which reads no input, instead of a. For the empty-set regex ∅, which matches nothing, use two states and no arrow.

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

Each base case (an alphabet symbol, ε or ∅), `|` and `*` adds exactly two states, and concatenation adds none (just an ε-arrow). Counting them gives the size:

```formula
N = 2k
N ≤ 2|R|
where
N: the number of states in the Thompson NFA (this lesson's version)
k: the number of base-case occurrences (alphabet symbols, ε or ∅) plus the number of | and * operators in the regex; a positive integer
R: the regex
|R|: the length of the regex: how many symbols and operators it contains, counting concatenations as well
≤: is less than or equal to
In words: every base case, union and star costs exactly two states, so the NFA has twice as many states as the regex has base cases and union and star operators, and never more than twice the regex's length.
```

For `(a|b)*abb` there are five symbols, one `|` and one `*`, so k is 7 and the NFA has 2 × 7 = 14 states. Each state also has at most two outgoing arrows. The NFA is **linear in the size of the regex**, which is the property everything else relies on.

> [!note] Textbook variant
> Many textbooks, including the Dragon Book (Aho, Lam, Sethi and Ullman), merge R's accept state with S's start state during concatenation instead of adding an ε-arrow. That saves one state per concatenation. Both versions accept the same language.

## Parsing first: postfix

Building fragments needs a stack, and stacks work best on **postfix** notation. Two steps convert `(a|b)*abb`:

1. Insert an explicit regex-concatenation operator `.` wherever two items sit next to each other: `(a|b)*.a.b.b`.
2. Run the shunting-yard algorithm with regex precedence `*` > `.` > `|`: the result is `ab|*a.b.b.`.

Read the postfix left to right. A symbol pushes a new fragment. `*` pops one fragment and pushes its star. `.` and `|` pop two and push the combination.

## Key takeaways
- Each fragment has one entry and one accepting exit.
- Union and star add two states in this version; concatenation joins fragments with an epsilon arrow.

## Further reading
- [Russ Cox: simple and fast regular-expression matching](https://swtch.com/~rsc/regexp/regexp1.html)
- [MIT: regexes to finite automata](https://ocw.mit.edu/courses/18-404j-theory-of-computation-fall-2020/resources/mit18_404f20_lec2-1/)
