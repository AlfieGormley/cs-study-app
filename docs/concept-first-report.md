# Concept-first library review

Status: **in progress**. 15/60 modules and 254/1845 active lessons have current independent editorial reviews.

This report counts only active lesson IDs from module.json. Retired subjects (os, architecture, theory, languages; see `content/retired-subjects.json`) are excluded. Pending modules have not been certified by keyword scans or by renderer tests.

The rule for future content is in [the authoring brief](concept-first-brief.md), [CONTENT_SPEC.md](../CONTENT_SPEC.md) and [the content process](CONTENT_PROCESS.md). Essential relationships remain visible; selected reference maths opens on demand. Redundant equations and routine calculation questions are removed or rewritten around interpretation, prediction and diagnosis.

Comparison baseline: `5b8fb6f2709893396373ba979ba194aacf5cb034`. Lesson IDs, question IDs and question ownership must match this baseline. Archived originals and progress migrations remain unchanged.

Focused dictionary integration corrections and exact-definition equivalence reviews are recorded in [the integration review](concept-first-integration-review.json). A focused glossary correction does not count as a completed module rewrite. Reviewer records retain checks that were pending at handoff; subsequent compiled-check closure is recorded separately in the integration report.

“Review units” below retain each independent reviewer’s stated counting method. Some are grouped claim sets, not atomic assertions; counts must not be compared as a quality score. The linked verification records preserve earlier factual/glossary history and define the fresh review scope.

| Module | Status | Lessons | Questions | Lesson formula cards before → after | Essential / reference | Question cards before → after | Glossary terms | Review units | Corrections |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| databases / SQL Fundamentals | Pending review | 40 | — | — | — | — | — | — | — |
| databases / Advanced SQL | Pending review | 41 | — | — | — | — | — | — | — |
| databases / Relational Theory & Normalisation | Pending review | 35 | — | — | — | — | — | — | — |
| databases / Query Processing & Optimisation | Pending review | 33 | — | — | — | — | — | — | — |
| databases / PostgreSQL | Pending review | 13 | — | — | — | — | — | — | — |
| [dsa / Complexity Analysis](../content/dsa/01-complexity/verification.json) | Reviewed | 35 | 81 | 79 → 17 | 13 / 4 | 211 → 14 | 150 | 181 | 24 |
| dsa / Arrays, Lists, Stacks & Queues | Pending review | 32 | — | — | — | — | — | — | — |
| dsa / Hash Tables & Hashing | Pending review | 37 | — | — | — | — | — | — | — |
| dsa / Trees & Heaps | Pending review | 35 | — | — | — | — | — | — | — |
| dsa / Sorting & Searching | Pending review | 46 | — | — | — | — | — | — | — |
| dsa / Graphs | Pending review | 37 | — | — | — | — | — | — | — |
| dsa / Recursion, Backtracking & Greedy | Pending review | 40 | — | — | — | — | — | — | — |
| dsa / Dynamic Programming | Pending review | 46 | — | — | — | — | — | — | — |
| dsa / Problem-Solving Patterns | Pending review | 42 | — | — | — | — | — | — | — |
| dsa / Advanced Structures & Algorithms | Pending review | 49 | — | — | — | — | — | — | — |
| [dsp / Samples, Signals and Levels](../content/dsp/01-signals/verification.json) | Reviewed | 9 | 27 | 16 → 7 | 1 / 6 | 12 → 0 | 69 | 142 | 2 |
| [dsp / Systems, Convolution and Filters](../content/dsp/02-filters/verification.json) | Reviewed | 9 | 27 | 10 → 5 | 0 / 5 | 11 → 0 | 55 | 105 | 5 |
| [dsp / Fourier Analysis and Practical DSP](../content/dsp/03-spectra/verification.json) | Reviewed | 9 | 27 | 13 → 7 | 2 / 5 | 10 → 0 | 42 | 83 | 3 |
| [embedded / Firmware and Microcontroller Foundations](../content/embedded/01-foundations/verification.json) | Reviewed | 6 | 18 | 0 → 0 | 0 / 0 | 0 → 0 | 55 | 96 | 9 |
| [embedded / C and Device I/O](../content/embedded/02-c-and-io/verification.json) | Reviewed | 8 | 16 | 3 → 2 | 0 / 2 | 2 → 0 | 88 | 54 | 7 |
| [embedded / Timing, Interrupts & Serial Buses](../content/embedded/03-timing-and-buses/verification.json) | Reviewed | 6 | 18 | 1 → 1 | 0 / 1 | 1 → 0 | 54 | 173 | 2 |
| [embedded / Debugging, Reliability & First Projects](../content/embedded/04-debugging-and-projects/verification.json) | Reviewed | 6 | 18 | 0 → 0 | 0 / 0 | 0 → 0 | 36 | 90 | 2 |
| [networks / Network Foundations & the Link Layer](../content/networks/01-foundations/verification.json) | Reviewed | 37 | 72 | 47 → 19 | 0 / 19 | 34 → 0 | 433 | 139 | 2 |
| networks / IP, Addressing & Routing | Pending review | 38 | — | — | — | — | — | — | — |
| networks / Transport Layer: TCP & UDP in Depth | Pending review | 43 | — | — | — | — | — | — | — |
| networks / Application-Layer Protocols | Pending review | 42 | — | — | — | — | — | — | — |
| networks / Network Security | Pending review | 36 | — | — | — | — | — | — | — |
| networks / Wireless, Mobile & Modern Networks | Pending review | 37 | — | — | — | — | — | — | — |
| [react / Components and JSX](../content/react/01-components/verification.json) | Reviewed | 8 | 24 | 0 → 0 | 0 / 0 | 0 → 0 | 70 | 102 | 4 |
| [react / State and Interactive Forms](../content/react/02-state/verification.json) | Reviewed | 9 | 27 | 0 → 0 | 0 / 0 | 0 → 0 | 44 | 80 | 4 |
| [react / Hooks, Effects and Shared Logic](../content/react/03-hooks/verification.json) | Reviewed | 9 | 27 | 0 → 0 | 0 / 0 | 0 → 0 | 52 | 94 | 3 |
| security / Security Fundamentals | Pending review | 27 | — | — | — | — | — | — | — |
| security / Cryptography Basics | Pending review | 37 | — | — | — | — | — | — | — |
| security / Applied Cryptography & PKI | Pending review | 39 | — | — | — | — | — | — | — |
| security / Web Application Security | Pending review | 14 | — | — | — | — | — | — | — |
| security / Systems Security | Pending review | 15 | — | — | — | — | — | — | — |
| security / Security Engineering in Practice | Pending review | 23 | — | — | — | — | — | — | — |
| software-engineering / Design Principles & Clean Code | Pending review | 26 | — | — | — | — | — | — | — |
| software-engineering / Design Patterns | Pending review | 28 | — | — | — | — | — | — | — |
| software-engineering / Testing | Pending review | 22 | — | — | — | — | — | — | — |
| software-engineering / Version Control & CI/CD | Pending review | 26 | — | — | — | — | — | — | — |
| software-engineering / Software Architecture at the Code Level | Pending review | 25 | — | — | — | — | — | — | — |
| software-engineering / Engineering Practices | Pending review | 24 | — | — | — | — | — | — | — |
| [synth / Sound & Digital Audio](../content/synth/01-sound-sampling/verification.json) | Reviewed | 32 | 69 | 52 → 23 | 1 / 22 | 60 → 0 | 297 | 128 | 24 |
| [synth / Synthesis & DSP](../content/synth/02-synthesis-dsp/verification.json) | Reviewed | 44 | 82 | 56 → 18 | 4 / 14 | 60 → 0 | 112 | 234 | 18 |
| synth / Electronics for Synth Builders | Pending review | 39 | — | — | — | — | — | — | — |
| synth / Embedded Audio & Interfaces | Pending review | 44 | — | — | — | — | — | — | — |
| synth / MIDI & Studio Integration | Pending review | 44 | — | — | — | — | — | — | — |
| synth / Audio Engineering | Pending review | 50 | — | — | — | — | — | — | — |
| [system-design / Fundamentals](../content/system-design/01-fundamentals/verification.json) | Reviewed | 27 | 84 | 42 → 12 | 0 / 12 | 65 → 0 | 379 | 130 | 23 |
| system-design / Networking & Traffic | Pending review | 34 | — | — | — | — | — | — | — |
| system-design / Caching | Pending review | 39 | — | — | — | — | — | — | — |
| system-design / Databases & Storage | Pending review | 37 | — | — | — | — | — | — | — |
| system-design / Distributed Systems & Consensus | Pending review | 40 | — | — | — | — | — | — | — |
| system-design / Messaging & Streaming | Pending review | 34 | — | — | — | — | — | — | — |
| system-design / API Design | Pending review | 38 | — | — | — | — | — | — | — |
| system-design / Architecture & Scaling Patterns | Pending review | 41 | — | — | — | — | — | — | — |
| system-design / Reliability, Operations & Security | Pending review | 38 | — | — | — | — | — | — | — |
| system-design / Case Studies I | Pending review | 43 | — | — | — | — | — | — | — |
| system-design / Case Studies II | Pending review | 42 | — | — | — | — | — | — | — |

The report certifies editorial provenance only. Build, migration, rendering, offline and deployed-version evidence must be checked separately before publication.

## dsa / Complexity Analysis

81 question objects changed. Every changed question has a specific independent-review reason in the linked record.

**Corrections in this review:**

- Removed universal20–40 exponential feasibility threshold; hardware statements explicitly conditional on candidate/check cost and budget.
- Removed nonstandard total-problem terminology; preserved glossary ID but replaced display label with Termination guarantee.
- Corrected streaming total space, generator memory, word-RAM width and reallocation assumptions.
- Removed cache-aware alias from cache-oblivious and binary-insertion-sort alias from ordinary insertion sort.
- Removed stale matrix exponent record and blanket never-practical claim; BLAS interface no longer mandates cubic algorithm.
- Added exact Master power-gap/log-extension/regularity and Akra polynomial-growth conditions outside reference card.
- Selection recurrence is a worst-case upper bound with rounding, not an exact equality.
- Binary counter starts zero, array potential starts capacityzero, and aggregate examples state starting state.
- Removed unsupported throughput models and hardware/cache ratios; retained the distinction between incident-specific evidence and general exponential backtracking after the independent correction below.
- Fixed dangling removed-card references, numeric crossover residue, and binary insertion comparison/move distinction.
- Induction question cx-recurrences-q11 had a second true distractor about a missing base case; changed it to claim this is the only flaw and would repair the proof.
- Added constant-cost work/arithmetic assumptions to the standalone nested-loop, geometric-loop, harmonic-loop and recurrence-from-code prompts.
- CPython operation question now explicitly requests amortised end-pop cost and worst-case costs for the other operations, removing an ambiguous selection contract.
- Scoped the merge-sort space distractor to standard array merge sort so specialised in-place merge methods do not make the blanket wording defensible.
- Defined Phi as stored potential in the standalone potential-method question.
- Replaced dangling c in simplification feedback with fixed bound multipliers after the original defining arithmetic had been removed.
- Defined n and the logarithm locally in the operation-budget question.
- Removed the unsupported exact quadratic classification of the2019 Cloudflare outage; primary report establishes excessive backtracking/CPU exhaustion and does not justify one universal degree for all search inputs.
- Qualified the basic-operation glossary example: fixed-size inputs alone do not guarantee a fixed-size running total.
- Replaced blur-filter glossary source with official OpenCV neighbourhood/kernel documentation; the introductory algorithm chapter did not substantiate that definition.
- Replaced insertion-sort glossary source with the actual Princeton textbook section covering ordinary versus binary insertion comparisons/moves.
- Replaced two-pointer glossary source with MIT k-SUM lecture material proving the bounded monotonic scans.
- Replaced galactic-algorithm glossary source with a primary researcher article that actually explains this informal usage.
- Rephrased child-cost prose to avoid recursive-term opening an unrelated recursive-SQL dictionary entry.

**Scope gaps and exclusions:**

- Universal cross-language speed ratios and memory latency figures lack reproducible measurements and are explicitly omitted.
- No benchmark-derived crossover recommendation for a particular deployment.
- Code execution uses small representative inputs and explicit harness assumptions; it is not a proof for arbitrary inputs.
- The35 units preserve the depth of the seven originals. Two naturally small units retain honest two-minute estimates;33 units use three-to-five-minute estimates. Some focused units have one question rather than padding them with unrelated questions.
- No target-machine benchmark or universal deadline/feasibility cutoff is supplied; practical claims are conditional and recommend measurement.
- Full arbitrary Akra–Bazzi perturbation proof is linked rather than taught; visible exact-fraction assumptions and the examples remain complete.
- Unchanged historical glossary provenance is retained; this pass does not assert a fresh primary-source citation for every unchanged dictionary sentence.

**Low-confidence areas, including preserved qualifications:**

- medium confidence, cx-growth-rates: Version- and implementation-sensitive runtime details or illustrative cost assumptions Core asymptotic reasoning checked against teaching sources and code/counts recomputed. Implementation details are qualified and valid only for the cited builds/model; this record does not assert a primary source individually attached to every retained sentence.
- medium confidence, cx-asymptotic-notation: Version- and implementation-sensitive runtime details or illustrative cost assumptions Core asymptotic reasoning checked against teaching sources and code/counts recomputed. Implementation details are qualified and valid only for the cited builds/model; this record does not assert a primary source individually attached to every retained sentence.
- medium confidence, cx-analysing-code: Version- and implementation-sensitive runtime details or illustrative cost assumptions Core asymptotic reasoning checked against teaching sources and code/counts recomputed. Implementation details are qualified and valid only for the cited builds/model; this record does not assert a primary source individually attached to every retained sentence.
- medium confidence, cx-space-complexity: Version- and implementation-sensitive runtime details or illustrative cost assumptions Core asymptotic reasoning checked against teaching sources and code/counts recomputed. Implementation details are qualified and valid only for the cited builds/model; this record does not assert a primary source individually attached to every retained sentence.
- medium confidence, cx-amortised-analysis: Version- and implementation-sensitive runtime details or illustrative cost assumptions Core asymptotic reasoning checked against teaching sources and code/counts recomputed. Implementation details are qualified and valid only for the cited builds/model; this record does not assert a primary source individually attached to every retained sentence.
- medium confidence, cx-recurrences: Version- and implementation-sensitive runtime details or illustrative cost assumptions Core asymptotic reasoning checked against teaching sources and code/counts recomputed. Implementation details are qualified and valid only for the cited builds/model; this record does not assert a primary source individually attached to every retained sentence.
- medium confidence, cx-in-practice: Version- and implementation-sensitive runtime details or illustrative cost assumptions Core asymptotic reasoning checked against teaching sources and code/counts recomputed. Implementation details are qualified and valid only for the cited builds/model; this record does not assert a primary source individually attached to every retained sentence.
- medium confidence, cx-growth-rates: Glossary term 'Total problem' (used in the lesson's definition of an algorithm) retrofit: 'total problem' is not a standard textbook term; the definition is a reasonable reading by analogy with total vs partial functions (Wikipedia: Partial function), but no primary algorithms text defines it this way.
- medium confidence, cx-space-complexity: Glossary alias 'two pointers' now resolves DSA-wide to the general two-pointer-technique entry (overriding dsa/02's fast/slow entry) retrofit: the definition now covers both opposite-ends and same-direction (fast/slow) variants, so dsa/02 and dsa/09 uses read correctly; but several DSA lessons use 'two pointers' literally (e.g. 'one or two pointers plus allocator bookkeeping' in dsa/02, 'only two pointers are stored' in dsa/04), which will also link. Those modules are outside this verifier's scope.
- medium confidence, cx-growth-rates: Glossary 'Exponential time': practical only up to about n = 20 to 40 for 2^n retrofit: an order-of-magnitude rule of thumb consistent with the lesson's 10^8 ops/s model (2^25 to 2^35 steps), not a sourced figure.
- medium confidence, cx-counting-work: Inherited nonstandard total-problem glossary terminology Core algorithm properties are primary-source checked. The unchanged glossary term still lacks a primary algorithms textbook definition, as the inherited record honestly states.
- medium confidence, cx-recursive-hidden-work: Simplified costs for CPython operations Current implementation is fetched and examples run. Counts assume bounded-value or constant-cost comparisons/hash operations and describe this cost model; arbitrary user objects or large integers require separate analysis.
- medium confidence, cx-recursion-memory: CPython recursion limit and atomic-number space model Current source defines1000 and the independent local Python3.14.4 run observed1000. Builds and user configuration can differ; whole-number bit storage is explicitly treated separately.
- medium confidence, cx-in-place-memory: Implementation-specific list-sort auxiliary allocation Current CPython listsort primary source supports up to half-list temporary pointers; it is an implementation statement, not a permanent Python-language guarantee.
- medium confidence, cx-memory-tradeoffs: Typical64-bit CPython object sizes and packed-buffer memory budgets The text is qualified and asks the reader to measure their build. This run observes28-byte int(1); 80/360MB arithmetic is recomputed, but allocator, value magnitude and construction overhead depend on the deployment.
- medium confidence, cx-resizing-policies: CPython/OpenJDK/libstdc++ growth factors Fetched current implementation sources support the qualified factors. These are version-sensitive implementation details; Rust documents no particular factor guarantee.
- medium confidence, cx-amortised-latency: Resize latency and Redis incremental-rehash implementation The data movement model and current Redis source are checked. The module does not claim a reproducible latency distribution or promise that every incremental step has a fixed wall-clock bound.
- medium confidence, cx-constants-locality: Practical performance ratios, sorting/multiplication crossover and cache-line assumptions Algorithm and implementation structure are source-checked; the preserved qualitative several-times performance language has no reproducible target-specific benchmark.64-byte lines and8-byte elements are explicit illustrative assumptions where calculations depend on them.
- medium confidence, cx-measuring-algorithms: Historical Knuth quotation and deployment-specific timing interpretation timeit measurement guidance is fetched and ratios recomputed. The original quotation attribution is retained but its primary paper was inaccessible through the web tool; the citation is not upgraded to high confidence.
- medium confidence, cx-recursive-hidden-work: Runtime-specific implementation and practical performance scope Core mechanism, cited implementation/API and model arithmetic are verified. CPython3.14 branches, configured recursion limits, allocation, cache effects and target timing can vary; visible text preserves their scope and no target performance guarantee is asserted.
- medium confidence, cx-recursion-memory: Runtime-specific implementation and practical performance scope Core mechanism, cited implementation/API and model arithmetic are verified. CPython3.14 branches, configured recursion limits, allocation, cache effects and target timing can vary; visible text preserves their scope and no target performance guarantee is asserted.
- medium confidence, cx-in-place-memory: Runtime-specific implementation and practical performance scope Core mechanism, cited implementation/API and model arithmetic are verified. CPython3.14 branches, configured recursion limits, allocation, cache effects and target timing can vary; visible text preserves their scope and no target performance guarantee is asserted.
- medium confidence, cx-memory-tradeoffs: Runtime-specific implementation and practical performance scope Core mechanism, cited implementation/API and model arithmetic are verified. CPython3.14 branches, configured recursion limits, allocation, cache effects and target timing can vary; visible text preserves their scope and no target performance guarantee is asserted.
- medium confidence, cx-aggregate-appends: Runtime-specific implementation and practical performance scope Core mechanism, cited implementation/API and model arithmetic are verified. CPython3.14 branches, configured recursion limits, allocation, cache effects and target timing can vary; visible text preserves their scope and no target performance guarantee is asserted.
- medium confidence, cx-resizing-policies: Runtime-specific implementation and practical performance scope Core mechanism, cited implementation/API and model arithmetic are verified. CPython3.14 branches, configured recursion limits, allocation, cache effects and target timing can vary; visible text preserves their scope and no target performance guarantee is asserted.
- medium confidence, cx-amortised-latency: Runtime-specific implementation and practical performance scope Core mechanism, cited implementation/API and model arithmetic are verified. CPython3.14 branches, configured recursion limits, allocation, cache effects and target timing can vary; visible text preserves their scope and no target performance guarantee is asserted.
- medium confidence, cx-constants-locality: Runtime-specific implementation and practical performance scope Core mechanism, cited implementation/API and model arithmetic are verified. CPython3.14 branches, configured recursion limits, allocation, cache effects and target timing can vary; visible text preserves their scope and no target performance guarantee is asserted.
- medium confidence, cx-measuring-algorithms: Runtime-specific implementation and practical performance scope Core mechanism, cited implementation/API and model arithmetic are verified. CPython3.14 branches, configured recursion limits, allocation, cache effects and target timing can vary; visible text preserves their scope and no target performance guarantee is asserted.
- medium confidence, cx-memory-tradeoffs: Historical two pointers alias can match a literal two-pointer count in another DSA module The corrected definition covers opposite-end and monotonic-window patterns; the existing broad alias remains because other modules use it. Those other modules require their own semantic rendering review; prior qualification is preserved.


## dsp / Samples, Signals and Levels

14 question objects changed. Every changed question has a specific independent-review reason in the linked record.

**Corrections in this review:**

- Rephrased four recorded instants in the timing lesson: the phrase four timestamps automatically opened an unrelated NTP-exchange definition.
- Replaced signed values with positive and negative values in RMS question feedback: the old phrase automatically opened a signed-integer definition although the lesson permits real-valued samples.

**Scope gaps and exclusions:**

- Fractional-delay design, converter hardware coding, dither/quantisation-noise statistics and full reconstruction proofs remain outside this introductory scope.
- Correlation normalisation is intentionally not specified as one algorithm: overlap, mean removal and zero-energy policies must be chosen before implementation.
- Complex multiplication/exponential notation and a general repeated-folding algorithm are deferred; neither is a prerequisite for the retained objectives or questions.

**Low-confidence areas, including preserved qualifications:**

None recorded in this editorial review.


## dsp / Systems, Convolution and Filters

16 question objects changed. Every changed question has a specific independent-review reason in the linked record.

**Corrections in this review:**

- Replaced the frequency-response further-reading URL labelled steady sinusoidal response, which actually opened a general appendix introduction, with Smith's Finding the Frequency Response. Used the directly supporting source for its first question and three relevant glossary source fields.
- Replaced the block-duration/latency question's unrelated SciPy filtering source with PortAudio's callback-period and latency guidance.
- Added the missing response-zero dictionary definition and precise plural aliases, including the undefined-phase qualification.
- Replaced the ambiguous bold term memory with filter memory and added its precise signal-history dictionary entry.
- Removed the stale glossary wording that described an integer-wraparound code demonstration no longer present; retained and independently recomputed the numerical example.

**Scope gaps and exclusions:**

- General high-order pole/zero design, fixed-point implementation, exhaustive band-extremum certification and production audio callbacks remain beyond these introductory objectives.
- The FIR unit teaches a specification/inspect/revise workflow; it does not provide a certified full-band design or device deadline guarantee.

**Low-confidence areas, including preserved qualifications:**

None recorded in this editorial review.


## dsp / Fourier Analysis and Practical DSP

11 question objects changed. Every changed question has a specific independent-review reason in the linked record.

**Corrections in this review:**

- STFT q1 repeated q2’s hop-only scenario. It now independently tests the frame-duration time/frequency trade-off, retaining q1 and its answer index.
- The ordinary rhythm action Tap/taps opened the FIR-tap dictionary entry. Clapping preserves the same analogy mapping without the incorrect term annotation.
- Spectrogram prose used vertical scaling, which linked to server scaling. It now says strength normalisation, preserving the spectral meaning without the unrelated dictionary definition.

**Scope gaps and exclusions:**

- Implementation listings and long derivations are intentionally linked instead of reproduced. The project provides an experiment contract and checked expected results, not a copy-and-run program.
- Welch variance, equivalent-noise-bandwidth derivations, production resampling stopband design and streaming performance benchmarks remain outside this introductory module.
- Synthetic acceleration checks do not validate a physical sensor, its clock, drift, environmental noise, uncertainty budget or hardware timing.

**Low-confidence areas, including preserved qualifications:**

None recorded in this editorial review.


## embedded / Firmware and Microcontroller Foundations

3 question objects changed. Every changed question has a specific independent-review reason in the linked record.

**Corrections in this review:**

- Changed response time to response deadline in esb-what-embedded-q3 feedback so the requirement does not open the CPU-scheduler response-time sense.
- Changed initial values to specified starting values in C startup prose, avoiding an unrelated React state definition.
- Replaced memory layout/logical errors in the instruction-pack limitation and firmware-image definition with code and data locations/decision bugs. Independently caught that the author replacement device memory opened a device-register definition.
- Rephrased the loop analogy response-time limit to how soon work will finish, avoiding a timeout definition while retaining the absence of a timing guarantee.
- Replaced startup code with startup support/routines in relevant prose, a distractor and the bare-metal definition to avoid a shared definition that universalises the first code after reset and main sequence.
- Used the literal main identifier in the startup question and C-runtime definition to avoid the hosted-process main-function definition and its exit/thread claims.
- Used Pico SDK and original Pico in narrative prose instead of Raspberry Pi, whose cross-subject dictionary entry describes Linux single-board computers; manufacturer source-link attribution is retained.
- Clarified the State machine glossary definition to allow a transition back to the same state, consistent with the existing State transition definition and the primary state-machine specification.
- Replaced the Press event glossary source: a blink implementation contains no button event handling; the fetched QP event conceptual model supports discrete occurrences versus persistent conditions.

**Scope gaps and exclusions:**

- No physical board, electrical behavior, flash operation or worst-case timing was tested; the module claims only source-checked device examples and host decision-model checks.
- Compiler installation and commands remain board-specific; the original Pico BOOTSEL/UF2 route is a documented illustration, not a universal flashing procedure.
- Executable C teaching belongs to module 2; foundations deliberately uses one labeled pseudocode loop. Production bootloaders, linker scripts and retention implementation are outside the agreed introductory scope.
- C11 N1570 downloaded successfully and link checked; web PDF extraction timed out. The generic C startup/static-duration clauses were independently read in the fetched WG14 N3096 draft 5.1.2/5.1.2.1, corroborated by CMSIS and host C11 experiments. No version-specific new C claim was introduced.

**Low-confidence areas, including preserved qualifications:**

None recorded in this editorial review.


## embedded / C and Device I/O

7 question objects changed. Every changed question has a specific independent-review reason in the linked record.

**Corrections in this review:**

- Author added local non-null-pointer, C array-index and timer-counting-mode meanings so the module does not open SQL nullability, React indexing or cryptographic counter-mode definitions; independently checked against N1570 and the Pico SDK 2.2.0 PWM header.
- Verifier corrected the pointer introduction and existing object-pointer definition: a pointer can be null or one past an array, so existence of a pointer does not imply an accessible object (N1570 6.3.2.3 and 6.5.6).
- Verifier added a fixed-size-buffer definition to prevent the memory lesson opening the unrelated io_uring registered-buffer entry.
- Verifier added a sample-index definition that does not assume a regular sampling interval, matching the debounce lesson’s explicit schedule dependence.
- Verifier made the SDK prose name RP2040 explicitly to avoid the Raspberry Pi dictionary sense for Linux single-board computers.

**Scope gaps and exclusions:**

- No physical switch, board, ADC source or load was tested. Actual voltage limits, acquisition, bounce timing, peripheral routing and output behaviour remain device/circuit dependent as stated in the lessons.
- This pass used strict optimised hosted C execution and behavioural probes, without sanitizer execution. The author reported sanitizer startup hangs; no new ASan or UBSan success is claimed.
- Browser rendering, offline behaviour and actual generated dictionary lookups are assigned to root integration; this record covers source semantics, source glossary matches and scoped validation.
- Calibration, detailed analogue acquisition design, load drivers, dynamic allocation and concurrency implementation remain outside the intended eight beginner lessons.

**Low-confidence areas, including preserved qualifications:**

None recorded in this editorial review.


## embedded / Timing, Interrupts & Serial Buses

4 question objects changed. Every changed question has a specific independent-review reason in the linked record.

**Corrections in this review:**

- The lesson phrase processor exception resolved to an OS definition limited to instruction-caused faults. Added the embedded Cortex-M exception meaning, including device interrupts, with a local alias; preserved all existing glossary IDs.
- Setup and hold time cited the SPI API header, which does not explain its timing margins. Replaced its source with the RP2040 datasheet sections describing sampling and selection setup/hold requirements.

**Scope gaps and exclusions:**

- No real RP2040 execution, ISR installation/acknowledgement, measured interrupt latency, DMA concurrency or electrical waveform tests. Host models validate C logic and saved-state behavior only; SDK instructions and hardware claims were source-reviewed.
- Fictional I2C/SPI examples deliberately provide their own command contracts. Actual sensor registers, resistor sizing, multiple-controller arbitration and production bus recovery remain outside this introductory scope.
- The UART lesson explains bounded partial parsing and resynchronisation policy without implementing a production parser; specific error recovery and throughput must be designed for the actual application.
- Renderer, iPhone layout and offline checks are delegated to root integration; this record claims source/content and scoped build verification only.

**Low-confidence areas, including preserved qualifications:**

None recorded in this editorial review.


## embedded / Debugging, Reliability & First Projects

2 question objects changed. Every changed question has a specific independent-review reason in the linked record.

**Corrections in this review:**

- esr-sensor-state-machine-q2 feedback: fault path → FAULT state, avoiding an unrelated OS page-fault dictionary meaning while retaining the same diagnosis and answer.
- esr-project-workflow-q2 feedback: controlled input → known test reading, avoiding an unrelated React controlled-input dictionary meaning while retaining the same acceptance-test reasoning.

**Scope gaps and exclusions:**

- No physical board, sensor, output wiring, watchdog, reset circuitry, timing instrument or actual FreeRTOS port executed. Host tests establish exercised policy, not target timing/electrical reliability.
- Board adapter remains clearly labelled integration pseudocode. Choosing a real board/sensor still requires documented acquisition/decoding/timeout resolution/output mapping and separate hardware observations.
- Health/degraded-operation policy is a deliberately constructed course example; no general safety, timing or recovery guarantee is inferred from a watchdog refresh.
- Advanced bootloaders, updates, power characterization, production recovery, safety certification and full timing proof remain outside the introductory brief.
- No physical board, sensor, debug probe, watchdog/reset circuit or FreeRTOS port was executed. Host programs and abstract policy traces do not establish electrical behaviour, hardware timing or target reliability.
- Board adapter remains deliberately labelled pseudocode; a real target still needs its documented completion/deadline resolution, decoding/output mapping and integration checks.
- Advanced schedulability proofs, production fault safety, bootloaders, updates and power characterisation remain outside this introductory module.
- Whole-app rendering, mobile/offline integration and full-library stale-hash resolution are delegated to the root integration pass.

**Low-confidence areas, including preserved qualifications:**

None recorded in this editorial review.


## networks / Network Foundations & the Link Layer

39 question objects changed. Every changed question has a specific independent-review reason in the linked record.

**Corrections in this review:**

- FCS glossary example implied every damaged frame necessarily fails CRC; now states conditional mismatch detection and acknowledges undetected patterns (factual correction).
- Backoff reference lacked explicit units on both time quantities; both now specify seconds.
- Fibre lesson retained a dangling calculation lead-in and repeated multiplication; now states the result and multiplicative power interpretation directly.
- Pipeline example ended in a colon left by a removed substitution; now reads as a complete explanation.
- Wire-efficiency definition now uses the precise existing glossary term Link efficiency.
- MIT glossary entry referred to an approximate Go-Back-N formula removed in this rewrite; now describes the university and its coding/ARQ teaching materials.
- The packet-pipeline table was marked as an explicit diagram unsupported by the compiler; converted it to a four-column Markdown table and made zero propagation/processing assumptions explicit.

**Scope gaps and exclusions:**

- No physical Ethernet, optical or Wi-Fi equipment was measured; duplex, switching, STP, radio and failover behaviour is explained from protocol/configuration sources, not a universal measured outcome.
- Python snippets are bounded educational models, not complete frame/VLAN/FCS parsers, production switches or ARQ stacks.
- Ancillary inherited glossary entries supported by secondary references are explicitly medium confidence. Their definitions and aliases were independently reviewed, but family-source coverage is not a claim of primary verification of each historical/product statement.
- Queueing, independent-bit-error, propagation and ARQ timing models retain ideal assumptions; no general measured-network throughput guarantee is made.
- No new physical-network measurements. Browser/mobile/offline integration checks are delegated to the root integration pass.

**Low-confidence areas, including preserved qualifications:**

- medium confidence, nf-copper-wireless: Protocol and model reasoning is checked; vendor/OS behaviour, hardware examples and ancillary historical details require the stated configuration or remain supported by secondary references. No physical equipment or production deployment was exercised; explicit ideal-model assumptions and product snapshots are retained.
- medium confidence, nf-fibre-power-speed: Protocol and model reasoning is checked; vendor/OS behaviour, hardware examples and ancillary historical details require the stated configuration or remain supported by secondary references. No physical equipment or production deployment was exercised; explicit ideal-model assumptions and product snapshots are retained.
- medium confidence, nf-shared-ethernet: Protocol and model reasoning is checked; vendor/OS behaviour, hardware examples and ancillary historical details require the stated configuration or remain supported by secondary references. No physical equipment or production deployment was exercised; explicit ideal-model assumptions and product snapshots are retained.
- medium confidence, nf-arp-cache-failover: Protocol and model reasoning is checked; vendor/OS behaviour, hardware examples and ancillary historical details require the stated configuration or remain supported by secondary references. No physical equipment or production deployment was exercised; explicit ideal-model assumptions and product snapshots are retained.
- medium confidence, nf-stp-recovery: Protocol and model reasoning is checked; vendor/OS behaviour, hardware examples and ancillary historical details require the stated configuration or remain supported by secondary references. No physical equipment or production deployment was exercised; explicit ideal-model assumptions and product snapshots are retained.


## react / Components and JSX

0 question objects changed. Every changed question has a specific independent-review reason in the linked record.

**Corrections in this review:**

- Author corrected DOM definition to distinguish the whole tree from individual element/text nodes; independently corroborated against MDN and the Notice DOM.
- Author extended the parent component definition to explain its linked DOM parent-node meaning.
- Author extended the child component definition to explain its linked DOM child-node meaning while keeping the children prop distinct.
- Author renamed the list-key heading to stable React key so it no longer opens an unrelated Function identity definition.

**Scope gaps and exclusions:**

- No missing objective found in the scoped components/JSX module. It assumes basic JavaScript and a prepared React-enabled project, as the subject brief requires.
- Project setup, root bootstrap instructions and full JavaScript/CSS instruction are intentionally outside scope; state queues/forms and effects/context belong to the following modules.
- Component behaviour was mounted with React 19.3.1 and jsdom; physical-browser layout, installed-app/offline behaviour and existing-progress checks remain root integration work.
- Project installation, advanced state queues/reset rules, and Effects are deliberately deferred by the lessons; no unmet prerequisite found for these 24 questions.
- Mobile rendering, compiled dictionary integration, whole-library build and offline checks are owned by the coordinating agent and are not claimed by this scoped review.

**Low-confidence areas, including preserved qualifications:**

None recorded in this editorial review.


## react / State and Interactive Forms

1 question objects changed. Every changed question has a specific independent-review reason in the linked record.

**Corrections in this review:**

- Four nonexistent static Array.method aliases corrected to canonical prototype forms by author and independently verified.
- Reducer q1 revised to test immutable reset and preserved fields; verifier made the plain object explicit.

**Scope gaps and exclusions:**

No additional gaps recorded in this editorial review.

**Low-confidence areas, including preserved qualifications:**

None recorded in this editorial review.


## react / Hooks, Effects and Shared Logic

1 question objects changed. Every changed question has a specific independent-review reason in the linked record.

**Corrections in this review:**

- {"kind":"glossary-target","id":"react-try-catch","by":"author","detail":"Added try block/try blocks aliases so JavaScript error-handling prose opens the JavaScript entry instead of a Python fallback; independently checked MDN try...catch."}
- {"kind":"question-clarity","id":"rh-custom-hooks-q1","by":"verifier","detail":"Made the useState-backed implementation explicit in the prompt, removing reliance on recalling the lesson and avoiding a universal claim about custom Hooks that use shared external stores."}
- {"kind":"glossary-target","id":"react-asynchronous","by":"verifier","detail":"Added asynchronous work alias to the local Promise/await entry. The previous cross-subject fallback described queued fire-and-forget work shielding the caller from worker failures, which does not describe this fetch example."}

**Scope gaps and exclusions:**

- Mounted React checks run against React/React DOM19.3.1 in jsdom; real study-app mobile/desktop and offline integration remains root verification work.
- The client-only fetch assumes a same-origin array/id/text contract and does not implement production caching, request sharing, schema validation, authentication or cancellation.
- AbortController cancellation is defined and distinguished from ignoring a result, but is not implemented in the teaching component.
- Performance explanations and Compiler configuration are sourced as of this review, without claiming a measured speedup or executing React Compiler in this scratch harness.
- The final task project implements search and completion toggles. Add-task UI and persistence are explicitly labelled extensions rather than implemented features.
- The client fetch example intentionally assumes a same-origin array/id/text contract; production validation, caching, deduplication, authentication and cancellation are outside this lifecycle lesson.
- No performance speedup or React Compiler execution is claimed or benchmarked.
- Adding tasks and persistence are clearly labelled extensions; browser/mobile/offline integration remains the root integration check.

**Low-confidence areas, including preserved qualifications:**

None recorded in this editorial review.


## synth / Sound & Digital Audio

60 question objects changed. Every changed question has a specific independent-review reason in the linked record.

**Corrections in this review:**

- Counter precision: an incrementing float32 counter can stall at 2^24, rather than merely drifting.
- Waveform terminology now distinguishes a time-varying signal description from a propagating wave.
- Mixing feedback no longer denies beats: linear addition creates no new spectral frequencies, but close existing components interfere.
- Float headroom no longer implies that intervening effects cannot clip or that floating-point processing is lossless.
- General cancellation now requires opposite polarity rather than an arbitrary waveform shifted by half a cycle.
- Above-Nyquist harmonics are not all inharmonic after folding; some coincide with genuine harmonic bins.
- A genuine 15 kHz third-harmonic bin may also contain higher aliases; presence alone cannot identify alias-only content.
- Ideal 24-bit sample code spacing is distinguished from real converter noise performance.
- Clipper aliases fall in the represented band and may be audible, rather than all necessarily lying in the audible band.
- Hard-versus-tanh ninth-harmonic ordering is tied to the demonstrated drive, not a universal ordering of every harmonic.
- Sub-step sine/dither question now explicitly assumes an otherwise noiseless signal and nearest rounding.
- Added local FFT symmetry, frequency-axis API and odd/even Nyquist endpoint prerequisites outside optional maths.
- Whole-cycle DC interpretation no longer contradicts the partial-cycle mean caveat.
- Window feedback preserves the main-lobe/sidelobe trade-off instead of universally preferring widening.
- FFT and Hann readings are described at numerical precision, rather than exact for all finite computations.
- Float-format WAV reads can exceed nominal full scale; default float64 dtype does not impose a range limit.
- FLOAT export preserves headroom at float32 precision and can round float64 input.
- Tap analogy now compares simultaneous flow rates with drain capacity, avoiding misleading accumulated jug volume.
- Added the hearing precaution referenced by line-level question feedback to visible lesson prose.
- Pitch-discrimination link replaced after its PubMed response contained only a placeholder; fetched open primary study supports the retained qualitative claim.
- Glossary enob: replaced generic noise/SNR definition and unjustified dynamic-range-derived 18.6-bit example with SINAD-based noise-and-distortion performance under stated test conditions; identified noise-only estimates separately.
- Glossary phase-jump: replaced guaranteed waveform-value jump/click with possible discontinuity, a verified equal-value phase counterexample, and a slope/transient caveat.
- Glossary peak-level: separated sample peak from reconstructed true peak and downstream range, replacing the claim that sample peak alone decides clipping.
- Glossary monitor-level: removed the equipment alias studio monitors and sourced playback-volume meaning and low-level test precautions.

**Scope gaps and exclusions:**

- Scope: independent concept-first review of all active lessons and questions, retained formula/code/analogy behaviour and changed surrounding claims; 292 unchanged glossary definitions retain prior independent records and unresolved limitations in lowConfidence.
- No active lesson IDs, question IDs/counts/ownership, migrations, archive files changed. Four existing dictionary entries were corrected in the subsequent scoped review. Twenty-nine redundant lesson cards and all 60 quiz cards were removed; useful maths remains in 22 optional references and one essential sine relationship.
- No hardware, hearing/audibility threshold, target-processor timing or finished-board noise measurements were performed. Converter figures remain conditional; library and product conventions remain version-sensitive.
- BLIT/BLEP, practical anti-alias filter design and true-peak reconstruction remain conceptual pointers to later modules. No implementation-depth claim is made for them.
- Root coordinates full application build/tests, iPhone rendering and offline behaviour; this module verifier runs scoped content checks.

**Low-confidence areas, including preserved qualifications:**

- medium confidence, glossary: coherent-sampling No dedicated authoritative page fetched (Analog Devices article timed out); source is the Spectral leakage article
- medium confidence, glossary: note-space Course-specific term; Pitch space article supports the linear MIDI pitch-space idea
- medium confidence, glossary: crest-factor "12–20 dB for real music" is a broad typical range that varies by genre and mastering
- medium confidence, glossary: zipper-noise Source (Smoothing) is generic; definition is standard practice
- medium confidence, glossary: parameter-smoothing Source (Smoothing) is generic; definition is standard practice
- medium confidence, glossary: offline-render Source is a computer-graphics rendering article; meaning is standard audio usage
- medium confidence, glossary: correlated-signals Source (Coherence) is loose; power-addition of uncorrelated signals is standard
- medium confidence, glossary: power-signal Source (Power (physics)) is loose; mean-square definition is standard
- medium confidence, glossary: vibrato Example settings are a typical choice, not a standard
- medium confidence, glossary: audio-block Course usage; PortAudio callback docs describe frames per buffer
- medium confidence, glossary: ableton-live Existing medium-confidence glossary record preserved. Current manufacturer manual documents C-2 to G8 full MIDI range, from which note 60 = C3 is inferred; product labels remain version-sensitive.
- medium confidence, glossary: just-noticeable-difference Existing definition and original confidence retained unchanged. Its 3 Hz/0.6% examples come from a secondary summary; primary research supports condition dependence, not a universal threshold.
- medium confidence, snd-midi-frequency: Ableton note-60 display label C3 is inferred from the current manual’s full MIDI range C-2 to G8; future versions/products may use other octave labels.
- medium confidence, snd-float-integer-boundary: Target-processor subnormal handling cost Primary Intel documentation and older x86 measurements support variable penalties. No benchmark on the reader’s embedded target was performed; fixed-cycle claim removed.
- medium confidence, snd-dither-converter-noise: Finished-board dynamic range and noise-only ENOB estimate Chip figures verified with datasheet configurations and A-weighting; finished-board noise and SINAD were not measured. Dynamic-range substitution remains an explicitly approximate noise-only estimate.
- medium confidence, snd-peak-rms-dbfs: AES17 convention and typical music crest-factor ranges AES authoritative reference and indexed Audio Precision primary-manual excerpt support the conventions; full normative AES17 text not obtained. Music range is programme- and averaging-dependent and is hedged.
- medium confidence, snd-wav-write-readback: PCM flooring/clipping and library conversion behaviour Confirmed in independent experiments with soundfile 0.14.0/libsndfile 1.2.2 and inspected versioned source. Behaviour can depend on library/platform/rounding configuration; text ties it to this runtime.


## synth / Synthesis & DSP

64 question objects changed. Every changed question has a specific independent-review reason in the linked record.

**Corrections in this review:**

- syn-synthesis-overview-tables-models lesson and q3: 'round trip' (opened the system-design/networking round-trip definition) -> 'loop' / 'delay around the loop'.
- syn-bandlimited-q8 workedExample: 'Precomputed tables' (opened a password-cracking precomputed-table definition) -> 'Tables built offline'.
- syn-filters-biquad-svf: 'integrator/state structure' (opened React 'state shape') -> 'specific integrator arrangement analysed in those papers'.
- syn-filters-iir-fir: 'recursive' (opened the core function-recursion definition) -> 'feedback', including the key takeaway.
- syn-bandlimited-additive-tables analogy: 'spare capacity' (opened system-design capacity headroom) -> 'unused room'.
- glossary oscillator-duty-fraction: added 'duty cycle'/'duty cycles' aliases and wording; the module's duty-cycle uses previously opened the networks radio duty-cycle entry. Id preserved.
- glossary free-running: unconditional 'giving slight note-to-note variation' -> starting phases can vary but whole-cycle timing can revisit the same phase (matches the reset-policy correction).
- syn-synthesis-overview-q6 workedExample: stale '(lesson 7)' pointer -> the control-rate unit.
- syn-bandlimited-q1 workedExample: stale 'Lesson 3' pointer -> the harmonic units.
- syn-modulation-q11 option explanation: 'as in the lesson's code' -> 'the LFO unit's code' (the code is not in that lesson).
- syn-envelopes-retrigger-legato: 'as the code above does' referred to code in another unit -> names the exponential ADSR state-machine unit.
- syn-envelopes-smoothing-domain: cutoff bullet implied octave-domain smoothing gives each octave equal time -> only a constant-rate octave ramp does; an exponential smoother slows near its target. 'Smoothing linearly' -> 'a linear ramp in hertz'.
- syn-modulation-tempo-tremolo: 'Free-running LFOs drift relative to the notes' -> phase at note-on depends on timing and can differ.
- syn-harmonics-gibbs-timbre: ambiguous 'not a mandatory 18% peak' -> an overshoot of about 18% above the flat level is not mandatory.
- syn-harmonics-phase-headroom: phase-sensitivity dependence on 'harmonic resolution' is not established by the cited Schroeder-phase study -> 'factors such as fundamental frequency, the listener and listening conditions'; reading label 'mdft' -> 'Mathematics of the DFT'.
- syn-harmonics-fourier-patterns: sentence comparing with a removed code example -> statement that equal magnitudes can start cycles at different-looking points.
- syn-harmonics-fourier-foundations: overtone wording aligned with the newly verified synth/01 overtone entry (fundamental is not an overtone; inharmonic overtones exist).
- syn-modulation-vibrato-depth: key takeaway about fixed-hertz deviation in linear FM had no supporting body text -> one sentence added.
- Editorial (not counted as errors): dangling colons left by removed formula cards fixed in integer-phase, fourier-foundations, gibbs-timbre, alias-folding, polyblep-experiment, pulse-libraries, time-constants, smoothing-domain, response-slope, measure-one-pole, ladder, lfo-ranges and phase-shapes; PolyBLEP reading label 'finke' -> 'PolyBLEP oscillator tutorial — Martin Finke'.
- Accepted after independent re-check (edit made by the earlier incomplete verifier pass, already present in the frozen drafts): syn-synthesis-overview-fm-pm: Qualify implementation cost and explain programming difficulty.
- Accepted after independent re-check (edit made by the earlier incomplete verifier pass, already present in the frozen drafts): syn-envelopes-retrigger-legato: A phase reset does not necessarily cause an output-value discontinuity.
- Accepted after independent re-check (edit made by the earlier incomplete verifier pass, already present in the frozen drafts): syn-envelopes-retrigger-legato: Distinguish constant-speed log ramps from arbitrary log-domain smoothing.
- Accepted after independent re-check (edit made by the earlier incomplete verifier pass, already present in the frozen drafts): syn-envelopes-smoothing-domain: Only a constant-rate log ramp gives the stated constant octave speed.
- Accepted after independent re-check (edit made by the earlier incomplete verifier pass, already present in the frozen drafts): syn-envelopes-smoother-ramp: Parameter jumps do not guarantee output-value jumps or audible noise.
- Accepted after independent re-check (edit made by the earlier incomplete verifier pass, already present in the frozen drafts): syn-envelopes-smoother-ramp syn-envelopes-q3: Avoid the false general claim that aliasing cannot depend on moving controls.
- Accepted after independent re-check (edit made by the earlier incomplete verifier pass, already present in the frozen drafts): syn-envelopes-smoother-ramp syn-envelopes-q3: Avoid asserting that clipping necessarily persists whenever a knob stops.
- Accepted after independent re-check (edit made by the earlier incomplete verifier pass, already present in the frozen drafts): syn-envelopes-smoother-ramp syn-envelopes-q3: Retain 128 values rather than incorrectly calling them 128 adjacent steps.
- Accepted after independent re-check (edit made by the earlier incomplete verifier pass, already present in the frozen drafts): syn-bandlimited-alias-folding: Aliasing can coincide with harmonic frequencies; scope statement to this example.
- Accepted after independent re-check (edit made by the earlier incomplete verifier pass, already present in the frozen drafts): syn-bandlimited-alias-folding syn-bandlimited-q3: Avoid making inharmonicity universal.
- Accepted after independent re-check (edit made by the earlier incomplete verifier pass, already present in the frozen drafts): syn-bandlimited-antialias-methods syn-bandlimited-q12: Avoid unsupported universal claim that most folded energy lands outside the retained band.
- Accepted after independent re-check (edit made by the earlier incomplete verifier pass, already present in the frozen drafts): syn-bandlimited-antialias-methods syn-bandlimited-q7: Keep exactness assumptions available in the question’s own summary.
- Accepted after independent re-check (edit made by the earlier incomplete verifier pass, already present in the frozen drafts): syn-bandlimited-polyblep-experiment syn-bandlimited-q10: Aliasing does not universally sound harsher or exclude reduced brightness.
- Accepted after independent re-check (edit made by the earlier incomplete verifier pass, already present in the frozen drafts): syn-bandlimited-polyblep-experiment syn-bandlimited-q10: Replace listening inference and malformed wording with the measured two-part comparison.
- Accepted after independent re-check (edit made by the earlier incomplete verifier pass, already present in the frozen drafts): syn-filters-measure-one-pole syn-filters-q9: The bare condition coefficient less than one wrongly includes unstable negative coefficients.
- Accepted after independent re-check (edit made by the earlier incomplete verifier pass, already present in the frozen drafts): syn-modulation-matrix: Finite input does not prevent exponential overflow before the clamp.
- Accepted after independent re-check (edit made by the earlier incomplete verifier pass, already present in the frozen drafts): syn-modulation-control-rate syn-modulation-q11: A 2 ms attack at 1.5 kHz spans three updates, not one or two.
- Accepted after independent re-check (edit made by the earlier incomplete verifier pass, already present in the frozen drafts): syn-modulation-lfo-ranges syn-modulation-q12: Distinguish one-pole exponential motion from a linear ramp and qualify clicks.
- Accepted after independent re-check (edit made by the earlier incomplete verifier pass, already present in the frozen drafts): syn-oscillators-reset-policy syn-oscillators-q11: Note timing can also revisit the same phase; variation is possible, not guaranteed.
- Accepted after independent re-check (edit made by the earlier incomplete verifier pass, already present in the frozen drafts): syn-oscillators-reset-policy syn-oscillators-q11: Free running is deterministic and does not guarantee a different phase every note.
- Accepted after independent re-check (edit made by the earlier incomplete verifier pass, already present in the frozen drafts): syn-oscillators-reset-policy syn-oscillators-q11: Resetting one phase alone does not guarantee the entire attack waveform.
- Accepted after independent re-check (edit made by the earlier incomplete verifier pass, already present in the frozen drafts): syn-oscillators-reset-policy syn-oscillators-q11: Make repeatability conditions explicit.
- Accepted after independent re-check (edit made by the earlier incomplete verifier pass, already present in the frozen drafts): syn-oscillators-reset-policy syn-oscillators-q11: Avoid unconditional attack identity and free-running variation.
- Accepted after independent re-check (edit made by the earlier incomplete verifier pass, already present in the frozen drafts): glossary key-sync: Free running does not guarantee a different phase on every note.
- Accepted after independent re-check (edit made by the earlier incomplete verifier pass, already present in the frozen drafts): glossary exponential-fm: The stated mean requires a sinusoidal control and complete cycles, not arbitrary swings.

**Scope gaps and exclusions:**

- Code is an offline Python learning bridge. Original C/DDS semantics preserved and natively exercised; no new C++ teaching introduced.
- Host compilation of pinned libraries verifies shown algorithms and source claims, not firmware integration, hardware capacity, real-time deadlines or acoustic measurements.
- Advanced anti-aliasing, loop-filter tuning, arbitrary time-varying filters and extreme modulation require further design analysis; approximate PolyBLEP is not certified alias-free.
- Source dependency follow-ups have separately scoped independent records: Sound3, Soundfive/body/Q, and Audio06 linear-phase. Audio06 remains unsplit.
- No target-hardware (Daisy/Teensy) timing, CPU budget or analogue-output measurement in this module; all experiments are host-side.
- Wavetable interpolation error, table crossfading and hard sync are described qualitatively only.
- BLAMP, minBLEP table construction and oversampling decimation-filter design are named but not demonstrated.
- Stray Further-reading choices (NumPy rfft listed in the LFO and control-rate units) are harmless but weakly related; left unchanged.

**Low-confidence areas, including preserved qualifications:**

- medium confidence, syn-harmonics-phase-headroom: Audibility of phase changes in harmonic complexes. Primary human study supports conditional sensitivity; no personal listening or universal perceptual guarantee is claimed.
- medium confidence, syn-bandlimited-pulse-libraries: Relative implementation cost and suitability for a target board. Actual pinned DaisySP/PJRC native code executed, but host execution does not establish board CPU budgets, firmware integration or listener thresholds.
- medium confidence, syn-modulation-control-rate: Audibility of block-rate stairs and fast-envelope artefacts. Bandwidth and step counts independently checked; playback conditions and masking determine audibility.
- medium confidence, syn-bandlimited-pulse-libraries: DaisySP host measurements (-29.83/-55.45 dB, -1.95 dB tenth-harmonic droop) from the source compiled on a desktop host. Reproduced exactly by this verifier's float32 hand port of the pinned DaisySP Process/Polyblep code; this verifier's own compilation of the downloaded C++ was refused by the sandbox, so the compiled run rests on the author's and earlier pass's evidence. Not a target-board measurement.
- medium confidence, syn-harmonics-phase-headroom: Harmonic phase differences can be audible in steady harmonic complexes. Supported by Drennan et al. (Schroeder-phase discrimination); wording hedged to listener, F0 and listening conditions. No listening test of the lesson's pair.
- medium confidence, syn-envelopes-time-constants: Subnormal floating-point values can be slow on some processors. Hedged. The Intel page passes the link checker but its body could not be read by automated fetch; claim is widely documented but not re-read here.
- medium confidence, syn-harmonics-gibbs-timbre: Piano high harmonics decay faster than the fundamental; brass brightens as it gets louder. Standard acoustics illustrations, unchanged from earlier review; not re-checked against a fetched source in this pass.
- medium confidence, syn-harmonics-fourier-patterns: Timbre descriptors (square 'hollow, woody, clarinet-like'; triangle 'close to a sine'). Perceptual descriptors; the spectral facts behind them were recomputed, the descriptors are conventional rather than measured.
- medium confidence, syn-synthesis-overview-tables-models: Digitakt II is a stereo sampler; library revision facts (DaisySP 2c72eaf9eac5, PJRC Audio 3039be2773e8). Time-sensitive product/library facts; manufacturer page re-fetched 2026-10-29 and pinned sources read. Lessons already tell the learner to confirm the actual model and installed library.


## system-design / Fundamentals

66 question objects changed. Every changed question has a specific independent-review reason in the linked record.

**Corrections in this review:**

- Removed dangling reference to a deleted pair-count formula.
- Removed orphaned equation introduction after the pair-count formula was deleted.
- Removed duplicate bit/byte explanation and orphaned formula introduction.
- Joined a leftover formula lead-in to the recovery-stage explanation.
- Kept independence in the standalone visible explanation of the optional series formula.
- Corrected 100 ms downtime each minute to about 99.83%, preserving the reliability comparison.
- Separated linearisability from the additional remote-durability contract, matching the revised question assumptions.
- Qualified the batching trade-off: it can improve end-to-end latency by reducing queueing, as Kafka documents.
- Removed an unconditional throughput promise from the batching description.
- Added the missing independent-capacity assumptions behind roughly doubling maximum throughput.
- Replaced load-percentage and under-100ms guarantees with request-count reasoning, independent-pause and spare-capacity assumptions.
- Removed an unsupported generic 1–2 ms cross-zone replication claim and kept the replicated-versus-flushed distinction visible in feedback.
- Avoided asserting that raising a timeout necessarily changes the intrinsic backend latency distribution.
- Corrected glossary batching; retained previous independent provenance for every unchanged term.
- Corrected glossary availability-zone; retained previous independent provenance for every unchanged term.
- Corrected glossary latency-bound; retained previous independent provenance for every unchanged term.
- Corrected glossary percentile; retained previous independent provenance for every unchanged term.
- Corrected glossary stateless-service; retained previous independent provenance for every unchanged term.
- Corrected glossary majority-quorum; retained previous independent provenance for every unchanged term.
- Corrected glossary quorum-overlap; retained previous independent provenance for every unchanged term.
- Expanded CAP labels to avoid opening the certificate-authority definition.
- Replaced 4k prose with 4,000 to avoid the video-resolution definition.
- Described invalidating issued tokens explicitly to avoid the certificate-revocation definition.

**Scope gaps and exclusions:**

- No fresh exhaustive source audit of the 372 unchanged glossary entries or unrelated historical product details is claimed; their prior records and low-confidence caveats are preserved in reviewHistory.
- No production benchmarks or failure-injection tests. Scenario capacities, timings and object sizes remain illustrative.
- Four conditional SQL executions used SQLite to verify predicate effects; PostgreSQL locking/SKIP LOCKED and Kafka/Redis settings were reviewed against fetched primary docs, not a live deployment.
- Full app phone rendering, offline checks and library-wide integration remain the parent agent responsibility.

**Low-confidence areas, including preserved qualifications:**

- medium confidence, glossary / zookeeper-sync: A ZooKeeper call that makes the client's server catch up with the leader before the next read; it improves freshness but is not a quorum operation or a strict l sync() not being a quorum operation is documented in the ZooKeeper dev list / ZOOKEEPER-1675 discussion, not in the current programmer guide.
- medium confidence, glossary / idempotent-producer: A Kafka producer mode that tags messages with sequence numbers so retries do not create duplicates in a partition. On by default since Kafka 3.0. Default flipped in Kafka 3.0 (KIP-679), but a bug kept it off in 3.0.0/3.1.0 until fixed in 3.0.1.
- medium confidence, glossary / peak-load: The highest load a system sees, usually in its busiest minutes, as opposed to the average. Capacity must cover the peak; peaks of 2–10 times the average are com "Peaks of 2–10 times the average are common" is a rule of thumb shared with the lesson, not a measured statistic.
- medium confidence, glossary / snappy: A fast compression library from Google that favours speed over compression ratio. The ~2 µs to compress 1 KB is from widely circulated latency-number tables, not a reproduced benchmark.
- medium confidence, glossary / ssd: Storage built from flash memory chips with no moving parts. Random reads take tens to hundreds of microseconds, far faster than a spinning disk. 20–150 µs random 4 KB read is a broad, device-dependent range.
- medium confidence, glossary / truetime: Google's clock API, backed by GPS receivers and atomic clocks, that reports the time with a bounded uncertainty. Spanner waits out that uncertainty to order tra "Typically a few milliseconds" of commit wait is from the Spanner paper era; current figures not published on the cited page.
- medium confidence, fund-latency-orders-magnitude: Hardware timing table, Snappy and SSD ratios Explicit hypothetical exercise inputs, not measured contemporary benchmarks. Unchanged glossary Snappy/SSD entries retain earlier medium confidence.
- medium confidence, fund-constraints-scale: Peak factors, tenfold growth allowance and small-team design guidance Planning heuristics and scenario recommendations need actual workload and team evidence.
- medium confidence, fund-queueing-headroom: 50–70% peak utilisation planning range A qualified heuristic, not a universal SLO-safe threshold; M/M/1 arithmetic is verified but real workload behaviour must be measured.
- medium confidence, fund-scaling-state: Cloud sizes, costs and scaling-up versus scaling-out guidance Size capabilities checked against current AWS docs; costs and operational trade-offs vary by purchase model and workload.
- medium confidence, fund-latency-orders-magnitude: Snowball retirement notices and product availability Official announcements checked on 2026-10-14; re-check before choosing a transfer service.
- medium confidence, fund-pacelc-latency-consistency: DynamoDB read and global-table API modes Public contracts checked against current AWS docs; mode availability and constraints change over time.
- medium confidence, fund-partition-policy-conflicts: Spanner 99.999% availability commitment Current conditional SLA checked; does not promise measured uptime or CAP availability.
- medium confidence, fund-quorum-read-guarantees: ZooKeeper sync() is not a strict linearisability guarantee under every failure Supported by Apache project issue/developer discussion, while the programmer guide presents a simpler freshness description.
- medium confidence, fund-durable-write-batching: Kafka and PostgreSQL defaults and Redis persistence exposure Current version-specific docs checked, including Kafka historical idempotence bug; configuration and failure assumptions must be rechecked for deployment.
- medium confidence, fund-estimation-fleet-capacity: Per-node capacity and resource headroom examples Hypothetical exercise capacities; arithmetic checked without production benchmarking.

