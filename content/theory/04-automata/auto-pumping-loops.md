---
id: auto-pumping-loops
title: Why a long accepting run contains a loop
level: intermediate
minutes: 5
sourceLesson: auto-pumping
summary: The first pumping-length symbols visit more states than a DFA has.
---

The DFA units claimed that no DFA recognises "equal numbers of a's and b's" or "balanced brackets". Claiming is easy. How do you **prove** that no DFA exists, out of the infinitely many you could build?

You cannot try them all. Instead you find a property that every regular language has, then show your language lacks it. The most famous such property is the **pumping lemma for regular languages**. It comes from one observation: a machine with p states that reads a string of length p or more must visit some state twice.

## The pigeonhole idea

Count the states a run visits. Reading each symbol moves to the next state, and the start state counts too, so a run is always one state longer than the string.

```formula
n ≥ p
n + 1 > p
where
p: the number of states in the DFA
n: the length of the input string, in symbols; an integer count, non-negative unless a positive lower bound is stated
≥: is greater than or equal to
>: is greater than
In words: if the string is at least as long as the number of states, the run visits more states than exist, so some state must appear twice.
```

This is the **pigeonhole principle**: put more than p pigeons into p holes and some hole holds two. It also tells you where the repeat happens. The first p symbols already give p + 1 visits, so some state repeats within the first p symbols.

For example, a 3-state DFA reading 5 symbols visits 6 states, so at least one of its 3 states appears twice, and the first repeat comes within the first 3 symbols.

Look at what happens between the two visits. The machine read some non-empty chunk and came back to where it was. So it is in an **automaton loop**:

```
          y
        +---+
        v   |
--> ... (q) +  ... --> accept
   x         z
```

Cut the string into three pieces around the loop:

```formula
s = x · y · z
δ̂(q₀, x) = q
δ̂(q, y) = q
δ̂(q, z) ∈ F
x · y^i · z ∈ L   for all i ≥ 0
where
s: the accepted string
x: the part read before first reaching the repeated state
y: the part read going round the loop, from q back to q; it is not empty
z: the rest of the string, read after the loop
·: concatenation: one string straight after another
q₀: the start state
q: the state that is visited twice
δ̂: "delta hat": δ̂(state, string) is the state you end in after reading the whole string from that state
∈: is an element of
F: the set of accepting states
L: the language the DFA recognises
y^i: i copies of y in a row; y^0 is the empty string, y^2 = y · y
i: how many times you go round the loop, 0, 1, 2, …
≥: is greater than or equal to
In words: x leads to q, y goes from q back to q, and z leads from q to acceptance. Because y returns to q, the machine cannot tell how many times it went round, so repeating y, or deleting it, leaves a string the machine still accepts.
```

So xz (skip the loop), xyz, xyyz and xyyyz all end in the same state. If one is accepted, they all are.

### A concrete loop

Take the 3-state "divisible by 3" DFA from the DFA units and the string `1111` (15). The run is:

```
state:  0  1  0  1  0
read:     1  1  1  1
```

State 0 repeats after `11`. So the pieces are:

```formula
x = ε     y = "11"     z = "11"
x · y^0 · z = "11"         (3)
x · y^1 · z = "1111"       (15)
x · y^2 · z = "111111"     (63)
v_k = 4^k − 1
where
x, y, z: the three pieces of 1111 around the loop at state 0
ε: Greek epsilon: the empty string
"11": the two-symbol string 1 then 1 (the quotes mark a string of bits, not the number eleven)
·: concatenation: one string straight after another
y^i: i copies of y in a row
i: a non-negative integer repetition count
k: the number of pairs of 1s in the string after pumping; with i copies of y it is i + 1, because z adds one more pair; an integer count, non-negative unless a positive lower bound is stated
v_k: the value, in ordinary numbers, of a binary string of k pairs of 1s, that is 2k ones
In words: deleting the loop gives 11 (three), keeping it gives 1111 (fifteen), doubling it gives 111111 (sixty-three). In general k pairs of 1s is worth 4^k − 1, and all of these are divisible by 3.
```

The DFA says so, and arithmetic agrees: 4 leaves remainder 1 when divided by 3, so every power of 4 does too, and subtracting 1 leaves a multiple of 3.

## Key takeaways
- The first pumping-length symbols visit more states than a DFA has.
- A repeated state gives a non-empty loop that can be deleted or repeated.

## Further reading
- [MIT: the regular pumping lemma and automata to regexes](https://ocw.mit.edu/courses/18-404j-theory-of-computation-fall-2020/resources/mit18_404f20_lec3-1/)
