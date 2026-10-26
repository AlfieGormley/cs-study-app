---
id: auto-pumping-loops
title: Why a long accepting run contains a loop
level: intermediate
minutes: 4
sourceLesson: auto-pumping
summary: The first pumping-length symbols visit more states than a DFA has.
---

The DFA units claimed that no DFA recognises "equal numbers of a's and b's" or "balanced brackets". Claiming is easy. How do you **prove** that no DFA exists, out of the infinitely many you could build?

You cannot try them all. Instead you find a property that every regular language has, then show your language lacks it. The most famous such property is the **pumping lemma for regular languages**. It comes from one observation: a machine with p states that reads a string of length p or more must visit some state twice.

## The pigeonhole idea

Count state visits, including the start. Repeated visits count separately: the run does not gain new states when it loops.

Reading as many symbols as the DFA has states visits one extra state, because the start counts too. Some visit must repeat an earlier state. This already happens within that initial portion of the run.

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

```formula essential
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

Skip the loop, follow it once or follow it repeatedly: after the unchanged suffix, every run ends in the same state. If one is accepted, they all are.

> [!analogy] Real-world analogy: An extra lap
> On a walking route, a lap returns you to the same junction before you continue to your destination.
>
> **How it maps:** The junction is the repeated DFA state, the lap is the non-empty pumped piece, and the remaining route is the unchanged suffix. Taking zero or several laps still lets you follow that suffix.
>
> **Where it stops:** A physical walk may track elapsed time or tiredness. A DFA stores only its current state, so completing the loop leaves no extra memory of how often it happened.

### A concrete loop

Take the 3-state "divisible by 3" DFA from the DFA units and the string `1111` (15). The run is:

```
state:  0  1  0  1  0
read:     1  1  1  1
```

State 0 repeats after `11`.

The loop reads `11`. Skip it and the remaining input is `11`; take it once and the input is `1111`; take it twice and the input is `111111`. Each run returns to the same state before reading the final `11`, so all three strings are accepted.

The state path is enough to explain why all repetitions work; converting each binary string to a number adds no new justification.

## Key takeaways
- The first pumping-length symbols visit more states than a DFA has.
- A repeated state gives a non-empty loop that can be deleted or repeated.

## Further reading
- [MIT: the regular pumping lemma and automata to regexes](https://ocw.mit.edu/courses/18-404j-theory-of-computation-fall-2020/resources/mit18_404f20_lec3-1/)
