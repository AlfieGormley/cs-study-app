# Formula and glossary retrofit: report (8–11 October 2026)

## What was asked

1. **Glossary:** "too many is better than too little". Every term a beginner could trip over should be
   underlined and defined, including in the synth lessons.
2. **Quiz:** make it obvious which answer was correct.
3. **Formulas:** give them their own writing skill. Explain every symbol, assuming the reader knows none.
   Apply this everywhere.

## What was done

**Tooling (commit 7ece17f and follow-ups)**

- **Formula blocks.** A ```` ```formula ```` block holds the equation, a "where" table and an "In words" line.
  The build rejects any block that leaves a symbol undefined, has no "In words" line, or defines a connective
  word as a symbol.
- **Per-module glossaries.** Each module has a `glossary.json`. Every term is verified and hash-stamped like a
  lesson.
- **Two mandatory skills:** `.claude/skills/writing-formulas` and `.claude/skills/glossary-terms`.
- **Support tools:** `scripts/lint-formulas.mjs`, `scripts/glossary-coverage.mjs` and
  `scripts/glossary-links.mjs`.
- **Quiz reveal.** The verdict names the correct answer. The correct option and the one you chose get ribbons,
  and the remaining options fold into "Why not".
- **Matching rules in `glossary-rules.js`**, tightened during the sweep:
  - A subject's own terms win inside that subject.
  - These match exact case only: acronyms, single capital letters (Δ ≠ δ), ALL-CAPS phrases (NOT IN, MUST NOT)
    and short mixed-case names (reST).
  - Only multi-word phrases fall back to other subjects. Phrases that start with an article or preposition, or
    end with a preposition, never do ("the stack", "in parallel", "multiple of").
  - A term never matches straight after a number and hyphen ("24-bit clock").
- **Renderer fix.** Text written on the same line as a closing ``` used to be dropped silently. It now shows
  as its own paragraph. This affected 17 question lines.

**Content (all 76 modules)**

- For each module, an author agent added formula blocks and wrote the glossary.
- A separate verifier agent then re-checked every formula and number and checked definitions against
  sources. It fixed what was wrong, recorded a "formula + glossary retrofit" revision in `verification.json`
  and stamped the module.
- A final reconciliation pass covered each subject. It:
  - narrowed or removed glossary aliases that opened the wrong definition in other modules or subjects;
  - broadened definitions that legitimately link from several places;
  - replaced the off-by-one phrase "2 multiplied by itself n times" (which literally means 2ⁿ⁺¹) with
    "n copies of 2 multiplied together" about 330 times.

  Each module this pass touched was re-verified and re-stamped.

## Totals

| | |
|---|---|
| Modules verified | 76 of 76 |
| Formula blocks | 5,158 |
| Glossary entries (module files) | 20,271. The build keeps 18,779 unique module terms plus 151 core terms. |
| Claims checked by retrofit verifiers | ≈ 22,200 |
| Errors corrected by retrofit verifiers | 1,360 |
| Further fixes in the reconciliation pass | ≈ 250 recorded, plus alias clean-up |
| Claims hedged or removed | 197 |
| Low-confidence items recorded (cumulative, including earlier audits) | 694 |

## Notable factual corrections (a selection)

- **Theory**
  - ⊢ was being used as "therefore".
  - DPLL authorship.
  - NaN comparisons.
  - HALT_ε "In words" was false.
  - Myhill–Nerode is 1957.
  - The coupon-collector note was 13 % low.
  - "BPP ⊆ P/poly" attribution.
  - "Sub-exponential" was defined backwards.
  - A metric TSP ratio.
- **Security**
  - Toy RSA forgery value: 5¹⁷ mod 3233 is 3086, not 3150.
  - Certificate lifetime is now 200 days, falling to 100 days and then 47.
  - ECH is RFC 9849.
  - CNSA 2.0 and NIST IR 8547 scope.
  - The HMAC ipad/opad rationale was presented as fact.
  - The GCM limit wording.
  - The COEP credentialless rule.
  - Safe methods include TRACE.
  - Log4j backport version.
  - EO 14028 wording.
  - The fstack-protector rule.
- **Databases**
  - The PostgreSQL 18 autovacuum insert and ANALYZE rules.
  - Loose index scan vs skip scan.
  - jsonb operator classes.
  - Generated columns: only STORED can be indexed.
  - ONLY_FULL_GROUP_BY arrived in MySQL 5.7.5.
  - AUTOINCREMENT reuse.
  - The relational algebra under bags and NULLs.
  - A false normal-form sentence.
- **Software Engineering**
  - Fowler's YAGNI costs.
  - stacklevel.
  - `from None` belongs to PEP 409/415.
  - The Bridge 2×2 example gives no saving.
  - PBKDF2 iterations.
  - The git bisect step count ("roughly 9 steps").
  - The SRE on-call rule.
  - Martin's instability counts classes.
- **Earlier subjects** (System Design, DSA, OS, Networks, Architecture, Languages, Synth): see each module's
  `verification.json` corrections list. Examples include MongoDB's 16 MiB limit, Hyrum's law and Postel
  misquotes, DCTCP g, AccECN (RFC 9768), PLT32, the Kubernetes oom_score_adj clamp and E12 rounding.

## Gaps and low-confidence areas

- **Glossary definitions not all fetched live.** API stalls cut several verifiers short. In Software
  Engineering 02, 03 and 04 most glossary definitions were checked by reading rather than by fetching every
  source; SE 04 marks about 240 Git/CI terms medium for this reason. In Databases 03 the bulk source-URL check
  timed out; the important sources were checked one by one.
- **Secondary sources only:**
  - CNSA 2.0 and NIST IR 8547 dates (the PDFs block automated fetches).
  - Birsan as the originator of "dependency confusion".
  - The Medium and O'Reilly pages behind some SE and Security terms.
- **Hedged estimates:**
  - Pollard's rho constant.
  - Shor resource estimates (pinned to Gidney 2025).
  - Some illustrative timings.
  - Example numbers labelled as made up, such as the SE 06 velocity history.
- **Lesson confidence:** most lessons stay at the medium confidence set by the earlier audit. Verifiers
  re-checked the retrofit changes, not every pre-existing sentence.
- **Lint hits.** `lint-formulas.mjs` is a heuristic and still reports hits. Verifiers judged the ones they
  reviewed as allowed Rule 6 exceptions: code, plain numeric statements, Big-O once n is defined, and symbols
  reused after their defining block. In the largest modules (DSA 01 reports about 550) not every hit was
  individually re-read.
- **Known minor link leaks left on purpose.** Removing these would cut many correct links. Examples:
  - "absolute maximum" (one wrong link in DSA);
  - "post-order" (one wrong link);
  - "shifting left" (one wrong link in DSA 10);
  - "per loop" (two wrong links outside Databases).
- **Duplicate ids.** Some duplicate ids remain within a subject (for example os-time-slice, cpu-quota and
  os-operating-system). The build resolves them by curriculum order; they are harmless but redundant.
- **Formula checker loophole.** A where-key such as `{o}` counts as defining `o`.

## Checks run (11 October 2026)

- **Full build:** `node scripts/build.mjs` passes ("content valid", 79 data files).
- **Tests:** 29 Node tests pass.
- **Links:** `scripts/check-links.mjs` covered 3,282 lesson URLs and 116 failed.
  - Rechecked one at a time: 20 return 200 directly. 27 GitHub pages that returned 503 from rate limiting
    exist (each confirmed via raw.githubusercontent.com).
  - Unreachable from this machine: 65 man7.org pages (connection fails here).
  - Bot-blocked here: 2 Cornell PDFs (421), 1 Infineon page (403) and 1 Zeek page (429).
- **390 px render:** every lesson (482) went through its real app route, and every question (5,565) through
  the quiz markup, in headless Chrome at 390 px. Before the fixes, three long identifiers in lessons and one
  long setting name in a formula's where-table pushed the page wider than the screen. The CSS fixes are: long
  inline code and dictionary terms wrap; where-table text wraps. After them, no page or question overflows and
  there are no JavaScript errors. The dictionary page is clean too.

## Per-module table

| Module | Formula blocks | Glossary terms | Claims checked | Errors fixed (retrofit) | Hedged | Fixed in reconciliation | Low-confidence items |
|---|---|---|---|---|---|---|---|
| system-design/01-fundamentals | 107 | 379 | 508 | 77 | 1 | 0 | 14 |
| system-design/02-networking | 61 | 433 | 540 | 13 | 14 | 0 | 10 |
| system-design/03-caching | 73 | 352 | 450 | 105 | 6 | 0 | 10 |
| system-design/04-databases | 53 | 309 | 380 | 14 | 15 | 0 | 12 |
| system-design/05-distributed-systems | 63 | 293 | 130 | 9 | 2 | 1 | 11 |
| system-design/06-messaging | 55 | 287 | 150 | 11 | 2 | 0 | 10 |
| system-design/07-api-design | 67 | 376 | 118 | 9 | 2 | 0 | 18 |
| system-design/08-architecture | 84 | 261 | 360 | 8 | 1 | 0 | 4 |
| system-design/09-reliability | 92 | 200 | 317 | 19 | 3 | 0 | 14 |
| system-design/10-case-studies-1 | 97 | 178 | 290 | 15 | 3 | 1 | 14 |
| system-design/11-case-studies-2 | 93 | 234 | 345 | 11 | 1 | 0 | 10 |
| dsa/01-complexity | 141 | 150 | 326 | 8 | 0 | 0 | 10 |
| dsa/02-linear | 43 | 292 | 96 | 8 | 3 | 0 | 3 |
| dsa/03-hashing | 90 | 158 | 280 | 11 | 2 | 0 | 7 |
| dsa/04-trees | 68 | 169 | 290 | 11 | 2 | 0 | 7 |
| dsa/05-sorting-searching | 93 | 192 | 330 | 10 | 1 | 0 | 2 |
| dsa/06-graphs | 111 | 169 | 352 | 9 | 3 | 0 | 5 |
| dsa/07-design-techniques | 75 | 133 | 262 | 31 | 3 | 0 | 3 |
| dsa/08-dynamic-programming | 128 | 155 | 340 | 29 | 2 | 0 | 4 |
| dsa/09-patterns | 73 | 99 | 215 | 13 | 3 | 0 | 4 |
| dsa/10-advanced | 123 | 144 | 310 | 15 | 3 | 0 | 9 |
| os/01-processes | 25 | 460 | 503 | 22 | 1 | 14 | 16 |
| os/02-threads-scheduling | 53 | 227 | 302 | 30 | 3 | 10 | 8 |
| os/03-synchronisation | 24 | 322 | 373 | 15 | 0 | 9 | 10 |
| os/04-deadlock | 32 | 164 | 118 | 12 | 1 | 2 | 12 |
| os/05-memory | 80 | 250 | 342 | 15 | 2 | 7 | 10 |
| os/06-file-systems | 46 | 336 | 422 | 13 | 3 | 9 | 8 |
| os/07-io | 29 | 356 | 420 | 18 | 1 | 4 | 17 |
| os/08-virtualisation | 33 | 509 | 96 | 11 | 1 | 5 | 15 |
| networks/01-foundations | 80 | 427 | 560 | 30 | 4 | 4 | 15 |
| networks/02-ip-routing | 54 | 430 | 560 | 32 | 3 | 35 | 4 |
| networks/03-tcp | 89 | 316 | 430 | 13 | 7 | 1 | 9 |
| networks/04-application | 65 | 620 | 310 | 34 | 0 | 19 | 10 |
| networks/05-network-security | 40 | 366 | 461 | 31 | 1 | 16 | 3 |
| networks/06-wireless-modern | 71 | 524 | 640 | 23 | 2 | 2 | 20 |
| architecture/01-data-representation | 58 | 391 | 482 | 8 | 0 | 14 | 9 |
| architecture/02-digital-logic | 116 | 252 | 420 | 13 | 4 | 11 | 9 |
| architecture/03-isa | 58 | 373 | 215 | 14 | 2 | 5 | 16 |
| architecture/04-pipelining | 65 | 180 | 275 | 33 | 3 | 3 | 11 |
| architecture/05-memory-hierarchy | 90 | 181 | 236 | 13 | 1 | 2 | 15 |
| architecture/06-parallelism | 72 | 202 | 486 | 12 | 1 | 6 | 8 |
| languages/01-paradigms | 19 | 444 | 118 | 10 | 3 | 0 | 25 |
| languages/02-types | 28 | 255 | 305 | 14 | 2 | 0 | 9 |
| languages/03-memory-management | 29 | 274 | 96 | 8 | 1 | 0 | 12 |
| languages/04-functional | 43 | 239 | 330 | 8 | 13 | 0 | 7 |
| languages/05-compilers | 36 | 287 | 362 | 41 | 0 | 0 | 10 |
| languages/06-concurrency-models | 16 | 254 | 292 | 20 | 0 | 0 | 11 |
| security/01-fundamentals | 13 | 405 | 96 | 40 | 2 | 0 | 8 |
| security/02-crypto-basics | 118 | 236 | 420 | 11 | 3 | 0 | 9 |
| security/03-applied-crypto | 49 | 259 | 340 | 16 | 0 | 0 | 9 |
| security/04-web-security | 7 | 209 | 72 | 21 | 0 | 0 | 11 |
| security/05-systems-security | 21 | 194 | 290 | 15 | 0 | 0 | 4 |
| security/06-security-practice | 13 | 247 | 96 | 9 | 3 | 0 | 7 |
| software-engineering/01-principles | 8 | 277 | 96 | 17 | 3 | 0 | 3 |
| software-engineering/02-design-patterns | 12 | 264 | 310 | 12 | 1 | 0 | 3 |
| software-engineering/03-testing | 15 | 187 | 48 | 9 | 3 | 0 | 3 |
| software-engineering/04-git-cicd | 15 | 272 | 64 | 5 | 2 | 5 | 2 |
| software-engineering/05-code-architecture | 9 | 165 | 48 | 6 | 1 | 6 | 2 |
| software-engineering/06-practices | 22 | 227 | 96 | 15 | 1 | 15 | 8 |
| theory/01-logic-proofs | 162 | 271 | 240 | 16 | 3 | 5 | 3 |
| theory/02-discrete-structures | 198 | 338 | 645 | 34 | 1 | 5 | 2 |
| theory/03-probability | 171 | 206 | 411 | 25 | 0 | 2 | 3 |
| theory/04-automata | 90 | 158 | 185 | 13 | 1 | 3 | 1 |
| theory/05-computability | 72 | 170 | 295 | 21 | 20 | 2 | 6 |
| theory/06-complexity | 174 | 246 | 430 | 17 | 3 | 5 | 5 |
| databases/01-sql-fundamentals | 30 | 263 | 340 | 14 | 0 | 0 | 8 |
| databases/02-advanced-sql | 52 | 134 | 213 | 15 | 1 | 0 | 8 |
| databases/03-relational-theory | 108 | 167 | 168 | 10 | 0 | 10 | 9 |
| databases/04-query-processing | 64 | 181 | 148 | 14 | 3 | 14 | 12 |
| databases/05-postgresql | 3 | 86 | 128 | 10 | 2 | 0 | 5 |
| synth/01-sound-sampling | 110 | 295 | 420 | 12 | 3 | 0 | 20 |
| synth/02-synthesis-dsp | 115 | 98 | 168 | 15 | 3 | 0 | 9 |
| synth/03-electronics | 69 | 174 | 262 | 15 | 1 | 0 | 15 |
| synth/04-embedded-audio | 66 | 362 | 140 | 10 | 0 | 0 | 10 |
| synth/05-midi-studio | 64 | 149 | 225 | 2 | 0 | 0 | 9 |
| synth/06-audio-engineering | 167 | 429 | 240 | 12 | 6 | 0 | 20 |
| **Total** | **5158** | **20271** | **22177** | **1360** | **197** | **252** | **694** |
