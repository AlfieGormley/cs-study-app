# Concept-first library review

Status: **in progress**. 37/60 modules and 1071/1845 active lessons have current independent editorial reviews.

This report counts only active lesson IDs from module.json. Retired subjects (os, architecture, theory, languages; see `content/retired-subjects.json`) are excluded. Pending modules have not been certified by keyword scans or by renderer tests.

The rule for future content is in [the authoring brief](concept-first-brief.md), [CONTENT_SPEC.md](../CONTENT_SPEC.md) and [the content process](CONTENT_PROCESS.md). Essential relationships remain visible; selected reference maths opens on demand. Redundant equations and routine calculation questions are removed or rewritten around interpretation, prediction and diagnosis.

Comparison baseline: `5b8fb6f2709893396373ba979ba194aacf5cb034`. Lesson IDs, question IDs and question ownership must match this baseline. Archived originals and progress migrations remain unchanged.

Focused dictionary integration corrections and exact-definition equivalence reviews are recorded in [the integration review](concept-first-integration-review.json). A focused glossary correction does not count as a completed module rewrite. Reviewer records retain checks that were pending at handoff; subsequent compiled-check closure is recorded separately in the integration report.

“Review units” below retain each independent reviewer’s stated counting method. Some are grouped claim sets, not atomic assertions; counts must not be compared as a quality score. The linked verification records preserve earlier factual/glossary history and define the fresh review scope.

| Module | Status | Lessons | Questions | Lesson formula cards before → after | Essential / reference | Question cards before → after | Glossary terms | Review units | Corrections |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| [databases / SQL Fundamentals](../content/databases/01-sql-fundamentals/verification.json) | Reviewed | 40 | 74 | 18 → 4 | 0 / 4 | 13 → 0 | 270 | 118 | 10 |
| [databases / Advanced SQL](../content/databases/02-advanced-sql/verification.json) | Reviewed | 41 | 71 | 30 → 3 | 0 / 3 | 22 → 0 | 149 | 135 | 10 |
| [databases / Relational Theory & Normalisation](../content/databases/03-relational-theory/verification.json) | Reviewed | 35 | 72 | 55 → 34 | 5 / 29 | 96 → 2 | 192 | 160 | 7 |
| [databases / Query Processing & Optimisation](../content/databases/04-query-processing/verification.json) | Reviewed | 33 | 67 | 33 → 20 | 5 / 15 | 32 → 0 | 193 | 149 | 4 |
| databases / PostgreSQL | Pending review | 13 | — | — | — | — | — | — | — |
| [dsa / Complexity Analysis](../content/dsa/01-complexity/verification.json) | Reviewed | 35 | 81 | 79 → 17 | 13 / 4 | 211 → 14 | 150 | 181 | 24 |
| [dsa / Arrays, Lists, Stacks & Queues](../content/dsa/02-linear/verification.json) | Reviewed | 32 | 67 | 23 → 15 | 2 / 13 | 31 → 0 | 293 | 181 | 8 |
| [dsa / Hash Tables & Hashing](../content/dsa/03-hashing/verification.json) | Reviewed | 37 | 73 | 48 → 26 | 4 / 22 | 55 → 0 | 158 | 182 | 9 |
| [dsa / Trees & Heaps](../content/dsa/04-trees/verification.json) | Reviewed | 35 | 80 | 38 → 15 | 5 / 10 | 37 → 0 | 170 | 207 | 12 |
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
| [networks / IP, Addressing & Routing](../content/networks/02-ip-routing/verification.json) | Reviewed | 38 | 84 | 28 → 7 | 2 / 5 | 26 → 0 | 438 | 158 | 16 |
| [networks / Transport Layer: TCP & UDP in Depth](../content/networks/03-tcp/verification.json) | Reviewed | 43 | 81 | 50 → 17 | 4 / 13 | 39 → 1 | 323 | 195 | 15 |
| [networks / Application-Layer Protocols](../content/networks/04-application/verification.json) | Reviewed | 42 | 69 | 41 → 8 | 4 / 4 | 24 → 0 | 633 | 180 | 8 |
| [networks / Network Security](../content/networks/05-network-security/verification.json) | Reviewed | 36 | 67 | 19 → 12 | 2 / 10 | 21 → 0 | 371 | 171 | 8 |
| networks / Wireless, Mobile & Modern Networks | Pending review | 37 | — | — | — | — | — | — | — |
| [react / Components and JSX](../content/react/01-components/verification.json) | Reviewed | 8 | 24 | 0 → 0 | 0 / 0 | 0 → 0 | 70 | 102 | 4 |
| [react / State and Interactive Forms](../content/react/02-state/verification.json) | Reviewed | 9 | 27 | 0 → 0 | 0 / 0 | 0 → 0 | 44 | 80 | 4 |
| [react / Hooks, Effects and Shared Logic](../content/react/03-hooks/verification.json) | Reviewed | 9 | 27 | 0 → 0 | 0 / 0 | 0 → 0 | 52 | 94 | 3 |
| [security / Security Fundamentals](../content/security/01-fundamentals/verification.json) | Reviewed | 27 | 66 | 9 → 5 | 3 / 2 | 4 → 0 | 416 | 135 | 8 |
| [security / Cryptography Basics](../content/security/02-crypto-basics/verification.json) | Reviewed | 37 | 72 | 55 → 25 | 9 / 16 | 66 → 3 | 251 | 243 | 8 |
| security / Applied Cryptography & PKI | Pending review | 39 | — | — | — | — | — | — | — |
| security / Web Application Security | Pending review | 14 | — | — | — | — | — | — | — |
| security / Systems Security | Pending review | 15 | — | — | — | — | — | — | — |
| security / Security Engineering in Practice | Pending review | 23 | — | — | — | — | — | — | — |
| [software-engineering / Design Principles & Clean Code](../content/software-engineering/01-principles/verification.json) | Reviewed | 26 | 69 | 4 → 1 | 1 / 0 | 4 → 0 | 294 | 98 | 5 |
| [software-engineering / Design Patterns](../content/software-engineering/02-design-patterns/verification.json) | Reviewed | 28 | 66 | 4 → 0 | 0 / 0 | 9 → 0 | 284 | 116 | 9 |
| software-engineering / Testing | Pending review | 22 | — | — | — | — | — | — | — |
| software-engineering / Version Control & CI/CD | Pending review | 26 | — | — | — | — | — | — | — |
| software-engineering / Software Architecture at the Code Level | Pending review | 25 | — | — | — | — | — | — | — |
| software-engineering / Engineering Practices | Pending review | 24 | — | — | — | — | — | — | — |
| [synth / Sound & Digital Audio](../content/synth/01-sound-sampling/verification.json) | Reviewed | 32 | 69 | 52 → 23 | 1 / 22 | 60 → 0 | 297 | 128 | 24 |
| [synth / Synthesis & DSP](../content/synth/02-synthesis-dsp/verification.json) | Reviewed | 44 | 82 | 56 → 18 | 4 / 14 | 60 → 0 | 112 | 234 | 18 |
| [synth / Electronics for Synth Builders](../content/synth/03-electronics/verification.json) | Reviewed | 39 | 80 | 38 → 12 | 2 / 10 | 33 → 0 | 194 | 103 | 4 |
| [synth / Embedded Audio & Interfaces](../content/synth/04-embedded-audio/verification.json) | Reviewed | 44 | 90 | 33 → 5 | 1 / 4 | 34 → 0 | 374 | 133 | 5 |
| [synth / MIDI & Studio Integration](../content/synth/05-midi-studio/verification.json) | Reviewed | 44 | 74 | 30 → 15 | 6 / 9 | 34 → 1 | 173 | 149 | 3 |
| [synth / Audio Engineering](../content/synth/06-audio-engineering/verification.json) | Reviewed | 50 | 100 | 91 → 37 | 6 / 31 | 77 → 0 | 447 | 210 | 9 |
| [system-design / Fundamentals](../content/system-design/01-fundamentals/verification.json) | Reviewed | 27 | 84 | 42 → 12 | 0 / 12 | 65 → 0 | 379 | 130 | 23 |
| [system-design / Networking & Traffic](../content/system-design/02-networking/verification.json) | Reviewed | 34 | 96 | 22 → 7 | 3 / 4 | 40 → 0 | 433 | 176 | 9 |
| [system-design / Caching](../content/system-design/03-caching/verification.json) | Reviewed | 39 | 84 | 37 → 12 | 2 / 10 | 38 → 0 | 355 | 195 | 7 |
| [system-design / Databases & Storage](../content/system-design/04-databases/verification.json) | Reviewed | 37 | 98 | 21 → 6 | 2 / 4 | 34 → 0 | 311 | 202 | 7 |
| system-design / Distributed Systems & Consensus | Pending review | 40 | — | — | — | — | — | — | — |
| system-design / Messaging & Streaming | Pending review | 34 | — | — | — | — | — | — | — |
| system-design / API Design | Pending review | 38 | — | — | — | — | — | — | — |
| system-design / Architecture & Scaling Patterns | Pending review | 41 | — | — | — | — | — | — | — |
| system-design / Reliability, Operations & Security | Pending review | 38 | — | — | — | — | — | — | — |
| system-design / Case Studies I | Pending review | 43 | — | — | — | — | — | — | — |
| system-design / Case Studies II | Pending review | 42 | — | — | — | — | — | — | — |

The report certifies editorial provenance only. Build, migration, rendering, offline and deployed-version evidence must be checked separately before publication.

## databases / SQL Fundamentals

14 question objects changed. Every changed question has a specific independent-review reason in the linked record.

**Corrections in this review:**

- sql-affinity-natural-keys: the author's analogy callout began mid-paragraph ('...updating them all. > [!analogy] ...'), so markdown.js rendered literal '> [!analogy]' text and a plain visible quote instead of a closed disclosure -> callout moved to its own block (render re-checked: 17 analogy disclosures, no stray markers).
- sql-exact-money-types (+ sql-schema-ddl-q1 workedExample): author stated SQLite 3.52.0 and later display 0.1 + 0.2 as 0.30000000000000004 -> 3.52.0 was withdrawn (changes.html) and the 3.53.0 release notes make 17-digit rounding the default; now '3.53.0 and later show ... by default; earlier releases round to 15 significant digits'. Executed in 3.51.0 (0.3) and 3.53.0 (0.30000000000000004).
- sql-alter-sqlite: 'adding and dropping named CHECK constraints' -> 'adding CHECK constraints and dropping a named constraint with DROP CONSTRAINT' (SQLite 3.53.0 executed: unnamed ADD CHECK accepted; DROP CONSTRAINT requires a name).
- sql-generated-identifiers: 'Delete product 5 and the next insert gets id 5 again' was not reproducible on the shop fixture, whose enforced foreign keys refuse to delete the Mug -> example now uses a table holding ids 1 to 5, with a note about the shop's FK refusal (both executed).
- sql-outer-predicates analogy limit: 'A teacher might treat a blank as no and keep it' contradicted the mapping -> limit now explains that a padded NULL makes tests UNKNOWN, so even o.status <> 'pending' drops padded rows unless OR o.id IS NULL is added (executed).
- sql-group-single-value analogy: false contrast 'unlike a sorting clerk, SQL puts every NULL label into one shared tray' -> states the real surprise (NULLs pooled although NULL = NULL is not true elsewhere); 'Sort a pile' (opened query-processing Sort node) -> 'Divide a pile'.
- sql-delete-transactions analogy limit: 'unlike an email, a committed change cannot be unsent' (emails cannot be unsent either) -> 'just as a sent email cannot be recalled, ROLLBACK cannot undo a committed change'.
- sql-inner-join-pairs analogy: 'candidate list' linked to the security dictionary-attack glossary entry -> 'list of candidates'.
- sql-statement-error-recovery analogy: 'sequence numbers' (opened an API-design sequence-number entry) and 'roll back' (deploy rollback sense) -> 'values already taken from a PostgreSQL sequence' and `ROLLBACK`.
- Glossary integer-type: alias '32-bit' made every '32-bit' in the databases subject open the INTEGER column-type definition, including PostgreSQL 32-bit transaction-ID counters in 05-postgresql -> alias removed (kept '32-bit integer') and new generic entry thirty-two-bit added, mirroring the existing 64-bit entry.

**Scope gaps and exclusions:**

- Advanced SQL subqueries, CTEs, windows, upserts and recursive queries receive brief previews and remain assigned to the following module; this preserves the original module boundary.
- Normalisation theory and physical query processing are signposted to their dedicated modules.
- Native fixtures substantiate semantics and observed plans, not universal production throughput or latency guarantees.
- No browser render at 390 px in this pass; renderer-level check only (markdown.js, renderer and diagram tests).
- PostgreSQL claims executed on 18.6 only; version-gated statements (PostgreSQL 11 defaults, 12 SET NOT NULL skip, 15 NULLS NOT DISTINCT, 18 uuidv7 and nondeterministic LIKE) rely on the fetched docs for their starting versions.
- Advanced SQL (subqueries, CTEs, windows, upserts) remains assigned to module 2.

**Low-confidence areas, including preserved qualifications:**

None recorded in this editorial review.


## databases / Advanced SQL

24 question objects changed. Every changed question has a specific independent-review reason in the linked record.

**Corrections in this review:**

- C1 asql-window-ranking analogy: "dead heat" yet "finish-line camera still lists one of them first" (self-contradictory: a dead heat is declared because the photo cannot separate them) -> results printout must put one name above the other; limit reworded (printer may choose a rule; ROW_NUMBER none) + convention-varies note.
- C2 asql-conditional-pivots: per-customer month-count table listed Ana, Dev, Eve only (Ben and Cat silently omitted from a 5-customer result) -> added Ben 1/0/1 and Cat 0/1/1 (executed SQLite 3.51).
- C3 asql-relational-division: author moved the COUNT vs COUNT(DISTINCT) pitfall (Ana counted 3 and excluded; Kettle-twice-no-Mug wrongly passes) inside the collapsed analogy's 'Where it stops', hiding a fact that question asql-interview-problems-q4 tests -> restored as visible prose after the callout.
- C4 asql-median-rows: "part of the SQLite source from 3.51.0 ... the macOS 3.51.0 CLI had it" misattributed why the CLI works: the sqlite3 CLI has bundled median()/percentile*() since 3.47.0 (changes.html), whereas the library amalgamation includes it from 3.51.0 only with SQLITE_ENABLE_PERCENTILE (and before that it was in the source tree as a separately compiled loadable extension, so "part of the source from 3.51.0" was wrong). macOS /usr/bin/sqlite3 PRAGMA compile_options has no ENABLE_PERCENTILE yet median() works. Reworded; also noted SQLite's percentile_cont(total, 0.5) spelling (no WITHIN GROUP without SQLITE_ENABLE_ORDERED_SET_AGGREGATES).
- C5 glossary sqlite-percentile-extension: same "included in the SQLite source from 3.51.0" error -> amalgamation from 3.51.0 behind SQLITE_ENABLE_PERCENTILE; CLI since 3.47.0. Example reworded.
- C6 asql-json-storage analogy limit: 'jsonb ... discards only presentation details such as whitespace, key order and duplicate keys' overstated fidelity (executed PG 18.6: '1.230e-5' -> 0.00001230, 'é' -> é) and called dropped duplicate keys presentation -> values kept but spelling may be rewritten; original text (whitespace, key order, earlier duplicate keys) not kept.
- C7 asql-atomic-upserts analogy limit: 'waits ... until the first transaction commits or rolls back' implied the waiter then always succeeds; two-session test on PG 18.6 (race.sh/race.out): same-key waits on transactionid lock (new and existing key, DO UPDATE and DO NOTHING), different key does not wait; after commit READ COMMITTED takes the update path (2 -> 12, 1 -> 17) but REPEATABLE READ fails 'could not serialize access due to concurrent update' -> limit now states both outcomes.
- C8 asql-upsert-batch-replace: author moved the REPLACE side effects (delete triggers only with recursive_triggers, ON DELETE CASCADE removes child rows) and the 'use DO UPDATE' advice from visible prose into the collapsed analogy limit; question asql-json-upsert-q5's workedExample relies on them -> restored as visible prose after the callout (executed SQLite 3.51/3.53: child row cascaded, trigger logged only with PRAGMA recursive_triggers=ON).
- C9 glossary wrong-sense links in new author prose: exists-null-trap analogy "rule of three-valued logic" opened software-engineering 'rule-of-three' -> "fixed rules of SQL's three-valued logic"; correlated-subqueries analogy (x2) and quantified-comparisons "outer row" opened databases/04 join outer/inner side -> "row of the outer query". (My own new upsert text: "serialization error" would open system-design entry -> "serialization failure", this module's own entry.)
- C10 pre-existing wrong-sense cross-subject links reworded in this module: 'request deduplication' (atomic-upserts intro) opened React request-sharing -> 'must recognise and skip a repeated request'; 'error handling' (merge-concurrency) opened JavaScript try...catch -> 'raise errors that the application must handle or retry'. 'result types' in unchanged question asql-ctes-q9 (opens software-engineering Result/error-value) recorded as integration dependency instead of editing an unchanged question.

**Scope gaps and exclusions:**

- Historical minimum versions checked in official version-specific manuals/releases rather than obsolete binaries.
- Production latency, index-size and plan-selection comparisons remain conditional; native fixtures demonstrate mechanisms rather than workload benchmarks.
- As the author reported, the module has no transaction-isolation or general indexing lessons (only JSON indexes and upsert concurrency); those topics live in other modules.
- Several lessons keep one question (e.g. asql-quantified-comparisons, asql-set-precedence, asql-revenue-thresholds); no questions were added in this pass.
- LATERAL vs ROW_NUMBER performance (asql-top-group-strategies, q10) is argued from plan mechanics, not a large-table timing run.
- Older-version behaviour (PostgreSQL 11 CTE fence, PG 13/14 hash_mem_multiplier 1.0, PG < 16 subquery alias, SQLite thresholds 3.24-3.47) verified from release notes only; no old binaries executed.

**Low-confidence areas, including preserved qualifications:**

- medium confidence, asql-json-indexes: Relative production performance and physical I/O of the conditional plan/index strategy. Documented mechanism and native small fixtures checked; no production benchmark is claimed. Text states data, selectivity, visibility and planner qualifications.
- medium confidence, asql-subquery-plans: Relative production performance and physical I/O of the conditional plan/index strategy. Documented mechanism and native small fixtures checked; no production benchmark is claimed. Text states data, selectivity, visibility and planner qualifications.
- medium confidence, asql-top-group-strategies: Relative production performance and physical I/O of the conditional plan/index strategy. Documented mechanism and native small fixtures checked; no production benchmark is claimed. Text states data, selectivity, visibility and planner qualifications.
- medium confidence, asql-window-last-value: Relative production performance and physical I/O of the conditional plan/index strategy. Documented mechanism and native small fixtures checked; no production benchmark is claimed. Text states data, selectivity, visibility and planner qualifications.
- medium confidence, asql-median-rows: Which SQLite builds expose median()/percentile functions. Primary docs (percentile.html, compile.html, 3.51.0 release notes, changes.html 3.47.0) and three builds checked (macOS 3.51.0 CLI and Homebrew 3.53.0 CLI have them; node:sqlite 3.53.0 too), but third-party/embedded builds vary; the lesson now hedges and recommends the portable query.
- high confidence, asql-atomic-upserts: Analogy limit: a second session waits only on the same unfinished key; READ COMMITTED then inserts/updates; REPEATABLE READ can fail with a serialization failure. Two-session test (5 cases) on PG 18.6 plus transaction-iso and index-unique-checks docs; SERIALIZABLE not separately executed, so the text says 'a stricter level such as REPEATABLE READ'.
- high confidence, asql-merge-concurrency: PG 18 RETURNING old/new for INSERT, UPDATE, DELETE and MERGE. Release-18 notes and executed for all four statements in PG 18.6.
- medium confidence, asql-window-ranking: Dead-heat placing convention (shared place, next skipped). Sporting conventions vary; the analogy now says so. Teaching aid only, not a factual claim the questions rely on.
- medium confidence, module-wide: Version thresholds for PostgreSQL < 18 (11 CTE fence, 12 inlining, 13 WITH TIES/hash_mem_multiplier, 14 SEARCH/CYCLE, 15 MERGE/run conditions/hash_mem 2.0, 16 optional subquery alias, 17 MERGE RETURNING) and SQLite < 3.51 (3.24 upsert, 3.25 windows, 3.28 GROUPS, 3.30 FILTER, 3.35 RETURNING/MATERIALIZED, 3.44 ordered aggregates, 3.45 JSONB, 3.47 CLI percentile). Each confirmed in the official release notes or version-specific manual; behaviour executed only on PG 18.6 and SQLite 3.51.0/3.53.0.
- medium confidence, asql-subquery-plans: A hashed SubPlan must fit its size estimate within work_mem x hash_mem_multiplier. Defaults verified in docs; the switch to a plain SubPlan reproduced by lowering work_mem in PG 18.6; the exact estimate rule is in planner source rather than user documentation.


## databases / Relational Theory & Normalisation

41 question objects changed. Every changed question has a specific independent-review reason in the linked record.

**Corrections in this review:**

- C1 rel-th-bcnf-and-prime: 'can pass 3NF but fail BCNF only when it has overlapping composite candidate keys' left the condition vague and unattributed → now states the exact necessary condition (at least two candidate keys, both composite, sharing at least one attribute), says it is necessary but not sufficient, and attributes it to Vincent & Srinivasan (1993). Verifier proved the condition independently (evidence exec/3nf-bcnf-proof.txt) and found 0 counterexamples among 4,556 random 3NF-not-BCNF schemas.
- C2 rel-th-dependency-sql: 'Optimisers use FDs to drop redundant grouping or sorting columns' → PostgreSQL drops GROUP BY columns determined by the primary key (9.6) or a unique index on NOT NULL columns (18), and uses unique keys to prove a join cannot multiply rows. EXPLAIN on 18.6 showed ORDER BY id, name keeps both sort keys, so the sorting claim was unsupported and removed; nullable unique index was not used.
- C3 rel-th-functional-deps-q10: the question needed the 3NF prime-attribute rule four units before it is taught, and its option 3 depended on BCNF → prompt now states the 3NF rule in one sentence; option 3 replaced by a distractor that tests the same rule (D fixes A, A is prime); BCNF mentions labelled as a later topic.
- C4 rel-th-functional-deps-q3: prompt claimed 'The options use functional-dependency notation' although all options are prose → sentence and the generic X → Y card removed.
- C5 rel-th-algebra-q9: the formula card's In words line referred to '∅ in the options', which no option uses, and option 2's explanation used π notation in prose → prompt rewritten in words; explanation reworded.
- C6 rel-th-anomalies-and-1nf: dangling sentence 'The formula below states the business rules. Every card defines its notation locally...' (placed before the section that contains the card) removed; lead-in now states the rules hold in every legal state.
- C7 rel-th-decomposition-algorithms: attribution of the extra key relation in 3NF synthesis now names Biskup, Dayal and Bernstein (1979) (hedged as 'notably'; medium confidence).
- Formula load (not counted as accuracy corrections): lesson essential cards 13 → 5 (8 demoted to reference where visible prose and the visible In words line carry the relationship: set-operators 'not enrolled', theta join, division, equivalent-plans expression, FD formal definition, shop FDs, 2NF partial dependencies, Teaching FDs); question formula cards 21 → 2 (19 removed from 19 questions; kept only algebra-q1 and algebra-q8, which test reading σ/π/ρ notation that rel-th-restrict-project-rename keeps essential).

**Scope gaps and exclusions:**

- Full prime-attribute NP-completeness proof was not retrieved; primary publisher abstract checked.
- Flat 1NF and atomicity are explicitly chosen modeling conventions; no universal SQL array prohibition is asserted.
- Finite native and mathematical cases corroborate examples, while general algebra, normal-form and inference theorems rely on primary definitions and proofs.
- Workload latency and ratio examples are illustrative calculations rather than measured performance promises. Higher-normal-form unit introduces predicates and counterexamples, not a full chase implementation.
- No new topics added; as before, the module does not cover temporal/bitemporal modelling, domain-key normal form beyond a mention, or a worked 5NF decomposition.
- glossary-coverage still lists bold step labels, single-letter attribute names and emphasis words; not converted (consistent with earlier records).
- Original papers for Vincent & Srinivasan (1993), Biskup/Dayal/Bernstein (1979), Bernstein (1976) and Lucchesi/Osborn (1978) could not be read (paywalled or scanned without OCR); see lowConfidence.
- Further-reading lists in the denormalisation units still repeat shared module links (pre-existing).

**Low-confidence areas, including preserved qualifications:**

- medium confidence, rel-th-enumerate-keys: Prime-attribute decision is NP-complete for a schema with an FD basis. Primary Lucchesi/Osborn publisher abstract explicitly states the theorem. Full proof was not retrieved; numerical key enumeration was independently checked.
- medium confidence, rel-th-anomalies-and-1nf: Atomicity and 1NF under the explicitly chosen classical flat convention. Textbook-author source supports flat domains; relational domain conventions vary. The lesson and array question explicitly declare their flat convention.
- medium confidence, rel-th-bcnf-and-prime: Attribution of the 3NF-not-BCNF overlapping-composite-keys condition to Vincent & Srinivasan (1993), IPL 48(6):281–283. The mathematical condition is high confidence (verifier's own proof plus exhaustive random check); the paper itself is paywalled and its zbMATH summary is withheld, so the attribution rests on Crossref metadata and Wikipedia's citation of it. Zaniolo (1982) is not cited in the lesson; it concerns elementary-key normal form.
- medium confidence, rel-th-decomposition-algorithms: The extra candidate-key relation in 3NF synthesis comes from later refinements of Bernstein (1976), notably Biskup, Dayal & Bernstein (1979). Bernstein 1976 PDF available only as scanned images; Biskup et al. 1979 abstract elided by the publisher. Bibliographic records (Semantic Scholar, bibtex.github.io) and an R implementation citing Bernstein's synthesis with an optional key relation support the wording, which is hedged.
- medium confidence, rel-th-enumerate-keys: Lucchesi and Osborn (1978) showed that deciding whether an attribute is prime is NP-complete. Original paper paywalled; confirmed by the abstract of Demetrovics & Thi (Acta Cybernetica 11(3), 1994), which states the result and cites Lucchesi & Osborn, plus Crossref metadata for the 1978 JCSS paper.
- medium confidence, rel-th-precomputed-results: Oracle fast-refresh materialised views and SQL Server indexed views maintain results incrementally, with query-shape restrictions. Carried from the earlier verified text; not re-fetched in this pass (vendor docs listed in the top-level sources).


## databases / Query Processing & Optimisation

41 question objects changed. Every changed question has a specific independent-review reason in the linked record.

**Corrections in this review:**

- V1 qp-hash-partition-io: 'If many rows share a key ... some partitions are too big and must be partitioned again' implied repartitioning fixes key skew. Rehashing cannot split rows that share one join-key value (PostgreSQL nodeHash.c disables further nbatch growth and lets the batch exceed its budget) -> body now says repartitioning helps only for a badly spread hash, and a single very common key must be joined another way or allowed to exceed memory; analogy limit and takeaway updated.
- V2 qp-join-variants: 'the hash join (8 batches, 587 ms) beat a merge join that had to sort 3 million rows' was presented as a general result, but in the module's own dataset (order_items(order_id) index present) PostgreSQL 18.6 merge-joined two index scans with no sort and finished faster (768 vs 818 ms) though estimated costlier -> reframed as one illustrative run without that index, with a caveat that an index can remove the sort and change the comparison.
- V3 qp-external-join-io-q1 option 3 explanation: 'only possible when one input fits in memory for an in-memory hash join' -> 'needs one input to fit in memory, as in an in-memory hash join' (a block nested loop with one input in memory also reads each table once).
- V4 qp-index-page-selectivity: 'the index halved the time' for 23 ms vs 9.3 ms (less than half) -> 'the bitmap scan took well under half the time', labelled as an illustrative run.
- H1 (hedge, not an error) illustrative-run labels added to single-run figures: qp-pull-and-blocking LIMIT 5 (85 rows/2 pages are position-dependent; my run read 354 rows/7 pages), qp-hash-join-mechanics 16% spill slowdown (27% in my run), qp-composite-index-order '2,400 descents' (2,401 here), qp-plan-operators 47 ms, qp-sargable-predicates 7.6x, qp-subquery-semantics 4x, qp-covering-partial-indexes 25x.
- Author corrections re-verified and kept: generic-plan behaviour (qp-generic-plans-counts, qp-anti-patterns-q9) against plancache.c and execution; SQLite USE TEMP B-TREE FOR ORDER BY; extended-statistics estimate about 12,400; hash build-side relabel; EXISTS Semi Join hedge; merge-join causal claim removed; refresh-statistics cross-reference; 'fixture' wording; Content-gap notes removed from 11 question objects.

**Scope gaps and exclusions:**

- Original laptop timing provenance is unavailable. Existing active notes label plan numbers as hypothetical teaching inputs, not measured performance promises.
- Vendor behaviour is verified at the explicit PostgreSQL18/17, MySQL8.0 and cited documentation versions; illustrative cost and cardinality models intentionally state simplifying assumptions. This short-lesson split retains the original scope rather than adding a complete DBMS implementation.
- Plan figures are illustrative from one generated dataset; the setup script that reproduces most of them (evidence cf2-dbs-query-author2/sql/setup-pg.sql) is not shown to the reader.
- Parallel query, JIT tuning and join-order hints (pg_hint_plan) are only mentioned or out of scope; all examples are serial.
- Some questions cite figures 'in the lesson' that appear in a sibling lesson (qp-reading-explain-q7 cites explain-loops; qp-reading-explain-q11 cites the composite-index lesson); left unchanged as the figures are present in the module.
- The join-variants cost table (23,290 / 25,539 / 30,572 / 46,172,536) is from the original run; mine gave 23,224 / 26,430 / 33,186 (Memoize) / 98.7 million, same ordering, so 'about 2,000 times' holds only for that run (the text calls the table illustrative).

**Low-confidence areas, including preserved qualifications:**

- medium confidence, qp-selectivity-dependencies: Welsh analogy proportions: one in twenty people from Wales, one in a hundred speaking Welsh, nearly all Welsh speakers from Wales. Framed as a hypothetical stadium. Census 2021 gives 538,300 Welsh speakers aged 3+ (17.8% of Wales), about 0.8% of the UK population, and Wales is about 4.6% of the UK, so the round figures are UK-like but not exact; the share of Welsh speakers living outside Wales was not fetched.
- medium confidence, all PostgreSQL lessons: Timings, buffer counts, row counts and plan costs in plan excerpts. Machine-, cache-, sample- and data-dependent. Shapes and exact cost-model figures reproduced; single-run numbers differ and are labelled illustrative (lesson headers plus the run-specific labels I added).
- medium confidence, qp-selectivity-dependencies / qp-statistics-optimiser-q5: Extended-statistics estimate about 12,400 (12,423 in one run). Sample-dependent: my two ANALYZE runs gave 12,283 and 12,343. The text says the figure varies with the sample.
- medium confidence, qp-index-maintenance / qp-covering-partial-indexes / qp-index-tuning-q11: Date index size '6.9 MB'. pg_size_pretty shows 6,912 kB (6.75 MiB); the figure is 6,912 kB divided by 1,000. Not material to any answer; left unchanged.


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


## dsa / Arrays, Lists, Stacks & Queues

48 question objects changed. Every changed question has a specific independent-review reason in the linked record.

**Corrections in this review:**

- lin-array-shrink-boundaries: the vague 'very recent CPython 3.14-branch source also skips shrinking small allocations' is now the verified scope. gh-158592 (no shrink while allocated ≤ 32) first ships in CPython 3.14.9 and 3.15.1, both released 21 Oct 2026; it is absent from 3.14.8 and 3.15.0. Thrash wording now matches q10's 'half full or less' rule. (Edit first drafted by the stopped verifier; independently re-verified and adopted.)
- lin-array-runtime-layouts: 'common libraries use factors such as 2 or 1.5' now names the verified factors: libstdc++ (_M_check_len) and libc++ (__recommend) double, MSVC (_Calculate_growth) grows by half. (Stopped-verifier draft, re-verified and adopted.)
- glossary modulo: the definition now warns that C and Java % can return a negative remainder (−1 % 5 is −1) while Python's takes the divisor's sign (4). Added the alias 'modulo' so DSA lessons open the remainder-operation entry instead of dsa/07's 'Modulus' (the divisor). (Stopped-verifier draft, re-verified and adopted.)
- glossary fifo: added the aliases 'FIFO queue' and 'FIFO queues' so the phrase no longer falls back to networks/03-tcp's router-specific FIFO entry. (Stopped-verifier draft, adopted.)
- lin-stack-shunting-yard: the associativity card is now reference, with a standalone In words giving 512 vs 64, and the analogy's naming claim matches the source ('named because its operation resembles a railroad shunting yard'). (Stopped-verifier draft, re-verified and adopted.)
- lin-list-techniques-q9: options B, C and D's feedback counted the extra iteration as 'stepping onto None'; it is the switch from None to the other list's head (13 iterations measured).
- lin-arrays-q8: option A's feedback used O(n²) without defining n; it now says n is the side length, 4,096.
- lin-array-cache-row-layout: 'built-in C or C++ array' opened React's 'Built-in' dictionary entry; reworded to an explicit `int grid[3][4]` example.

**Scope gaps and exclusions:**

- All six original topics retained across32 focused units; substantive diagrams/native fragments preserved apart from the two explicitly documented conversion/trace-format changes. No original question was lost, added, retyped, relevelled or rekeyed.
- No physical hardware locality/latency benchmark, allocator real-time test, GC timing, concurrent ring/lock-free-stack verification, service load test or user-visible grapheme production parser was executed. The content states those limits.
- Both C++ snippets were compiled in an isolated GCC14/libstdc++14 container. ASan reports expected use-after-free for the deliberately unsafe quiz under this implementation; no particular undefined output, universal initial capacity or growth factor is guaranteed. No stalled host sanitizer was rerun.
- The two merge-question ellipsis skeletons are labelled partial and executed only on empty inputs to avoid presenting them as full merges; the complete lesson merge was executed on sorted inputs, ties and disjoint lists.
- Intel landing page and ARM manual paths returned403; AMD portal returned an HTML shell and an attempted direct AMD PDF failed. They are not claimed as factual hardware corroboration. The active hardware example now explicitly assumes64-byte lines and removes unsupported speed ratios.
- Original-reader links include authoritative secondary explanations. Actual source claims use independently fetched CPython/OpenJDK/Unicode/C++/Linux/NumPy material and direct derivation; this report does not claim a unique sentence-to-primary-source mapping for every prose sentence.
- Whole isolated release/mobile rendering, original-progress dates, offline update and publication are the coordinator’s checks; no shared generated files were written by this verifier.
- AddressSanitizer did not finish on this macOS host (killed after 60 s). A plain libc++ build confirms reallocation (capacity 3 → 6 … 192) and a stale read printing 2, so the use-after-reallocation claim rests on the standard's invalidation rule and that run.
- Rendering at 390 px, closed-disclosure keyboard/touch checks and offline loading were not run by this verifier.
- Cache-locality effects (cache-row layout, linked-list scans, vector vs list) were not benchmarked; the lessons state them as hardware- and workload-dependent.
- Lesson level metadata (for example FIFO basics marked advanced) was not changed; this is outside the concept-first scope.

**Low-confidence areas, including preserved qualifications:**

- medium confidence, lin-array-cache-row-layout: Cache locality effects depend on hardware and workload; no latency or speed ratio was measured. The numerical example now assumes a64-byte line rather than certifying a universal size. Cache locality effects depend on hardware and workload; no latency or speed ratio was measured. The numerical example now assumes a64-byte line rather than certifying a universal size.
- medium confidence, lin-array-runtime-layouts: CPython3.14/OpenJDK21 details checked against fetched source; growth, reference width and GIL/free-threaded resize paths are implementation-dependent and time-sensitive. Illustrative JVM storage is an assumed model, not a measured object layout. CPython3.14/OpenJDK21 details checked against fetched source; growth, reference width and GIL/free-threaded resize paths are implementation-dependent and time-sensitive. Illustrative JVM storage is an assumed model, not a measured object layout.
- medium confidence, lin-string-immutable-sharing: Runtime-specific sharing/interning examples checked against current source; language implementations and optimisation paths may change. Runtime-specific sharing/interning examples checked against current source; language implementations and optimisation paths may change.
- medium confidence, lin-string-unicode-units: Encoding units and scalar/grapheme distinctions verified against Unicode/PEP393; runtime compact-string representations are implementation/version-specific. Encoding units and scalar/grapheme distinctions verified against Unicode/PEP393; runtime compact-string representations are implementation/version-specific.
- medium confidence, lin-string-building-cost: Full-copy model and newline-inclusive arithmetic verified, but actual allocation/optimisation/performance depends on compiler/runtime; no timing benchmark is asserted. Full-copy model and newline-inclusive arithmetic verified, but actual allocation/optimisation/performance depends on compiler/runtime; no timing benchmark is asserted.
- medium confidence, lin-string-operation-pitfalls: Historical Java7u5 versus7u6 source directly confirms proper-substring copying. CPython search thresholds and cached-object shortcuts are version-dependent. Historical Java7u5 versus7u6 source directly confirms proper-substring copying. CPython search thresholds and cached-object shortcuts are version-dependent.
- medium confidence, lin-list-circular-tradeoffs: Portable pointer/iterator contracts checked; real allocation/locality/latency trade-offs are explicitly workload-dependent and not benchmarked. Portable pointer/iterator contracts checked; real allocation/locality/latency trade-offs are explicitly workload-dependent and not benchmarked.
- medium confidence, lin-list-reversal-pattern: Native algorithm and bounded cases verified; startup/default recursion limit checked against CPython header and configured runtime, rather than a universal safe input length. Native algorithm and bounded cases verified; startup/default recursion limit checked against CPython header and configured runtime, rather than a universal safe input length.
- medium confidence, lin-list-middle-cycle-detection: Detection proof and625 independent shapes verified. Named-algorithm historical attribution rests on fetched authoritative reference rather than an original Floyd publication. Detection proof and625 independent shapes verified. Named-algorithm historical attribution rests on fetched authoritative reference rather than an original Floyd publication.
- medium confidence, lin-list-cycle-entry-proof: Reset proof recomputed including completed slow laps and head-start cycles; named historical attribution uses an authoritative reference. Reset proof recomputed including completed slow laps and head-start cycles; named historical attribution uses an authoritative reference.
- medium confidence, lin-stack-storage-choices: Standard-library operation contracts and native snippets verified; Treiber/ABA/reclamation are an introductory conceptual outline, not a validated concurrent implementation or latency guarantee. Standard-library operation contracts and native snippets verified; Treiber/ABA/reclamation are an introductory conceptual outline, not a validated concurrent implementation or latency guarantee.
- medium confidence, lin-stack-nested-state: Ordinary call-frame model explicitly qualified; native thread-stack layout/failure and CPython guarded frames vary by runtime and configuration. Ordinary call-frame model explicitly qualified; native thread-stack layout/failure and CPython guarded frames vary by runtime and configuration.
- medium confidence, lin-stack-shunting-yard: Conversion/evaluation traces recomputed independently. Full production grammar with unary operators/functions is expressly outside this short unit. Conversion/evaluation traces recomputed independently. Full production grammar with unary operators/functions is expressly outside this short unit.
- medium confidence, lin-queue-ring-full-overload: Single-threaded ring, bitmask and constant-rate backlog models verified; concurrent wraparound protocols and production service throughput are separate contracts. Single-threaded ring, bitmask and constant-rate backlog models verified; concurrent wraparound protocols and production service throughput are separate contracts.
- medium confidence, lin-queue-deque-ends: CPython3.14 block source and Java21 docs verified; implementation layout and individual thread-safe operations are not whole-protocol atomicity guarantees. CPython3.14 block source and Java21 docs verified; implementation layout and individual thread-safe operations are not whole-protocol atomicity guarantees.
- medium confidence, lin-queue-priority-ties: Python3.14 max-heap APIs/Java21 contracts checked; level/shift models are abstract operations and do not certify a measured speedup. Python3.14 max-heap APIs/Java21 contracts checked; level/shift models are abstract operations and do not certify a measured speedup.
- medium confidence, lin-array-shrink-boundaries: CPython 3.14.9/3.15.1 and later do not shrink lists with 32 or fewer allocated slots. Verified in tagged source and on the python.org release pages, but implementation detail is version-specific and could change again; the local 3.14.4 still shrinks small lists.
- medium confidence, lin-array-runtime-layouts: CPython growth formula and resize paths, OpenJDK 21 ArrayList growth, and libstdc++/libc++/MSVC vector growth factors. Read in current sources and partly measured, but implementation-specific and time-sensitive; the lesson labels them implementation details.
- medium confidence, lin-array-runtime-layouts: About 20 bytes per boxed Integer element vs 4 for int[] (q11 illustration). Measured 20.1 B/element on JDK 21 and 25 with default flags (compressed oops); larger heaps, other JVMs or flags change it. Presented as illustrative.
- medium confidence, lin-queue-deque-ends: C++ std::deque is typically an array of pointers to fixed-size chunks. [deque.overview] specifies complexity, not layout; hedged as typical.
- medium confidence, lin-array-cache-row-layout: 64-byte cache lines and the resulting locality advantages. Hardware-dependent; stated as the lesson assumption and not measured here.


## dsa / Hash Tables & Hashing

45 question objects changed. Every changed question has a specific independent-review reason in the linked record.

**Corrections in this review:**

- hash-table-interface: 'You never search the rest of the array' overstated lookup (open addressing probes other slots). Now: 'You never scan the whole array; at most you check the few keys that landed in the same place.'
- hash-maps-sets-q4: option B's explanation said 3 s is the balanced-tree (logarithmic per insert) shape; doubling n log n work gives about 4.3 s. Now explains that 3 s would be sub-linear growth, impossible when each insert scans a longer chain.
- hash-collision-robin-hood: the analogy said 'nobody ends up walking the whole length of the train', contradicting the lesson's own linear adversarial worst case. Now 'the total walking stays the same, but the longest walks get shorter', and the mapping states why the total is invariant under linear probing (verified by argument and 2,000 random trials).
- hash-collision-swiss-designs and glossary swiss-table: Swiss tables were 'presented in 2017' / '(Abseil, 2017)'. Now 'presented at CppCon in 2017 and open-sourced in Abseil in 2018' (Abseil 2018 announcement; Go Swiss-table blog). swiss-table is owned by this module (no earlier dsa owner).
- hash-resize-hysteresis-incremental: Redis's extra rehash work came from 'a background timer'. It runs in the server's periodic housekeeping cron (activerehashing, default yes, about 1 ms per 100 ms), not a background thread; now 'by default, a little extra work from its periodic housekeeping timer'.
- hash-prob-bloom-sizing (prose and reference In words) and hash-probabilistic-q4: 'about 0.69 hashes per bit per item' garbled k = (m/n) ln 2. Now 'about 0.69 times the bits per item'.
- hash-probabilistic-q12: option A's feedback cited an exponent in what is now optional maths; option D's 'position-setting load is approximately 1.46' was opaque. Both now explain about 77% of bits set and 0.77^7 ≈ 16% in words.
- hash-probabilistic-q7: worked step 1 said each filter 'independently' contributes expected reads, contradicting step 2 (linearity needs no independence). 'independently' removed.
- hash-functions-q12: option D's explanation stated the correct rule as though describing the option; now says it wrongly gives the arriving character weight 31² and subtracts only 97.

**Scope gaps and exclusions:**

- All substantive original topics are retained. This split does not add a full production hash-map implementation, a production-compatible Count-Min hash family, or a full HyperLogLog implementation.
- Tombstone and Robin Hood examples remain explicit fragments with preconditions. Independent fixtures validate their demonstrated behaviours; they are not complete general-purpose containers.
- No live cache/database/CDN I/O, distributed server movement, SIMD throughput, or workload latency benchmark was performed. Probe/formula numbers are models, not measurements.
- No original unsupported 0.84% Bloom benchmark or comparisons-per-second throughput estimate was restored; their existing evidence-gap notes remain.
- Full release build, generated dictionary integration, phone rendering, offline/PWA and publication are performed by the coordinator in an isolated release checkout. This verifier changes only its module source and verification record.
- Backward-shift deletion and cuckoo-hash insertion remain prose-only, as before.
- Rendering was checked with the app's markdown renderer (all 17 analogies become closed <details>; no literal callout tags or stray Markdown outside code), not in a browser at 390 px or offline; leave the device/offline check to the orchestrator.
- Celis's 1986 thesis was fetched but is a scanned PDF without extractable text; the Robin Hood total-distance invariant rests on the occupied-set argument plus 2,000 randomised trials rather than a quoted primary sentence.

**Low-confidence areas, including preserved qualifications:**

- medium confidence, hash-table-interface: Version/build-dependent runtime behaviour, vendor examples, practical speed or finite-sketch accuracy Core algorithm and documented implementation facts were checked against fetched primary sources and executable fixtures. Runtime details can change; memory/timing depends on build and workload, and approximate-sketch assumptions are explicitly scoped.
- medium confidence, hash-table-cost-model: Version/build-dependent runtime behaviour, vendor examples, practical speed or finite-sketch accuracy Core algorithm and documented implementation facts were checked against fetched primary sources and executable fixtures. Runtime details can change; memory/timing depends on build and workload, and approximate-sketch assumptions are explicitly scoped.
- medium confidence, hash-exact-lookup-tradeoffs: Version/build-dependent runtime behaviour, vendor examples, practical speed or finite-sketch accuracy Core algorithm and documented implementation facts were checked against fetched primary sources and executable fixtures. Runtime details can change; memory/timing depends on build and workload, and approximate-sketch assumptions are explicitly scoped.
- medium confidence, hash-function-fibonacci: Version/build-dependent runtime behaviour, vendor examples, practical speed or finite-sketch accuracy Core algorithm and documented implementation facts were checked against fetched primary sources and executable fixtures. Runtime details can change; memory/timing depends on build and workload, and approximate-sketch assumptions are explicitly scoped.
- medium confidence, hash-function-polynomial: Version/build-dependent runtime behaviour, vendor examples, practical speed or finite-sketch accuracy Core algorithm and documented implementation facts were checked against fetched primary sources and executable fixtures. Runtime details can change; memory/timing depends on build and workload, and approximate-sketch assumptions are explicitly scoped.
- medium confidence, hash-function-flooding: Version/build-dependent runtime behaviour, vendor examples, practical speed or finite-sketch accuracy Core algorithm and documented implementation facts were checked against fetched primary sources and executable fixtures. Runtime details can change; memory/timing depends on build and workload, and approximate-sketch assumptions are explicitly scoped.
- medium confidence, hash-collision-chaining: Version/build-dependent runtime behaviour, vendor examples, practical speed or finite-sketch accuracy Core algorithm and documented implementation facts were checked against fetched primary sources and executable fixtures. Runtime details can change; memory/timing depends on build and workload, and approximate-sketch assumptions are explicitly scoped.
- medium confidence, hash-collision-swiss-designs: Version/build-dependent runtime behaviour, vendor examples, practical speed or finite-sketch accuracy Core algorithm and documented implementation facts were checked against fetched primary sources and executable fixtures. Runtime details can change; memory/timing depends on build and workload, and approximate-sketch assumptions are explicitly scoped.
- medium confidence, hash-resize-load-thresholds: Version/build-dependent runtime behaviour, vendor examples, practical speed or finite-sketch accuracy Core algorithm and documented implementation facts were checked against fetched primary sources and executable fixtures. Runtime details can change; memory/timing depends on build and workload, and approximate-sketch assumptions are explicitly scoped.
- medium confidence, hash-resize-hysteresis-incremental: Version/build-dependent runtime behaviour, vendor examples, practical speed or finite-sketch accuracy Core algorithm and documented implementation facts were checked against fetched primary sources and executable fixtures. Runtime details can change; memory/timing depends on build and workload, and approximate-sketch assumptions are explicitly scoped.
- medium confidence, hash-resize-cpython-layout: Version/build-dependent runtime behaviour, vendor examples, practical speed or finite-sketch accuracy Core algorithm and documented implementation facts were checked against fetched primary sources and executable fixtures. Runtime details can change; memory/timing depends on build and workload, and approximate-sketch assumptions are explicitly scoped.
- medium confidence, hash-resize-java-bins: Version/build-dependent runtime behaviour, vendor examples, practical speed or finite-sketch accuracy Core algorithm and documented implementation facts were checked against fetched primary sources and executable fixtures. Runtime details can change; memory/timing depends on build and workload, and approximate-sketch assumptions are explicitly scoped.
- medium confidence, hash-resize-java-presizing: Version/build-dependent runtime behaviour, vendor examples, practical speed or finite-sketch accuracy Core algorithm and documented implementation facts were checked against fetched primary sources and executable fixtures. Runtime details can change; memory/timing depends on build and workload, and approximate-sketch assumptions are explicitly scoped.
- medium confidence, hash-pattern-frequency: Version/build-dependent runtime behaviour, vendor examples, practical speed or finite-sketch accuracy Core algorithm and documented implementation facts were checked against fetched primary sources and executable fixtures. Runtime details can change; memory/timing depends on build and workload, and approximate-sketch assumptions are explicitly scoped.
- medium confidence, hash-prob-bloom-membership: Version/build-dependent runtime behaviour, vendor examples, practical speed or finite-sketch accuracy Core algorithm and documented implementation facts were checked against fetched primary sources and executable fixtures. Runtime details can change; memory/timing depends on build and workload, and approximate-sketch assumptions are explicitly scoped.
- medium confidence, hash-prob-bloom-limits: Version/build-dependent runtime behaviour, vendor examples, practical speed or finite-sketch accuracy Core algorithm and documented implementation facts were checked against fetched primary sources and executable fixtures. Runtime details can change; memory/timing depends on build and workload, and approximate-sketch assumptions are explicitly scoped.
- medium confidence, hash-prob-count-min: Version/build-dependent runtime behaviour, vendor examples, practical speed or finite-sketch accuracy Core algorithm and documented implementation facts were checked against fetched primary sources and executable fixtures. Runtime details can change; memory/timing depends on build and workload, and approximate-sketch assumptions are explicitly scoped.
- medium confidence, hash-prob-hll-registers: Version/build-dependent runtime behaviour, vendor examples, practical speed or finite-sketch accuracy Core algorithm and documented implementation facts were checked against fetched primary sources and executable fixtures. Runtime details can change; memory/timing depends on build and workload, and approximate-sketch assumptions are explicitly scoped.
- medium confidence, hash-prob-hll-merging: Version/build-dependent runtime behaviour, vendor examples, practical speed or finite-sketch accuracy Core algorithm and documented implementation facts were checked against fetched primary sources and executable fixtures. Runtime details can change; memory/timing depends on build and workload, and approximate-sketch assumptions are explicitly scoped.
- medium confidence, hash-resize-cpython-layout: CPython 3.14 layout details: 1/2/4/8-byte indices, two-thirds usable fraction, growth to the next power of two ≥ 3 × live keys, dummy-slot reuse only in GIL builds ('for lookup safety'). Verified in 3.14 dictobject.c and on CPython 3.14.4, but implementation details can change between versions; the 'lookup safety' reason for the free-threaded rule is inferred, not stated in the source.
- medium confidence, hash-function-flooding: Rust's HashMap defaults to SipHash-1-3; common CPython builds default to SipHash-1-3 from 3.11. Verified in current Rust std docs and the 3.11 What's New, but both are documented as changeable defaults; the text already hedges.
- medium confidence, hash-prob-bloom-limits: RocksDB ~10 bits/key ≈ 1%; Cassandra bloom_filter_fp_chance; Akamai one-hit wonders. Verified against the RocksDB wiki, Cassandra docs and Maggs & Sitaraman (2015, an un-refereed CCR editorial note); product docs are time-sensitive.
- medium confidence, hash-prob-count-min: Caffeine's W-TinyLFU uses a 4-bit Count-Min sketch. Verified in FrequencySketch.java on Caffeine master; implementation detail of a third-party library that could change.
- medium confidence, hash-collision-swiss-designs: Go 1.24 maps use Swiss tables with eight-slot groups; Abseil SSE2 compares 16 control bytes and allows 7/8 load. Verified in the Go blog/release notes and Abseil raw_hash_set.h; implementation details of evolving libraries.


## dsa / Trees & Heaps

37 question objects changed. Every changed question has a specific independent-review reason in the linked record.

**Corrections in this review:**

- tree-null-serialisation: the author's analogy edit had absorbed two visible facts ('Level-order with nulls … works too'; JSON/Protocol Buffers schemas) into the collapsed 'Where it stops' paragraph → restored as visible prose before the analogy.
- tree-red-black-invariants analogy: 'no route … can be more than about twice as long as the shortest one' implied distance → the red-black bound is on node counts: 'twice as many stops as the route with the fewest'; mapping line now 'how many more nodes one path can have'.
- tree-morris-threads analogy: the arrow was chalked on arrival at a dead end, but Morris creates the thread from the current node before descending and removes it on the return visit → arrow placed at the passage's last dead end (the in-order predecessor) before entering, rubbed out on return; mapping names the junction as the current node.
- tree-binary-counts analogy limit: 'every round happens for everyone at once' was not the real difference (rounds also equal height) → the phone tree must reach everyone, a lookup follows one path; real calls are sequential.
- tree-heap-order-layout analogy: 'a junior officer in one unit may outrank a senior one elsewhere' was self-contradictory → 'someone low down in one unit may hold a higher rank than someone near the top of another'.
- tree-heap-merging analogy: 'each step costs only about ten comparisons' with 1,000 piles undercounts (a pop compares two children per level) → 'walks only about ten levels of the heap'.
- tree-lca-single-query analogy limit: said the general-tree algorithm works by 'checking both routes upward' → it searches down from the root; reworded.
- tree-lca-preprocessing reference card: the visible In words line relied on the hidden symbol k (2^k) → standalone wording (each stored jump is two half-size jumps from the previous level).
- tree-depth-height: 'call stack is as deep as the longest root-to-leaf path, plus one' was off by one under the module's edge convention → one frame per node on the longest path plus one for the empty-child call (h + 2 frames).
- tree-basics-q5 option C explanation was incoherent ('uses 9 // 2 = 4 … but then reads index 3') → explains that 20 is the parent of indices 7 and 8 and 40 is index 1's right child.
- Height convention: tree-balanced-q8 option D 'at most 19 levels' and tree-heaps-q11 'a heap of 1,024 items has about … 10 levels' counted levels where the module counts edges → 'height at most 19' and 'height 10'.
- tree-bst-q8: prompt did not exclude the lesson's recursive insert, which raises RecursionError on a 10,000-key chain → 'using an iterative insert'; worked example '14 to 17' nodes → '13 to 17' (log₂ 10,000 ≈ 13.3).

**Scope gaps and exclusions:**

- All 35 active units and all 80 prompts, options, explanations and worked examples reviewed; inherited topics, examples and diagrams preserved across coherent ordered groups. Question keys/types/levels/option counts and all 14 archive files match the fixed baseline.
- All 32 lesson and 10 quiz Python fragments executed with explicit earlier prerequisites; actual C free-tree fragment compiled with warnings-as-errors. Tests cover 626 binary shapes, all 5040 seven-key AVL insertion permutations, 100 BST successor/deletion fixtures and 250 heap streams. Finite fixtures supplement the general arguments rather than proving all possible inputs.
- No pinned CPython object-size/cache-miss/corpus-memory, AVL/red-black speed or sortedcontainers benchmark. The visible inherited evidence-gap notes remain.
- Red-black insertion remains a clearly labelled conventional outline; no full red-black or AVL deletion implementation. No Java/C++/Go/kernel/routing/Redis/Ethereum integration execution.
- Morris original-paper full text not obtained: publisher metadata confirms the 1979 attribution, and actual traversal/restoration is independently executed. Aho–Corasick original 1975 paper was obtained and read; current GNU grep application is sourced to the GNU manual.
- Primary source families checked targeted factual claims and changed glossary definitions. Correct unchanged entries retain their existing confidence/hash provenance; this review does not claim fresh sentence-by-sentence primary corroboration of every unchanged background definition.
- Root performs full-course build and mobile/PWA integration; this worker writes no shared/generated application files. Isolated actual glossary compiler and app lookup were executed to check current subject meanings.
- Rendering checked with the app's markdown renderer (22 analogies become closed <details>, no literal callout tags or stray Markdown); not checked in a browser at 390 px or offline — left to the orchestrator.
- The Haeupler–Sen–Tarjan 'Rank-balanced trees' PDF was fetched but its text could not be extracted locally; AVL deletion's multi-level rebalancing rests on Wikipedia's retracing description plus the verifier's own experiments (Fibonacci trees: up to h/2 rotations per delete; random trees: rebalancing at adjacent levels), not a quoted primary sentence. CLRS/Knuth were not available online.
- Lesson minutes were left as baseline (frontmatter unchanged); most added words are in collapsed analogies.
- Scope unchanged: no B-tree/B+-tree, segment-tree or Fenwick-tree lessons in this module (pointed to System Design and the advanced module).

**Low-confidence areas, including preserved qualifications:**

- medium confidence, tree-morris-threads: 1979 Morris attribution and full original-paper discussion Publisher search metadata retrieved, direct full-page fetch blocked; algorithm and restoration checked by independent native fixtures.
- medium confidence, tree-balanced-workloads: Library/kernel implementation details and historical/current CFS/EEVDF uses Current primary docs/source checked; facts can change and no live integration benchmark is claimed.
- medium confidence, tree-python-top-k: Python heapq API/version and algorithm-selection details Current official docs and CPython3.14 implementation checked; growth bounds are models, not latency guarantees.
- medium confidence, tree-heap-merging: Merge work scale and alternative priority-queue speed Abstract list/heap-level scale intentionally omits implementation constants; concrete speed requires measurements.
- medium confidence, tree-radix-variants: Routing, Redis, Ethereum and Linux production uses Current official docs/implementations checked; version-sensitive and not run as integrations.
- medium confidence, tree-avl-height-bound: Leading AVL height coefficient versus finite exact heights Leading approximation qualified; exact 27/28 finite recurrence recomputed. No measured runtime conclusion follows.
- medium confidence, glossary: glossary term vruntime Weight-adjusted and hierarchical run-queue semantics checked in kernel docs/source; simplified teaching definition and version-sensitive scheduler context.
- medium confidence, glossary: glossary term cpp-std-map Current C++ draft contracts and common implementation source checked; concrete library representations remain implementation-dependent.
- medium confidence, glossary: glossary term write-heavy General workload label; inherited confidence remains medium and no benchmark advantage is asserted.
- medium confidence, glossary: glossary term heapreplace Current Python min/max API contracts checked; implementation and practical speed depend on version and workload.
- medium confidence, glossary: glossary term heapify-max Exact Python3.14 version note is now confirmed in fresh official docs; original medium confidence retained as requested.
- medium confidence, glossary: glossary term go-container-heap Current Go API interface checked, but production implementation/API facts are version-sensitive.
- medium confidence, glossary: glossary term ethereum Current official state-trie documentation fetched; production details can evolve and no integration run is claimed.
- medium confidence, glossary: glossary term merkle-patricia-trie Official Ethereum encoding exception checked; implementation summary is deliberately simplified and version-sensitive.
- medium confidence, glossary: glossary term xarray Current kernel official docs support its API and radix-tree relationship, but definition remains a simplified implementation summary.
- medium confidence, glossary: glossary term fgrep Current GNU fixed-pattern algorithm documented; earlier historical attribution replaced because original implementation history was not independently corroborated.
- medium confidence, tree-memory-layouts: About 100 bytes per plain three-field node object on 64-bit CPython 3.14. Measured with tracemalloc on CPython 3.14.4 (Homebrew, macOS arm64): 96–100 B per object excluding values. Object layout varies with version, build and class definition; the lesson says so.
- medium confidence, tree-avl-insertion-repair: An AVL delete may need O(log n) rotations, up to one rebalancing step per level. Supported by Wikipedia retracing analysis and own experiments (multi-level and adjacent-level rebalancing observed); Knuth/primary paper text not obtained. The per-level phrasing is an upper bound.
- medium confidence, tree-red-black-insertion / tree-balanced-workloads: Conventional bottom-up red-black insertion uses at most two rotations, deletion at most three. Wikipedia's case analysis states it explicitly (citing standard texts); CLRS not fetched. The lesson scopes it to conventional bottom-up algorithms.
- medium confidence, tree-balanced-workloads: CFS history, cached leftmost pointer, EEVDF transition from 6.6, epoll/rbtree uses. Kernel docs fetched and match (EEVDF doc: transition began in 6.6); kernel facts are time-sensitive.
- medium confidence, tree-bst-deletion-cases: Common std::map implementations relink the successor rather than copy keys. Verified in libstdc++ and libc++ source and Linux rbtree; MSVC not checked; the standard implies it only through iterator-invalidation rules. Wording is hedged.
- medium confidence, tree-morris-threads: Joseph M. Morris, 1979. Wikipedia's text and citation give 1979 (its reference spells the initial 'H.'); the original paper was not fetched.


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


## networks / IP, Addressing & Routing

31 question objects changed. Every changed question has a specific independent-review reason in the linked record.

**Corrections in this review:**

- glossary total-length: author-added alias 'Total Length' is a case-insensitive multi-word phrase, so it fell back into other subjects and captured ordinary 'total length' in security/02-crypto-basics, security/03-applied-crypto and several DSA lessons → alias removed; ip-ipv4-header-fields bullet and ip-ipv4-q1 explanation reworded to the full 'Total Length field' term so the bold term still links.
- glossary port-forwarding: author-added alias 'static mapping' captured static ARP/neighbour-cache mappings (networks/01 nf-arp questions; ip-nat-ipv6-q10 here) → alias removed (baseline plural 'static mappings' kept, which is used in the NAT sense).
- glossary nat66 (new): definition/example implied NPTv6 could substitute for a larger delegation; RFC 6296 NPTv6 is stateless and 1:1 (Abstract, §3.7), so it cannot fit more internal subnets into a smaller external prefix → definition rewritten (stateless 1:1 NPTv6 vs stateful port-translating forms) and example changed to RFC 6296's provider-independence use.
- ip-nat-ipv6-q4 option C explanation said IPv6-to-IPv6 translation 'can be made to work in some designs' for three subnets in one /64 → now states that NPTv6 maps addresses 1:1 and cannot, and only stateful port-translating NAT66 could, at NAT's usual cost.
- ip-ipv4-path-mtu analogy: the bridge keeper 'turns it back', implying an oversized DF packet returns to the sender → the lorry is stopped (dropped), only the note (ICMP) returns, and any resend comes from the sender's transport; also removed 'posted', which opened the HTTP POST entry.
- ip-subnet-route-aggregation q6 worked example: RFC 4632 §5.1 rule 2 says the aggregating router 'must discard' unmatched packets; author wrote 'should' → corrected, with the discard/null route named.
- ip-bgp-sessions-reflectors: 'deploying more than one reflector avoids a single point of failure' → aligned with RFC 4456 §7 (a single-RR cluster is a single point of failure, so clients usually peer with at least two).
- ip-routing-ecmp-asymmetry analogy: 'redrawing the ranges moves most families' overstated the till picture (about half move under even letter ranges) and 'avoids' reordering overstated flow affinity → 'many families who were not at the closed till' and 'reduces the chance of'.
- ip-dhcp-lease-timers q4: the key (renewal succeeds after the 12:30–14:00 outage, before T2) relied on unstated retry timing → worked example now cites RFC 2131 §4.4.5 (retry after half the remaining time to T2, minimum 60 s, so about 14:30); prompt 'What does the user experience?' opened the UX entry → 'What will the user notice?'.
- ip-subnet-prefix-mask analogy: 'can reach each other directly' contradicted the lesson's own caveat that a subnet match does not prove layer-2 reachability → 'normally deliver to each other directly, without a router'.
- ip-routing-longest-prefix analogy: 'Manchester' opened Manchester coding and 'M1' opened TLS handshake messages → reworded without those tokens.
- ip-ospf-areas-designated analogy and ip-interior-routing-q9: 'the segment', 'Ethernet segment' and 'broadcast segment' opened networks/03-tcp's TCP 'segment' entry → reworded to shared/LAN segment phrases that open shared-segment; bare 'INIT' (unlinked; an INIT alias would capture SFTP INIT in networks/04) → 'the INIT state'.
- ip-bgp-sessions-reflectors lesson table/takeaway and ip-bgp-q2: bare 'hold time' opened embedded/03 'setup and hold time' → reworded to 'BGP hold time' / 'a negotiated hold time of zero', which open the BGP hold-time entry.
- ip-ipv4-fragment-sizing analogy and ip-ipv4-q11 explanation: 'higher layer' opened software-engineering 'higher and lower layers' → 'TCP or the application'.
- ip-ipv6-transition-paths (2 lesson lines, ip-nat-ipv6-q9 explanation): 'client-side' opened the security client-side-code entry → 'on the client device'.
- ip-ospf-interface-costs intro 'lowest total cost' opened a database query-cost entry; ip-ipv4-q12 prompt 'error handling' opened a React try/catch entry → both reworded without changing meaning or answer keys.

**Scope gaps and exclusions:**

- No live BGP announcements, rogue DHCP injection, host route changes, firewall changes or physical-router experiments were performed. No protocol convergence, forwarding latency, current market share or Internet adoption benchmark is claimed.
- The Python examples are bounded teaching models, not complete parsers, routers, NATs, OSPF speakers or DHCP clients. Their omissions are retained beside the code.
- The illustrative Linux ip-route/ip-rule mutation commands were source-checked rather than executed against a full matching topology; this remains a concrete execution gap for the verifier.
- Author phone verification uses exact app CSS, Markdown renderer, glossary compiler section and diagram compiler in an isolated fixture. Full production lesson/quiz routes, progress migration, PWA update and offline checks remain coordinating integration work after independent verification.
- Inherited omitted-after-review notes remain explicit: no unsupported universal OS defaults, pricing/allocation timeline, route/adoption counts, timing guarantees, client-mode prevalence or incident financial-loss total was reintroduced.
- The standalone OSPF cost model does not model platform maximum-cost handling or every vendor rounding policy; its examples stay within the specified positive 16-bit interface-cost range.
- All 435 glossary definitions, examples and aliases were read. The actual compiled renderer was separately inspected for opposite meanings; precise application NAT traversal and routing link cost were added rather than changing other modules’ aliases.
- Primary-source review uses relevant passages, not a claim to have read entire protocol specifications or to have independently reproduced historical Internet outages.
- No browser render at iPhone width in this pass; node-renderer checks only (delegated to release QA, as for networks/01).
- Unchanged lessons (ip-ipv4-icmp-traceroute, ip-subnet-special-ranges, ip-nat-traversal-connectivity, ip-routing-selection-rib-fib, ip-routing-per-hop, ip-igp-count-to-infinity, ip-ospf-neighbours-lsdb, ip-bgp-commercial-policy, ip-bgp-routing-incidents, the DHCP units) keep an inherited first paragraph that repeats the summary line, and some keep long shared reading lists; cosmetic, left to avoid churn.
- ip-interior-routing-q4 uses exactly the lesson's worked numbers (Y 2/7, Z 5/3), so it partly tests recall of the example; inherited and left unchanged.
- Archival source files (ip-ipv4, ip-bgp, etc.) still contain phrases that open wrong-sense entries ('hold time', 'export restrictions', 'error handling'); they are not active and were not edited.
- No live routing, NAT, DHCP or timer measurements were made; timer defaults are from standards and Linux headers, not device surveys.

**Low-confidence areas, including preserved qualifications:**

- medium confidence, ip-ospf-interface-costs: Integer truncation in the stated classic Cisco-style bandwidth-derived cost model. The fetched Cisco FAQ states reference/interface bandwidth, default 100 Mbit/s, a 16-bit limit and manual overrides. Truncation is a teaching-model assumption consistent with quoted examples, not a portable protocol mandate or independently measured current router behaviour.
- medium confidence, ip-ospf-worked-spf: The 1,000-vertex/3,000-edge illustration of about 40,000 counted steps. The substituted asymptotic expression is correct, but omits constants, implementation details and arbitrary-precision costs. It is explicitly an order-of-magnitude illustration, not a runtime measurement.
- medium confidence, ip-bgp-rpki-validation: ASPA verification specification status. The retrieved primary datatracker page identifies draft-ietf-sidrops-aspa-verification-28, dated 24 August 2026, still an Internet-Draft as of this review. Status and validation coverage can change.
- medium confidence, ip-routing-ecmp-asymmetry: Illustrative source-policy route/rule mutation commands. Syntax, separate table reachability and rule precedence were independently checked against fetched iproute2 manuals. No matching Linux topology was configured or mutated in this review; the Python lookup does not establish those exact commands at runtime.
- medium confidence, ip-bgp-routing-incidents: Historical incident details and approximate duration in the Facebook glossary entry. Primary RIPE diagrams, affected-network postmortems and original Cloudflare analysis support the reported narratives, not independent packet-level reconstruction. The roughly six-hour duration remains an approximate timeline description rather than a duration stated in Meta’s post.
- medium confidence, glossary: Vendor/platform/default and optional ecosystem descriptions listed as medium-confidence glossary entries. Primary documentation and standards support the stated examples and qualified mechanisms. They do not establish universal hardware cost, network prevalence, current platform defaults, measured convergence or every product configuration. Generic supplementary descriptions retain their existing secondary links; no benchmark or universal configuration claim is inferred.
- medium confidence, ip-ospf-areas-designated: q9 worked example: INIT or EXSTART states are 'signs worth investigating'; glossary ospf-neighbour-states: ExStart/Exchange 'can point to' an MTU mismatch. RFC 2328 §10.1 defines the states and §10.6 rejects DD packets whose MTU exceeds the receiver's, which supports the hedged association; the diagnostic framing is operational practice (a Cisco troubleshooting page could not be fetched).
- medium confidence, glossary:nat66: Stateful, port-translating NAT66 brings back the per-connection state of IPv4 NAPT. NPTv6 behaviour is verified in RFC 6296 (experimental); stateful NAT66 is implementation practice without an IETF standard, so the text describes it only in general terms.
- medium confidence, ip-ospf-interface-costs: Classic Cisco 100 Mbit/s reference and integer truncation in the reference cost card. Inherited from the earlier verified record (Cisco FAQ); not re-fetched in this pass. The lesson presents it as one implementation's model.
- medium confidence, ip-bgp-rpki-validation: ASPA verification Internet-Draft dated August 2026. Inherited, time-sensitive draft status; not re-fetched.


## networks / Transport Layer: TCP & UDP in Depth

36 question objects changed. Every changed question has a specific independent-review reason in the linked record.

**Corrections in this review:**

- tcp-udp-header (lesson + tcp-udp-ports-q2): 'Linux UDP normally uses PMTU discovery and can return EMSGSIZE' → Linux's default socket mode (IP_PMTUDISC_WANT) fragments an oversized datagram locally; IP_PMTUDISC_DO returns EMSGSIZE. Verified in a Linux 6.12 container (60,000-byte send: 41 fragments by default; EMSGSIZE with DO/PROBE) and in IP_MTU_DISCOVER(2const); udp(7)'s default-EMSGSIZE sentence is outdated.
- tcp-rto-estimator q5: 'samples fall between 98 and 102 ms / swing between 60 and 140 ms' did not determine the stated ≈110/≈260–270 ms RTOs (evenly spread 60–140 ms samples settle near 140–200 ms) → prompt says the samples alternate; worked example says ≈270 ms and notes the spread-sample case.
- tcp-syn-flood-cookies analogy: cloakroom still stored a coat per customer, contradicting the stateless cookie → stamped ticket carrying the party size, nothing kept at the door.
- tcp-nagle-delayed-acks: the fact that Nagle never delays full-sized segments had been moved into the collapsed analogy only, although tcp-flow-control-q6 depends on it → restored to the visible text.
- tcp-reno-round-trace lesson and tcp-congestion-q5: 'ssthresh is halved' / 'A timeout halves ssthresh' → ssthresh is set to about half the window (FlightSize) at the loss (RFC 5681 eq. 4).
- tcp-slow-start-flights q1: a loss-free switch at 80 segments on a new connection was attributed to ssthresh without explaining where a low ssthresh came from (RFC 5681 starts it arbitrarily high) → worked example names cached/route ssthresh or Linux CUBIC HyStart (sets ssthresh = cwnd).
- tcp-reno-large-path-recovery q9: the 12,000-segment sawtooth peak lacked its assumptions → states steady one-loss-per-10-minutes, fast recovery only, peak where P/2 + 6,000 = P, ≈9,000-segment (≈1 Gbit/s) average.
- tcp-bufferbloat-aqm q6: 'roughly doubles' assumed one tail-drop FIFO → prompt states it.
- tcp-port-numbers q5: reuse of the source-port pool against a second destination is OS-dependent → hedged in the explanation (Linux behaviour tested).
- tcp-graceful-close-time-wait analogy: 'the side that hung up first' contradicted lingering on the line → 'said goodbye first'.
- tcp-slow-start-flights analogy: leftovers mapped to ssthresh itself → leftovers are the signal that ends doubling (reaching ssthresh or detecting loss).
- tcp-ecn-congestion-feedback analogy: title said 'running late' while the body said 'kitchen busy'; limit omitted on-path ECN bleaching → aligned and extended.
- tcp-bbr-versioned-model: duplicated 'ideal operating point' sentence removed; analogy title matched its café-manager text.
- Dictionary links: 'posted' (opened HTTP POST) in the postcard analogy, 'Chiu–Jain convergence' (opened routing convergence) in the AIMD analogy and 'next expected number' (opened DSA expected value) in tcp-connections-q11 → reworded.
- Glossary: application-heartbeat source changed from Wikipedia to RFC 6455 §5.5.2 (WebSocket Ping as keepalive/liveness check); added ip-mtu-discover (IP_MTU_DISCOVER/IP_PMTUDISC_DO/WANT) and tcp-hystart for terms introduced by the corrections.

**Scope gaps and exclusions:**

- No WAN packet-capture experiment, SYN flood, AQM benchmark or QUIC migration experiment. Source-supported algorithms and explicit bounded models do not imply measured deployment performance.
- The selector loop deliberately retains partial-write/would-block defects for its own debugging question; it is not a production server. Services need total deadlines and resource/connection policies.
- Advanced UDP options and implementation-specific recovery/state handling are described selectively rather than implementing a full transport stack.
- The Chiu/Jain scanned first page/abstract was inspected visually, not a complete independent proof of the paper; the fairness attribution remains limited to its simplified model.
- No browser render at 390 px; node renderer checks only (left to release QA).
- Linux behaviour was tested on one kernel (6.12, linuxkit) and loopback only; no WAN, AQM, BBR or migration measurements.
- QUIC lesson's tuning checklist remains TCP-centric (inherited).
- BBRv2/v3 only summarised and hedged; the BBRv3 draft date is time-sensitive (inherited).
- Several cross-subject multi-word fallbacks in inherited text still open other subjects' entries ('length field' → security payload-length, 'data byte(s)' → MIDI, 'unsigned integer' → DSA, 'side channels' → crypto, 'error handling' → React try/catch); recorded, not changed.

**Low-confidence areas, including preserved qualifications:**

- medium confidence, tcp-port-numbers: Versioned operating-system behaviour, deployment effects or bounded timing/congestion models. Fetched primary specification/implementation supports the qualified teaching claim, but loopback/model checks do not establish arbitrary WAN behaviour, scale or future defaults.
- medium confidence, tcp-syn-flood-cookies: Versioned operating-system behaviour, deployment effects or bounded timing/congestion models. Fetched primary specification/implementation supports the qualified teaching claim, but loopback/model checks do not establish arbitrary WAN behaviour, scale or future defaults.
- medium confidence, tcp-graceful-close-time-wait: Versioned operating-system behaviour, deployment effects or bounded timing/congestion models. Fetched primary specification/implementation supports the qualified teaching claim, but loopback/model checks do not establish arbitrary WAN behaviour, scale or future defaults.
- medium confidence, tcp-close-states-production: Versioned operating-system behaviour, deployment effects or bounded timing/congestion models. Fetched primary specification/implementation supports the qualified teaching claim, but loopback/model checks do not establish arbitrary WAN behaviour, scale or future defaults.
- medium confidence, tcp-rto-backoff-ambiguity: Versioned operating-system behaviour, deployment effects or bounded timing/congestion models. Fetched primary specification/implementation supports the qualified teaching claim, but loopback/model checks do not establish arbitrary WAN behaviour, scale or future defaults.
- medium confidence, tcp-rack-tail-probes: Versioned operating-system behaviour, deployment effects or bounded timing/congestion models. Fetched primary specification/implementation supports the qualified teaching claim, but loopback/model checks do not establish arbitrary WAN behaviour, scale or future defaults.
- medium confidence, tcp-buffer-autotuning: Versioned operating-system behaviour, deployment effects or bounded timing/congestion models. Fetched primary specification/implementation supports the qualified teaching claim, but loopback/model checks do not establish arbitrary WAN behaviour, scale or future defaults.
- medium confidence, tcp-nagle-delayed-acks: Versioned operating-system behaviour, deployment effects or bounded timing/congestion models. Fetched primary specification/implementation supports the qualified teaching claim, but loopback/model checks do not establish arbitrary WAN behaviour, scale or future defaults.
- medium confidence, tcp-split-write-latency: Versioned operating-system behaviour, deployment effects or bounded timing/congestion models. Fetched primary specification/implementation supports the qualified teaching claim, but loopback/model checks do not establish arbitrary WAN behaviour, scale or future defaults.
- medium confidence, tcp-aimd-reno-recovery: Versioned operating-system behaviour, deployment effects or bounded timing/congestion models. Fetched primary specification/implementation supports the qualified teaching claim, but loopback/model checks do not establish arbitrary WAN behaviour, scale or future defaults.
- medium confidence, tcp-reno-large-path-recovery: Versioned operating-system behaviour, deployment effects or bounded timing/congestion models. Fetched primary specification/implementation supports the qualified teaching claim, but loopback/model checks do not establish arbitrary WAN behaviour, scale or future defaults.
- medium confidence, tcp-cubic-time-target: Versioned operating-system behaviour, deployment effects or bounded timing/congestion models. Fetched primary specification/implementation supports the qualified teaching claim, but loopback/model checks do not establish arbitrary WAN behaviour, scale or future defaults.
- medium confidence, tcp-bbr-versioned-model: Versioned operating-system behaviour, deployment effects or bounded timing/congestion models. Fetched primary specification/implementation supports the qualified teaching claim, but loopback/model checks do not establish arbitrary WAN behaviour, scale or future defaults.
- medium confidence, tcp-ecn-congestion-feedback: Versioned operating-system behaviour, deployment effects or bounded timing/congestion models. Fetched primary specification/implementation supports the qualified teaching claim, but loopback/model checks do not establish arbitrary WAN behaviour, scale or future defaults.
- medium confidence, tcp-short-transfer-timing: Versioned operating-system behaviour, deployment effects or bounded timing/congestion models. Fetched primary specification/implementation supports the qualified teaching claim, but loopback/model checks do not establish arbitrary WAN behaviour, scale or future defaults.
- medium confidence, tcp-mathis-loss-model: Versioned operating-system behaviour, deployment effects or bounded timing/congestion models. Fetched primary specification/implementation supports the qualified teaching claim, but loopback/model checks do not establish arbitrary WAN behaviour, scale or future defaults.
- medium confidence, tcp-bufferbloat-aqm: Versioned operating-system behaviour, deployment effects or bounded timing/congestion models. Fetched primary specification/implementation supports the qualified teaching claim, but loopback/model checks do not establish arbitrary WAN behaviour, scale or future defaults.
- medium confidence, tcp-stream-blocking-ossification: Versioned operating-system behaviour, deployment effects or bounded timing/congestion models. Fetched primary specification/implementation supports the qualified teaching claim, but loopback/model checks do not establish arbitrary WAN behaviour, scale or future defaults.
- medium confidence, tcp-quic-transport-tradeoffs: Versioned operating-system behaviour, deployment effects or bounded timing/congestion models. Fetched primary specification/implementation supports the qualified teaching claim, but loopback/model checks do not establish arbitrary WAN behaviour, scale or future defaults.
- medium confidence, tcp-socket-calls-backlogs: Versioned operating-system behaviour, deployment effects or bounded timing/congestion models. Fetched primary specification/implementation supports the qualified teaching claim, but loopback/model checks do not establish arbitrary WAN behaviour, scale or future defaults.
- medium confidence, tcp-length-prefixed-service: Versioned operating-system behaviour, deployment effects or bounded timing/congestion models. Fetched primary specification/implementation supports the qualified teaching claim, but loopback/model checks do not establish arbitrary WAN behaviour, scale or future defaults.
- medium confidence, tcp-readiness-asyncio: Versioned operating-system behaviour, deployment effects or bounded timing/congestion models. Fetched primary specification/implementation supports the qualified teaching claim, but loopback/model checks do not establish arbitrary WAN behaviour, scale or future defaults.
- medium confidence, tcp-udp-header: Linux default fragments an oversized UDP datagram locally; IP_PMTUDISC_DO returns EMSGSIZE. Tested on Linux 6.12 and documented in IP_MTU_DISCOVER(2const), but udp(7) still says EMSGSIZE by default and the behaviour depends on ip_no_pmtu_disc, per-route settings and kernel version; the lesson names the tested kernel.
- medium confidence, tcp-port-numbers: q5: a second backend or source address lets the proxy reuse the same source-port pool. Tested for Linux connect() and bind-to-source; other operating systems may allocate ephemeral ports globally, which the explanation now notes.
- high confidence, tcp-rto-estimator: q5: RTOs settle near 110 ms and 270 ms. Re-derived by simulation for the alternating samples now stated in the prompt (108.4–108.7 ms; 268–273 ms).
- medium confidence, tcp-reno-large-path-recovery: q9: sawtooth peaking near 12,000 segments, ≈1 Gbit/s average. Idealised steady-state model; assumptions now stated in the worked example; real flows add slow start, timeouts and RTT variation.
- medium confidence, tcp-bufferbloat-aqm: q6: doubling a tail-drop modem buffer roughly doubles queueing delay. Holds for one FIFO kept near full by a loss-based sender at a constant uplink rate (now stated); real cable modems may shape or use several queues.
- medium confidence, tcp-slow-start-flights: q1: a loss-free switch to linear growth at 80 segments reflects ssthresh (cached/route value or HyStart). HyStart's exit and ssthresh assignment verified in tcp_cubic.c v6.12; a real CUBIC trace would grow cubically, not by exactly one segment, after the switch.
- high confidence, multiple: 25 analogies (mapping and limit). Each reviewed against the lesson's primary sources; five corrected. They remain teaching aids, not evidence.


## networks / Application-Layer Protocols

27 question objects changed. Every changed question has a specific independent-review reason in the linked record.

**Corrections in this review:**

- app-quic-streams-and-recovery q8 (app-http2-quic-q8): link cited RFC 9000 section 2.2 for per-stream head-of-line blocking, but that text is in section 13 -> link now https://www.rfc-editor.org/rfc/rfc9000#section-13.
- app-dns-poisoning-defences: 'a NAT that rewrites ports sequentially can undo it' overstated RFC 5452 -> 'RFC 5452 warns that a NAT which assigns outgoing ports sequentially, or from a small range, can dramatically reduce it'.
- app-ssh-channels-and-sftp reference formula: 'T <= kb / RTT' read like kilobits -> 'T <= (k x b) / RTT'.
- app-quic-packet-protection-q1 workedExample: 'certificate compression avoid it' -> 'certificate compression (RFC 8879) can avoid it' (compression reduces size but does not guarantee fitting 3,600 bytes).
- Glossary dmarc-test-mode: removed alias 'test mode', which as a multi-word cross-subject fallback would have linked synth 'Diode test mode' and Stripe 'test mode' (system-design) to DMARC.
- Glossary dns-negative-caching: removed aliases 'negative answer' (captured DSA Bloom-filter and SQL window-function text) and 'negatively cached' (captured a URL-shortener 404 cache in system-design/10).
- Glossary h264-access-unit: term 'Access unit' -> 'Access unit (video)' with aliases 'video access unit(s)', 'H.264 access unit', 'access units'; the bare term captured 'zero trust access unit' in networks/05. q9 workedExample now says 'video access unit'.
- Wrong-sense links in text changed by this pass reworded: 'transaction ID(s)' -> 'DNS transaction ID(s)' (DHCP/PostgreSQL entries) in app-dns-poisoning-defences (lesson and reference card) and app-dns-wire-q5; STUN IPv6 sentence reworded; 'one-time code' (OTP entry) in the QUIC migration analogy; 'code word' (coding-theory codeword) in the WebRTC analogy; 'audio sample rate' (synth sample entry) in app-rtp-header-and-clocks; 'an empty string' (React entry) in app-dns-wire-q11; 'Strict mode'/'strict mode' (React Strict Mode) in app-email-dmarc-alignment and app-email-q4.

**Scope gaps and exclusions:**

- Cookie revision is a live draft; browser enforcement, partitioning/eviction and restore behaviour remain implementation/policy dependent.
- No production HTTP parser or current browser cookie matrix is claimed.
- HTTP/2 and SFTP throughput examples are ideal feedback models, not measured benchmarks.
- No live QUIC migration/load-balancer or HTTP/2 reset-exhaustion experiment; research attack rate is attributed historical reporting.
- No resolver or DNSSEC validator interoperability lab; the ASCII encoder is explicitly restricted.
- No present-day resolver entropy, DNSSEC prevalence, KeyTrap CPU duration or browser/device policy matrix.
- Kademlia PDF required visual reading separately; SAD DNS text was extracted through native PDFKit and its rate-limit passages read.
- Local STARTTLS SMTP exercises certificate/hostname checking, AUTH and actual message/envelope serialisation, but no external provider delivery is claimed.
- Provider bulk policies and RFC 9989 deployment compatibility are time-sensitive; no rollout duration or inbox-delivery guarantee.
- No clock-accuracy measurement, NTS exchange or SSH/SFTP interoperability session; wire dialogues are labelled abbreviated protocol fixtures.
- OpenSSH defaults are release-specific, PTP accuracy requires engineered deployment, and gRPC library defaults/propagation/receive limits differ.
- Kademlia original PDF has broken text extraction; native PDFKit rendered pages 2–6 and those images were read for metric, state, uptake assumptions and lookup. No every-page read is claimed.
- No torrent swarm, DHT convergence, NAT traversal or WebRTC media benchmark; finite consistency checks are not live protocol proofs.
- No current DHT population/typical rounds/TURN share or universal interactive-latency limit.
- Receiver DMARC pass and RFC 9989 Domain Owner full-participation requirements are now distinguished; existing deployments based on RFC 7489 can differ.
- Secondary glossary references are retained for background concepts; their entries are scored medium rather than presented as fresh deployment measurements.
- No lessons on HTTP caching semantics (RFC 9111) or page-load round-trip budgets in this module; identity rules prevented adding lessons (author gap, confirmed).
- No browser render at 390 px; renderer checks only via the build.
- SMTP code tested only against local fake servers on loopback, not a real provider.
- No measurement of receiver t= support, Android's current DoH3 behaviour, or NAT port-allocation prevalence; these are date-hedged or attributed.
- Pre-existing wrong-sense links in unchanged text remain and are recorded as integration dependencies (e.g. bare 'transaction ID' -> DHCP entry in networks/02, 'padding' -> Ethernet frame padding).

**Low-confidence areas, including preserved qualifications:**

- medium confidence, app-cookie-scope-and-lifetime: Source-specific operational, product or deployment details Cookie revision and browser storage behaviour are draft/policy dependent.
- medium confidence, app-cookie-cross-site-and-cost: Source-specific operational, product or deployment details Cookie draft, prefixes, implementation policies and encoder choices can change.
- medium confidence, app-h2-credit-and-shutdown: Source-specific operational, product or deployment details Rapid Reset and Chrome removal are attributed historical/product claims; throughput is an ideal feedback model.
- medium confidence, app-quic-migration-and-discovery: Source-specific operational, product or deployment details Actual migration, routing and fallback require coordinated deployment; no live migration lab.
- medium confidence, app-dns-poisoning-defences: Source-specific operational, product or deployment details Case preservation and side-channel feasibility are implementation-specific; historical research is attributed.
- medium confidence, app-dnssec-validation-chain: Source-specific operational, product or deployment details Standards checked; KeyTrap behaviour and operational rollover failures depend on implementation and state.
- medium confidence, app-dns-encrypted-transports: Source-specific operational, product or deployment details Browser/device encrypted-DNS policies are version- and configuration-dependent.
- medium confidence, app-email-dmarc-alignment: Source-specific operational, product or deployment details New May 2026 RFC conformance requirements checked; deployment compatibility and provider policy remain time-sensitive.
- medium confidence, app-email-framing-and-tls-policy: Source-specific operational, product or deployment details Smuggling outcome depends on the vulnerable parser pair and policy; no external relay experiment.
- medium confidence, app-ntp-asymmetry-and-clocks: Source-specific operational, product or deployment details Clock discipline, chrony/ntpd options and future UTC policy are source-specific.
- medium confidence, app-ntp-wire-and-authentication: Source-specific operational, product or deployment details Wire fields verified; no clock-accuracy, NTS or PTP interoperability measurement.
- medium confidence, app-ssh-transport-and-authentication: Source-specific operational, product or deployment details Release-specific OpenSSH defaults and affected Terrapin modes are source-specific; no SSH interoperability session.
- medium confidence, app-ssh-channels-and-sftp: Source-specific operational, product or deployment details OpenSSH request defaults and SFTP draft are version-specific; throughput is an ideal model.
- medium confidence, app-grpc-status-and-operations: Source-specific operational, product or deployment details Library defaults, propagation/cancellation and balancing depend on implementation/configuration.
- medium confidence, app-kademlia-distance-and-buckets: Source-specific operational, product or deployment details Historical uptime rationale and distribution assumptions are not present-day population guarantees.
- medium confidence, app-kademlia-lookup-and-threats: Source-specific operational, product or deployment details Logarithmic progress relies on maintained routing and identifier assumptions; no convergence/latency lab.
- medium confidence, app-webrtc-signalling-and-ice: Source-specific operational, product or deployment details Actual candidate reachability and traversal depend on NAT/filtering/network policy.
- medium confidence, app-webrtc-security-and-groups: Source-specific operational, product or deployment details Group topologies and key access depend on deployment; no browser/media interoperability benchmark.
- medium confidence, app-rtcp-feedback-and-timing: Source-specific operational, product or deployment details RFC timing checked; GCC/transport feedback references are drafts and implementation-specific.
- medium confidence, app-cookie-scope-and-lifetime: RFC 6265bis approved but still waiting in the RFC Editor queue in October 2026. Verified on the datatracker on 2026-10-30 (IESG 'RFC Ed Queue', RFC Editor 'blocked: Final Approval Pending', rev 22) but it can be published at any time; the lesson and glossary are date-hedged.
- medium confidence, app-email-dmarc-alignment: Google requires SPF, DKIM and DMARC for senders of more than 5,000 messages a day to personal Gmail accounts, unchanged since February 2024. Provider policy; page re-fetched 2026-10-30 and dated in the text, but it can change without notice.
- medium confidence, app-email-dmarc-alignment: RFC 9989 t=y test mode and removal of pct=. Wording verified against RFC 9989 (May 2026), but receiver support for t= and continued handling of legacy pct= records is not measured; the text warns that RFC 7489-era guides can be out of date.
- medium confidence, app-dns-encrypted-transports: Android 11+ devices use DoH over HTTP/3 instead of DoT for well-known resolvers that support it. Verified against Google's July 2022 announcement; current Android behaviour can change with system updates. The text is dated to the announcement.
- medium confidence, app-dns-poisoning-defences: Sequential or small-range NAT port assignment can dramatically reduce source-port randomisation. Now paraphrases RFC 5452 directly; real-world prevalence of such NATs is not measured.
- medium confidence, app-quic-packet-protection: A large certificate chain can cost an extra round trip under QUIC's 3x limit; certificate compression can avoid it. Mechanism verified (RFC 9000 s8, RFC 8879); whether a given chain exceeds 3,600 bytes depends on the chain and on what else the server sends.
- medium confidence, app-dns-header-and-labels: q2: the NXDOMAIN clears at about 10:10. Follows RFC 2308 under the prompt's stated assumption; resolvers can impose their own maximum (BIND 3 h, Unbound 1 h by default) and, if configured, a minimum negative TTL that could lengthen it.


## networks / Network Security

24 question objects changed. Every changed question has a specific independent-review reason in the linked record.

**Corrections in this review:**

- nsec-dos-resources: Cloudflare 29.7 Tbps (2025 Q3 report) was no longer Cloudflare's largest reported attack -> record 31.4 Tbps, about 35 seconds, from the 2025 Q4 report (5 Feb 2026), dated "as of October 2026" after checking the H1 2026 and 2026 Q3 reports; link updated.
- nsec-amplification-budget: "reflected through DNS resolvers with a BAF of about 50" contradicted the table's 28.7 for open resolvers (inherited from baseline) -> "DNS servers with a BAF of about 50 (a round figure near the table's authoritative-server measurement)".
- nsec-tls-handshake-proof: added RFC 9846 s4.1.3's limit on the DOWNGRD sentinel: it protects only when the TLS 1.2 handshake signs the server random (ephemeral key exchange), not with static RSA.
- nsec-vpns-q9 workedExample: "some gateways fragment ... others drop it and rely on an ICMP message reaching the sender" -> RFC 4301 s8 behaviour: the outer DF bit is set, cleared or copied per SA; with DF clear the outer packet is fragmented, with DF set the ICMP must reach the gateway so it can lower the SA path MTU and signal the inner senders.
- nsec-vpns-q9 option 3 explanation: presented ESP padding as always 0-3 bytes for 4-byte alignment -> depends on the cipher's alignment and packet length (0-3 bytes for AES-GCM).
- nsec-wireless-q9 workedExample: stale "lesson 1's MITM principle" -> "the man-in-the-middle principle from the threat units".
- nsec-krack-key-state: the fact wireless-q6 needs (KRACK does not recover the passphrase or PMK) existed only inside the collapsed analogy -> visible sentence sourced from krackattacks.com, including that changing the password does not help.
- nsec-wpa2-derived-keys: the key fact that every WPA2-Personal passphrase holder derives the same PMK (and can derive a captured client's PTK) existed only in the analogy limit -> visible sentence.
- nsec-alert-base-rates reference formula: "tp / (tp + f(1 − p))" read as a function call -> "tp / (tp + (1 − p)f)".
- Wrong-sense links: "MAC-table exhaustion" (bare MAC -> medium access control) -> "exhausting the switch's MAC address table" (nsec-packet-identities); takeaway "Segment remote users" (verb -> TCP segment) -> "Put remote users in their own network segment" (nsec-vpn-access-boundaries).
- Seven reviewer meta-notes removed from learner-visible text: "Content omitted after review" in nsec-amplification-controls, nsec-zero-trust-access, nsec-tls-mutual-authentication, nsec-vpn-access-boundaries and nsec-enterprise-wifi-identities; "Content gap" in nsec-vpn-access-boundaries and nsec-ids-placement-signatures.
- Nine analogies removed as forced, redundant or repeated (32 -> 23): nsec-amplification-controls, nsec-tls-security-properties, nsec-tls-mutual-authentication, nsec-tunnel-byte-budgets, nsec-ipsec-replay-window, nsec-vxlan-isolation, nsec-vpn-access-boundaries, nsec-wpa2-derived-keys, nsec-krack-key-state (reasons in analogyReview).
- Glossary nxdomain: NODATA contrast made exact: NODATA is RCODE 0 (NOERROR) with an empty answer (RFC 2308 s2.2; RFC 9499).

**Scope gaps and exclusions:**

- No new substantive course topic was dropped. Existing disclosed gaps remain: universal attack success/provider capacities, complete Target forensics, live endpoint chain guarantees, trusted-root/adoption counts, vendor exploit-frequency comparisons, universal hardware guessing rates, WEP exact deprecation/test-vector attribution, industry dwell/retention and detector precision rankings are not supplied without comparable evidence.
- No live kernel nftables-policy application was performed: this disposable environment returned netlink Operation not permitted. No permission was lifted and no retry bypass was attempted.
- WireGuard/IPsec/enterprise Wi-Fi deployments were checked against primary specifications; no live VPN, radio, RADIUS or physical-NIC deployment is claimed.
- Synthetic packet fixtures check tool semantics and one example signature, not production detection coverage or malicious intent.
- No formal cryptographic security proof, unbounded implementation correctness or real throughput guarantee is claimed.
- The independent verifier did not lift nftables netlink restrictions; the actual EPERM result is retained. Only offline packet fixtures, local TLS inspection, verified remote TLS and configuration parsing were executed.
- No browser render at 390 px in this pass; rendering was checked only through the build, the analogy-format audit and the formula checker.
- No question tests the downgrade-requirements paragraph in nsec-tls-handshake-proof directly (author gap, confirmed); identity rules did not justify adding a question.
- DNSSEC is not taught here; it is covered by networks/04-application.
- Shadowed dead glossary entries left untouched (author gap, confirmed owner): nat-gateway (owned by networks/02-ip-routing) and the alias "Wi-Fi association" (owned by networks/02).
- Pre-existing cross-module links in unchanged text remain: "padding" opens networks/01 frame-padding (definition generic first, Ethernet example), generic "rate limiting" opens networks/02 icmp-rate-limiting (generic first sentence), "handshake" opens networks/03 handshake.
- Historical figures not re-verified beyond the fetched sources (PTW frame counts, Target breach report, AWS timeouts) keep their earlier verification.

**Low-confidence areas, including preserved qualifications:**

- medium confidence, nsec-packet-identities: Operational examples, security-model assumptions, historical reports and/or time-sensitive deployment details Protocol core verified against fetched primary standards; examples are bounded models, platform/policy facts can change, and no arbitrary security proof or live radio/VPN/kernel-policy deployment is claimed.
- medium confidence, nsec-authentication-replay: Operational examples, security-model assumptions, historical reports and/or time-sensitive deployment details Protocol core verified against fetched primary standards; examples are bounded models, platform/policy facts can change, and no arbitrary security proof or live radio/VPN/kernel-policy deployment is claimed.
- medium confidence, nsec-dos-resources: Operational examples, security-model assumptions, historical reports and/or time-sensitive deployment details Protocol core verified against fetched primary standards; examples are bounded models, platform/policy facts can change, and no arbitrary security proof or live radio/VPN/kernel-policy deployment is claimed.
- medium confidence, nsec-amplification-budget: Operational examples, security-model assumptions, historical reports and/or time-sensitive deployment details Protocol core verified against fetched primary standards; examples are bounded models, platform/policy facts can change, and no arbitrary security proof or live radio/VPN/kernel-policy deployment is claimed.
- medium confidence, nsec-amplification-controls: Operational examples, security-model assumptions, historical reports and/or time-sensitive deployment details Protocol core verified against fetched primary standards; examples are bounded models, platform/policy facts can change, and no arbitrary security proof or live radio/VPN/kernel-policy deployment is claimed.
- medium confidence, nsec-firewall-rule-order: Operational examples, security-model assumptions, historical reports and/or time-sensitive deployment details Protocol core verified against fetched primary standards; examples are bounded models, platform/policy facts can change, and no arbitrary security proof or live radio/VPN/kernel-policy deployment is claimed.
- medium confidence, nsec-firewall-state-cloud: Operational examples, security-model assumptions, historical reports and/or time-sensitive deployment details Protocol core verified against fetched primary standards; examples are bounded models, platform/policy facts can change, and no arbitrary security proof or live radio/VPN/kernel-policy deployment is claimed.
- medium confidence, nsec-segmentation-boundaries: Operational examples, security-model assumptions, historical reports and/or time-sensitive deployment details Protocol core verified against fetched primary standards; examples are bounded models, platform/policy facts can change, and no arbitrary security proof or live radio/VPN/kernel-policy deployment is claimed.
- medium confidence, nsec-zero-trust-access: Operational examples, security-model assumptions, historical reports and/or time-sensitive deployment details Protocol core verified against fetched primary standards; examples are bounded models, platform/policy facts can change, and no arbitrary security proof or live radio/VPN/kernel-policy deployment is claimed.
- medium confidence, nsec-tls-security-properties: Operational examples, security-model assumptions, historical reports and/or time-sensitive deployment details Protocol core verified against fetched primary standards; examples are bounded models, platform/policy facts can change, and no arbitrary security proof or live radio/VPN/kernel-policy deployment is claimed.
- medium confidence, nsec-tls-handshake-proof: Operational examples, security-model assumptions, historical reports and/or time-sensitive deployment details Protocol core verified against fetched primary standards; examples are bounded models, platform/policy facts can change, and no arbitrary security proof or live radio/VPN/kernel-policy deployment is claimed.
- medium confidence, nsec-tls-resumption-replay: Operational examples, security-model assumptions, historical reports and/or time-sensitive deployment details Protocol core verified against fetched primary standards; examples are bounded models, platform/policy facts can change, and no arbitrary security proof or live radio/VPN/kernel-policy deployment is claimed.
- medium confidence, nsec-tls-certificate-path: Operational examples, security-model assumptions, historical reports and/or time-sensitive deployment details Protocol core verified against fetched primary standards; examples are bounded models, platform/policy facts can change, and no arbitrary security proof or live radio/VPN/kernel-policy deployment is claimed.
- medium confidence, nsec-tls-certificate-operations: Operational examples, security-model assumptions, historical reports and/or time-sensitive deployment details Protocol core verified against fetched primary standards; examples are bounded models, platform/policy facts can change, and no arbitrary security proof or live radio/VPN/kernel-policy deployment is claimed.
- medium confidence, nsec-tls-ech-privacy: Operational examples, security-model assumptions, historical reports and/or time-sensitive deployment details Protocol core verified against fetched primary standards; examples are bounded models, platform/policy facts can change, and no arbitrary security proof or live radio/VPN/kernel-policy deployment is claimed.
- medium confidence, nsec-tls-mutual-authentication: Operational examples, security-model assumptions, historical reports and/or time-sensitive deployment details Protocol core verified against fetched primary standards; examples are bounded models, platform/policy facts can change, and no arbitrary security proof or live radio/VPN/kernel-policy deployment is claimed.
- medium confidence, nsec-tunnel-byte-budgets: Operational examples, security-model assumptions, historical reports and/or time-sensitive deployment details Protocol core verified against fetched primary standards; examples are bounded models, platform/policy facts can change, and no arbitrary security proof or live radio/VPN/kernel-policy deployment is claimed.
- medium confidence, nsec-tunnel-pmtu: Operational examples, security-model assumptions, historical reports and/or time-sensitive deployment details Protocol core verified against fetched primary standards; examples are bounded models, platform/policy facts can change, and no arbitrary security proof or live radio/VPN/kernel-policy deployment is claimed.
- medium confidence, nsec-ipsec-security-associations: Operational examples, security-model assumptions, historical reports and/or time-sensitive deployment details Protocol core verified against fetched primary standards; examples are bounded models, platform/policy facts can change, and no arbitrary security proof or live radio/VPN/kernel-policy deployment is claimed.
- medium confidence, nsec-ipsec-replay-window: Operational examples, security-model assumptions, historical reports and/or time-sensitive deployment details Protocol core verified against fetched primary standards; examples are bounded models, platform/policy facts can change, and no arbitrary security proof or live radio/VPN/kernel-policy deployment is claimed.
- medium confidence, nsec-wireguard-peer-routing: Operational examples, security-model assumptions, historical reports and/or time-sensitive deployment details Protocol core verified against fetched primary standards; examples are bounded models, platform/policy facts can change, and no arbitrary security proof or live radio/VPN/kernel-policy deployment is claimed.
- medium confidence, nsec-vxlan-isolation: Operational examples, security-model assumptions, historical reports and/or time-sensitive deployment details Protocol core verified against fetched primary standards; examples are bounded models, platform/policy facts can change, and no arbitrary security proof or live radio/VPN/kernel-policy deployment is claimed.
- medium confidence, nsec-vpn-access-boundaries: Operational examples, security-model assumptions, historical reports and/or time-sensitive deployment details Protocol core verified against fetched primary standards; examples are bounded models, platform/policy facts can change, and no arbitrary security proof or live radio/VPN/kernel-policy deployment is claimed.
- medium confidence, nsec-wifi-wep-reused-ivs: Operational examples, security-model assumptions, historical reports and/or time-sensitive deployment details Protocol core verified against fetched primary standards; examples are bounded models, platform/policy facts can change, and no arbitrary security proof or live radio/VPN/kernel-policy deployment is claimed.
- medium confidence, nsec-wep-keying-integrity: Operational examples, security-model assumptions, historical reports and/or time-sensitive deployment details Protocol core verified against fetched primary standards; examples are bounded models, platform/policy facts can change, and no arbitrary security proof or live radio/VPN/kernel-policy deployment is claimed.
- medium confidence, nsec-wpa2-derived-keys: Operational examples, security-model assumptions, historical reports and/or time-sensitive deployment details Protocol core verified against fetched primary standards; examples are bounded models, platform/policy facts can change, and no arbitrary security proof or live radio/VPN/kernel-policy deployment is claimed.
- medium confidence, nsec-wpa2-offline-guesses: Operational examples, security-model assumptions, historical reports and/or time-sensitive deployment details Protocol core verified against fetched primary standards; examples are bounded models, platform/policy facts can change, and no arbitrary security proof or live radio/VPN/kernel-policy deployment is claimed.
- medium confidence, nsec-krack-key-state: Operational examples, security-model assumptions, historical reports and/or time-sensitive deployment details Protocol core verified against fetched primary standards; examples are bounded models, platform/policy facts can change, and no arbitrary security proof or live radio/VPN/kernel-policy deployment is claimed.
- medium confidence, nsec-wpa3-sae-transition: Operational examples, security-model assumptions, historical reports and/or time-sensitive deployment details Protocol core verified against fetched primary standards; examples are bounded models, platform/policy facts can change, and no arbitrary security proof or live radio/VPN/kernel-policy deployment is claimed.
- medium confidence, nsec-enterprise-wifi-identities: Operational examples, security-model assumptions, historical reports and/or time-sensitive deployment details Protocol core verified against fetched primary standards; examples are bounded models, platform/policy facts can change, and no arbitrary security proof or live radio/VPN/kernel-policy deployment is claimed.
- medium confidence, nsec-ids-placement-signatures: Operational examples, security-model assumptions, historical reports and/or time-sensitive deployment details Protocol core verified against fetched primary standards; examples are bounded models, platform/policy facts can change, and no arbitrary security proof or live radio/VPN/kernel-policy deployment is claimed.
- medium confidence, nsec-alert-base-rates: Operational examples, security-model assumptions, historical reports and/or time-sensitive deployment details Protocol core verified against fetched primary standards; examples are bounded models, platform/policy facts can change, and no arbitrary security proof or live radio/VPN/kernel-policy deployment is claimed.
- medium confidence, nsec-packet-filter-reading: Operational examples, security-model assumptions, historical reports and/or time-sensitive deployment details Protocol core verified against fetched primary standards; examples are bounded models, platform/policy facts can change, and no arbitrary security proof or live radio/VPN/kernel-policy deployment is claimed.
- medium confidence, nsec-capture-offloads-storage: Operational examples, security-model assumptions, historical reports and/or time-sensitive deployment details Protocol core verified against fetched primary standards; examples are bounded models, platform/policy facts can change, and no arbitrary security proof or live radio/VPN/kernel-policy deployment is claimed.
- medium confidence, nsec-encrypted-traffic-evidence: Operational examples, security-model assumptions, historical reports and/or time-sensitive deployment details Protocol core verified against fetched primary standards; examples are bounded models, platform/policy facts can change, and no arbitrary security proof or live radio/VPN/kernel-policy deployment is claimed.
- medium confidence, nsec-flow-record-investigations: Operational examples, security-model assumptions, historical reports and/or time-sensitive deployment details Protocol core verified against fetched primary standards; examples are bounded models, platform/policy facts can change, and no arbitrary security proof or live radio/VPN/kernel-policy deployment is claimed.
- medium confidence, nsec-dos-resources: Cloudflare's record 31.4 Tbps attack (2025 Q4 report, Feb 2026) is still the largest it has reported as of October 2026. Provider-reported measurement; the "still largest" part rests on the H1 2026 and 2026 Q3 reports (fetched 2026-10-30) not reporting a larger one, and a new record can be announced at any time. Dated and attributed in the text.
- medium confidence, nsec-tls-certificate-operations: Maximum validity 398/200/100/47 days by issue date (15 Mar 2026, 15 Mar 2027, 15 Mar 2029). Verified in BR v2.3.1 (4 Oct 2026) s6.3.2, but CA/Browser Forum ballots can change the schedule; the lesson dates and hedges it.
- medium confidence, nsec-tls-certificate-operations: Let's Encrypt turned off OCSP in August 2025 and publishes revocation only via CRLs; BR SC063 made OCSP optional from March 2024. Verified in the Let's Encrypt post (6 Aug 2025) and the BR revision table; provider policy can change.
- medium confidence, nsec-ipsec-security-associations: vpns-q9: after moving behind NAT, full-size packets exceed the link by 8 bytes and stall when ICMP is blocked. NAT-T overhead and RFC 4301 DF handling verified; actual behaviour depends on the gateway's DF-bit policy and where the 1,500-byte limit sits, which the worked example now states.
- medium confidence, nsec-capture-offloads-storage: Most web traffic is encrypted and encrypted bytes barely compress; teams commonly keep summaries longer than full packets. General practice statements, hedged in the text; no single measurement cited.


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


## security / Security Fundamentals

13 question objects changed. Every changed question has a specific independent-review reason in the linked record.

**Corrections in this review:**

- secf-kill-chain-stages.md: Unified Kill Chain "(Paul Pols, 2017) ... 18 phases grouped as getting in, getting through and getting out" -> "(Paul Pols, first published in 2017) ... 18 phases, grouped as In (gaining a foothold), Through (spreading through the network) and Out (acting on the objective)", matching the white paper's In/Through/Out grouping.
- secf-password-storage.md: scrypt reference card In words "the cost and the block-size settings" linked "block-size" to the subnetting Block size term -> "the cost setting and the block-size parameter".
- secf-least-privilege-design.md: valet-key analogy limit "A car key's limits are fixed when it is made" -> "usually fixed" (some keys are programmable).
- secf-detection-evidence.md: shoplifter analogy said a hash or IP address is "trivial to change"; the Pyramid of Pain ranks IPs as easy and only hashes as trivial -> "easy to change".
- secf-phishing-resistant-login.md: pitfall "MFA on login but not recovery" linked bare "recovery" to incident recovery (security/06) -> "account recovery".
- secf-intrusion-defence.questions.json secf-kill-chain-q11 workedExample: reviewer-voice "This lesson does not establish jurisdiction-specific legal duties." -> "Legal notification duties depend on the jurisdiction and the data involved."
- glossary secf-persistence: "keeping access across restarts, logons or credential changes ... corresponds to the kill chain's installation stage" -> ATT&CK wording "across restarts, changed credentials and other interruptions" and "roughly corresponds to the Lockheed Martin kill chain's installation stage".
- glossary secf-scheduled-task: "ATT&CK records as a persistence and execution technique" omitted privilege escalation -> "ATT&CK lists under the execution, persistence and privilege-escalation tactics" (T1053.005).

**Scope gaps and exclusions:**

- No production authentication/recovery provider, SIEM/EDR, AWS/Windows/SELinux policy, PostgreSQL RLS or ReBAC service was deployed; handler fixtures are local sketches.
- Bell–LaPadula and strict Biba remain level-only teaching models without compartments, complete formal proofs, covert-channel treatment or trusted-subject policy.
- Inherited encyclopedic/background dictionary terms and some historical/general explanations retain medium confidence where every detail has not been established by a primary source. The per-term ledger identifies all 408 reviewed records and their confidence.
- The TOCTOU C fragment was compiled as an ordinary object only; no setuid binary or privilege-race exploit was deployed or executed.
- Password-search rates and additive attack costs are explicit hypothetical models. Native assertions verify only finite cases; no attacker-performance benchmark, constant-time timing proof or intrusion exercise is supplied.
- The Uber vendor disclosure was independently readable through the browser tool (redirecting to /de/en/); CLI returned 406. This is a transport distinction, not a successful curl claim.
- Bare word "recovery" in unchanged questions (secf-cia-aaa-q4 explanation and workedExample, secf-authentication-q10/q11, secf-kill-chain-q5) and the phishing lesson title still links to security/06 incident-recovery; not reworded to avoid churning unchanged questions. Integration dependency on security/06.
- Browser rendering at 390 px and offline checks were not run in this module pass; delegated to the root integration pass.
- The setuid C TOCTOU fragment (secf-principles-q8) was reviewed against access(2) semantics but not executed as a privileged race.

**Low-confidence areas, including preserved qualifications:**

- medium confidence, secf-security-properties: Deployment-dependent controls, threat-model assumptions, historical taxonomy or inherited explanatory vocabulary. Primary core checked and examples bounded; this unit does not establish complete production control effectiveness, formal security, human attribution or every inherited secondary detail.
- medium confidence, secf-security-tradeoffs: Deployment-dependent controls, threat-model assumptions, historical taxonomy or inherited explanatory vocabulary. Primary core checked and examples bounded; this unit does not establish complete production control effectiveness, formal security, human attribution or every inherited secondary detail.
- medium confidence, secf-identity-permission: Deployment-dependent controls, threat-model assumptions, historical taxonomy or inherited explanatory vocabulary. Primary core checked and examples bounded; this unit does not establish complete production control effectiveness, formal security, human attribution or every inherited secondary detail.
- medium confidence, secf-accounting-evidence: Deployment-dependent controls, threat-model assumptions, historical taxonomy or inherited explanatory vocabulary. Primary core checked and examples bounded; this unit does not establish complete production control effectiveness, formal security, human attribution or every inherited secondary detail.
- medium confidence, secf-system-boundaries: Deployment-dependent controls, threat-model assumptions, historical taxonomy or inherited explanatory vocabulary. Primary core checked and examples bounded; this unit does not establish complete production control effectiveness, formal security, human attribution or every inherited secondary detail.
- medium confidence, secf-stride-threats: Deployment-dependent controls, threat-model assumptions, historical taxonomy or inherited explanatory vocabulary. Primary core checked and examples bounded; this unit does not establish complete production control effectiveness, formal security, human attribution or every inherited secondary detail.
- medium confidence, secf-attack-tree-costs: Deployment-dependent controls, threat-model assumptions, historical taxonomy or inherited explanatory vocabulary. Primary core checked and examples bounded; this unit does not establish complete production control effectiveness, formal security, human attribution or every inherited secondary detail.
- medium confidence, secf-risk-responses: Deployment-dependent controls, threat-model assumptions, historical taxonomy or inherited explanatory vocabulary. Primary core checked and examples bounded; this unit does not establish complete production control effectiveness, formal security, human attribution or every inherited secondary detail.
- medium confidence, secf-least-privilege-design: Deployment-dependent controls, threat-model assumptions, historical taxonomy or inherited explanatory vocabulary. Primary core checked and examples bounded; this unit does not establish complete production control effectiveness, formal security, human attribution or every inherited secondary detail.
- medium confidence, secf-layers-defaults: Deployment-dependent controls, threat-model assumptions, historical taxonomy or inherited explanatory vocabulary. Primary core checked and examples bounded; this unit does not establish complete production control effectiveness, formal security, human attribution or every inherited secondary detail.
- medium confidence, secf-mediation-open-design: Deployment-dependent controls, threat-model assumptions, historical taxonomy or inherited explanatory vocabulary. Primary core checked and examples bounded; this unit does not establish complete production control effectiveness, formal security, human attribution or every inherited secondary detail.
- medium confidence, secf-shared-authority-usability: Deployment-dependent controls, threat-model assumptions, historical taxonomy or inherited explanatory vocabulary. Primary core checked and examples bounded; this unit does not establish complete production control effectiveness, formal security, human attribution or every inherited secondary detail.
- medium confidence, secf-factors-password-failures: Deployment-dependent controls, threat-model assumptions, historical taxonomy or inherited explanatory vocabulary. Primary core checked and examples bounded; this unit does not establish complete production control effectiveness, formal security, human attribution or every inherited secondary detail.
- medium confidence, secf-random-password-entropy: Deployment-dependent controls, threat-model assumptions, historical taxonomy or inherited explanatory vocabulary. Primary core checked and examples bounded; this unit does not establish complete production control effectiveness, formal security, human attribution or every inherited secondary detail.
- medium confidence, secf-password-policy: Deployment-dependent controls, threat-model assumptions, historical taxonomy or inherited explanatory vocabulary. Primary core checked and examples bounded; this unit does not establish complete production control effectiveness, formal security, human attribution or every inherited secondary detail.
- medium confidence, secf-password-storage: Deployment-dependent controls, threat-model assumptions, historical taxonomy or inherited explanatory vocabulary. Primary core checked and examples bounded; this unit does not establish complete production control effectiveness, formal security, human attribution or every inherited secondary detail.
- medium confidence, secf-guessing-costs: Deployment-dependent controls, threat-model assumptions, historical taxonomy or inherited explanatory vocabulary. Primary core checked and examples bounded; this unit does not establish complete production control effectiveness, formal security, human attribution or every inherited secondary detail.
- medium confidence, secf-phishing-resistant-login: Deployment-dependent controls, threat-model assumptions, historical taxonomy or inherited explanatory vocabulary. Primary core checked and examples bounded; this unit does not establish complete production control effectiveness, formal security, human attribution or every inherited secondary detail.
- medium confidence, secf-permission-matrix: Deployment-dependent controls, threat-model assumptions, historical taxonomy or inherited explanatory vocabulary. Primary core checked and examples bounded; this unit does not establish complete production control effectiveness, formal security, human attribution or every inherited secondary detail.
- medium confidence, secf-unix-dac: Deployment-dependent controls, threat-model assumptions, historical taxonomy or inherited explanatory vocabulary. Primary core checked and examples bounded; this unit does not establish complete production control effectiveness, formal security, human attribution or every inherited secondary detail.
- medium confidence, secf-mandatory-labels: Deployment-dependent controls, threat-model assumptions, historical taxonomy or inherited explanatory vocabulary. Primary core checked and examples bounded; this unit does not establish complete production control effectiveness, formal security, human attribution or every inherited secondary detail.
- medium confidence, secf-policy-models: Deployment-dependent controls, threat-model assumptions, historical taxonomy or inherited explanatory vocabulary. Primary core checked and examples bounded; this unit does not establish complete production control effectiveness, formal security, human attribution or every inherited secondary detail.
- medium confidence, secf-object-authorisation: Deployment-dependent controls, threat-model assumptions, historical taxonomy or inherited explanatory vocabulary. Primary core checked and examples bounded; this unit does not establish complete production control effectiveness, formal security, human attribution or every inherited secondary detail.
- medium confidence, secf-kill-chain-stages: Deployment-dependent controls, threat-model assumptions, historical taxonomy or inherited explanatory vocabulary. Primary core checked and examples bounded; this unit does not establish complete production control effectiveness, formal security, human attribution or every inherited secondary detail.
- medium confidence, secf-attack-vocabulary: Deployment-dependent controls, threat-model assumptions, historical taxonomy or inherited explanatory vocabulary. Primary core checked and examples bounded; this unit does not establish complete production control effectiveness, formal security, human attribution or every inherited secondary detail.
- medium confidence, secf-intrusion-defence: Deployment-dependent controls, threat-model assumptions, historical taxonomy or inherited explanatory vocabulary. Primary core checked and examples bounded; this unit does not establish complete production control effectiveness, formal security, human attribution or every inherited secondary detail.
- medium confidence, secf-detection-evidence: Deployment-dependent controls, threat-model assumptions, historical taxonomy or inherited explanatory vocabulary. Primary core checked and examples bounded; this unit does not establish complete production control effectiveness, formal security, human attribution or every inherited secondary detail.
- medium confidence, secf-detection-evidence: M-Trends 2026: 14-day global median dwell time for 2025 investigations, up from 11 days in 2024. Figures fetched from the official M-Trends 2026 blog; the dwell sentence does not repeat the year, which is taken from the post's statement that the data come from investigations conducted in 2025. Annual and time-sensitive.
- medium confidence, secf-attack-vocabulary: ATT&CK v20 Enterprise lists 15 tactics including Stealth and Defense Impairment. Verified on the live page (October 2026), but tactic names and counts change between ATT&CK versions; the lesson dates the claim.
- medium confidence, secf-least-privilege-design: Valet-key analogy: some valet keys start the car but cannot open the boot or glovebox. Supported by a secondary source (Wikipedia car-key article); behaviour varies by manufacturer and the text says "Some cars".
- medium confidence, secf-factors-password-failures: Skimmer limit: a tampered card reader can capture card data and PIN together. Supported by a secondary source (Wikipedia credit card fraud, Skimming section); an FBI page was blocked to automated fetch.


## security / Cryptography Basics

47 question objects changed. Every changed question has a specific independent-review reason in the linked record.

**Corrections in this review:**

- crypto-public-key-transition.md and crypto-asymmetric-q11: 'found tens of thousands of RSA keys sharing a prime factor' / 'factored tens of thousands of real keys' → 'more than 16,000 distinct RSA public keys that shared a prime factor … exposing the private keys of about 64,000 TLS hosts' (Heninger et al. 2012: 16,717 distinct keys, 64,081 TLS hosts).
- crypto-hash-uses-encoding.md: undated 'Git … now hardened against SHAttered-style collisions and gradually moving to SHA-256' → dated status from the Git 2.56 docs: SHA-1 remains the default with a hardened implementation, SHA-256 repositories are supported, and Git plans to make SHA-256 the default for new repositories in Git 3.0 (no release date).
- crypto-gcm-nonce-limits.md: added that the 2^32/2^-32 figures come from the 2007 SP 800-38D and that NIST's revision has so far issued only pre-draft calls for comments (January 2025, June 2026; proposing to drop tags under 96 bits), no draft.
- crypto-x25519-derived-keys.md: unqualified 'Python's cryptography raises ValueError' → 'Python's cryptography library (checked with version 50) raises ValueError' (behaviour comes from its OpenSSL backend and is not in the API docs).
- crypto-dh-agreement.md: the discrete-logarithm hardness (what Eve would need) was stated only inside the collapsed paint analogy after the diagram conversion → added a visible sentence after the toy check.
- crypto-ecc-scalar-security.questions.json crypto-asymmetric-q10: prompt formula card defined × as scalar multiplication while using it for ordinary multiplication in '2 × x' → toy data restated in prose (card removed).
- crypto-elliptic-curve-points-q1: link title 'Primary specification' → 'SEC 1: Elliptic Curve Cryptography, version 2.0'.
- glossary block-size-crypto: definition covered only cipher/hash blocks, but the entry now captures security/01's 'r the block size' (scrypt) → added scrypt's block-size parameter r (128 × r-byte blocks, RFC 7914).
- Wrong-sense links introduced by new text: crypto-hash-uses-encoding 'dictionary recovery' (→ incident recovery) reworded; till-receipt analogy 'running total' (→ DSA prefix sum) → 'total so far'/'printed total'; bracket analogy title 'knockout tournament' (→ DSA selection method) → 'sports tournament'; crypto-symmetric-q10 workedExample 'enable recovery and forgery' → 'pin down H and forge tags'.
- Formula load (editorial, not counted as accuracy errors): removed essential P′ = (C ⊕ D) ⊕ K = P ⊕ D (crypto-ciphertext-malleability) and essential g^a ≡ A (mod p) (crypto-dh-groups-assumptions), replacing both with visible prose; removed the reference Euler-theorem derivation (crypto-rsa-roundtrip); demoted to reference the length-extension card (crypto-hash-constructions), textbook-RSA malleability card (crypto-textbook-rsa-failures) and ECDH card (crypto-x25519-derived-keys), rewriting their In words lines and surrounding prose so no hidden symbol is needed. Essentials 14 → 9; reference 14 → 16; question cards 4 → 3.

**Scope gaps and exclusions:**

- Formal HMAC security reductions and complete asymptotic attack proofs are not taught; constructions and assumptions are checked against standards and original-author cryptography references.
- No hardware throughput benchmarks, resource-backed quantum attack estimate or proof that a toy implementation is secure is supplied. Hypothetical rates and generic work models are explicitly conditional.
- Demonstrations omit complete production authentication, provisioning, replay protection, storage, rotation and operational error handling. Library boundaries and per-protocol requirements remain necessary.
- Original 2004 MD5 collision paper endpoints returned HTTP 403 in this environment. The historical date is supported by later original research and retained at medium confidence; no direct access to that original paper is claimed.
- Generic mathematical definitions use original-author Handbook of Applied Cryptography chapters as authoritative references, supplemented by native checks and standards; not every basic definition has a separate first-publication source.
- This is a subdivision of existing material, not a complete course in modern cryptographic protocol proofs or post-quantum migration.
- No dedicated signature lesson (ECDSA/EdDSA nonce generation appears only through the PS3 incident); signatures are covered in later modules (author gap, confirmed).
- AES-GCM-SIV and XChaCha20-Poly1305 are named with their key property but not explained in depth.
- SP 800-90A DRBG internals are not taught (only 'use the OS CSPRNG').
- Browser rendering at 390 px and offline checks were not run in this module pass; delegated to the root integration pass.
- Unchanged question crypto-passwords-kdfs-q12 still links bare 'recovery' (key recovery) to security/06 incident recovery; not reworded here to avoid churning an unchanged question (integration dependency).

**Low-confidence areas, including preserved qualifications:**

- medium confidence, crypto-aes-keys: Current library behaviour, policy guidance, historical observations and/or idealised attack bounds in this unit Primary/official sources and local fixtures support the stated scope. Product defaults and policy change; idealised work estimates are not measured runtimes, and historical figures do not establish current prevalence.
- medium confidence, crypto-cbc-padding: Current library behaviour, policy guidance, historical observations and/or idealised attack bounds in this unit Primary/official sources and local fixtures support the stated scope. Product defaults and policy change; idealised work estimates are not measured runtimes, and historical figures do not establish current prevalence.
- medium confidence, crypto-aead-api: Current library behaviour, policy guidance, historical observations and/or idealised attack bounds in this unit Primary/official sources and local fixtures support the stated scope. Product defaults and policy change; idealised work estimates are not measured runtimes, and historical figures do not establish current prevalence.
- medium confidence, crypto-gcm-nonce-limits: Current library behaviour, policy guidance, historical observations and/or idealised attack bounds in this unit Primary/official sources and local fixtures support the stated scope. Product defaults and policy change; idealised work estimates are not measured runtimes, and historical figures do not establish current prevalence.
- medium confidence, crypto-hash-security-goals: Current library behaviour, policy guidance, historical observations and/or idealised attack bounds in this unit Primary/official sources and local fixtures support the stated scope. Product defaults and policy change; idealised work estimates are not measured runtimes, and historical figures do not establish current prevalence.
- medium confidence, crypto-hash-birthday: Current library behaviour, policy guidance, historical observations and/or idealised attack bounds in this unit Primary/official sources and local fixtures support the stated scope. Product defaults and policy change; idealised work estimates are not measured runtimes, and historical figures do not establish current prevalence.
- medium confidence, crypto-hash-constructions: Current library behaviour, policy guidance, historical observations and/or idealised attack bounds in this unit Primary/official sources and local fixtures support the stated scope. Product defaults and policy change; idealised work estimates are not measured runtimes, and historical figures do not establish current prevalence.
- medium confidence, crypto-hash-algorithm-choices: Current library behaviour, policy guidance, historical observations and/or idealised attack bounds in this unit Primary/official sources and local fixtures support the stated scope. Product defaults and policy change; idealised work estimates are not measured runtimes, and historical figures do not establish current prevalence.
- medium confidence, crypto-hash-uses-encoding: Current library behaviour, policy guidance, historical observations and/or idealised attack bounds in this unit Primary/official sources and local fixtures support the stated scope. Product defaults and policy change; idealised work estimates are not measured runtimes, and historical figures do not establish current prevalence.
- medium confidence, crypto-mac-goals: Current library behaviour, policy guidance, historical observations and/or idealised attack bounds in this unit Primary/official sources and local fixtures support the stated scope. Product defaults and policy change; idealised work estimates are not measured runtimes, and historical figures do not establish current prevalence.
- medium confidence, crypto-hmac-construction: Current library behaviour, policy guidance, historical observations and/or idealised attack bounds in this unit Primary/official sources and local fixtures support the stated scope. Product defaults and policy change; idealised work estimates are not measured runtimes, and historical figures do not establish current prevalence.
- medium confidence, crypto-mac-deployments: Current library behaviour, policy guidance, historical observations and/or idealised attack bounds in this unit Primary/official sources and local fixtures support the stated scope. Product defaults and policy change; idealised work estimates are not measured runtimes, and historical figures do not establish current prevalence.
- medium confidence, crypto-encryption-mac-order: Current library behaviour, policy guidance, historical observations and/or idealised attack bounds in this unit Primary/official sources and local fixtures support the stated scope. Product defaults and policy change; idealised work estimates are not measured runtimes, and historical figures do not establish current prevalence.
- medium confidence, crypto-rsa-public-keys: Current library behaviour, policy guidance, historical observations and/or idealised attack bounds in this unit Primary/official sources and local fixtures support the stated scope. Product defaults and policy change; idealised work estimates are not measured runtimes, and historical figures do not establish current prevalence.
- medium confidence, crypto-rsa-oaep-hybrid: Current library behaviour, policy guidance, historical observations and/or idealised attack bounds in this unit Primary/official sources and local fixtures support the stated scope. Product defaults and policy change; idealised work estimates are not measured runtimes, and historical figures do not establish current prevalence.
- medium confidence, crypto-ecc-scalar-security: Current library behaviour, policy guidance, historical observations and/or idealised attack bounds in this unit Primary/official sources and local fixtures support the stated scope. Product defaults and policy change; idealised work estimates are not measured runtimes, and historical figures do not establish current prevalence.
- medium confidence, crypto-public-key-transition: Current library behaviour, policy guidance, historical observations and/or idealised attack bounds in this unit Primary/official sources and local fixtures support the stated scope. Product defaults and policy change; idealised work estimates are not measured runtimes, and historical figures do not establish current prevalence.
- medium confidence, crypto-dh-groups-assumptions: Current library behaviour, policy guidance, historical observations and/or idealised attack bounds in this unit Primary/official sources and local fixtures support the stated scope. Product defaults and policy change; idealised work estimates are not measured runtimes, and historical figures do not establish current prevalence.
- medium confidence, crypto-dh-authentication: Current library behaviour, policy guidance, historical observations and/or idealised attack bounds in this unit Primary/official sources and local fixtures support the stated scope. Product defaults and policy change; idealised work estimates are not measured runtimes, and historical figures do not establish current prevalence.
- medium confidence, crypto-dh-parameter-validation: Current library behaviour, policy guidance, historical observations and/or idealised attack bounds in this unit Primary/official sources and local fixtures support the stated scope. Product defaults and policy change; idealised work estimates are not measured runtimes, and historical figures do not establish current prevalence.
- medium confidence, crypto-x25519-derived-keys: Current library behaviour, policy guidance, historical observations and/or idealised attack bounds in this unit Primary/official sources and local fixtures support the stated scope. Product defaults and policy change; idealised work estimates are not measured runtimes, and historical figures do not establish current prevalence.
- medium confidence, crypto-forward-secrecy: Current library behaviour, policy guidance, historical observations and/or idealised attack bounds in this unit Primary/official sources and local fixtures support the stated scope. Product defaults and policy change; idealised work estimates are not measured runtimes, and historical figures do not establish current prevalence.
- medium confidence, crypto-randomness-sources: Current library behaviour, policy guidance, historical observations and/or idealised attack bounds in this unit Primary/official sources and local fixtures support the stated scope. Product defaults and policy change; idealised work estimates are not measured runtimes, and historical figures do not establish current prevalence.
- medium confidence, crypto-hkdf-purpose-labels: Current library behaviour, policy guidance, historical observations and/or idealised attack bounds in this unit Primary/official sources and local fixtures support the stated scope. Product defaults and policy change; idealised work estimates are not measured runtimes, and historical figures do not establish current prevalence.
- medium confidence, crypto-password-salts-cost: Current library behaviour, policy guidance, historical observations and/or idealised attack bounds in this unit Primary/official sources and local fixtures support the stated scope. Product defaults and policy change; idealised work estimates are not measured runtimes, and historical figures do not establish current prevalence.
- medium confidence, crypto-password-algorithms: Current library behaviour, policy guidance, historical observations and/or idealised attack bounds in this unit Primary/official sources and local fixtures support the stated scope. Product defaults and policy change; idealised work estimates are not measured runtimes, and historical figures do not establish current prevalence.
- medium confidence, crypto-argon2-login-migration: Current library behaviour, policy guidance, historical observations and/or idealised attack bounds in this unit Primary/official sources and local fixtures support the stated scope. Product defaults and policy change; idealised work estimates are not measured runtimes, and historical figures do not establish current prevalence.
- medium confidence, crypto-password-peppers: Current library behaviour, policy guidance, historical observations and/or idealised attack bounds in this unit Primary/official sources and local fixtures support the stated scope. Product defaults and policy change; idealised work estimates are not measured runtimes, and historical figures do not establish current prevalence.
- medium confidence, crypto-x25519-derived-keys: Python's cryptography raises ValueError from X25519 exchange when the shared secret would be all zero (low-order peer point). Executed with cryptography 50.0.2/OpenSSL 4.0.3 and confirmed in the pyca Rust backend and Wycheproof test, but the public API docs do not document it; behaviour depends on the backend and could change. Text says 'checked with version 50'.
- medium confidence, crypto-gcm-nonce-limits: SP 800-38D: at most 2^-32 chance of a repeated IV per key and at most 2^32 invocations with random IVs. Verified in the current 2007 final; NIST is revising SP 800-38D (pre-draft calls January 2025 and June 2026, no draft yet). Time-sensitive; the lesson now says so.
- medium confidence, crypto-hash-algorithm-choices / crypto-rsa-oaep-hybrid / crypto-public-key-transition: NIST IR 8547 (final, 27 October 2026): deprecate quantum-vulnerable public-key algorithms after 2030, disallow after 2035; replaces the 1 January 2031 projection for 112-bit schemes; SHA-1 disallowed in FIPS-validated modules after 2030; HQC FIPS under development; earlier deadlines under EO 14412/OMB M-26-15. Verified against the freshly fetched final PDF; policy is time-sensitive and application-specific guidance may set earlier dates.
- medium confidence, crypto-hash-uses-encoding: Git defaults to (hardened) SHA-1, supports SHA-256 repositories and plans SHA-256 as the default in Git 3.0. From the Git 2.56 documentation fetched 2026-10-30; release-dependent and dated in the text.
- medium confidence, crypto-password-algorithms / crypto-password-salts-cost: OWASP minimums: Argon2id 19 MiB/2/1; scrypt 2^17/8/1; bcrypt ≥10 with 72-byte limit; PBKDF2-HMAC-SHA-256 600,000. Fetched 2026-10-30 and matched; guidance is periodically revised.
- medium confidence, crypto-randomness-sources: Debian OpenSSL keys had to be regenerated after the fix. Versions from NVD; regeneration requirement from Ubuntu USN-612-1 ('keys … must be considered untrustworthy … even after the update'); the Debian advisory DSA-1571 and its mailing-list copy are behind a JavaScript challenge and were not read.
- medium confidence, crypto-password-salts-cost (q6): Salted SHA-256 versus Argon2id at OWASP's minimum differ by 'many orders of magnitude' per guess. Qualitative and hardware-dependent; no benchmark was run and the text deliberately gives no figure.


## software-engineering / Design Principles & Clean Code

9 question objects changed. Every changed question has a specific independent-review reason in the linked record.

**Corrections in this review:**

- {"lesson":"sep-names-and-units","before":"Behaviour is unchanged: the threshold is still 5 and the lockout still lasts 86,400 seconds","after":"The rule is unchanged ... In the \"after\" version lock receives a timedelta rather than a bare number of seconds, so the unit travels with the value.","reason":"The before passes the int 86400 and the after passes timedelta(days=1); the call's argument type changed, so 'behaviour is unchanged' overstated it."}
- {"lesson":"sep-solid-subtype-contracts","before":"She and Jeannette Wing formalised it in 1994 as **behavioural subtyping**:","after":"She and Jeannette Wing formalised it in their 1994 paper *A Behavioral Notion of Subtyping*. In **behavioural subtyping**, ...","reason":"The wording implied Liskov and Wing coined 'behavioural subtyping'; Pierre America used the term first. The paper title is now cited instead."}
- {"lesson":"sep-solid-dependency-direction","before":"Robert C. Martin set out this principle in a 1996 article.","after":"Robert C. Martin described this idea in his mid-1990s writing and set it out as a named principle in his 1996 article *The Dependency Inversion Principle*.","reason":"Martin's October 1994 'OO Design Quality Metrics' paper already describes dependency inversion; the 1996 C++ Report column names the principle."}
- {"glossary":"separation-of-concerns","before":"single responsibility and information hiding are later, more specific applications of the idea","after":"Parnas's information hiding (1972) and Martin's single responsibility principle are closely related, more specific ways of drawing such boundaries.","reason":"Information hiding (Parnas, December 1972) predates Dijkstra's 1974 coinage, so 'later' was wrong."}
- {"lesson":"sep-yagni-change-cost","before":"gave up a holiday ... the forgone holiday is the cost of delay","after":"put off a holiday ... the postponed holiday is the cost of delay","reason":"Fowler defines cost of delay as delayed value from other work, not value given up permanently; the analogy now maps that."}
- {"lesson":"sep-coupling-boundaries","before":"gave the most influential answer ... such as a storage format, an algorithm or a device interface","after":"gave a classic answer ... such as an input format, how data is stored or which sorting algorithm is used","reason":"Unverifiable superlative hedged; examples aligned with the decisions Parnas's paper actually lists."}
- {"lesson":"sep-solid-small-interfaces","before":"Robert C. Martin formulated this while consulting for Xerox, where one \"fat\" job class ...","after":"Robert C. Martin set it out in a 1996 article. Its origin is usually traced to his consulting work for Xerox, where, as the story is told, ...","reason":"The 1996 ISP column is confirmed; the Xerox story appears only in Wikipedia (citing Baeldung) and retellings, not in a Martin text the verifier could fetch, so it is presented as the usual account."}
- {"lesson":"sep-simple-design-cost","before":"A flat list of 1,000 elements needs about half a million element copies; 100,000 elements need about 5 billion.","after":"Counting each element reference that `+` copies (a model of the work, not a timing), a flat list of 1,000 elements needs about half a million copies and 100,000 elements need about 5 billion.","reason":"The figures are a counted model (n(n+1)/2), so the counting assumption is now stated; values re-derived by instrumentation."}

**Scope gaps and exclusions:**

- Original schematic SQL/checkout, SMTP, payment/webhook, retry-signature and validation examples remain sketches. They do not implement production transactions, durable deduplication, exhaustive email validation, bounded jittered retry or adversarial filesystem protection. These limits are explicit in the units.
- The original unsourced measured speedup remains removed from active content. No replacement benchmark is invented.
- Specific acronym coinage and several historical dates/credits were removed where fetched originals did not substantiate them. Core concepts remain.
- Traditional coupling and cohesion labels are diagnostic vocabularies rather than universal rankings; the external-coupling label and exact rule-of-three heuristic retain medium confidence.
- Sixteen conventional glossary definitions retain medium source confidence where only the fetched reference, rather than a sufficiently specific original, substantiated the complete entry; see glossaryLowConfidence. Their associated code/maths examples were checked independently.
- No 390 px browser render was run by the verifier; a node render found 8 analogy disclosures, no literal callout tags, and the only stray-markup hit is ** inside a Python code example.
- The top-level 2026-10-15 gap note that acronym coinage and several historical credits were removed is superseded for the attributions now restored and sourced in this pass (Feathers, Meyer 1988, Liskov 1987, Page-Jones, Holland 1987, Roberts, Parnas, Martin 1996); the rule-of-three and Xerox items remain medium.
- Retry design (backoff, jitter, budgets) remains a short anti-pattern list; system-design modules cover it.
- Coupling, cohesion and connascence scales are taught as vocabulary; empirical evidence on which metrics predict defects is not covered.

**Low-confidence areas, including preserved qualifications:**

- medium confidence, sep-coupling-boundaries: The additional external-coupling category is an explicitly traditional taxonomy drawn from secondary reference material; the original Structured Design textbook supports the core coupling/cohesion concepts but does not use this exact six-label list. Core technical content independently verified; this explicitly qualified reference taxonomy/heuristic lacks the original-source support described here.
- medium confidence, sep-knowledge-abstractions: The rule of three is presented as a practical heuristic, not a measured theorem. Its exact count is corroborated by the cited reference; an original Don Roberts source was not available, so personal attribution was removed. Core technical content independently verified; this explicitly qualified reference taxonomy/heuristic lacks the original-source support described here.
- medium confidence, sep-solid-small-interfaces: ISP's origin is usually traced to Martin's consulting work for Xerox (fat Job class). Only Wikipedia (citing Baeldung) and retellings; no Martin text fetched. Hedged in the lesson as the usual account.
- medium confidence, sep-solid-responsibility: Clean Architecture (2017) states SRP as 'a module should be responsible to one, and only one, actor'. Book text not fetched; supported by Wikipedia's citation of the book, the publisher's chapter list (Chapter 7, SRP; published 10 September 2017) and Martin's consistent 2014 essay.
- medium confidence, sep-knowledge-abstractions: The rule of three is attributed to Don Roberts and popularised by Fowler's Refactoring. Book not fetched; Wikipedia and a university lecture quoting the book agree. The text says 'attributed to'.
- medium confidence, sep-clear-function-calls: sep-clean-code-q7: TypeError message 'along the lines of takes 0 positional arguments but 1 was given'. CPython 3.14.4 adds '(and 2 keyword-only arguments)'; the hedge covers it and the key is unaffected, so the unchanged question was left as is.


## software-engineering / Design Patterns

12 question objects changed. Every changed question has a specific independent-review reason in the linked record.

**Corrections in this review:**

- {"lesson":"pattern-matching-families","before":"When families change often. Adding a new *kind* of part (say, `slider()`) means changing every factory.","after":"When the set of product kinds changes often. Adding a new *kind* of part ... means changing every factory; adding a whole new family is the cheap direction.","reason":"The bullet said changing families is the costly case, contradicting the takeaway and GoF (new kinds of product are hard; new families are easy)."}
- {"lesson":"pattern-incremental-builders","before":"popularised by Joshua Bloch's *Effective Java*","after":"recommended in the second edition (2008) of Joshua Bloch's *Effective Java*","reason":"Influence claim replaced by a verifiable one: Item 2 'Consider a builder ...' is in the 2008 edition's table of contents; the 2001 edition has no builder item."}
- {"lesson":"pattern-names-and-catalogue","before":"An opening is a fixed sequence of moves that you can play exactly.","after":"An opening is defined by a fixed sequence of first moves that you can play exactly.","reason":"Analogy limit implied the whole game is fixed; only the opening moves are."}
- {"lesson":"pattern-names-and-catalogue","before":"*Class* patterns ... *object* patterns ...","after":"*Class patterns* ... *object patterns* ... Most of the 23 are object patterns.","reason":"Made the scope terms reach the new gof-pattern-scope dictionary entry and added the GoF 1.5 note that most patterns have object scope."}
- {"lesson":"pattern-observer-lifecycles","before":"Where it stops: ... a handler that raises can stop the rest.","after":"... And a forgotten software subscriber costs more than wasted post: the subject's reference keeps the whole object alive in memory.","reason":"The analogy mapped the lapsed listener to wasted post, understating the real cost (memory retention, continued callbacks)."}
- {"lesson":"pattern-visitors-and-extension","before":"JEP 441, which added it,","after":"JEP 441, which made this a standard feature in Java 21,","reason":"Pattern matching for switch was previewed in earlier JEPs (Java 17-20); JEP 441 finalised it."}
- {"lesson":"pattern-factory-callables","question":"pattern-creational-q8","before":"A base-class algorithm deferring object creation to a subclass method is the GoF factory method.","after":"... is the factory method shape. Strictly, the GoF intent is letting subclasses decide which class to instantiate ... best described as a factory-method-style hook; of these options, factory method is still the closest fit.","reason":"Overclaimed relative to the lesson's own hedge and the Django docs (get_queryset returns the items to list, usually the same QuerySet class)."}
- {"lesson":"pattern-incremental-builders","question":"pattern-creational-q5","before":"the telescoping-constructor problem builders were invented to fix; Builders exist in Java largely because ...","after":"the long positional-argument problem that fluent builders are used to avoid; Fluent builders are common in Java largely because ...","reason":"The GoF Builder was not invented for optional parameters; the explanations now match the lesson's two meanings of builder."}
- {"glossary":"builder-pattern","before":"A GoF creational pattern: a separate object collects settings step by step and creates the finished object in a final build() call ...","after":"A creational pattern. In the GoF original, a director object drives a builder through construction steps so the same steps can produce different representations ... The common modern form collects settings step by step ...","reason":"The definition attributed the fluent many-options builder to the GoF; the GoF intent is one construction process, different representations (RTFReader director example). Not shadowed by any earlier SE module."}
- {"glossary":"factory-method-pattern","before":"example: Django's ListView calls self.get_queryset(); your subclass decides which records it returns.","after":"example: An Exporter base class calls self.make_writer(); CsvExporter overrides it to return a CsvWriter. Django's ListView.get_queryset() is a looser, factory-method-style hook.","reason":"The only example was the looser Django hook; it now leads with a case that chooses the product class, matching the GoF intent and the lesson. Not shadowed."}
- {"glossary":"oopsla","before":"was presented at its workshops","after":"was submitted to its workshops","reason":"c2.com copy of the paper says 'Submitted to the OOPSLA-87 workshop'."}
- {"glossary":"effective-java","before":"Its advice to use a builder when a constructor has many parameters popularised the fluent Builder style in Java. (source: Wikipedia Joshua Bloch)","after":"Its second edition (2008) added the item \"Consider a builder when faced with many constructor parameters\", which helped spread the fluent Builder style in Java. (source: InformIT 2nd edition page)","reason":"Builder advice is not in the 2001 first edition; the source now shows the item."}
- {"glossary":"jdk-enhancement-proposal","before":"the public document that describes a planned change to the Java platform ... usually referred to ... (source: JEP 441)","after":"the public OpenJDK document that proposes a change to the JDK, explains its motivation and design, and ends up as the record of what changed and why ... often referred to ... (source: JEP 1)","reason":"Definition and source now follow JEP 1, which defines the process; 'usually' softened."}
- {"glossary":"copy-replace","before":"copy.replace(), added in Python 3.13, works on any class that supports it.","after":"copy.replace(), added in Python 3.13, works on named tuples, dataclasses and other classes that define __replace__().","reason":"Precision from the copy module docs; a plain class raises TypeError (executed)."}

**Scope gaps and exclusions:**

- The original selected catalogue remains: chain of responsibility, interpreter, mediator and memento are introduced, without new standalone implementations.
- No production Qt/Java UI, Spring deployment, Celery broker, remote payment/cloud effect or production server database was deployed. Exact Python fences, real Django 5.2.18/SQLite, and documented API semantics were checked; illustrative fixtures do not prove omitted business operations.
- Several naturally small named-pattern units are below 400 words; they keep coherent boundaries, realistic three-minute study targets and focused questions.
- Library API statements are tied to fetched documentation; PBKDF2’s million iterations is explicitly Django 5.2-specific and CPython integer caching is explicitly an implementation detail.
- Chain of responsibility, mediator, interpreter and memento are named only (now stated in the catalogue lesson).
- Five structural lessons keep one question each; not expanded under the identity rules.
- No 390 px browser render was run by the verifier.
- Gang of Four co-authors (Helm, Johnson, Vlissides), Norvig and Wadler have no individual dictionary entries; baseline coverage decision, not changed.

**Low-confidence areas, including preserved qualifications:**

- medium confidence, pattern-copying-prototypes: Java cloning preference is conventional design advice, rather than an API rule. Core technical behaviour verified; retained ancillary historical/descriptive judgement has the stated limited provenance.
- medium confidence, pattern-tangled-responsibilities: Koenig naming attribution and original Blob naming rely on secondary historical accounts; attribution is qualified. Core technical behaviour verified; retained ancillary historical/descriptive judgement has the stated limited provenance.
- medium confidence, pattern-legacy-and-duplication: Golden-hammer/lava-flow names and rule of three are contextual design heuristics; source dates not primary-verified were removed. Core technical behaviour verified; retained ancillary historical/descriptive judgement has the stated limited provenance.
- medium confidence, glossary:anti-pattern: anti-pattern Koenig attribution rests on secondary historical accounts; now explicitly commonly attributed.
- medium confidence, glossary:andrew-koenig: andrew-koenig Original 1995 article unavailable; credited wording makes attribution explicit.
- medium confidence, glossary:kent-beck: kent-beck Biographical association checked through author/book accounts and secondary biography; unsupported priority/rediscovery details removed.
- medium confidence, glossary:copy-constructor: copy-constructor Java preference is design advice rather than an API guarantee.
- medium confidence, glossary:telescoping-constructor: telescoping-constructor Historical motivation and pattern terminology are conventional author advice rather than a Java requirement.
- medium confidence, glossary:god-object: god-object Core responsibilities/coupling description checked; original AntiPatterns Blob naming depends on secondary book accounts.
- medium confidence, glossary:lava-flow: lava-flow Core legacy-code risk checked against Foote/Fowler; exact AntiPatterns label definition uses secondary historical catalogue.
- medium confidence, glossary:golden-hammer: golden-hammer Named heuristic, not a measured universal rule. Exact Maslow/date attribution removed from lesson.
- medium confidence, glossary:characterization-test: characterization-test Core preserve-existing-behaviour concept checked; terminology also rests on secondary description of Feathers’s practice.
- medium confidence, glossary:dylan: dylan Language behaviour and Apple manual primary; ancillary early-1990s history is secondary.
- medium confidence, pattern-incremental-builders: The 2001 first edition of Effective Java has no builder item (so the 2008 edition added it). Second-edition contents fetched from the publisher; first-edition contents seen only in unofficial copies via search (Item 2 there is the singleton item).
- medium confidence, glossary:effective-java: The book's builder item helped spread the fluent Builder style in Java. Influence claim, hedged ('helped spread'); the item itself is verified.
- high confidence, pattern-costs-and-scales: GoF section 1.8 warning wording. Matched against the book text in a scanned copy and a quotation site; no publisher-hosted excerpt was found, so the URL cited is the quotation.


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


## synth / Electronics for Synth Builders

48 question objects changed. Every changed question has a specific independent-review reason in the linked record.

**Corrections in this review:**

- elec-ground-reference analogy limit: 'Sea level is one agreed datum' (contrast unclear; sea level itself varies) → 'A height datum is a fixed, agreed reference that nothing flows through', contrasting it with current-carrying ground conductors.
- elec-shared-ground-impedance analogy limit: added that the shower's shared pipe is a supply path whereas the lesson's shared section is usually a return, so the mapping is not read literally.
- elec-studio-ground-loops: 'Hum that appears equally on both conductors is rejected by a balanced input' overstated rejection → 'largely rejected ... within its common-mode limits' (consistent with Rane note 110 and the module's own balanced-wiring lesson).
- elec-ohms-law-q7 prompt omitted the 3.3 V supply that option 1 and the worked example rely on → prompt now states it.
- Checked-on dates for re-fetched product/datasheet facts updated to 29 October 2026 (Teensy 4.1, SN74HC00/HCT00, Vishay diodes, OPA1612, Kingbright WP7113ID); figures themselves unchanged and confirmed.

**Scope gaps and exclusions:**

- No physical circuit was powered, wired, measured or safety-certified. Exact board revision and equipment/part limits govern any build.
- Manufacturer documents describe specified parts and conditions; moving URLs may change. Generic diode/LED drops, shunt examples and resistor-load board models are explicitly illustrative.
- Original14archives and prior verification are immutable evidence; archived inaccuracies are retained there while active teaching has independently corrected wording.
- Original Keysight PDF URL returns an asset landing page to direct retrieval; official indexed primary excerpt corroborates output-capacitor transient current. ADI/CDC/C&K local fetch limitations were independently cross-checked with official web primary evidence.
- No calculation code remains; the earlier calculator snippets were removed under the concept-first rule (stated results and links instead).
- Worst-case tolerance design (LED resistor, divider) is prose-only; no worked worst-case numeric example remains.
- Many split lessons have one question (counts preserved from the baseline split; no questions added or removed).
- Render check at 390 px and offline check were not run by the verifier (no browser in this pass).
- Glossary coverage: 97 active candidates remain unlinked by design (reference designators, document numbers, bold step headings, emphasis words, UK/US); reviewed and accepted.

**Low-confidence areas, including preserved qualifications:**

- medium confidence, elec-breadboard-net-wiring: Physical execution/applicability Primary-backed practical procedure, but exact physical board, instrument, connection and operating conditions have not been exercised. Follow actual equipment limits and documentation.
- medium confidence, elec-first-power-checks: Physical execution/applicability Primary-backed practical procedure, but exact physical board, instrument, connection and operating conditions have not been exercised. Follow actual equipment limits and documentation.
- medium confidence, elec-meter-series-current: Physical execution/applicability Primary-backed practical procedure, but exact physical board, instrument, connection and operating conditions have not been exercised. Follow actual equipment limits and documentation.
- medium confidence, elec-scope-voltage-time: Physical execution/applicability Primary-backed practical procedure, but exact physical board, instrument, connection and operating conditions have not been exercised. Follow actual equipment limits and documentation.
- medium confidence, elec-solder-alloys-safety: Physical execution/applicability Primary-backed practical procedure, but exact physical board, instrument, connection and operating conditions have not been exercised. Follow actual equipment limits and documentation.
- medium confidence, elec-solder-joint-technique: Physical execution/applicability Primary-backed practical procedure, but exact physical board, instrument, connection and operating conditions have not been exercised. Follow actual equipment limits and documentation.
- medium confidence, elec-studio-ground-loops: Physical execution/applicability Primary-backed practical procedure, but exact physical board, instrument, connection and operating conditions have not been exercised. Follow actual equipment limits and documentation.
- medium confidence, elec-supply-noise-hunt: Physical execution/applicability Primary-backed practical procedure, but exact physical board, instrument, connection and operating conditions have not been exercised. Follow actual equipment limits and documentation.
- medium confidence, elec-unpowered-meter-tests: Physical execution/applicability Primary-backed practical procedure, but exact physical board, instrument, connection and operating conditions have not been exercised. Follow actual equipment limits and documentation.
- medium confidence, elec-capacitor-types-ratings / elec-components-q11: Class 2 ceramics can sometimes lose well over half their capacitance near rated voltage Murata FAQ (fetched) confirms the effect only by chart; Knowles (manufacturer, 2023) states losses of up to 90 percent or more without giving the voltage. No part-specific numeric DC-bias curve could be retrieved (TDK/ADI pages blocked or timed out). The text is hedged ('sometimes') and tells readers to use the exact part's curve.
- medium confidence, elec-scope-voltage-time / elec-measurement-soldering-q10: Two-pin laptop adapters usually leave the output floating; some three-pin adapters earth it Product-dependent; no manufacturer document fetched. A two-pin adapter has no protective-earth conductor by construction, and the guidance is conservative ('Don't rely on knowing which').
- medium confidence, elec-diodes-and-polarity: Typical forward-drop ranges in the table (1N4148 ~0.6–0.75 V at a few mA; 1N400x ~0.7–1 V; Schottky ~0.2–0.4 V small current, ~0.45–0.6 V at 1 A) Read from typical curves and family maxima (1N5817/18/19: 0.45/0.55/0.60 V max at 1 A); the table is labelled approximate. The cited maxima and revision dates were re-fetched and are exact.
- high confidence, elec-supply-versus-pin-limits, elec-pot-wiper-adc, elec-logic-levels-q2, elec-dividers-q11: Teensy 4.1 pins 0–3.3 V, not 5 V tolerant Re-fetched from PJRC 29 Oct 2026 ('not 5V tolerant. Do not drive any digital pin higher than 3.3V'; analogue range fixed at 0–3.3 V). Time-sensitive product page: re-check for future board revisions.
- high confidence, elec-solder-alloys-safety: SparkFun 'good medium heat (325-375 degrees C)' Exact wording re-fetched from SparkFun's through-hole soldering tutorial on 29 Oct 2026; presented as a starting point subject to alloy/component instructions.
- high confidence, elec-led-resistor-choice: LED reverse ratings are often only a few volts Five fetched Kingbright WP7113-series datasheets (ID, QBC/D, SGD, GD, YD) all list VR = 5 V; text instructs readers to use the exact part's rating.
- medium confidence, all: Practical procedures (first power, current measurement, soldering, hum diagnosis) Preserved from the earlier record: procedures are primary-backed but were not physically exercised on real equipment in this pass.


## synth / Embedded Audio & Interfaces

31 question objects changed. Every changed question has a specific independent-review reason in the linked record.

**Corrections in this review:**

- emb-gpio-buttons-led-current: colour forward-voltage ranges came from a secondary Wikipedia table (blue 'roughly 2.5-3.7 V') -> replaced with fetched Kingbright datasheet values (WP7113ID red 1.9 V typ / 2.3 V max at 10 mA; WP7113QBC/D blue 3.3 V typ / 4.0 V max at 20 mA, checked 2026-10-29) and the Wikipedia link replaced by the blue datasheet.
- emb-gpio-buttons-led-current + glossary ohmic-component: wording implied LEDs have a fixed forward-voltage threshold ('rises steeply once the voltage passes its forward voltage') -> current rises steeply and non-linearly over a narrow voltage range, and forward voltage at a given current shifts with temperature, colour and part (Kingbright VF tempco -1.9/-3.0 mV/degC, I-V curves; Wikipedia Ohm's law non-ohmic diode). Raised by the synth/03 verifier because bare 'ohmic' in synth/03 opens this entry.
- glossary rc-filter: bare 'RC' alias opened a filter-only definition for synth/03 readers -> alias removed (unused bare in synth/04 lessons); bare 'RC' now resolves to synth/06 rc-circuit ('filter or timing network').
- emb-serial-buses-uart-midi (lesson and q11): 'transmitter tolerance of +/-1%' -> CA-033 states the hardware interface operates at 31.25 (+/-1%) kbaud; reworded as the rate tolerance.
- emb-gpio-buttons-debounce-methods analogy: mapped the integrator to 'waiting for a still period' -> integrator tolerates occasional opposite readings and counts net evidence; only stable-for-N needs an unbroken period.
- emb-realtime-audio-q2: garbled correct-option explanation -> rewritten for clarity (no factual change).
- Author report (not content): it said synth/06 owns the bare 'Omega' link. Replicating build.mjs shows synth/06's duplicate 'ohm' id is skipped and its spare aliases ('Ohm (Omega)', 'Omega') are donated to synth/04's ohm entry, so readers see synth/04's definition. scripts/glossary-links.mjs does not model donation.
- 2026-10-29 follow-up by claude-opus-5-5/cf2-synth04-alias-verifier (independent verifier; release QA evidence/cf2-release/qa-5c52702adad4/dictionary.log): glossary time-constant listed the alias "RC time constant", which synth/03-electronics rc-time-constant owns in the compiled synth lookup, so the alias was dead and failed the release alias-ownership check. No active synth/04 lesson or question uses the phrase; all uses are in synth/03, where the RC definition is the right sense. Removed that alias only; id, term, definition, example, source and other aliases unchanged. Definition re-verified against https://en.wikipedia.org/wiki/Time_constant and https://en.wikipedia.org/wiki/Exponential_smoothing. This resolves the 'Unresolved' shadowed-alias note in integrationDependencies.

**Scope gaps and exclusions:**

- No target platform selected: no verified project-specific wiring/BOM, complete interface/USB-role compatibility or physical build is claimed.
- No board cross-build/flash/recovery, oscilloscope/logic-analyser/ADC/button/audio-loopback measurements or proven target WCET; these remain practical exercises.
- Host atomic/native wrappers and finite models do not establish MCU ISR support, instruction lowering, bounded exclusive-access retries or physical concurrency.
- Display waveform-type requirement is included, but screen/model/bus/driver and measured update cost remain configuration choices.
- Target linker/cache/DMA implementation, advanced RTOS/USB/codec drivers and C++ teaching remain beyond this foundation module; low-voltage work only.
- No hardware bench measurements, project-specific wiring, BOM or measured latency (stated in the compare-gaps lesson).
- 390 px browser render check not run by this verifier (not required by the task); build renderer checks and markdown/formula-fence checks pass.
- Ohm's law has no dedicated lesson in this module; it is taught in context. Fundamentals live in synth/03-electronics.

**Low-confidence areas, including preserved qualifications:**

- medium confidence, emb-codecs-i2s-control-registers: Manufacturer product/revision, platform configuration or hardware experiment specifics Primary manufacturer/code snapshots independently checked and dated in the lesson. Product/SDK details can change; no selected physical board, flash/recovery or lab measurement is certified.
- medium confidence, emb-gpio-buttons-pin-limits: Manufacturer product/revision, platform configuration or hardware experiment specifics Primary manufacturer/code snapshots independently checked and dated in the lesson. Product/SDK details can change; no selected physical board, flash/recovery or lab measurement is certified.
- medium confidence, emb-mcu-firmware-boot-recovery: Manufacturer product/revision, platform configuration or hardware experiment specifics Primary manufacturer/code snapshots independently checked and dated in the lesson. Product/SDK details can change; no selected physical board, flash/recovery or lab measurement is certified.
- medium confidence, emb-mcu-firmware-chip-memory: Manufacturer product/revision, platform configuration or hardware experiment specifics Primary manufacturer/code snapshots independently checked and dated in the lesson. Product/SDK details can change; no selected physical board, flash/recovery or lab measurement is certified.
- medium confidence, emb-platform-comparison-compare-gaps: Manufacturer product/revision, platform configuration or hardware experiment specifics Primary manufacturer/code snapshots independently checked and dated in the lesson. Product/SDK details can change; no selected physical board, flash/recovery or lab measurement is certified.
- medium confidence, emb-platform-comparison-criteria-configurations: Manufacturer product/revision, platform configuration or hardware experiment specifics Primary manufacturer/code snapshots independently checked and dated in the lesson. Product/SDK details can change; no selected physical board, flash/recovery or lab measurement is certified.
- medium confidence, emb-platform-comparison-experiment-record: Manufacturer product/revision, platform configuration or hardware experiment specifics Primary manufacturer/code snapshots independently checked and dated in the lesson. Product/SDK details can change; no selected physical board, flash/recovery or lab measurement is certified.
- medium confidence, emb-platform-comparison-official-evidence: Manufacturer product/revision, platform configuration or hardware experiment specifics Primary manufacturer/code snapshots independently checked and dated in the lesson. Product/SDK details can change; no selected physical board, flash/recovery or lab measurement is certified.
- medium confidence, emb-platform-comparison-score-sensitivity: Manufacturer product/revision, platform configuration or hardware experiment specifics Primary manufacturer/code snapshots independently checked and dated in the lesson. Product/SDK details can change; no selected physical board, flash/recovery or lab measurement is certified.
- medium confidence, emb-control-to-audio-atomic-latest: Target atomic/interrupt timing and measured worst-case performance Language-level primary sources, exact host compiled helper and finite state/arithmetic models checked. Selected MCU compiler/ABI, ISR contracts, atomic retry/progress bounds, DMA/cache behavior and physical WCET still require target evidence; lesson explicitly requires those checks.
- medium confidence, emb-control-to-audio-preset-ownership: Target atomic/interrupt timing and measured worst-case performance Language-level primary sources, exact host compiled helper and finite state/arithmetic models checked. Selected MCU compiler/ABI, ISR contracts, atomic retry/progress bounds, DMA/cache behavior and physical WCET still require target evidence; lesson explicitly requires those checks.
- medium confidence, emb-control-to-audio-spsc-ring: Target atomic/interrupt timing and measured worst-case performance Language-level primary sources, exact host compiled helper and finite state/arithmetic models checked. Selected MCU compiler/ABI, ISR contracts, atomic retry/progress bounds, DMA/cache behavior and physical WCET still require target evidence; lesson explicitly requires those checks.
- medium confidence, emb-realtime-audio-measure-load: Target atomic/interrupt timing and measured worst-case performance Language-level primary sources, exact host compiled helper and finite state/arithmetic models checked. Selected MCU compiler/ABI, ISR contracts, atomic retry/progress bounds, DMA/cache behavior and physical WCET still require target evidence; lesson explicitly requires those checks.
- medium confidence, emb-codecs-i2s-converter-revisions: Codec fitted to board revision and SDK configuration Manufacturer revision snapshots and exact pinned source checked; recheck actual board and installed SDK before wiring/configuring.
- medium confidence, emb-codecs-i2s-output-connections: q9 distractor explanation: 'Equipment normally has headroom above nominal' General engineering practice without a single primary source; it is hedged and immediately directs the reader to the manual's maximum input level.
- medium confidence, emb-platform-comparison-official-evidence: Dated product facts for Daisy Seed Rev 7, Teensy 4.1/audio adaptor D2 and Raspberry Pi 5/DAC+ Re-checked against fetched manufacturer pages on 2026-10-29 but time-sensitive; the lesson keeps its 2026-10-16 check date and tells readers to re-verify before buying.
- medium confidence, emb-codecs-i2s-converter-revisions: libDaisy distinguishes Rev 7 (PD5) and shares the Rev 4-compatible audio configuration Confirmed in fetched libDaisy master daisy_seed.cpp, but the Daisy datasheet v1.2.0 says libDaisy 'detects hardware as Rev 4'; source code can change between versions.
- medium confidence, emb-gpio-buttons-led-current: Kingbright example forward voltages and 'a blue or white LED on 3.3 V may be dim or not light' Datasheet values are for specific parts at stated currents (10/20 mA); behaviour at a few mA on 3.3 V depends on the selected part, so the lesson hedges and directs readers to their own datasheet.


## synth / MIDI & Studio Integration

33 question objects changed. Every changed question has a specific independent-review reason in the linked record.

**Corrections in this review:**

- midi-synth-handling-controller-curves analogy: 'every key is the same width … equal physical steps' was inaccurate (white and black keys differ; a piano's semitone steps are not equal-width) → 'moving up one key, white or black, raises the pitch by the same semitone' and 'each step up is the same frequency ratio'.
- midi-fundamentals-q6: timing 'first and last edge' of a Note On can span only 29 bit-times (about 0.93 ms) when the stop bit follows a 0, so it did not match the 30-bit explanation → prompt now times from the start of the first start bit to the end of the last stop bit.
- Glossary diode: 'the LED never sees a damaging reverse voltage' was absolute → the reverse-connected diode holds the LED's reverse voltage to about one diode forward drop.
- midi-hardware-q1 worked example: garbled 'along the socket rim around the socket' → 'do not run in numeric order around the socket rim' (editorial).
- midi-studio-integration-q7 option 1: typo 'Choose a one tempo sender' → 'Choose one tempo sender' (editorial).
- Hedged: midi-synth-handling-controller-curves: ratio perception of filter cutoffs and envelope times reframed as a widely used design rule of thumb, not an exact perceptual law (lesson text, takeaway and q7 worked example).
- Hedged: midi-hardware-usb-event-packets: 'many event packets per millisecond' now gives the 12 Mbit/s full-speed figure and states that throughput depends on device, host scheduling and driver.
- Hedged: midi-fundamentals-q12: USB chord spread now 'usually much less', timing depending on device, host and driver.
- Hedged: midi-hardware-q5: the ≈5.3 mA prediction now states its model (nominal 3.3 V, exact resistors, fixed LED drop, cable/driver ignored) in the prompt; worked example notes real forward drop varies with current (CA-033).
- Hedged: midi-messages-q8: recompute-on-range-change assumption made explicit in the prompt; worked example explains the alternative behaviour.

**Scope gaps and exclusions:**

- No physical MIDI receiver compliance/fault margin, measured complete-path latency, auditory threshold or device compatibility certification.
- Final platform/interface/BOM/full firmware/patch-dump decoder and final integrated demonstration remain unselected/unimplemented planning tasks.
- Manufacturer dBu peak convention is ambiguous; faithfully quoted, not converted to unspecified RMS/peak voltages.
- Old foreign Audio XLR fallback field is excluded from approval; root publication requires DIFFERENT full Audio verifier closure.
- No physical MIDI or audio hardware measurements: loop currents, levels and latencies are specification or model values.
- Render check at 390 px and offline view were not performed in this pass (build, renderer, diagram, formula and glossary unit tests pass).
- Glossary: diode (corrected) and full-speed-usb (added) were verified against sources; the other 171 entries were spot-checked for sense and alias capture, not re-verified exhaustively. Their earlier verification is inherited.
- velocity-note-end, lengths-pressure, control-change-map, rpn-bank-program, sysex-mode, midi-two-scope, parser-state, stuck-note-defences, din-loop, trs-thru and several studio lessons still have one-line key-takeaway sections; acceptable but thin.

**Low-confidence areas, including preserved qualifications:**

- medium confidence, midi-fundamentals-note-frequency: Dated product/OS/driver or hardware-specific measurement convention Exact manufacturer/standard primary snapshots independently fetched 2026-10-16. Models/OS/driver support may change; no selected physical hardware test or unspecified dBu peak convention inferred.
- medium confidence, midi-studio-integration-connection-plan: Dated product/OS/driver or hardware-specific measurement convention Exact manufacturer/standard primary snapshots independently fetched 2026-10-16. Models/OS/driver support may change; no selected physical hardware test or unspecified dBu peak convention inferred.
- medium confidence, midi-studio-integration-digitakt-sequence: Dated product/OS/driver or hardware-specific measurement convention Exact manufacturer/standard primary snapshots independently fetched 2026-10-16. Models/OS/driver support may change; no selected physical hardware test or unspecified dBu peak convention inferred.
- medium confidence, midi-studio-integration-ableton-record-sync: Dated product/OS/driver or hardware-specific measurement convention Exact manufacturer/standard primary snapshots independently fetched 2026-10-16. Models/OS/driver support may change; no selected physical hardware test or unspecified dBu peak convention inferred.
- medium confidence, midi-studio-integration-monitor-latency: Dated product/OS/driver or hardware-specific measurement convention Exact manufacturer/standard primary snapshots independently fetched 2026-10-16. Models/OS/driver support may change; no selected physical hardware test or unspecified dBu peak convention inferred.
- medium confidence, midi-studio-integration-gain-chain: Dated product/OS/driver or hardware-specific measurement convention Exact manufacturer/standard primary snapshots independently fetched 2026-10-16. Models/OS/driver support may change; no selected physical hardware test or unspecified dBu peak convention inferred.
- medium confidence, midi-studio-integration-hum-test-session: Dated product/OS/driver or hardware-specific measurement convention Exact manufacturer/standard primary snapshots independently fetched 2026-10-16. Models/OS/driver support may change; no selected physical hardware test or unspecified dBu peak convention inferred.
- medium confidence, midi-hardware-usb-host-roles: Dated manufacturer/platform or ambiguous maximum-level convention Primary snapshot checked on2026-10-16; product revisions/driver support can change. No physical compliance or unspecified dBu peak conversion inferred.
- medium confidence, midi-hardware-usb-event-packets: Dated manufacturer/platform or ambiguous maximum-level convention Primary snapshot checked on2026-10-16; product revisions/driver support can change. No physical compliance or unspecified dBu peak conversion inferred.
- medium confidence, midi-audio-levels-first-interface-check: Dated manufacturer/platform or ambiguous maximum-level convention Primary snapshot checked on2026-10-16; product revisions/driver support can change. No physical compliance or unspecified dBu peak conversion inferred.
- medium confidence, midi-audio-levels-sine-headroom: Dated manufacturer/platform or ambiguous maximum-level convention Primary snapshot checked on2026-10-16; product revisions/driver support can change. No physical compliance or unspecified dBu peak conversion inferred.
- medium confidence, midi-synth-handling-controller-curves: Filter cutoffs and envelope times are judged roughly by ratio, motivating exponential maps. Pitch-ratio perception is standard; extension to cutoff and times is a common design heuristic without a fetched psychoacoustic source. Now hedged in the text.
- medium confidence, midi-hardware-output-loop-current: q5: a 1.9 V receiver LED drop gives roughly 5.3 mA from the 3.3 V CA-033 output. Recomputed correctly (1.4 V / 263 Ω = 5.32 mA) under stated model assumptions; real LED drop varies with current and driver low-state voltage is ignored. Not measured.
- medium confidence, midi-hardware-usb-event-packets: USB MIDI carries many event packets per millisecond; a DIN chord is much less spread over USB (also midi-fundamentals-q12). 12 Mbit/s full speed is verified; actual USB MIDI throughput and timing depend on endpoint size, host polling and drivers and were not measured. Hedged.
- medium confidence, midi-audio-levels-balanced-connectors: Analogy limit: impedance imbalance converts common-mode interference into a difference signal; rejection is finite. Supported by the IEC 60268-3 statement as cited on Wikipedia (secondary); the Jensen primary application note now returns 404.
- medium confidence, midi-studio-integration-connection-plan: Digitakt / Digitakt II ports, ratings, menus and Ableton Live 12 behaviour (all studio-integration lessons, note-frequency, usb-host-roles, sine-headroom, load-bridging, dc-coupling). Re-fetched Digitakt OS 1.53 and Digitakt II OS 1.17 manuals and Live 12 manual pages on 2026-10-29 and confirmed the quoted facts, but product facts are time-sensitive and version-specific; lessons tell the reader to confirm their model and OS.
- medium confidence, midi-hardware-trs-thru: RP-054 recommends 2.5 mm TRS, 2 m adapter limit, shielded twisted pair, protection circuitry. Verified from a copy of RP-054 hosted on Google Drive; the official MIDI Association download requires membership, so the copy's provenance is not first-party.


## synth / Audio Engineering

73 question objects changed. Every changed question has a specific independent-review reason in the linked record.

**Corrections in this review:**

- aud-drivers-power-and-distance: 'around 1 % efficient: of that 40 W only about 0.4 W leaves as sound' applied the rule of thumb to Purdue's sample driver → '~1 %, and often less: Purdue's 86 dB/1 W/1 m sample works out at about 0.2 % (Small's reference-efficiency formula gives 0.19 %), so about a tenth of a watt'. (Edit made by the stopped verifier; independently recomputed and kept.)
- aud-drivers-impedance: Qms 'typically about 1–10' → 'roughly 0.5–10 and often about 3', as Purdue's notes state. (Stopped verifier's edit; checked against the fetched Purdue text and kept.)
- aud-sound-systems-coverage-and-delay: alignment was said to hold 'along the line from the main speakers through the delay speaker and beyond', which includes the stage-to-delay segment where the path difference shrinks → restricted to positions behind the delay speaker on that line. (Stopped verifier's edit; geometry rechecked and kept.)
- aud-sound-systems-feedback-control (+ q11): 'cut it with a narrow EQ band' and 'a narrow parametric band' → cuts of a few dB with a parametric band; RaneNote 158 recommends notch depth of about a couple of dB, warns that high-Q deep notches cope poorly with temperature/position changes, and says auto-notching typically adds only a couple of dB.
- Glossary angular-frequency: definition said 'these crossover lessons use u for that ratio', but no active lesson uses u any more → sentence removed. (Stopped verifier's edit; kept.)
- Glossary aud-restoring-spring: bare aliases 'spring'/'springs' (owned by this module) captured unrelated synth03/04 uses ('spring clips', 'spring return', 'spring-loaded door closer') → replaced with 'air spring', 'air-spring', 'box air spring', 'suspension spring', 'second spring'; two bolded 'spring' uses here reworded to 'suspension spring' and 'air spring'.
- Glossary solid-angle: 'how much of the space around a point a cone of directions covers' implied only cones → any region of directions, measured as the area covered on a unit sphere, unit steradian.
- aud-enclosures-q2: option-1 explanation answered a different question (open-baffle loss) → now explains why neither sealed nor ported boxes roll off at 6 dB/octave.
- aud-amplifiers-classes (+ q2, q8): citation title named TI SLAA701B while linking SLOA119B → titled 'Class-D LC filter design — SLOA119B'. (Stopped verifier's edit; kept.)
- 2026-10-29 follow-up (verifier: claude-opus-5-5/cf2-synth06-omega-verifier): Glossary omega-angular-frequency removed from this module. synth/01-sound-sampling defines the same id (aliases 'angular frequency', 'omega', 'ω') and, being earlier in the subject, owns it in the compiled dictionary, so this module's copy was never shown and its later edit made the release dictionary check report a changed term whose compiled definition was not its own. No active lesson or question in this module uses angular frequency, omega or ω; synth/01's definition (radians per second, 2π times the frequency in hertz) is correct and covers any use. The dropped sentence about normalised frequency ratios is not needed: aud-crossovers-summing defines its normalised Laplace variable inline. Structural fix; not counted in summary.errorsCorrected.

**Scope gaps and exclusions:**

- No physical loudspeaker, room, hearing, microphone, amplifier, or exposure measurements were made. Python and model results are offline illustrations, not production calibration or a hardware design sign-off.
- Full paid IEC 61938, IEC 60268-5, IEC 61672-1 and ISO 226 normative texts were not obtained. Manufacturer wiring/rating evidence, original weighting research and standards-body scope were checked; no claim of clause-by-clause standards conformance.
- No claim of medical safety for every listener or legal compliance for a workplace. WHO and NIOSH reference doses and GB action/limit values are distinguished and qualified; current equipment, conditions and competent assessments still matter.
- Read times are source estimates (1–5 minutes), not a timed learner trial. Real-world box alignment, crossover optimisation, transducer nonlinearities, coverage design and acoustical measurement remain introductions.
- This review counts 50 complete lesson bodies, 100 full question objects, 168 full formula cards and 446 glossary objects as 764 overlapping review groups, not 764 atomic independent factual assertions. There is no sentence-level automated entailment proof.
- Audio glossary changes affect prior modules. Exact before/after borrower approval and the independently verified E physical-clip wording follow-up are separate evidence; root must bind these at final integration.
- No 390 px render or offline check in this pass (build, formula, renderer, glossary and diagram unit tests pass: 46/46).
- Bare 'Fs' (free-air resonance) and 'Re' (voice-coil resistance) do not link. An 'Fs' alias is not case-sensitive under glossary-rules.js and would capture synth01's sample-rate 'fs'; a rules change outside this module would be needed.
- NIOSH page returned HTTP 403 to scripted fetches; NIOSH 85 dBA/3 dB figures are unchanged baseline text inherited from the earlier verified record.
- IEC 61672-1, IEC 61938 and IEC 60268-5 texts are paywalled and were not fetched; their quoted values are unchanged baseline content verified earlier or confirmed through secondary summaries.
- Glossary: changed or added entries (angular-frequency, sbir, room-response-controls, solid-angle, aud-restoring-spring) and FIR were verified; the other entries were spot-checked for alias capture only and keep their earlier verification.
- aud-crossovers-passive-values keeps its 'Calculate…' title; its maths is optional reference and its questions test predictions, so the title was not changed.

**Low-confidence areas, including preserved qualifications:**

- medium confidence, aud-amplifiers-classes: Qualified empirical ranges, model assumptions, dated products/guidance or standard attributions in this unit Core model and calculations checked independently. Real equipment/listeners/rooms vary; current manuals/regulators were fetched. Full paid normative texts and hardware measurements are outside this evidence. Specific limitations are retained in active prose and final report.
- medium confidence, aud-amplifiers-headphones: Qualified empirical ranges, model assumptions, dated products/guidance or standard attributions in this unit Core model and calculations checked independently. Real equipment/listeners/rooms vary; current manuals/regulators were fetched. Full paid normative texts and hardware measurements are outside this evidence. Specific limitations are retained in active prose and final report.
- medium confidence, aud-amplifiers-loads: Qualified empirical ranges, model assumptions, dated products/guidance or standard attributions in this unit Core model and calculations checked independently. Real equipment/listeners/rooms vary; current manuals/regulators were fetched. Full paid normative texts and hardware measurements are outside this evidence. Specific limitations are retained in active prose and final report.
- medium confidence, aud-amplifiers-ratings: Qualified empirical ranges, model assumptions, dated products/guidance or standard attributions in this unit Core model and calculations checked independently. Real equipment/listeners/rooms vary; current manuals/regulators were fetched. Full paid normative texts and hardware measurements are outside this evidence. Specific limitations are retained in active prose and final report.
- medium confidence, aud-drivers-impedance: Qualified empirical ranges, model assumptions, dated products/guidance or standard attributions in this unit Core model and calculations checked independently. Real equipment/listeners/rooms vary; current manuals/regulators were fetched. Full paid normative texts and hardware measurements are outside this evidence. Specific limitations are retained in active prose and final report.
- medium confidence, aud-drivers-power-and-distance: Qualified empirical ranges, model assumptions, dated products/guidance or standard attributions in this unit Core model and calculations checked independently. Real equipment/listeners/rooms vary; current manuals/regulators were fetched. Full paid normative texts and hardware measurements are outside this evidence. Specific limitations are retained in active prose and final report.
- medium confidence, aud-drivers-response-and-limits: Qualified empirical ranges, model assumptions, dated products/guidance or standard attributions in this unit Core model and calculations checked independently. Real equipment/listeners/rooms vary; current manuals/regulators were fetched. Full paid normative texts and hardware measurements are outside this evidence. Specific limitations are retained in active prose and final report.
- medium confidence, aud-enclosures-cabinet: Qualified empirical ranges, model assumptions, dated products/guidance or standard attributions in this unit Core model and calculations checked independently. Real equipment/listeners/rooms vary; current manuals/regulators were fetched. Full paid normative texts and hardware measurements are outside this evidence. Specific limitations are retained in active prose and final report.
- medium confidence, aud-enclosures-port-tuning: Qualified empirical ranges, model assumptions, dated products/guidance or standard attributions in this unit Core model and calculations checked independently. Real equipment/listeners/rooms vary; current manuals/regulators were fetched. Full paid normative texts and hardware measurements are outside this evidence. Specific limitations are retained in active prose and final report.
- medium confidence, aud-enclosures-small-signal: Qualified empirical ranges, model assumptions, dated products/guidance or standard attributions in this unit Core model and calculations checked independently. Real equipment/listeners/rooms vary; current manuals/regulators were fetched. Full paid normative texts and hardware measurements are outside this evidence. Specific limitations are retained in active prose and final report.
- medium confidence, aud-hearing-listening-dose: Qualified empirical ranges, model assumptions, dated products/guidance or standard attributions in this unit Core model and calculations checked independently. Real equipment/listeners/rooms vary; current manuals/regulators were fetched. Full paid normative texts and hardware measurements are outside this evidence. Specific limitations are retained in active prose and final report.
- medium confidence, aud-hearing-loudness: Qualified empirical ranges, model assumptions, dated products/guidance or standard attributions in this unit Core model and calculations checked independently. Real equipment/listeners/rooms vary; current manuals/regulators were fetched. Full paid normative texts and hardware measurements are outside this evidence. Specific limitations are retained in active prose and final report.
- medium confidence, aud-hearing-weighting: Qualified empirical ranges, model assumptions, dated products/guidance or standard attributions in this unit Core model and calculations checked independently. Real equipment/listeners/rooms vary; current manuals/regulators were fetched. Full paid normative texts and hardware measurements are outside this evidence. Specific limitations are retained in active prose and final report.
- medium confidence, aud-hearing-workplace-noise: Qualified empirical ranges, model assumptions, dated products/guidance or standard attributions in this unit Core model and calculations checked independently. Real equipment/listeners/rooms vary; current manuals/regulators were fetched. Full paid normative texts and hardware measurements are outside this evidence. Specific limitations are retained in active prose and final report.
- medium confidence, aud-microphones-phantom: Qualified empirical ranges, model assumptions, dated products/guidance or standard attributions in this unit Core model and calculations checked independently. Real equipment/listeners/rooms vary; current manuals/regulators were fetched. Full paid normative texts and hardware measurements are outside this evidence. Specific limitations are retained in active prose and final report.
- medium confidence, aud-microphones-polar-patterns: Qualified empirical ranges, model assumptions, dated products/guidance or standard attributions in this unit Core model and calculations checked independently. Real equipment/listeners/rooms vary; current manuals/regulators were fetched. Full paid normative texts and hardware measurements are outside this evidence. Specific limitations are retained in active prose and final report.
- medium confidence, aud-microphones-specifications: Qualified empirical ranges, model assumptions, dated products/guidance or standard attributions in this unit Core model and calculations checked independently. Real equipment/listeners/rooms vary; current manuals/regulators were fetched. Full paid normative texts and hardware measurements are outside this evidence. Specific limitations are retained in active prose and final report.
- medium confidence, aud-microphones-transducers: Qualified empirical ranges, model assumptions, dated products/guidance or standard attributions in this unit Core model and calculations checked independently. Real equipment/listeners/rooms vary; current manuals/regulators were fetched. Full paid normative texts and hardware measurements are outside this evidence. Specific limitations are retained in active prose and final report.
- medium confidence, aud-room-acoustics-boundary-measurement: Qualified empirical ranges, model assumptions, dated products/guidance or standard attributions in this unit Core model and calculations checked independently. Real equipment/listeners/rooms vary; current manuals/regulators were fetched. Full paid normative texts and hardware measurements are outside this evidence. Specific limitations are retained in active prose and final report.
- medium confidence, aud-room-acoustics-mode-position: Qualified empirical ranges, model assumptions, dated products/guidance or standard attributions in this unit Core model and calculations checked independently. Real equipment/listeners/rooms vary; current manuals/regulators were fetched. Full paid normative texts and hardware measurements are outside this evidence. Specific limitations are retained in active prose and final report.
- medium confidence, aud-room-acoustics-monitor-layout: Qualified empirical ranges, model assumptions, dated products/guidance or standard attributions in this unit Core model and calculations checked independently. Real equipment/listeners/rooms vary; current manuals/regulators were fetched. Full paid normative texts and hardware measurements are outside this evidence. Specific limitations are retained in active prose and final report.
- medium confidence, aud-room-acoustics-reverberation: Qualified empirical ranges, model assumptions, dated products/guidance or standard attributions in this unit Core model and calculations checked independently. Real equipment/listeners/rooms vary; current manuals/regulators were fetched. Full paid normative texts and hardware measurements are outside this evidence. Specific limitations are retained in active prose and final report.
- medium confidence, aud-room-acoustics-treatment: Qualified empirical ranges, model assumptions, dated products/guidance or standard attributions in this unit Core model and calculations checked independently. Real equipment/listeners/rooms vary; current manuals/regulators were fetched. Full paid normative texts and hardware measurements are outside this evidence. Specific limitations are retained in active prose and final report.
- medium confidence, aud-sound-systems-coverage-and-delay: Qualified empirical ranges, model assumptions, dated products/guidance or standard attributions in this unit Core model and calculations checked independently. Real equipment/listeners/rooms vary; current manuals/regulators were fetched. Full paid normative texts and hardware measurements are outside this evidence. Specific limitations are retained in active prose and final report.
- medium confidence, aud-sound-systems-gain-plan: Qualified empirical ranges, model assumptions, dated products/guidance or standard attributions in this unit Core model and calculations checked independently. Real equipment/listeners/rooms vary; current manuals/regulators were fetched. Full paid normative texts and hardware measurements are outside this evidence. Specific limitations are retained in active prose and final report.
- medium confidence, aud-room-acoustics-boundary-measurement: Moving a monitor very close to the wall moves the first SBIR notch up and it is usually shallower (q5). Frequency shift is geometric and matches Genelec's table. Depth: Genelec says close placement moves the cancellation to where the monitor is already forward-directing, 'preventing the cancellation'; but the shorter reflected path also loses less level, so the result depends on the monitor's directivity at that frequency. Hedged as 'usually'.
- medium confidence, aud-drivers-power-and-distance: Typical home loudspeakers are around 1 % efficient, and often less. Wikipedia's Loudspeaker article gives 'about 1 %'; computed half-space efficiency for 84–90 dB/1 W/1 m is about 0.15–0.6 %, so 'often less' is the accurate hedge. A rule of thumb, not a specification.
- medium confidence, aud-acoustics-pressure-level: IEC 61672-1 Fast = 125 ms and Slow = 1 s time weighting. The IEC standard text is paywalled; figures taken from Wikipedia's Sound level meter article, which summarises the standard. Widely consistent with manufacturer documentation.
- medium confidence, aud-room-acoustics-boundary-measurement: Room-response controls are often labelled bass tilt or desktop. Confirmed on one Genelec operating manual (8030C: Desktop 160 Hz −4 dB; Bass Tilt −2/−4/−6 dB). Names and ranges vary by manufacturer; the lesson wording is generic ('for example').
- medium confidence, aud-room-acoustics-mode-frequencies: Skipping-rope analogy: the still points map to nodes. The rope shows displacement nodes at its ends; room pressure has antinodes at rigid walls. The limit paragraph states this explicitly, so the mapping is acceptable but only for the particle-motion picture.


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


## system-design / Networking & Traffic

41 question objects changed. Every changed question has a specific independent-review reason in the linked record.

**Corrections in this review:**

- net-connection-handshakes reference card: RTT_min was defined in milliseconds while v was given in km/s (2d/v then yields seconds) -> v now defined in km/ms (about 200 km/ms), consistent with RTT_min in ms.
- net-first-byte-latency: 'the user sees roughly a tenth of the direct time' attributed the whole gap to shorter trips although 95 ms of it is the assumed DNS difference -> now says so, and that with equal DNS the hit is about seven times faster (245 vs 35 ms).
- net-request-lifecycle-q3 workedExample: unsupported claim that the CDN also gives 'DNS answered nearby' -> removed.
- net-cdn-q3 workedExample: 'one miss per PoP each time the 5-minute TTL runs out' -> one miss per PoP (or cache node) for each TTL period in which the page is requested there, fewer at the origin with a shield.
- net-dns-resolution-transport analogy limit: 'each desk is really many anycast servers' overstated anycast for all authoritative servers -> 'usually several servers, often anycast copies sharing one address'.
- net-dns-cache-lifetimes: convergence sentence ('one TTL after the last time anyone fetched the old answer') was ambiguous about which fetch -> 'within one TTL of the last time any cache fetched it from the authoritative servers'.
- net-api-gateway-bff analogy 'Where it stops' listed gateway pitfalls rather than where the comparison fails -> rewritten (per-request checks vs one door check; a BFF serves a client type, not a person; passing the gateway does not settle per-resource authorisation).
- glossary retry-budget: Envoy's budget described as 20% 'of active requests' -> 'of active plus pending requests (20% by default when the budget is configured)', per circuit_breaker.proto.
- net-cdn-hits-distribution: R_origin = (1 - CHR) x R_total reclassified from formula essential to formula reference (the prose already carries the miss-rate relationship; the In words line stands alone). Classification change, not an accuracy error.
- Wrong-sense glossary links produced by new text reworded: 'path costs' (routing metric) and 'shortest path' (graph) in net-connection-handshakes; 'separate origins' (security sandbox domain) in net-rendering-error-layers; 'opt-in' (marketing consent) in net-certificate-trust-renewal; 'Setup time' (embedded setup/hold time) in net-tls-resumption-replay; 'opaque identifiers' (IPv6) in net-tls-q11; 'Expected result' (software testing) in net-load-balancers-q12. Not counted as accuracy errors.

**Scope gaps and exclusions:**

- No live TCP/TLS/QUIC, DNS/CDN, cloud-balancer, mesh or multi-region deployment; no packet capture, signature throughput, purge, BGP convergence or failover benchmark. All timing/capacity arithmetic is a stated model, not a measurement.
- Existing content depth is divided rather than removed. Cache-header details, partitioning/hash analysis and write coordination remain in later modules as before.
- The unchanged 433-term glossary retains the prior 2026-10-11 audit/reconciliation provenance; this scoped split pass checks preservation and coverage, not a new 433-definition audit. packet-loss and bgp-convergence remain medium.
- Inherited glossary annotation limitation: PoPs has no ordinary-word pops alias; point of presence is defined. The inherited round trip alias can also match serialization wording elsewhere; no shared glossary edits are made here.
- No new runnable programs: 18 conceptual drawings plus one illustrative HTTP fragment and two incomplete DNS zone fragments were source-reviewed. The DNS record lines match the archive after removing native explanatory comments and the old visual TTL annotation.
- Project-wide generated data/diagram integration, tests and 390 px browser render checks remain the coordinating agent’s responsibility under docs/short-lessons-brief.md. No shared diagram override defect was found.
- No measured latency traces, packet captures or cloud deployments; all timings are labelled illustrative models (unchanged from earlier passes).
- Unchanged lessons (10) and unchanged questions (55) were re-read for concept-first fit and answerability but their factual content rests on the 2026-10-14 verification; this pass does not claim a fresh exhaustive audit of them.
- Glossary: one definition corrected (retry-budget); the other 432 entries keep earlier provenance. Only the entries the edited lessons depend on (about 30) were re-read against the edited text in this pass.
- The bare word 'resolver' (102 uses in this DNS-heavy module) links to the GraphQL 'resolver' entry owned by system-design/07-api-design, and bare 'endpoint(s)' to 07's API-endpoint entry; this module cannot fix that without capturing those words in 07's lessons (integration dependency).

**Low-confidence areas, including preserved qualifications:**

- medium confidence, net-url-dns-start: Deployment-specific timing, throughput, routing, configuration or workload heuristics in the retained examples Core factual mechanisms source-checked; keep inherited medium confidence for qualified performance, deployment/product and heuristic examples. No live deployment benchmarks were run.
- medium confidence, net-connection-handshakes: Deployment-specific timing, throughput, routing, configuration or workload heuristics in the retained examples Core factual mechanisms source-checked; keep inherited medium confidence for qualified performance, deployment/product and heuristic examples. No live deployment benchmarks were run.
- medium confidence, net-first-byte-latency: Deployment-specific timing, throughput, routing, configuration or workload heuristics in the retained examples Core factual mechanisms source-checked; keep inherited medium confidence for qualified performance, deployment/product and heuristic examples. No live deployment benchmarks were run.
- medium confidence, net-rendering-error-layers: Deployment-specific timing, throughput, routing, configuration or workload heuristics in the retained examples Core factual mechanisms source-checked; keep inherited medium confidence for qualified performance, deployment/product and heuristic examples. No live deployment benchmarks were run.
- medium confidence, net-dns-resolution-transport: Deployment-specific timing, throughput, routing, configuration or workload heuristics in the retained examples Core factual mechanisms source-checked; keep inherited medium confidence for qualified performance, deployment/product and heuristic examples. No live deployment benchmarks were run.
- medium confidence, net-dns-records-aliases: Deployment-specific timing, throughput, routing, configuration or workload heuristics in the retained examples Core factual mechanisms source-checked; keep inherited medium confidence for qualified performance, deployment/product and heuristic examples. No live deployment benchmarks were run.
- medium confidence, net-dns-cache-lifetimes: Deployment-specific timing, throughput, routing, configuration or workload heuristics in the retained examples Core factual mechanisms source-checked; keep inherited medium confidence for qualified performance, deployment/product and heuristic examples. No live deployment benchmarks were run.
- medium confidence, net-dns-steering-resilience: Deployment-specific timing, throughput, routing, configuration or workload heuristics in the retained examples Core factual mechanisms source-checked; keep inherited medium confidence for qualified performance, deployment/product and heuristic examples. No live deployment benchmarks were run.
- medium confidence, net-tcp-slow-start: Deployment-specific timing, throughput, routing, configuration or workload heuristics in the retained examples Core factual mechanisms source-checked; keep inherited medium confidence for qualified performance, deployment/product and heuristic examples. No live deployment benchmarks were run.
- medium confidence, net-udp-http1-concurrency: Deployment-specific timing, throughput, routing, configuration or workload heuristics in the retained examples Core factual mechanisms source-checked; keep inherited medium confidence for qualified performance, deployment/product and heuristic examples. No live deployment benchmarks were run.
- medium confidence, net-http2-streams-pools: Deployment-specific timing, throughput, routing, configuration or workload heuristics in the retained examples Core factual mechanisms source-checked; keep inherited medium confidence for qualified performance, deployment/product and heuristic examples. No live deployment benchmarks were run.
- medium confidence, net-quic-http3-migration: Deployment-specific timing, throughput, routing, configuration or workload heuristics in the retained examples Core factual mechanisms source-checked; keep inherited medium confidence for qualified performance, deployment/product and heuristic examples. No live deployment benchmarks were run.
- medium confidence, net-tls13-key-exchange: Deployment-specific timing, throughput, routing, configuration or workload heuristics in the retained examples Core factual mechanisms source-checked; keep inherited medium confidence for qualified performance, deployment/product and heuristic examples. No live deployment benchmarks were run.
- medium confidence, net-certificate-trust-renewal: Deployment-specific timing, throughput, routing, configuration or workload heuristics in the retained examples Core factual mechanisms source-checked; keep inherited medium confidence for qualified performance, deployment/product and heuristic examples. No live deployment benchmarks were run.
- medium confidence, net-tls-termination-mtls: Deployment-specific timing, throughput, routing, configuration or workload heuristics in the retained examples Core factual mechanisms source-checked; keep inherited medium confidence for qualified performance, deployment/product and heuristic examples. No live deployment benchmarks were run.
- medium confidence, net-tls-resumption-replay: Deployment-specific timing, throughput, routing, configuration or workload heuristics in the retained examples Core factual mechanisms source-checked; keep inherited medium confidence for qualified performance, deployment/product and heuristic examples. No live deployment benchmarks were run.
- medium confidence, net-l4-l7-routing: Deployment-specific timing, throughput, routing, configuration or workload heuristics in the retained examples Core factual mechanisms source-checked; keep inherited medium confidence for qualified performance, deployment/product and heuristic examples. No live deployment benchmarks were run.
- medium confidence, net-balancing-load-choices: Deployment-specific timing, throughput, routing, configuration or workload heuristics in the retained examples Core factual mechanisms source-checked; keep inherited medium confidence for qualified performance, deployment/product and heuristic examples. No live deployment benchmarks were run.
- medium confidence, net-hash-affinity-resizing: Deployment-specific timing, throughput, routing, configuration or workload heuristics in the retained examples Core factual mechanisms source-checked; keep inherited medium confidence for qualified performance, deployment/product and heuristic examples. No live deployment benchmarks were run.
- medium confidence, net-health-check-policies: Deployment-specific timing, throughput, routing, configuration or workload heuristics in the retained examples Core factual mechanisms source-checked; keep inherited medium confidence for qualified performance, deployment/product and heuristic examples. No live deployment benchmarks were run.
- medium confidence, net-session-affinity-draining: Deployment-specific timing, throughput, routing, configuration or workload heuristics in the retained examples Core factual mechanisms source-checked; keep inherited medium confidence for qualified performance, deployment/product and heuristic examples. No live deployment benchmarks were run.
- medium confidence, net-reverse-proxy-buffering: Deployment-specific timing, throughput, routing, configuration or workload heuristics in the retained examples Core factual mechanisms source-checked; keep inherited medium confidence for qualified performance, deployment/product and heuristic examples. No live deployment benchmarks were run.
- medium confidence, net-api-gateway-bff: Deployment-specific timing, throughput, routing, configuration or workload heuristics in the retained examples Core factual mechanisms source-checked; keep inherited medium confidence for qualified performance, deployment/product and heuristic examples. No live deployment benchmarks were run.
- medium confidence, net-mesh-planes-costs: Deployment-specific timing, throughput, routing, configuration or workload heuristics in the retained examples Core factual mechanisms source-checked; keep inherited medium confidence for qualified performance, deployment/product and heuristic examples. No live deployment benchmarks were run.
- medium confidence, net-retry-budgets-deadlines: Deployment-specific timing, throughput, routing, configuration or workload heuristics in the retained examples Core factual mechanisms source-checked; keep inherited medium confidence for qualified performance, deployment/product and heuristic examples. No live deployment benchmarks were run.
- medium confidence, net-cdn-hits-distribution: Deployment-specific timing, throughput, routing, configuration or workload heuristics in the retained examples Core factual mechanisms source-checked; keep inherited medium confidence for qualified performance, deployment/product and heuristic examples. No live deployment benchmarks were run.
- medium confidence, net-cdn-cache-key-safety: Deployment-specific timing, throughput, routing, configuration or workload heuristics in the retained examples Core factual mechanisms source-checked; keep inherited medium confidence for qualified performance, deployment/product and heuristic examples. No live deployment benchmarks were run.
- medium confidence, net-cdn-purges-origin-shields: Deployment-specific timing, throughput, routing, configuration or workload heuristics in the retained examples Core factual mechanisms source-checked; keep inherited medium confidence for qualified performance, deployment/product and heuristic examples. No live deployment benchmarks were run.
- medium confidence, net-cdn-dynamic-data-locality: Deployment-specific timing, throughput, routing, configuration or workload heuristics in the retained examples Core factual mechanisms source-checked; keep inherited medium confidence for qualified performance, deployment/product and heuristic examples. No live deployment benchmarks were run.
- medium confidence, net-global-dns-policy: Deployment-specific timing, throughput, routing, configuration or workload heuristics in the retained examples Core factual mechanisms source-checked; keep inherited medium confidence for qualified performance, deployment/product and heuristic examples. No live deployment benchmarks were run.
- medium confidence, net-anycast-bgp-routing: Deployment-specific timing, throughput, routing, configuration or workload heuristics in the retained examples Core factual mechanisms source-checked; keep inherited medium confidence for qualified performance, deployment/product and heuristic examples. No live deployment benchmarks were run.
- medium confidence, net-anycast-connections-capacity: Deployment-specific timing, throughput, routing, configuration or workload heuristics in the retained examples Core factual mechanisms source-checked; keep inherited medium confidence for qualified performance, deployment/product and heuristic examples. No live deployment benchmarks were run.
- medium confidence, net-region-data-headroom: Deployment-specific timing, throughput, routing, configuration or workload heuristics in the retained examples Core factual mechanisms source-checked; keep inherited medium confidence for qualified performance, deployment/product and heuristic examples. No live deployment benchmarks were run.
- medium confidence, net-region-failover-operations: Deployment-specific timing, throughput, routing, configuration or workload heuristics in the retained examples Core factual mechanisms source-checked; keep inherited medium confidence for qualified performance, deployment/product and heuristic examples. No live deployment benchmarks were run.
- medium confidence, net-dns-records-aliases: ALIAS/flattening target lookup can change the location signal used by a DNS-steered CDN A conditional inference from provider target resolution and ECS behaviour; no provider/CDN apex comparison was executed. Question now states its assumptions.
- medium confidence, net-certificate-trust-renewal: Public certificate and Let’s Encrypt lifetime milestones Current primary schedule/profile checked on 2026-10-14. Future milestones can change; lesson is explicitly dated and limited to new public certificates.
- medium confidence, net-tls-resumption-replay: Certificate size, signing cost and handshake throughput Algorithm/key-size and transport mechanisms source-reviewed; chain fields, hardware and implementation require benchmarking. Universal RSA speed/cost assertions removed.
- medium confidence, net-balancing-load-choices: 5.3 versus 3.8 from asymptotic leading load terms Original theorem and numerical values checked; additive constants and finite-size terms omitted, so these remain illustrations rather than maximum-load predictions.
- medium confidence, net-retry-budgets-deadlines: Rate-based 20% retry budget versus product-specific concurrency budgets Rate model and separate Envoy accounting checked. The illustrative 10–20% range is not a universal default.
- medium confidence, net-anycast-bgp-routing: BGP convergence duration No routing experiment; unsupported often-seconds numerical guidance removed. Routing depends on detection, topology, timers and policy. Inherited bgp-convergence glossary confidence remains medium.
- medium confidence, net-anycast-connections-capacity: 30-second failover objective and established-connection movement Requires tested health detection and client reconnect/timeout handling. Question states the no-shared-state/forwarding failure model; anycast itself gives no time guarantee.
- medium confidence, net-cdn-purges-origin-shields: One origin fetch/refresh from shielding and collapsing Ideal one-key cacheable request model and successful coalescing are explicit; bypasses, partitioned shields, headers and failure policy can add origin requests.
- medium confidence, net-http2-streams-pools: 87% loss-round probability Correct only for independent 2% packet losses among 100 packets. Correlation and real windows differ. Inherited packet-loss glossary confidence remains medium.
- medium confidence, net-certificate-trust-renewal: Let's Encrypt classic-profile schedule: 64 days from 10 Feb 2027 and 45 days from 16 Feb 2028. Confirmed in Let's Encrypt's 2 Dec 2025 post, but future dates are plans that can change; the lesson hedges them as 'scheduled' and dated 29 October 2026.
- medium confidence, net-certificate-trust-renewal: CA/B Forum maximum validity 100 days from 15 Mar 2027 and 47 days from 15 Mar 2029. Confirmed verbatim in Baseline Requirements section 6.3.2 (current text), but these are future steps that a later ballot could amend.
- medium confidence, net-first-byte-latency: Illustrative 80 ms London-Virginia RTT, 10 ms edge, 100 ms uncached and 5 ms resolver-cached DNS. Stated as assumed figures, not measurements; arithmetic verified, real values vary with routing and resolver placement.
- medium confidence, net-anycast-bgp-routing: AWS Global Accelerator provides two static IPv4 addresses (four with dual-stack). Confirmed in current AWS docs; a product detail that could change.
- medium confidence, net-health-check-policies: Envoy defaults: outlier consecutive_5xx = 5 and panic threshold 50%. Confirmed in current Envoy docs and proto; defaults can change between releases.


## system-design / Caching

32 question objects changed. Every changed question has a specific independent-review reason in the linked record.

**Corrections in this review:**

- cache-refresh-ahead: "A fifth pattern" was wrong; refresh-ahead follows five earlier patterns (cache-aside, read-through, write-through, write-back, write-around) -> "Another pattern".
- cache-failure-modes-q9: option C ("filter size stays the same; you only need more hash functions") was only wrong if the filter already used the best hash count, which the prompt did not state -> prompt now states it, and the explanation says 1% is then the lowest rate that size can reach.
- cache-frequency-and-expiry analogy (stopped-verifier edit, kept and completed): "this week's surprise success never gets in" misdescribed LFU, which admits new keys at a low count and evicts them first -> "is the first to be taken out again before its sales can build up"; mapping sentence aligned.
- cache-hot-key-relief (stopped-verifier edit, kept): Redis 8.6 HOTKEYS described as "reporting frequently accessed keys" -> tracks and reports the keys using the most CPU time or network bytes (HOTKEYS START METRICS CPU/NET, since 8.6.0).
- cache-slabs-and-admission analogy (stopped-verifier edit, kept): sections "allocated when the car park fills" -> painted as each kind of vehicle arrives, matching Memcached assigning pages to slab classes on demand.
- cache-proxy-topologies (stopped-verifier edit, kept): the 80-connections-per-node figure was not derivable -> states that each of the 20 proxies keeps 4 connections to every node.
- cache-application-and-buffer-caches (stopped-verifier edit, kept): further-reading link moved from innodb-buffer-pool-resize.html to innodb-buffer-pool.html, the MySQL 8.4 page that states "On dedicated servers, up to 80% of physical memory is often assigned to the buffer pool".
- HEDGE cache-stampede-and-coalescing essential card: n = r x t_rebuild -> n ≈ r x t_rebuild, defining ≈ and stating the steady-arrival, no-coalescing assumptions.
- PRESENTATION cache-background-and-early-refresh (stopped-verifier edit, kept): In words referred to "beta" without saying what it is, although the symbol definitions are hidden in the closed disclosure -> "a tuning factor (beta, normally 1)"; the paper says beta defaults to 1.
- LINKS cache-avalanche-defences intro and cache-failure-modes-q4 option 1: capitalised "Jitter" linked to system-design/07-api-design backoff-jitter (retry waits) -> "TTL jitter" (this module's ttl-jitter entry).
- WORDING (stopped-verifier edits, kept; not counted as accuracy errors): "two pointers" -> "a previous and a next pointer" (cache-redis-capacity-policies, cache-eviction-q5); "growth factor" -> "ratio (set by Memcached's -f option)"; "average value size" -> "average size of one value"; "rate-limiting misses/rebuilds" -> "rate limits on misses/rebuilds" (cache-fundamentals-q6, cache-failure-modes-q12).
- AUTHOR CORRECTIONS CONFIRMED (not counted here): cache-http-freshness-policy and cache-http-q11 (RFC 9111 4.2/4.2.1/4.2.3/5.2.2.10: browsers subtract the received Age from max-age; s-maxage only sets shared-cache lifetime); nginx weak ETags since 1.7.3 (CHANGES-1.8); cache-strategies-q8 Caffeine sentence (old value returned during refresh; expireAfterWrite separate).

**Scope gaps and exclusions:**

- No substantive topic intentionally removed: original bodies were read alongside all successors; author range coverage independently recomputed, executable statements/diagram traces retained, and all14 original archival files independently match the Git baseline. Source-proven factual corrections and hedges replace inaccurate originals.
- Naturally compact units remain1–2minutes and some have1question; all39 active units have their own content, stable completion ID,1–5 questions and a local objective. Reported reading minutes exclude quiz time.
- Controlled Python adapter checks and Redis8.6.7 Lua tests do not prove production atomic adapters, failover, partitions, persistence durability, performance, or HTTP/browser/CDN integration behaviour.
- 350 unchanged glossary entries rely on their inherited verification; their records and genuine confidence levels are preserved. Complete fresh per-entry primary-source review is outside this short-lesson split pass.
- Whole-project generated build, application tests and390px browser checks belong to the coordinating agent; this scoped verifier did not edit generated data or shared app/compiler files.
- No real-browser screenshot at 390 px: rendering was checked with the app's markdown.js (collapsed reference formulas): 16 analogy and 10 reference disclosures, none open, no literal callout tags, stray emphasis or fences; the build enforces line widths.
- The Facebook NSDI 2013 paper could not be text-extracted in this pass; its figures in unchanged lessons rest on earlier verification (see lowConfidence).
- Unchanged lessons (5) and unchanged questions (52) were re-read for concept-first fit and answerability; their factual content rests on earlier verification and this pass does not claim a fresh exhaustive audit of them.
- Glossary: 3 entries added and verified; the 352 existing entries keep earlier provenance; only entries the edited text depends on were re-read.
- 23 lessons have no analogy, each with a specific recorded reason.

**Low-confidence areas, including preserved qualifications:**

- medium confidence, cache-purpose-and-locality: Conservative evidence scope and inherited factual detail Full semantic pass and fetched primary-source groups support core claims; no complete separate citation ledger for every inherited sentence or deployment experiment. Original medium lesson confidence has not been upgraded.
- medium confidence, cache-response-cache-layers: Conservative evidence scope and inherited factual detail Full semantic pass and fetched primary-source groups support core claims; no complete separate citation ledger for every inherited sentence or deployment experiment. Original medium lesson confidence has not been upgraded.
- medium confidence, cache-application-and-buffer-caches: Conservative evidence scope and inherited factual detail Full semantic pass and fetched primary-source groups support core claims; no complete separate citation ledger for every inherited sentence or deployment experiment. Original medium lesson confidence has not been upgraded.
- medium confidence, cache-hit-ratios-and-latency: Conservative evidence scope and inherited factual detail Full semantic pass and fetched primary-source groups support core claims; no complete separate citation ledger for every inherited sentence or deployment experiment. Original medium lesson confidence has not been upgraded.
- medium confidence, cache-layered-misses-and-break-even: Conservative evidence scope and inherited factual detail Full semantic pass and fetched primary-source groups support core claims; no complete separate citation ledger for every inherited sentence or deployment experiment. Original medium lesson confidence has not been upgraded.
- medium confidence, cache-working-set-sizing: Conservative evidence scope and inherited factual detail Full semantic pass and fetched primary-source groups support core claims; no complete separate citation ledger for every inherited sentence or deployment experiment. Original medium lesson confidence has not been upgraded.
- medium confidence, cache-aside-and-read-through: Conservative evidence scope and inherited factual detail Full semantic pass and fetched primary-source groups support core claims; no complete separate citation ledger for every inherited sentence or deployment experiment. Original medium lesson confidence has not been upgraded.
- medium confidence, cache-synchronous-and-bypass-writes: Conservative evidence scope and inherited factual detail Full semantic pass and fetched primary-source groups support core claims; no complete separate citation ledger for every inherited sentence or deployment experiment. Original medium lesson confidence has not been upgraded.
- medium confidence, cache-write-behind-durability: Conservative evidence scope and inherited factual detail Full semantic pass and fetched primary-source groups support core claims; no complete separate citation ledger for every inherited sentence or deployment experiment. Original medium lesson confidence has not been upgraded.
- medium confidence, cache-refresh-ahead: Conservative evidence scope and inherited factual detail Full semantic pass and fetched primary-source groups support core claims; no complete separate citation ledger for every inherited sentence or deployment experiment. Original medium lesson confidence has not been upgraded.
- medium confidence, cache-fifo-and-lru: Conservative evidence scope and inherited factual detail Full semantic pass and fetched primary-source groups support core claims; no complete separate citation ledger for every inherited sentence or deployment experiment. Original medium lesson confidence has not been upgraded.
- medium confidence, cache-frequency-and-expiry: Conservative evidence scope and inherited factual detail Full semantic pass and fetched primary-source groups support core claims; no complete separate citation ledger for every inherited sentence or deployment experiment. Original medium lesson confidence has not been upgraded.
- medium confidence, cache-redis-capacity-policies: Conservative evidence scope and inherited factual detail Full semantic pass and fetched primary-source groups support core claims; no complete separate citation ledger for every inherited sentence or deployment experiment. Original medium lesson confidence has not been upgraded.
- medium confidence, cache-redis-lfu-counters: Conservative evidence scope and inherited factual detail Full semantic pass and fetched primary-source groups support core claims; no complete separate citation ledger for every inherited sentence or deployment experiment. Original medium lesson confidence has not been upgraded.
- medium confidence, cache-slabs-and-admission: Conservative evidence scope and inherited factual detail Full semantic pass and fetched primary-source groups support core claims; no complete separate citation ledger for every inherited sentence or deployment experiment. Original medium lesson confidence has not been upgraded.
- medium confidence, cache-clock-page-replacement: Conservative evidence scope and inherited factual detail Full semantic pass and fetched primary-source groups support core claims; no complete separate citation ledger for every inherited sentence or deployment experiment. Original medium lesson confidence has not been upgraded.
- medium confidence, cache-delete-on-write-races: Conservative evidence scope and inherited factual detail Full semantic pass and fetched primary-source groups support core claims; no complete separate citation ledger for every inherited sentence or deployment experiment. Original medium lesson confidence has not been upgraded.
- medium confidence, cache-stale-refills-and-double-delete: Conservative evidence scope and inherited factual detail Full semantic pass and fetched primary-source groups support core claims; no complete separate citation ledger for every inherited sentence or deployment experiment. Original medium lesson confidence has not been upgraded.
- medium confidence, cache-version-guards-and-tombstones: Conservative evidence scope and inherited factual detail Full semantic pass and fetched primary-source groups support core claims; no complete separate citation ledger for every inherited sentence or deployment experiment. Original medium lesson confidence has not been upgraded.
- medium confidence, cache-invalidation-leases: Conservative evidence scope and inherited factual detail Full semantic pass and fetched primary-source groups support core claims; no complete separate citation ledger for every inherited sentence or deployment experiment. Original medium lesson confidence has not been upgraded.
- medium confidence, cache-change-log-and-own-writes: Conservative evidence scope and inherited factual detail Full semantic pass and fetched primary-source groups support core claims; no complete separate citation ledger for every inherited sentence or deployment experiment. Original medium lesson confidence has not been upgraded.
- medium confidence, cache-http-freshness-policy: Conservative evidence scope and inherited factual detail Full semantic pass and fetched primary-source groups support core claims; no complete separate citation ledger for every inherited sentence or deployment experiment. Original medium lesson confidence has not been upgraded.
- medium confidence, cache-http-lifetimes-and-assets: Conservative evidence scope and inherited factual detail Full semantic pass and fetched primary-source groups support core claims; no complete separate citation ledger for every inherited sentence or deployment experiment. Original medium lesson confidence has not been upgraded.
- medium confidence, cache-http-conditional-validation: Conservative evidence scope and inherited factual detail Full semantic pass and fetched primary-source groups support core claims; no complete separate citation ledger for every inherited sentence or deployment experiment. Original medium lesson confidence has not been upgraded.
- medium confidence, cache-http-variants-and-shared-caches: Conservative evidence scope and inherited factual detail Full semantic pass and fetched primary-source groups support core claims; no complete separate citation ledger for every inherited sentence or deployment experiment. Original medium lesson confidence has not been upgraded.
- medium confidence, cache-http-stale-serving: Conservative evidence scope and inherited factual detail Full semantic pass and fetched primary-source groups support core claims; no complete separate citation ledger for every inherited sentence or deployment experiment. Original medium lesson confidence has not been upgraded.
- medium confidence, cache-distributed-engine-choice: Conservative evidence scope and inherited factual detail Full semantic pass and fetched primary-source groups support core claims; no complete separate citation ledger for every inherited sentence or deployment experiment. Original medium lesson confidence has not been upgraded.
- medium confidence, cache-modulo-and-consistent-hashing: Conservative evidence scope and inherited factual detail Full semantic pass and fetched primary-source groups support core claims; no complete separate citation ledger for every inherited sentence or deployment experiment. Original medium lesson confidence has not been upgraded.
- medium confidence, cache-redis-hash-slot-routing: Conservative evidence scope and inherited factual detail Full semantic pass and fetched primary-source groups support core claims; no complete separate citation ledger for every inherited sentence or deployment experiment. Original medium lesson confidence has not been upgraded.
- medium confidence, cache-replication-and-gutter: Conservative evidence scope and inherited factual detail Full semantic pass and fetched primary-source groups support core claims; no complete separate citation ledger for every inherited sentence or deployment experiment. Original medium lesson confidence has not been upgraded.
- medium confidence, cache-restart-persistence: Conservative evidence scope and inherited factual detail Full semantic pass and fetched primary-source groups support core claims; no complete separate citation ledger for every inherited sentence or deployment experiment. Original medium lesson confidence has not been upgraded.
- medium confidence, cache-proxy-topologies: Conservative evidence scope and inherited factual detail Full semantic pass and fetched primary-source groups support core claims; no complete separate citation ledger for every inherited sentence or deployment experiment. Original medium lesson confidence has not been upgraded.
- medium confidence, cache-stampede-and-coalescing: Conservative evidence scope and inherited factual detail Full semantic pass and fetched primary-source groups support core claims; no complete separate citation ledger for every inherited sentence or deployment experiment. Original medium lesson confidence has not been upgraded.
- medium confidence, cache-background-and-early-refresh: Conservative evidence scope and inherited factual detail Full semantic pass and fetched primary-source groups support core claims; no complete separate citation ledger for every inherited sentence or deployment experiment. Original medium lesson confidence has not been upgraded.
- medium confidence, cache-hot-key-relief: Conservative evidence scope and inherited factual detail Full semantic pass and fetched primary-source groups support core claims; no complete separate citation ledger for every inherited sentence or deployment experiment. Original medium lesson confidence has not been upgraded.
- medium confidence, cache-negative-cache-and-penetration: Conservative evidence scope and inherited factual detail Full semantic pass and fetched primary-source groups support core claims; no complete separate citation ledger for every inherited sentence or deployment experiment. Original medium lesson confidence has not been upgraded.
- medium confidence, cache-bloom-filter-sizing: Conservative evidence scope and inherited factual detail Full semantic pass and fetched primary-source groups support core claims; no complete separate citation ledger for every inherited sentence or deployment experiment. Original medium lesson confidence has not been upgraded.
- medium confidence, cache-avalanche-defences: Conservative evidence scope and inherited factual detail Full semantic pass and fetched primary-source groups support core claims; no complete separate citation ledger for every inherited sentence or deployment experiment. Original medium lesson confidence has not been upgraded.
- medium confidence, cache-cold-start-warming: Conservative evidence scope and inherited factual detail Full semantic pass and fetched primary-source groups support core claims; no complete separate citation ledger for every inherited sentence or deployment experiment. Original medium lesson confidence has not been upgraded.
- medium confidence, cache-restart-persistence: Copy-on-write peak memory model and AOF loss window First-order M(1+f) excludes page/buffer/allocator effects. everysec is typical loss exposure, not a measured hard fault bound; sizing is qualified.
- medium confidence, cache-http-lifetimes-and-assets: Ten-percent heuristic freshness RFC9111 presents a possible typical fraction; browsers/CDNs choose their own policies.
- medium confidence, cache-http-stale-serving: Actual support of optional stale-serving directives Normative semantics checked against RFC5861; no browser/provider integration experiment. Unverified major-browser/general CDN support assertion removed.
- medium confidence, cache-distributed-engine-choice: Version-dependent engine features, managed-service support and licences Official docs fetched on2026-10-14; selected Redis8.6, Memcached1.6.39, Caffeine3.2.3 and Valkey ancestry sources reviewed. Re-check the deployed engine/service version.
- medium confidence, cache-stampede-and-coalescing: Distributed lock safety Adapter control flow checked; no production atomic publication client/failover/partition test. Async failover can lose a lock; ownership guards do not order database invalidations or guarantee latest returned values.
- medium confidence, cache-change-log-and-own-writes: Historical remote markers Primary paper explicitly permits stale-read risk from concurrent removal or marker eviction; added caveat. Historical distributed system not reproduced.
- medium confidence, cache-cold-start-warming: Historical two-second warmup holdoff Primary paper reread; delayed invalidations can still cause rare consistency issues. The timing safeguard is qualified as an operational trade-off.
- medium confidence, glossary: Inherited unchanged glossary verification 350 entry objects and their records remain unchanged;26 existing medium scores retained. This pass semantically reverified only the two corrected entries and cross-checked terms relevant to active lessons. Author’s additional236 glossary-source URL checks are inherited evidence, not claimed as independent semantic checks.
- medium confidence, cache-redis-capacity-policies: Redis 8.6 added allkeys-lrm and volatile-lrm; default noeviction, 5 samples, 16-entry pool. Confirmed on redis.io (eviction page, 8.6 what's new), 8.6 source and a redis:8.6.7 container on 2026-10-30, but version-specific; forks and managed services differ (hedged in text, dated late 2026).
- medium confidence, cache-hot-key-relief: Redis 8.6 added HOTKEYS commands that track the keys using the most CPU time or network bytes. Confirmed on redis.io HOTKEYS START (since 8.6.0, METRICS CPU/NET) and present in redis:8.6.7; new and time-sensitive, may differ in forks and managed services.
- medium confidence, cache-distributed-engine-choice: March 2024 move to RSALv2/SSPLv1, Valkey continuing from Redis 7.2.4 under the Linux Foundation, Redis 8 adding AGPLv3, ElastiCache and Memorystore offering Valkey. Each confirmed in official announcements and product pages, but licensing and managed-service offerings can change; dated "as of late 2026" in the text.
- medium confidence, cache-invalidation-leases: Facebook lease figures (one token per key per 10 s; peak DB queries 17K/s -> 1.3K/s), gutter figures (about 1% of servers, 99% fewer client-visible failures, 10-25% of failures converted to hits, 35% hit rate within four minutes, one key up to 20% of a server's requests) and cold-cluster warm-up (2 s hold-off; hours instead of days). Unchanged baseline text verified in earlier passes. In this pass the NSDI 2013 PDF was fetched but its custom font encoding defeated text extraction, so these figures were not re-read; lessons cache-replication-and-gutter and cache-cold-start-warming carry the same figures.
- medium confidence, cache-application-and-buffer-caches: InnoDB buffer pool often given up to about 80% of RAM on a dedicated host. Wording matches the MySQL 8.4 manual sentence (fetched via a web reader because direct download returned 403); it is common practice guidance, not a rule.
- medium confidence, cache-layered-misses-and-break-even: q8 scenario: in-process tier answers 60%, Redis hit ratio falls 90% -> 80%, database share 10% -> 8%. Illustrative, self-consistent numbers rather than measured data; the qualitative effect (upper tier removes the most repetitive reads) is standard but its size depends on the workload.
- medium confidence, cache-modulo-and-consistent-hashing: Consistent hashing moves about 1/(N+1) of keys (about 20% for 4->5, about 9% for 10->11). Expected values with balanced ownership; this verifier's 150-vnode simulation gave 18.2% and 8.3%, so real rings vary with vnode count and placement (text says "about" and "when ownership is balanced").


## system-design / Databases & Storage

33 question objects changed. Every changed question has a specific independent-review reason in the linked record.

**Corrections in this review:**

- db-failover-fencing-history: GitHub September 2012 sentence said the report "describes this kind of failure" (implying the ID-reuse mechanism, which the post does not state) and omitted that the out-of-date node was elected after a Pacemaker cluster-manager partition -> now "a related failure", names the cluster-manager partition, paraphrases the post (MySQL-id-to-Redis links fell out of sync for records created in that window; events on wrong dashboards; repositories misrouted). q4 worked example marked "A related real case" with an explicit note that the report does not spell out the ID mechanism.
- db-leaderless-quorums-repair essential card: overlap was defined as "the smallest possible number of replicas" in both sets, which makes "overlap >= w + r - n" inconsistent -> defined as the number of shared replicas for whichever replicas the two operations reach.
- db-btree-clustered-layout reference card: log_f defined as "how many times you must multiply f by itself to reach n" (off by one) -> "the power you must raise f to in order to reach n".
- db-lsm-buffer-flush-compaction analogy limit: said a tombstone "only removes the old value when folders are merged", implying the value stays visible -> lookups treat it as gone at once; only physical removal waits for compaction.
- db-lsm-compaction-strategies: author edit renamed "L1" to "the first level", ambiguous with L0 -> "the first level below L0" (two sentences).
- db-storage-amplification-accounting: "This is a worst case: it ignores the WAL ..." was self-contradictory (ignoring WAL understates writes) -> "simplified estimate ... the worst case for coalescing ... leaves out the redo log and device-level copying, which add more".
- db-partitioning-q12 (db-rebalancing-tenant-cutovers): parenthesis presented the routing-shards formula as the current Elasticsearch calculation -> applies to indices created before Elasticsearch 9.4 (current indices use hash(_routing) % number of primaries).
- db-declarative-sql-joins analogy limit: unsupported "Some ORMs also send per-row queries in parallel" -> "Sending the per-row queries concurrently shortens the wait but still multiplies the number of queries". (Hedge, counted under hedgedOrRemoved.)
- db-storage-internals-q9 option 0: "would reduce the amplification" -> "could reduce" (an LSM engine brings its own compaction amplification). (Hedge.)
- db-index-scan-budgets: 1 GB/s scan speed now stated as an assumption; EXPLAIN sentence now also names bitmap scans as index use. (Hedge/completeness.)
- db-scale-operational-budget: sensor numbers reframed as an explicit "Suppose ... at an assumed 100 bytes" scenario. (Hedge.)

**Scope gaps and exclusions:**

- No production benchmarks, storage-device crash tests, torn-page fault injection, watchdog/STONITH tests or cross-region partitions; no cloud DynamoDB, Aurora, InfluxDB or Elasticsearch deployment exercised.
- All lesson SQL/CQL/Cypher fences and relevant SQL question fragments were run with documented fixtures; statements with $1/$2 or <self> use declared substitutions. Retry code is a handler fragment with explicit application helpers, not a supplied library implementation.
- Cassandra and Redis checks use one-node fixtures. They verify syntax, ordering, rejection and key-slot behaviour, not replica repair, quorum failures, compaction workloads or cluster-scale latency.
- Major-version logical replication and tenant migration are documentation-reviewed workflows; complete cutover/failover deployments were not executed.
- Existing glossary confidence/source/alias records retained; 301 original definitions remain unchanged, eight corrected from fetched primary sources, two narrow new definitions checked. This split review does not claim a fresh per-entry fetch of all inherited glossary source pages.
- Six naturally small units are honestly estimated at two minutes; 31 units are 3–5 minutes. Every unit has its own completion id and 1–5 concept-matched questions.
- The ledger counts section/question/card review units, not every atomic factual assertion. Generic historical deployment anecdotes remain omitted and scenario throughput values remain illustrative.
- Cassandra behaviours (ALLOW FILTERING rejection, hinted handoff, repair) and Elasticsearch behaviours were checked against documentation only; a cassandra:5.0 image exists locally but was not run in this pass. PostgreSQL, InnoDB and Redis claims were executed.
- Glossary: no entries changed in this pass; the 311 existing entries and their confidence records are preserved, not re-audited. Only links produced by edited text were checked (new links: IDs/ID -> caching-identifier, cluster, bitmap scan, redo log, all correct senses).
- Optional analogies for WAL, consistent hashing and Bloom filters were judged not required; they could be added in a future authored pass.
- Render: markdown.js render of all 37 lessons and every question field re-run after the verifier edits (8 analogy disclosures, no literal callouts, stray ** or fences). A browser check at 390 px and offline was not re-run; edits change prose only.

**Low-confidence areas, including preserved qualifications:**

- medium confidence, db-schema-constraints: Inherited medium evidence scope Primary-source core semantics and bounded fixtures checked; product/version/configuration choices and production/failure behaviour remain deployment-specific. No promotion of inherited medium confidence.
- medium confidence, db-declarative-sql-joins: Inherited medium evidence scope Primary-source core semantics and bounded fixtures checked; product/version/configuration choices and production/failure behaviour remain deployment-specific. No promotion of inherited medium confidence.
- medium confidence, db-acid-transfer-guarantees: Inherited medium evidence scope Primary-source core semantics and bounded fixtures checked; product/version/configuration choices and production/failure behaviour remain deployment-specific. No promotion of inherited medium confidence.
- medium confidence, db-normalisation-read-models: Inherited medium evidence scope Primary-source core semantics and bounded fixtures checked; product/version/configuration choices and production/failure behaviour remain deployment-specific. No promotion of inherited medium confidence.
- medium confidence, db-key-value-access-durability: Inherited medium evidence scope Primary-source core semantics and bounded fixtures checked; product/version/configuration choices and production/failure behaviour remain deployment-specific. No promotion of inherited medium confidence.
- medium confidence, db-document-aggregate-bounds: Inherited medium evidence scope Primary-source core semantics and bounded fixtures checked; product/version/configuration choices and production/failure behaviour remain deployment-specific. No promotion of inherited medium confidence.
- medium confidence, db-wide-column-query-buckets: Inherited medium evidence scope Primary-source core semantics and bounded fixtures checked; product/version/configuration choices and production/failure behaviour remain deployment-specific. No promotion of inherited medium confidence.
- medium confidence, db-graph-traversal-locality: Inherited medium evidence scope Primary-source core semantics and bounded fixtures checked; product/version/configuration choices and production/failure behaviour remain deployment-specific. No promotion of inherited medium confidence.
- medium confidence, db-time-series-retention-cardinality: Inherited medium evidence scope Primary-source core semantics and bounded fixtures checked; product/version/configuration choices and production/failure behaviour remain deployment-specific. No promotion of inherited medium confidence.
- medium confidence, db-search-refresh-family-fit: Inherited medium evidence scope Primary-source core semantics and bounded fixtures checked; product/version/configuration choices and production/failure behaviour remain deployment-specific. No promotion of inherited medium confidence.
- medium confidence, db-index-scan-budgets: Inherited medium evidence scope Primary-source core semantics and bounded fixtures checked; product/version/configuration choices and production/failure behaviour remain deployment-specific. No promotion of inherited medium confidence.
- medium confidence, db-btree-clustered-layout: Inherited medium evidence scope Primary-source core semantics and bounded fixtures checked; product/version/configuration choices and production/failure behaviour remain deployment-specific. No promotion of inherited medium confidence.
- medium confidence, db-lsm-buffer-flush-compaction: Inherited medium evidence scope Primary-source core semantics and bounded fixtures checked; product/version/configuration choices and production/failure behaviour remain deployment-specific. No promotion of inherited medium confidence.
- medium confidence, db-composite-covering-indexes: Inherited medium evidence scope Primary-source core semantics and bounded fixtures checked; product/version/configuration choices and production/failure behaviour remain deployment-specific. No promotion of inherited medium confidence.
- medium confidence, db-index-maintenance-plans: Inherited medium evidence scope Primary-source core semantics and bounded fixtures checked; product/version/configuration choices and production/failure behaviour remain deployment-specific. No promotion of inherited medium confidence.
- medium confidence, db-isolation-anomaly-traces: Inherited medium evidence scope Primary-source core semantics and bounded fixtures checked; product/version/configuration choices and production/failure behaviour remain deployment-specific. No promotion of inherited medium confidence.
- medium confidence, db-isolation-engine-differences: Inherited medium evidence scope Primary-source core semantics and bounded fixtures checked; product/version/configuration choices and production/failure behaviour remain deployment-specific. No promotion of inherited medium confidence.
- medium confidence, db-mvcc-snapshot-conflicts: Inherited medium evidence scope Primary-source core semantics and bounded fixtures checked; product/version/configuration choices and production/failure behaviour remain deployment-specific. No promotion of inherited medium confidence.
- medium confidence, db-row-locks-race-fixes: Inherited medium evidence scope Primary-source core semantics and bounded fixtures checked; product/version/configuration choices and production/failure behaviour remain deployment-specific. No promotion of inherited medium confidence.
- medium confidence, db-ssi-whole-transaction-retries: Inherited medium evidence scope Primary-source core semantics and bounded fixtures checked; product/version/configuration choices and production/failure behaviour remain deployment-specific. No promotion of inherited medium confidence.
- medium confidence, db-leader-replication-acknowledgements: Inherited medium evidence scope Primary-source core semantics and bounded fixtures checked; product/version/configuration choices and production/failure behaviour remain deployment-specific. No promotion of inherited medium confidence.
- medium confidence, db-replica-lag-read-guarantees: Inherited medium evidence scope Primary-source core semantics and bounded fixtures checked; product/version/configuration choices and production/failure behaviour remain deployment-specific. No promotion of inherited medium confidence.
- medium confidence, db-failover-fencing-history: Inherited medium evidence scope Primary-source core semantics and bounded fixtures checked; product/version/configuration choices and production/failure behaviour remain deployment-specific. No promotion of inherited medium confidence.
- medium confidence, db-multi-leader-conflict-resolution: Inherited medium evidence scope Primary-source core semantics and bounded fixtures checked; product/version/configuration choices and production/failure behaviour remain deployment-specific. No promotion of inherited medium confidence.
- medium confidence, db-leaderless-quorums-repair: Inherited medium evidence scope Primary-source core semantics and bounded fixtures checked; product/version/configuration choices and production/failure behaviour remain deployment-specific. No promotion of inherited medium confidence.
- medium confidence, db-range-hash-placement: Inherited medium evidence scope Primary-source core semantics and bounded fixtures checked; product/version/configuration choices and production/failure behaviour remain deployment-specific. No promotion of inherited medium confidence.
- medium confidence, db-consistent-hash-hot-keys: Inherited medium evidence scope Primary-source core semantics and bounded fixtures checked; product/version/configuration choices and production/failure behaviour remain deployment-specific. No promotion of inherited medium confidence.
- medium confidence, db-sharded-secondary-indexes: Inherited medium evidence scope Primary-source core semantics and bounded fixtures checked; product/version/configuration choices and production/failure behaviour remain deployment-specific. No promotion of inherited medium confidence.
- medium confidence, db-rebalancing-tenant-cutovers: Inherited medium evidence scope Primary-source core semantics and bounded fixtures checked; product/version/configuration choices and production/failure behaviour remain deployment-specific. No promotion of inherited medium confidence.
- medium confidence, db-database-access-pattern-fit: Inherited medium evidence scope Primary-source core semantics and bounded fixtures checked; product/version/configuration choices and production/failure behaviour remain deployment-specific. No promotion of inherited medium confidence.
- medium confidence, db-scale-operational-budget: Inherited medium evidence scope Primary-source core semantics and bounded fixtures checked; product/version/configuration choices and production/failure behaviour remain deployment-specific. No promotion of inherited medium confidence.
- medium confidence, db-polyglot-outbox-handoff: Inherited medium evidence scope Primary-source core semantics and bounded fixtures checked; product/version/configuration choices and production/failure behaviour remain deployment-specific. No promotion of inherited medium confidence.
- medium confidence, db-pages-wal-crash-recovery: Inherited medium evidence scope Primary-source core semantics and bounded fixtures checked; product/version/configuration choices and production/failure behaviour remain deployment-specific. No promotion of inherited medium confidence.
- medium confidence, db-lsm-compaction-strategies: Inherited medium evidence scope Primary-source core semantics and bounded fixtures checked; product/version/configuration choices and production/failure behaviour remain deployment-specific. No promotion of inherited medium confidence.
- medium confidence, db-storage-amplification-accounting: Inherited medium evidence scope Primary-source core semantics and bounded fixtures checked; product/version/configuration choices and production/failure behaviour remain deployment-specific. No promotion of inherited medium confidence.
- medium confidence, db-bloom-filter-candidate-checks: Inherited medium evidence scope Primary-source core semantics and bounded fixtures checked; product/version/configuration choices and production/failure behaviour remain deployment-specific. No promotion of inherited medium confidence.
- medium confidence, db-column-store-analytical-work: Inherited medium evidence scope Primary-source core semantics and bounded fixtures checked; product/version/configuration choices and production/failure behaviour remain deployment-specific. No promotion of inherited medium confidence.
- medium confidence, db-pages-wal-crash-recovery: Indicative SSD/HDD IOPS and hardware throughput figures Retained as explicitly indicative examples, not measurements from this review; selected device, queue depth, cache and workload determine results.
- medium confidence, db-lsm-compaction-strategies: Roughly 90% last-level share Fetched RocksDB primary documentation supports dynamic targeting; static or underfilled levels, L0, retained versions and workload can change the share. Conditional caveat retained.
- medium confidence, glossary: innodb-flush-log confidence provenance Original medium record retained without upgrading. This pass fetched the primary MySQL manual and checked values 0/1/2, including the non-guaranteed approximate one-second flush interval; this does not test physical crash behaviour.
- medium confidence, glossary: resume-driven-development Inherited informal industry term with no authoritative formal standard; original confidence and source retained.
- medium confidence, glossary: io-optimized pricing description Inherited pricing/configuration description remains time-sensitive; no current regional price comparison or billing benchmark performed.
- medium confidence, db-scale-operational-budget: q11 option 1: sustained 200,000 writes/s with index maintenance and 90-day expiry of over 100 TB is "far beyond a typical single primary". Hedged engineering judgement ("Unlikely ... tests would need to show otherwise"); no benchmark exists for this exact workload. The 155 TB raw volume alone exceeds typical single-node storage.
- medium confidence, db-storage-amplification-accounting: q9 scenario: evenly spread 100-byte updates on a 2 TB InnoDB table with a 64 GB buffer pool produce host writes hundreds of times the logical bytes. Illustrative model (one change per flushed 16 KiB page, doublewrite doubling). Doublewrite and page size verified in MySQL docs and on mysql:8.0.46, but write amplification itself was not measured.
- medium confidence, db-index-scan-budgets: 100M rows -> ~8 GB, ~8 s at an assumed 1 GB/s; a B-tree lookup touches 3-4 pages, well under a millisecond when cached. Arithmetic verified; speed and latency figures are explicitly illustrative assumptions, not measurements.
- medium confidence, db-key-value-access-durability: DynamoDB per-partition 3,000 RCU / 1,000 WCU, 10 GB partitions, TTL deletion "within a few days". Verified in current AWS documentation (fetched 2026-10-30) but time-sensitive product facts that AWS can change.
- high confidence, db-failover-fencing-history: GitHub September 2012 incident as a related example of ids falling out of sync with Redis after an out-of-date node became primary. Wording now paraphrases the fetched post and explicitly avoids claiming the ID-reuse mechanism.

