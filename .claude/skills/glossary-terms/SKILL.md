---
name: glossary-terms
description: Mandatory rules for adding glossary (dictionary) terms to cs-study-app. Use whenever writing or changing lessons or questions, and when auditing glossary coverage. Too many terms is better than too few; every technical word, acronym and unit a learner could trip over must have an entry.
---

# Glossary terms

A glossary term in the app is underlined in lessons and questions; tapping it opens a short definition. A term
the reader doesn't know and can't tap is a dead end. **Too many entries is better than too few. If in doubt, add
it.**

## Where terms live

Each module has its own `content/<subject>/<module>/glossary.json`. It is a JSON array:

```json
[
  {
    "id": "low-pass-filter",
    "term": "Low-pass filter",
    "aliases": ["low-pass filters", "lowpass filter", "LPF"],
    "definition": "A filter that lets frequencies below its cut-off through and progressively reduces frequencies above it. In a synth it is what makes a bright sawtooth sound darker.",
    "example": "Turning the cut-off of a low-pass filter down from 5 kHz to 500 Hz removes most of a sawtooth's upper harmonics.",
    "source": "https://en.wikipedia.org/wiki/Low-pass_filter"
  }
]
```

| Field | Required | Notes |
|---|---|---|
| `id` | yes | lowercase-kebab-case, unique across the whole app |
| `term` | yes | the display name, normally singular |
| `definition` | yes | see "Writing a definition" |
| `aliases` | no, but nearly always needed | see "Aliases" |
| `example` | no | encouraged: one concrete sentence with real numbers |
| `source` | no | encouraged: an https primary or authoritative source |
| `category` | no | defaults to the subject title |

The build compiles every module's file into `glossary-terms.js`. The original core list lives in
`glossary-data.js` (don't add to it; add to module files).

## What to include: everything a beginner might pause on

Read every lesson and every question in the module (prompts, options, explanations, worked examples). Add an
entry for each of these:

- **Acronyms and initialisms**, every one, including "obvious" ones: `USB`, `LED`, `DC`, `CPU`, `HTTP`, `MIDI`,
  `ADC`, `GPIO`, `TCP`, `JSON`. Give the expansion as the term or an alias.
- **Every bolded term.** Lessons bold a term where they introduce it, so each one needs an entry.
- **Technical nouns and named concepts**, e.g. "voltage divider", "sample rate", "Nyquist frequency", "cache
  line", "consistent hashing", "back-pressure", "decibel", "impedance".
- **Units and their symbols**: hertz (Hz), decibel (dB), dBu, dBV, ohm (Ω), farad (F), volt (V), ampere (A),
  watt (W), millisecond (ms), byte, bit.
- **Named components, chips, protocols, standards, algorithms, data structures, tools and products** the lesson
  relies on: `I²S`, `SPI`, `op-amp`, `Teensy`, `PCM5102`, `Raft`, `B-tree`, `Kafka`, `git rebase`.
- **Everyday words with a technical meaning here**, when the meaning differs: "voice" (synth), "envelope",
  "gate" (CV/gate), "partition", "shard", "commit", "ground".
- **Symbols' names** used in formulas that a reader may meet in prose: "pi (π)", "lambda (wavelength)".

The finder lists bolded terms and acronyms that have no entry yet:

```sh
node scripts/glossary-coverage.mjs content/<subject>/<module>
```

Treat its output as the **minimum**. Then read the lessons yourself for jargon it can't see (unbolded technical
nouns, units, verbs used technically).

Skip only:
- part designators and arbitrary labels (`R1`, `U2`, `ADC0` as a pin name)
- country codes and similar non-technical capitals (`UK`, `US`)

Say what you skipped in your report.

## Aliases: make sure the word in the text actually matches

- Matching is whole-word, longest phrase first.
- **Acronyms (2–7 capitals, e.g. `DAC`, `REST`) match exact case only**, so "PA" (public address) and "Pa"
  (pascal) can both exist.
- Everything else is case-insensitive.

Add an alias for every form the lessons use:
- **plurals**: "filters", "capacitors"
- **spelling variants**: analogue/analog, hyphenated/unhyphenated, "low pass" and "low-pass"
- **acronym ↔ expansion**: "ADC" and "analogue-to-digital converter"
- **common short forms**: "op-amp", "op amp", "operational amplifier"

**Scope (see `glossary-rules.js`).** Short aliases mean different things in different subjects, so a module term's
short aliases link **only inside its own subject**:
- acronyms;
- anything of 3 characters or fewer;
- anything containing a symbol or digit (`I²S`, `m/s`, `dB`).

So "DAC" can mean digital-to-analogue converter in Synth Building and discretionary access control in
Security. **Don't drop an acronym** because another subject uses it differently. Inside one subject, an alias
still maps to one entry.

**Multi-word and hyphenated phrases also act as a fallback in other subjects** that don't define them.
Single words link only inside their own subject. Even so:
- **Ambiguity.** When a word means different things in different subjects ("gate", "filter", "key", "voice",
  "bus", "transformer", "table", "flash", "bounce"), don't use the bare word as an alias. Use precise multi-word
  terms instead: "logic gate", "gate signal", "noise gate", "audio transformer", "switch bounce".
- Never alias an ordinary English word ("tries", "set", "note", "rest", "chain", "atomic", "poll") to a
  specialised term.

## Writing a definition

- **1–3 sentences in plain English**, readable on its own by someone new to the subject.
- **No undefined jargon.** If the definition needs another technical term, that term should have its own entry
  (it then links in the dictionary).
- Say **what it is, and why it matters or what it's used for** in this subject.
- **Real numbers and units** where they help: "typically 44.1 kHz or 48 kHz".
- **Accurate and sourced.** No invented figures. Hedge anything approximate ("about", "typically").
- British English.

## Clashes between modules

Ids must be unique app-wide; aliases must be unique within their scope (see above).

**Before adding a term, search for it**, and if it already exists, reuse it. It links everywhere automatically,
so don't duplicate it:

```sh
grep -ril '"<term>"' content/*/*/glossary.json glossary-data.js
```

If two modules still define the same word, the build keeps the entry from the **earlier module in curriculum
order**. It skips the later entry, or drops just the clashing alias, and reports it. So a term belongs in the
first module where a learner meets it.

## Verification (mandatory, as for lessons)

Every glossary entry is checked by the **independent verifier** like any other content (docs/CONTENT_PROCESS.md).
The verifier:
- checks each definition against a primary source;
- checks that the aliases don't collide with ordinary words or other meanings;
- records each term in the module's `verification.json`:

```json
"glossary": { "low-pass-filter": { "confidence": "high" } }
```

Then it runs `node scripts/stamp-verification.mjs content/<subject>/<module>`, which writes a hash for each term.
Editing a term after stamping fails the build until it is re-verified.
