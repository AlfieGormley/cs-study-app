---
name: writing-formulas
description: Write mathematical formulas, equations and worked calculations in cs-study-app lessons or questions. Assume basic algebra, use clear grouping and conventional multiplication, and define each symbol's meaning and units.
---

# Writing formulas

The reader is studying on a phone. **Assume they can read basic algebra**, including ordinary arithmetic,
brackets, powers and implicit multiplication such as `2x`, `IR` and `a(b + c)`. Do not explain those conventions
or put multiplication signs between every factor. Still define what each variable represents, its units and
any domain-specific function or unfamiliar notation: basic algebra does not tell the reader what `V_out`,
`RTT`, `Hz`, `dB`, `Σ` or `mod` means in this lesson.

## Rule 1: every equation goes in a `formula` block

Any equation, relation or calculation that uses a symbol (a letter, a Greek letter, a function name or a unit)
goes in a fenced `formula` block, in lessons **and** in questions (prompt, explanations, worked example):

````
```formula
f_beam = c / (2πa)
where
f_beam: the frequency above which the cone starts to focus sound forwards instead of spreading it, in hertz (Hz)
c: the speed of sound in air, about 343 metres per second (m/s) at 20 °C
π: pi, the fixed ratio of a circle's circumference to its diameter, about 3.14159
a: the radius of the cone (half its diameter), in metres (m)
Hz: hertz, the unit of frequency: one cycle per second
In words: the bigger the cone, the lower the frequency at which it starts beaming. Double the radius and beaming starts an octave lower.
```
````

The app renders this as a card: the equation, a "where" table of every symbol, then the plain-English reading.

**The build rejects a formula block that:**
- leaves any symbol in its equation lines undefined, or
- has unmatched or incorrectly paired grouping brackets, or
- has no `In words:` line.

There is no way round this, by design.

## Rule 2: what a definition must say

Each `symbol: meaning` line must give, as far as it applies:
1. **What it is**, in plain words, with no undefined jargon. A glossary term is fine, because it links
   automatically.
2. **Its unit**, both symbol and name, e.g. "in ohms (Ω)".
3. **A typical value or range** where that helps, e.g. "about 343 m/s", "usually 0.5–0.7".
4. **What changing it does**, when that's the point of the formula.

Define **everything** used in the equation lines:
- variables (`n`, `x`, `f_c`)
- constants (`π`, `e`, `c`)
- functions (`log_2`, `sin`, `max`, `mod`, `floor`)
- units (`Hz`, `dB`, `V`, `Ω`, `ms`)
- named quantities (`RTT`, `SPL`, `Q`)

Also define any non-obvious operator, even though the checker can't see operators:
- `≈`, `∝`, `Σ`
- `⌈ ⌉` (ceiling), `|x|`, `!`, `mod`
- `→` (implication or limit)
- `O(...)`

The obvious ones (`+`, `−`, `=`, `×`, `/`, brackets) don't need definitions.

The same symbol appearing in several blocks is defined in **each** block: every card stands alone.

## Rule 3: notation the renderer understands

| Write | Means | Renders |
|---|---|---|
| `V_out`, `f_{c}` | subscript | V<sub>out</sub> |
| `x^2`, `10^{n/20}` | power | x<sup>2</sup> |
| `2x`, `IR`, `2πRC` | multiply | conventional algebra |
| `×` or `·` | multiply | explicit when needed |
| `/` | divide | |
| `√(x)` | square root | |
| `log_2(n)` | log base 2 | |

- **Make grouping explicit wherever it affects the meaning.** Put a compound numerator or denominator in
  brackets: `(a + b) / c`, `a / (b + c)` and `1 / (2πRC)`. Write `(a + b)^2` when the whole sum is squared;
  `a + b^2` squares only `b`. Group the whole exponent with braces or parentheses, as in `2^{n − 1}` or
  `2^(n − 1)`. Likewise, make the full argument of a root or function explicit: `√(x + y)` and `log_2(n + 1)`.
  Check bracket pairing across continuation lines as well as each complete calculation.
- **Use conventional implicit multiplication for clearly separated factors.** Prefer `IR`, `2πa` and
  `R(C_1 + C_2)` when their individual symbols are defined; `20 log_10(x)` needs no multiplication sign
  before the function. The checker recognises `RC` as `R` times `C` when both are defined and `RC` is not
  itself a defined quantity. Use spaces or braces to separate
  subscripted factors (`R_1 C_1` or `R_{1}C_{1}`).
- Keep `×` between numbers (`2 × 3`), between ambiguous names (`users × rate`), and wherever adjacency
  could look like another defined quantity or a unit (`m × s` must not become `ms`). After a slash,
  preserve the intended scope: write `(a / b)c` or `a / (bc)` rather than `a / bc`. Do not remove signs
  mechanically or add brackets that change the mathematical meaning.
- Preserve dedicated product operators for sets and vectors, such as Cartesian `×`, cross products and
  dot products `·`; these are not interchangeable with ordinary scalar multiplication.
- Use maths notation, **not programming syntax**: no `**`, `*`, `pi`, `sqrt()`, `math.log10()` or `10**(x/20)` in
  a formula block. Code belongs in a `python` (or `c`, `sql`, …) block. If you show both, put the formula block
  first and the code after it.
- Formula blocks can't go inside a callout (`> [!note]`) or a list item. Put the block straight after the
  callout or list; a numbered list can resume afterwards ("4." keeps its number).
- Keep each equation line within **44 characters** in lessons and **40** in questions. Split long derivations over
  several lines (all of them come before `where`).
- **Connective words need no definition**: `for`, `all`, `some`, `as`, `so`, `when`, `if`, `then`, `means`, `gives`,
  `and`, `or`, `not`, `is`, `to`, `of`, `at`, `per` and similar (the full list is `CONNECTIVES` in `formula.js`).
  Write conditions naturally, as in `n^2 ≤ cn   for all n ≥ n_0` or `1 / n → 0   as n → ∞`. **Never define a
  connective** in `where`: the build rejects that.
- A descriptive variable name (`users`, `rate`, `daily_writes`) is fine **if it is defined** like any other
  symbol. It's often clearer than a single letter in back-of-envelope estimates.
- **Never use an English word as a symbol** just to get past the checker. Lines like "to: …", "peak: …",
  "null: …" or "cardioid: …" are not allowed. Use proper symbols (`L_peak`, `θ_null`, `t_min`) or split the line
  (`t_min ≈ 127 ms` and `t_max ≈ 137 ms` instead of "(10 to 20) ms"). The verifier rejects word-symbols.
- **Explain non-obvious constants too.** A number that isn't self-explanatory (the 0.161 in Sabine's formula, the 20
  in 20 log_10, a safety factor of 2) may have its own `where` line saying where it comes from. Obvious numbers
  from the problem ("100 requests") need none.
- Numbers aren't symbols, so `343`, `1e-3` and `0x1F` need no definitions. Quoted text such as `hash("key")` is
  treated as literal and is skipped too.

## Rule 4: worked calculations

Show substitution step by step as extra equation lines, **with units on every line**. Define the units in
`where`:

````
```formula
f_c = 1 / (2πRC)
f_c = 1 / (2π × 1000 Ω × 100 nF)
f_c ≈ 1592 Hz
where
f_c: the cut-off frequency of the RC low-pass filter, in hertz (Hz): the point where the output has fallen to about 71 % of the input (−3 dB)
R: the resistance, in ohms (Ω); here 1 kΩ = 1000 Ω
C: the capacitance, in farads (F); here 100 nF = 0.0000001 F
π: pi, about 3.14159
≈: approximately equal to (the result is rounded)
Hz: hertz, cycles per second
Ω: ohm, the unit of resistance
nF: nanofarad, one billionth of a farad
In words: a 1 kΩ resistor with a 100 nF capacitor starts cutting frequencies above about 1.6 kHz.
```
````

## Rule 5: surround the formula with explanation

- **Before the block:** one or two sentences on what problem the formula answers and when you'd use it.
- **After the block:** a worked example with real numbers, unless the block already includes one. Also say where
  it stops being true: its assumptions and limits.
- In prose, a symbol may be mentioned again only **after** the block that defines it, in the same lesson section
  (for example "so doubling *a* halves *f_beam*").

## Rule 6: what may stay inline

Only these stay in prose without a formula block:
- **Plain numeric statements with units and no symbols**: "100 W into 8 Ω is about 28 V" or "1 Pa ≈ 94 dB SPL".
  In these, spell out any unit the reader may not know, or rely on its glossary link.
- **Big-O in prose**, once the lesson has defined what `n` (and any other variable) means in that section,
  either in a formula block or in a sentence like "where n is the number of items". In a question, the
  explanation must say what n is.
- **Real program code** in inline code spans or code blocks, e.g. `x = x + 1` in Python.

Everything else gets a formula block.

## Rule 7: questions

Each question is read on its own, out of lesson context:
- Define symbols again inside the question's own formula blocks; never write "see the lesson".
- Keep option text short. Put formulas in the `workedExample` and in the explanations.
- The worked example must show the calculation in a formula block, with every symbol defined.

## Checking your work

```sh
node scripts/lint-formulas.mjs content/<subject>/<module>   # equations still written outside formula blocks
node scripts/build.mjs --check content/<subject>/<module>   # undefined symbols / missing "In words"
```

The lint is a heuristic finder. Each hit must end up either converted into a formula block or justified as one
of the Rule 6 exceptions. Report the justified ones and why.

The verifier recomputes every formula and worked number. It checks the full grouping of numerators,
denominators, powers and function arguments, confirms implicit products cannot be mistaken for named
quantities or units, checks definitions and units against primary sources, and confirms the "In words"
line says what the maths says.
