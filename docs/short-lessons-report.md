# Short lessons and code comments

Verified modules: 3/76. Updated 2026-10-14.

Each converted lesson has its own completion status, completion date and focused questions. Original completed lessons carry their exact dates into all new parts. Existing question IDs, saved answers, bookmarks and quiz sessions remain compatible; old lesson links open the new units.

The material is divided by concept while retaining substantive explanations, examples, caveats, equations and diagrams. Most lessons take 3–5 minutes; a few naturally small units have honest shorter estimates. Useful code comments explain operations and outputs; incomplete examples remain clearly labelled.

| Subject/module | Original lessons | Short lessons | Questions | Formulas | Glossary | Review items | Corrections |
|---|---:|---:|---:|---:|---:|---:|---:|
| system-design/Fundamentals | 7 | 27 | 84 | 107 | 379 | 252 | 37 |
| dsa/Complexity Analysis | 7 | 35 | 81 | 144 | 150 | 260 | 6 |
| synth/Sound & Digital Audio | 6 | 32 | 69 | 112 | 296 | 220 | 26 |

Review-item counts follow each independent verifier’s recorded counting method. They include overlapping lesson claim groups, formula reviews and question reviews; they are not counts of distinct atomic facts. Existing glossary confidence and source records are preserved rather than automatically upgraded.

Validation includes independent source and answer-key review, maths and code checks, verification stamps, compiler validation, original-question preservation, mobile rendering, progress migration, saved quizzes, completion-age controls and offline practice. Remaining modules are being converted in subsequent batches.

## system-design: Fundamentals

[Independent verification record](../content/system-design/01-fundamentals/verification.json)

Corrections and qualifications in this conversion:

- Clarified the EEA transfer boundary and distinguished an organisational EU-residency policy from GDPR.
- Hedged the unsourced 2–10x peak statistic as an illustrative planning assumption.
- Relabelled the 70 ms link delay as an exercise input rather than a universal measured route latency.
- Kept the propagation calculation separate from the hypothetical route timing.
- Restricted nearest-rank percentiles to positive percentiles so the formula never returns rank zero.
- Explained wrk2 scheduled-start correction rather than implying every planned request is physically sent during a stall.
- Added the local prerequisites for tied requests, background-work isolation and partial-result deadline questions.
- Made the hardware ratio explicitly a calculation from hypothetical timings rather than a benchmark claim.
- Specified matching time units for every recovery stage in the MTTR sum.
- Qualified vertical scaling simplicity instead of promising no changes for every application.
- Removed an unsupported universal cloud price curve and made the fixed-size billing assumption explicit.
- Avoided a wrong-sense glossary match: queue policy resolved to SQS permissions rather than queue admission or scheduling.
- Qualified the formula peak factor as an exercise assumption.
- Removed the ambiguous use of B for both billions and bytes in one formula.
- Defined B consistently as bytes.
- Replaced the false claim that a numeric prefix alone disambiguates B.
- Qualified the inference from read/write ratio to feed architecture.
- Separated majority-protected writes from full API linearisability, avoiding an unqualified ZooKeeper CP guarantee.
- Stated the Spanner SLA as a conditional monthly commitment instead of inferring its measured uptime or causes.
- Labelled unsourced generic quorum timings as assumptions.
- Replaced DynamoDB leader-routing implementation trivia with the documented API contract and index restrictions.
- Added the official Kafka 3.0.0/3.1.0 idempotence-default bug and conflicting-setting caveat.
- Qualified cloud transfer charges to avoid treating every route and service as billable.
- Distinguished spending a full downtime allowance from forecasting expected outages.
- Corrected the nearest-rank domain and wrk2 explanation; clarified histogram quantiles are estimates.
- Replaced undocumented DynamoDB replica routing in the question table with its public freshness contract and clarified provisioned ordinary-read costs.
- Kept the hypothetical time-based SLA distinct from request failures and latency thresholds.
- Made the replication/overhead assumptions explicit so the storage distractor is unambiguously wrong.
- Moved a formula card out of its numbered-list indentation, preserving the calculation.
- Moved fund-tradeoffs-q11 from cost to build-versus-buy: its vendor/self-hosting assessment uses the build/buy checklist introduced in that unit, eliminating a later prerequisite.
- Added ms to the service-time substitutions in the M/M/1 question so each derivation carries matching units.
- Replaced pipe equality labels with accurate descriptive labels; pipe length/width are analogies rather than mathematical definitions.
- Changed three prose equality labels to words; their complete defined equations remain in formula cards.
- Removed an unsupported universal few-percent networking-overhead claim; overhead depends on packet size and protocol.
- Qualified strong-read coordination instead of claiming every implementation must read a leader or quorum.
- Clarified that idempotent jobs address duplicate execution, not recovery of lost queued jobs.
- Described ACID C and CAP C as different properties, avoiding the overstatement that transactional invariants and operation ordering are wholly unrelated.

Remaining gaps:

- No reproducible generic hardware latency, object-size or per-server throughput benchmark dataset; timing and capacity tables remain visibly illustrative.
- No production cloud load tests, failure-injection experiments or live PostgreSQL/Redis/Kafka deployment. Conditional SQL statement effects were checked in SQLite; protocol/config fragments are illustrative and were checked against primary documentation rather than run as full deployments.
- The unchanged glossary retains previous independent hashes/confidence/source records, including Kafka idempotence, peak-factor, Snappy/SSD and TrueTime timing caveats; this split review does not claim a new audit of all 379 definitions.
- Coverage tool still reports emphasis phrases, arbitrary labels and bare ordinary words. Technical meanings are covered by their existing qualified entries; ONE/ALL are defined within the Cassandra consistency-level entry, and admission is defined as admission control.
- Phone rendering and full-project tests remain the integrating parent agent's responsibility; this verifier ran module validation and global glossary/diagram validation in scoped build.

Low-confidence areas:

- **medium** — glossary: A ZooKeeper call that makes the client's server catch up with the leader before the next read; it improves freshness but is not a quorum operation or a strict l. sync() not being a quorum operation is documented in the ZooKeeper dev list / ZOOKEEPER-1675 discussion, not in the current programmer guide.
- **medium** — glossary: A Kafka producer mode that tags messages with sequence numbers so retries do not create duplicates in a partition. On by default since Kafka 3.0.. Default flipped in Kafka 3.0 (KIP-679), but a bug kept it off in 3.0.0/3.1.0 until fixed in 3.0.1.
- **medium** — glossary: The highest load a system sees, usually in its busiest minutes, as opposed to the average. Capacity must cover the peak; peaks of 2–10 times the average are com. "Peaks of 2–10 times the average are common" is a rule of thumb shared with the lesson, not a measured statistic.
- **medium** — glossary: A fast compression library from Google that favours speed over compression ratio.. The ~2 µs to compress 1 KB is from widely circulated latency-number tables, not a reproduced benchmark.
- **medium** — glossary: Storage built from flash memory chips with no moving parts. Random reads take tens to hundreds of microseconds, far faster than a spinning disk.. 20–150 µs random 4 KB read is a broad, device-dependent range.
- **medium** — glossary: Google's clock API, backed by GPS receivers and atomic clocks, that reports the time with a bounded uncertainty. Spanner waits out that uncertainty to order tra. "Typically a few milliseconds" of commit wait is from the Spanner paper era; current figures not published on the cited page.
- **medium** — fund-latency-orders-magnitude: Hardware timing table, Snappy and SSD ratios. Explicit hypothetical exercise inputs, not measured contemporary benchmarks. Unchanged glossary Snappy/SSD entries retain earlier medium confidence.
- **medium** — fund-constraints-scale: Peak factors, tenfold growth allowance and small-team design guidance. Planning heuristics and scenario recommendations need actual workload and team evidence.
- **medium** — fund-queueing-headroom: 50–70% peak utilisation planning range. A qualified heuristic, not a universal SLO-safe threshold; M/M/1 arithmetic is verified but real workload behaviour must be measured.
- **medium** — fund-scaling-state: Cloud sizes, costs and scaling-up versus scaling-out guidance. Size capabilities checked against current AWS docs; costs and operational trade-offs vary by purchase model and workload.
- **medium** — fund-latency-orders-magnitude: Snowball retirement notices and product availability. Official announcements checked on 2026-10-14; re-check before choosing a transfer service.
- **medium** — fund-pacelc-latency-consistency: DynamoDB read and global-table API modes. Public contracts checked against current AWS docs; mode availability and constraints change over time.
- **medium** — fund-partition-policy-conflicts: Spanner 99.999% availability commitment. Current conditional SLA checked; does not promise measured uptime or CAP availability.
- **medium** — fund-quorum-read-guarantees: ZooKeeper sync() is not a strict linearisability guarantee under every failure. Supported by Apache project issue/developer discussion, while the programmer guide presents a simpler freshness description.
- **medium** — fund-durable-write-batching: Kafka and PostgreSQL defaults and Redis persistence exposure. Current version-specific docs checked, including Kafka historical idempotence bug; configuration and failure assumptions must be rechecked for deployment.
- **medium** — fund-estimation-fleet-capacity: Per-node capacity and resource headroom examples. Hypothetical exercise capacities; arithmetic checked without production benchmarking.

## dsa: Complexity Analysis

[Independent verification record](../content/dsa/01-complexity/verification.json)

Corrections and qualifications in this conversion:

- cx-growth-rates-q7: the exact n//2 inner count used n/2 even for odd n. Replaced it with floor(n/2), defined floor, and kept the quadratic approximation and answer key.
- cx-input-size: the pair-count scaling chain ended with an exact equality to4C(n), although lower-order terms had been discarded. Replaced that equality with an approximation.
- cx-in-place-memory and cx-space-complexity-q9: a frame-count bound omitted the initial frame. Use floor(log_2(n))+1 for positive n, including the initial call; asymptotic bound and answer stay O(log n).
- cx-recursion-trees: its new introductory bounded-positive-base-case wording did not justify the retained exact level sums and2n² upper bound. Explicitly use powers of two and base-case cost one for exact examples; fixed positive alternatives have the same asymptotic bounds.
- cx-recurrences-q12: the internal-level arithmetic sum was stated as exact total running time despite omitting a linear leaf cost. Marked the sum approximate and explained the excluded fixed-base-case leaf cost; answer remains Theta(n log²n).
- Corrected subject/verb agreement in four rewritten cross-references after singular long lessons became plural short lessons.

Remaining gaps:

- Universal cross-language speed ratios and memory latency figures lack reproducible measurements and are explicitly omitted.
- No benchmark-derived crossover recommendation for a particular deployment.
- Code execution uses small representative inputs and explicit harness assumptions; it is not a proof for arbitrary inputs.
- Formula lint retains inherited prose/table mathematics alongside valid Big-O and real-code exceptions. Its542 active heuristic hits are not represented as zero findings or all as Rule6 exceptions; this split/comment scope did not rewrite the existing formula presentation everywhere.
- The35 units preserve the depth of the seven originals. Two naturally small units retain honest two-minute estimates;33 units use three-to-five-minute estimates. Some focused units have one question rather than padding them with unrelated questions.

Low-confidence areas:

- **medium** — cx-growth-rates: Version- and implementation-sensitive runtime details or illustrative cost assumptions. Core asymptotic reasoning checked against teaching sources and code/counts recomputed. Implementation details are qualified and valid only for the cited builds/model; this record does not assert a primary source individually attached to every retained sentence.
- **medium** — cx-asymptotic-notation: Version- and implementation-sensitive runtime details or illustrative cost assumptions. Core asymptotic reasoning checked against teaching sources and code/counts recomputed. Implementation details are qualified and valid only for the cited builds/model; this record does not assert a primary source individually attached to every retained sentence.
- **medium** — cx-analysing-code: Version- and implementation-sensitive runtime details or illustrative cost assumptions. Core asymptotic reasoning checked against teaching sources and code/counts recomputed. Implementation details are qualified and valid only for the cited builds/model; this record does not assert a primary source individually attached to every retained sentence.
- **medium** — cx-space-complexity: Version- and implementation-sensitive runtime details or illustrative cost assumptions. Core asymptotic reasoning checked against teaching sources and code/counts recomputed. Implementation details are qualified and valid only for the cited builds/model; this record does not assert a primary source individually attached to every retained sentence.
- **medium** — cx-amortised-analysis: Version- and implementation-sensitive runtime details or illustrative cost assumptions. Core asymptotic reasoning checked against teaching sources and code/counts recomputed. Implementation details are qualified and valid only for the cited builds/model; this record does not assert a primary source individually attached to every retained sentence.
- **medium** — cx-recurrences: Version- and implementation-sensitive runtime details or illustrative cost assumptions. Core asymptotic reasoning checked against teaching sources and code/counts recomputed. Implementation details are qualified and valid only for the cited builds/model; this record does not assert a primary source individually attached to every retained sentence.
- **medium** — cx-in-practice: Version- and implementation-sensitive runtime details or illustrative cost assumptions. Core asymptotic reasoning checked against teaching sources and code/counts recomputed. Implementation details are qualified and valid only for the cited builds/model; this record does not assert a primary source individually attached to every retained sentence.
- **medium** — cx-growth-rates: Glossary term 'Total problem' (used in the lesson's definition of an algorithm). retrofit: 'total problem' is not a standard textbook term; the definition is a reasonable reading by analogy with total vs partial functions (Wikipedia: Partial function), but no primary algorithms text defines it this way.
- **medium** — cx-space-complexity: Glossary alias 'two pointers' now resolves DSA-wide to the general two-pointer-technique entry (overriding dsa/02's fast/slow entry). retrofit: the definition now covers both opposite-ends and same-direction (fast/slow) variants, so dsa/02 and dsa/09 uses read correctly; but several DSA lessons use 'two pointers' literally (e.g. 'one or two pointers plus allocator bookkeeping' in dsa/02, 'only two pointers are stored' in dsa/04), which will also link. Those modules are outside this verifier's scope.
- **medium** — cx-growth-rates: Glossary 'Exponential time': practical only up to about n = 20 to 40 for 2^n. retrofit: an order-of-magnitude rule of thumb consistent with the lesson's 10^8 ops/s model (2^25 to 2^35 steps), not a sourced figure.
- **medium** — cx-counting-work: Inherited nonstandard total-problem glossary terminology. Core algorithm properties are primary-source checked. The unchanged glossary term still lacks a primary algorithms textbook definition, as the inherited record honestly states.
- **medium** — cx-recursive-hidden-work: Simplified costs for CPython operations. Current implementation is fetched and examples run. Counts assume bounded-value or constant-cost comparisons/hash operations and describe this cost model; arbitrary user objects or large integers require separate analysis.
- **medium** — cx-recursion-memory: CPython recursion limit and atomic-number space model. Current source defines1000 and the independent local Python3.14.4 run observed1000. Builds and user configuration can differ; whole-number bit storage is explicitly treated separately.
- **medium** — cx-in-place-memory: Implementation-specific list-sort auxiliary allocation. Current CPython listsort primary source supports up to half-list temporary pointers; it is an implementation statement, not a permanent Python-language guarantee.
- **medium** — cx-memory-tradeoffs: Typical64-bit CPython object sizes and packed-buffer memory budgets. The text is qualified and asks the reader to measure their build. This run observes28-byte int(1); 80/360MB arithmetic is recomputed, but allocator, value magnitude and construction overhead depend on the deployment.
- **medium** — cx-resizing-policies: CPython/OpenJDK/libstdc++ growth factors. Fetched current implementation sources support the qualified factors. These are version-sensitive implementation details; Rust documents no particular factor guarantee.
- **medium** — cx-amortised-latency: Resize latency and Redis incremental-rehash implementation. The data movement model and current Redis source are checked. The module does not claim a reproducible latency distribution or promise that every incremental step has a fixed wall-clock bound.
- **medium** — cx-constants-locality: Practical performance ratios, sorting/multiplication crossover and cache-line assumptions. Algorithm and implementation structure are source-checked; the preserved qualitative several-times performance language has no reproducible target-specific benchmark.64-byte lines and8-byte elements are explicit illustrative assumptions where calculations depend on them.
- **medium** — cx-measuring-algorithms: Historical Knuth quotation and deployment-specific timing interpretation. timeit measurement guidance is fetched and ratios recomputed. The original quotation attribution is retained but its primary paper was inaccessible through the web tool; the citation is not upgraded to high confidence.

## synth: Sound & Digital Audio

[Independent verification record](../content/synth/01-sound-sampling/verification.json)

Corrections and qualifications in this conversion:

- Moved snd-waves-q8 from wave measurements to sample-phase increment so its sampled-sine and samples-per-cycle prerequisites precede it; original ID and key retained.
- Added a local changing-frequency/absolute-time explanation and formula to wrapped-phase state before snd-waves-q11; its 44,880 Hz result independently recomputed.
- Phase preservation avoids an output-value jump but does not guarantee no transient; abrupt slope changes and finite rounding now explained in lesson and questions.
- Float headroom avoids clipping but is not lossless arithmetic; normal rounding still applies.
- Full relative float precision restricted to the normal range; subnormal precision differs.
- Digital full scale distinguished from the representable float range in dBFS prose, formula definition and question explanation.
- TPDF output error has input-independent mean and variance; removed the stronger claim that every property of nonsubtractive total error is statistically independent.
- Specified common TPDF dither as two quantisation steps peak-to-peak, including the moved dither question.
- Distinguished formal SINAD-based ENOB from the question’s explicitly requested noise-only estimate from dynamic range; added verified SINAD glossary definition.
- Separated BLIT impulse-train integration from BLEP/PolyBLEP step correction.
- FM described as generating sidebands, which need not be harmonics.
- Oversampling decimation filtering removes out-of-passband content; in-band aliases created at the oversampled rate survive.
- High-rate hard-clipping experiment greatly reduces alias contamination; finite rate cannot remove the infinite harmonic tail.
- Odd-only symmetric clipping statement restricted to a sine or other input with half-wave symmetry.
- Added DC/Nyquist endpoint exceptions to the first FFT scaling description, and excluded these bins explicitly in the amplitude question.
- Rectangular window allowed for coherent whole-cycle captures; removed universal “always window” instruction.
- Added local zero-padding and scalloping/flat-top/interpolation context before FFT-bin and leakage questions.
- DC question now specifies whole cycles of a steady waveform; lesson distinguishes partial-cycle mean from genuine DC offset.
- Full-scale sample counts labelled as warnings for investigation, not proof that clipping happened, in WAV checklist and moved questions.
- Eight-bit nearest-rounding question now explicitly excludes endpoint overload, retaining the same key.
- Block-budget question now asks about meeting each block’s deadline, rather than an average which could conceal overruns.
- Quantiser trace table reduced from five to four columns with all intermediate round/clip values retained.
- Rejected new bare fixed-point alias because current hyphenated fallback could capture mathematical fixed points in other subjects; retained precise arithmetic aliases.
- Rejected new bare phase alias because it would capture envelope “release phase” in another Synth module; used existing precise wave-phase phrase locally.
- Fractional/negative powers no longer described as fractional numbers of repeated copies; roots and reciprocals made explicit.
- Replaced obsolete original lesson-number cross-references with relevant short-unit names.

Remaining gaps:

- No original course topic removed: 68 original questions/keys, 51 original lesson equations, 20 Python lesson examples, three diagrams and two flow diagrams retained; one new sine question and one local glide formula added.
- The 295 existing glossary definitions and confidence records are inherited from prior independent verification, not claimed as a fresh exhaustive definition audit. Real source limitations are retained; ENOB/JND/phase-jump/peak-level shorthand is explicitly flagged above.
- Primary sources, formulas, all question keys/distractors and all code reviewed; claimsChecked counts 220 overlapping review units (32 lesson claim groups + 112 formula blocks + 69 question reviews + six requested alias-entry reviews + one new glossary definition), not 220 independently enumerated atomic claims.
- Offline examples and exact outputs were tested, including PCM conversion boundaries. Hardware, audible quality, embedded callback timing, board noise and processor-specific slow paths were not measured.
- BLIT/BLEP, oversampling filters and true-peak reconstruction are conceptual here; implementation depth remains in the later synthesis/audio-engineering modules.
- Repository-wide formula/glossary scans also enumerate preserved archival files; their unchanged old lint forms are out of the active short-lesson editing scope. All active formula-lint hits are real inline program code permitted by Rule 6.
- Complete app build, all-app tests and 390 px browser rendering are assigned to the coordinating session; this verifier does not modify generated data or shared compiler/app files.
- AES Pro Audio Reference was fetched with the web browser for evidence, but the final Node accessibility check returned HTTP 403. Its newly added Further reading link was removed; evidence URL remains recorded as a browser-fetched source.

Low-confidence areas:

- **medium** — glossary: coherent-sampling. No dedicated authoritative page fetched (Analog Devices article timed out); source is the Spectral leakage article
- **medium** — glossary: note-space. Course-specific term; Pitch space article supports the linear MIDI pitch-space idea
- **medium** — glossary: crest-factor. "12–20 dB for real music" is a broad typical range that varies by genre and mastering
- **medium** — glossary: zipper-noise. Source (Smoothing) is generic; definition is standard practice
- **medium** — glossary: parameter-smoothing. Source (Smoothing) is generic; definition is standard practice
- **medium** — glossary: offline-render. Source is a computer-graphics rendering article; meaning is standard audio usage
- **medium** — glossary: correlated-signals. Source (Coherence) is loose; power-addition of uncorrelated signals is standard
- **medium** — glossary: power-signal. Source (Power (physics)) is loose; mean-square definition is standard
- **medium** — glossary: vibrato. Example settings are a typical choice, not a standard
- **medium** — glossary: monitor-level. Alias "studio monitors" names the speakers rather than the level
- **medium** — glossary: audio-block. Course usage; PortAudio callback docs describe frames per buffer
- **medium** — glossary: ableton-live. Existing medium-confidence glossary record preserved. Current manufacturer manual documents C-2 to G8 full MIDI range, from which note 60 = C3 is inferred; product labels remain version-sensitive.
- **medium** — glossary: enob. Existing definition and original confidence retained unchanged as requested. Its SNR/dynamic-range shortcut describes noise-only resolution; formal ENOB uses SINAD. Active lesson/question explicitly distinguish this.
- **medium** — glossary: just-noticeable-difference. Existing definition and original confidence retained unchanged. Its 3 Hz/0.6% examples come from a secondary summary; primary research supports condition dependence, not a universal threshold.
- **medium** — glossary: phase-jump and peak-level. Existing definitions and confidences preserved. They simplify discontinuity and clipping conditions; active lessons now specify possible specially timed continuous phase changes and sample-peak versus reconstructed-peak limits.
- **medium** — snd-cents-beating: Pitch discrimination thresholds and fast-beat perceptual boundaries. Research and UNSW demonstrations support dependence on stimulus/task/listener; no universal numerical threshold established. Lesson retains only explicitly hedged secondary examples.
- **medium** — snd-midi-frequency: Ableton note-60 display label. C3 is inferred from the current manual’s full MIDI range C-2 to G8; future versions/products may use other octave labels.
- **medium** — snd-float-integer-boundary: Target-processor subnormal handling cost. Primary Intel documentation and older x86 measurements support variable penalties. No benchmark on the reader’s embedded target was performed; fixed-cycle claim removed.
- **medium** — snd-dither-converter-noise: Finished-board dynamic range and noise-only ENOB estimate. Chip figures verified with datasheet configurations and A-weighting; finished-board noise and SINAD were not measured. Dynamic-range substitution remains an explicitly approximate noise-only estimate.
- **medium** — snd-peak-rms-dbfs: AES17 convention and typical music crest-factor ranges. AES authoritative reference and indexed Audio Precision primary-manual excerpt support the conventions; full normative AES17 text not obtained. Music range is programme- and averaging-dependent and is hedged.
- **medium** — snd-wav-write-readback: PCM flooring/clipping and library conversion behaviour. Confirmed in independent experiments with soundfile 0.14.0/libsndfile 1.2.2 and inspected versioned source. Behaviour can depend on library/platform/rounding configuration; text ties it to this runtime.

