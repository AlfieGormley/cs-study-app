# Content audit complete — 5 October 2026

The user resumed after the second pause, and the current-corpus review and final integration are complete. Older pause and active allocations below are historical and superseded.

- 11 subjects, 76 modules, 482 lessons and 5,565 questions have full semantic-read records; all 76 independent verification records are current. The frozen legacy exception list is empty.
- Shared review covers 166 glossary entries, all 37 custom diagram overrides and metadata. Confidence is medium, not a guarantee that every assertion was individually sourced; exact evidence and limits are recorded.
- Final build version `7755893a85c6`; all 19 Node tests passed. All lessons/questions rendered cleanly at 390px; final dictionary, diagrams, quiz, responsive and offline browser checks passed.
- All 3,283 extracted links accounted for after documented rechecks; original automated failures remain in evidence.
- [Full per-module report](content-audit.html), [integration evidence](audit-integration.json), [link evidence](audit-links.json), [saved browser checks](audit-final-checks/).
- Unsupported synth project wiring/parts/voice-count/latency details remain omitted pending selected hardware and bench evidence. Existing skipped-content decisions below remain in force.

There is no pending audit queue. Future content edits require scoped independent verification and rebuilding. Do not rerun archived `fix-root*` scripts; they were already applied and are not idempotent.

---

# ACTIVE again — user explicitly resumed immediately after the second pause

The latest user instruction is to carry on to completion. The second-pause handoff remains a useful state snapshot, but its stop instruction is superseded. Agents resume TCP03/security05, security03/06, and security04/shared assets respectively; root completes integration.

# PAUSED at the user’s request — 5 October 2026

Wait for the user to explicitly resume after their usage allowance resets. Do not continue automatically.

Latest checkpoint: [second-pause handoff](audit-checkpoint-2026-10-05-second-pause/HANDOFF.md). Estimated90–95% overall;475/482lessons and5,486/5,565questions have recorded full reads;71/76modules have current independent records. System-design and synth priority reviews are complete. Remaining security work, shared independent review and final build/link/mobile/offline integration are detailed in the handoff. The historical “active” notes below are superseded.

---

## Current allocation — 2026-10-05 final subject reviews

Wireless06 independently complete/stamped (6 lessons/72 questions; author25,966 tests rerun;62 verifier correction groups). Network05 complete/stamped. TCP03 full independent read and102,543 assertions complete; source closure/stamp pending with audit_system_design, then security05. audit_synth takes security04 then shared assets (166glossarydefinitions, all diagram overrides and metadata); audit_systems takes security03 then06. Root author reports: docs/audit-shared-author.json and audit-networks-modern.json. Shared review was reassigned from systems to synth. All19Node tests passed before latest source edits; final repeat required. Full link sweep running externally, log /tmp/cs-study-audit-2026-10-04/link-check-final.txt (session92423). UI full-corpus harness prepared /tmp/cs-study-ui-tools/check-audit-full.cjs; only run after complete build.64verified stale legacy exceptions removed; pending6entries were retained for now. No root stamping.

## Latest audit checkpoint — 2026-10-05

Review remains active and incomplete. All DSA, architecture, OS, language, theory, software-engineering, database, system-design and synthesiser module passes are complete. Network01/02/04 complete; network05 final closure active; TCP03 author complete (7 lessons/80 questions, 102,543 assertions), independent audit_system_design next. Wireless06 author complete (6 lessons/72 questions, 25,966 assertions), independent audit_synth active. Security01 complete; security02 closure active, then audit_systems takes03/06; audit_synth takes04 after wireless, audit_system_design takes05 after TCP. Root moves shared glossary/diagram/app-text review. Full build, generated aggregate report, links, mobile/offline and all renderer tests remain. Helpers fix-root1–102 already applied: DO NOT rerun exact replacements. See per-module JSON reports for evidence and limitations.

## Live audit update — 2026-10-05 continuation

- Review is active, not paused. System design and synthesiser priority reviews were completed earlier; the whole-project audit is still incomplete.
- New completed independent reviews: languages types02 and memory03; OS processes01 and scheduling02; DSA linear02; theory logic01 and automata04. See individual audit JSON reports and verification records for exact counts and limitations.
- Root probability03 author pass: all 6 lessons and **70** questions fully read/corrected. All 10 lesson and 3 quiz Python fences executed; 7,187 checks pass. `docs/audit-theory-probability.json`; `/tmp/cs-study-audit-2026-10-04/check-probability.py`. Scoped build has only the six expected pending-verification errors. Independent verification assigned to audit_system_design after trees04.
- Applied root helper scripts fix-root31..36: DO NOT rerun; they perform exact replacements on pre-edit text.
- Root theory05 computability author pass complete: 6 lessons/67 questions, corrections applied in fix-root37..40 (DO NOT rerun). `docs/audit-theory-computability.json`; `check-computability.py` passes 19,188 assertions across 15 lesson Python fences plus quiz outputs and edge cases. Original binary increment trace was correct and retained. Independent verification assigned to audit_system_design before DSA06.
- Further completed independent passes: theory03 probability (44 follow-up correction groups; 27,433 independent assertions plus root 7,187); DSA04 trees; languages04 functional; OS03 synchronisation. Agents now: languages05 compilers, OS04 deadlocks, theory05 verification then DSA06–09. Root now owns architecture author reviews.
- Theory05 independently complete/stamped: 25 verifier correction groups, 7,379 independent checks plus author 19,188. Architecture01 author complete: six lessons/72 questions; 3,477,552 assertions including exhaustive scalar UTF encodings, native C and UBSan; `docs/audit-architecture-data.json`, `/tmp/cs-study-audit-2026-10-04/check-representation.py`. Independent verifier audit_synth queued after languages06. Root41..45 applied; DO NOT rerun. Languages05 and OS04 now independently complete/stamped. Agents active: DSA06 graphs; languages06 then architecture01/02; OS05 memory onward. Root will take remaining architecture modules avoiding agent-owned02.
- Generated data, aggregate report, all-project build/link checks and mobile/offline integration still need final refresh after review completion.

- ISA03 author review complete: 6 lessons/68 questions; root46..50 applied (DO NOT rerun). 1,273,319 assertions across native A64, x86 compatibility execution, Python toy machine and ELF relocation checks. `docs/audit-architecture-isa.json`; independent verifier audit_synth queued after digital-logic02. Architecture01 independently complete. Languages06, DSA06 and OS05 complete. Root will take architecture04 next.

# Current status: content audit resumed

The user explicitly resumed the review. The checkpoint below records the prior pause; active agents are continuing from its stopping points.

Read [the audit handoff](audit-checkpoint-2026-10-05/HANDOFF.md) for completed work, pending corrections, agent stopping points and validation requirements. The content audit is incomplete; the older completion statement below refers to initial content generation, not the current fact-check.

---

# Resuming content generation

Paused on 2026-10-01 at the user's request (usage limit). This file is the queue.

## State

**Complete** as of 2026-10-01: all 74 modules across 11 subjects (468 lessons, 5,413 questions). Every module
passes the build, all 2,940 links load, and every lesson and question renders cleanly at iPhone size.
The "Skipped lessons" section below lists what was left out on purpose. The queue is kept for reference and for
adding modules later.

## How to resume a module

1. Each module is written by one sub-agent, with up to 20 running at once.
2. Prompt template:
   > Read and follow `docs/new-module.md`. Subject: <Title> (content/<subject>/). Your module dir:
   > content/<subject>/<dir>/. module.json: id "<id>", title "<title>", order <n>. Lesson ids prefixed `<prefix>`.
   > Lessons: <outline below>
3. For an **interrupted** module, add this to the prompt: "This module was partly written before an interruption. Read what's there, keep finished lessons and
   their question ids, fix or complete any half-written files, then write the missing lessons."
4. Use a scratch folder named after the module (the old session scratchpad is gone).
5. After every module: run `node scripts/build.mjs`, then `node scripts/check-links.mjs`.

## Queue

### Data Structures & Algorithms (`dsa`)
- **10-advanced** (INTERRUPTED, 4 lessons have questions). id `dsa-advanced`, "Advanced Structures & Algorithms",
  order 10, prefix `adv-`. Lessons:
  1. LRU/LFU cache and O(1) getRandom design
  2. Union-Find in depth
  3. Segment trees with lazy propagation
  4. Fenwick trees
  5. String algorithms (KMP, Rabin–Karp, Z, suffix arrays intro)
  6. Skip lists, treaps, reservoir sampling, Fisher–Yates
  7. Sparse tables/RMQ and an overview of persistent structures and ropes

### Operating Systems (`os`): all INTERRUPTED, in content-wip/os/
- **01-processes**, `os-processes`, "OS Basics & Processes", order 1, prefix `proc-`. Lessons:
  1. What an OS does (kernel vs user space; monolithic, micro and hybrid kernels)
  2. System calls and modes, vDSO
  3. Processes and address-space layout, PCB, states
  4. fork/exec/wait, copy-on-write, zombies and orphans
  5. Context switching costs
  6. IPC (pipes, signals, shared memory, message queues, sockets)
- **02-threads-scheduling**, `os-threads`, "Threads & Scheduling", order 2, prefix `sched-`. Lessons:
  1. Threads and threading models
  2. pthreads, thread pools, the GIL
  3. Scheduling basics (FCFS, SJF, RR, Gantt charts)
  4. Priority, MLFQ, priority inversion (Mars Pathfinder)
  5. Linux CFS → EEVDF, nice, RT classes
  6. Multicore scheduling, affinity, NUMA, container CPU throttling
- **03-synchronisation**, `os-sync`, "Concurrency & Synchronisation", order 3, prefix `sync-`. Lessons:
  1. Races and critical sections
  2. Locks (TAS, CAS, futex, spinlocks)
  3. Semaphores, condition variables, monitors
  4. Classic problems
  5. Atomics, memory ordering, barriers, double-checked locking
  6. Lock-free structures, ABA, RCU, read-write locks
- **04-deadlock**, `os-deadlock`, "Deadlock & Liveness", order 4, prefix `dl-`. Lessons:
  1. Coffman conditions and resource-allocation graphs
  2. Prevention and lock ordering
  3. Banker's algorithm
  4. Detection and recovery (including databases)
  5. Livelock, starvation, priority inversion
  6. Debugging (thread dumps, lockdep, TSan) and design for no deadlock
- **05-memory**, `os-memory`, "Memory Management", order 5, prefix `mem-`. Lessons:
  1. Address spaces, base/bounds, segmentation
  2. Paging and multi-level page tables
  3. TLB, effective access time, huge pages
  4. Page faults, copy-on-write, mmap, swap
  5. Page replacement (FIFO, OPT, LRU, clock, Belady), thrashing
  6. Allocators (malloc, buddy, slab, jemalloc)
  7. The OOM killer, overcommit, RSS/VSZ, cgroup limits, leak tools
- **06-file-systems**, `os-filesystems`, "File Systems & Storage", order 6, prefix `fs-`. Lessons:
  1. File abstraction, file descriptors, VFS
  2. Inodes, links, allocation strategies
  3. Crash consistency, journaling, copy-on-write, fsync and fsyncgate
  4. Page cache, O_DIRECT, mmap, zero-copy
  5. HDD/SSD/NVMe, FTL, RAID maths
  6. ext4/XFS/ZFS, log-structured file systems, NFS, GFS/HDFS
- **07-io**, `os-io`, "I/O & Event-Driven Servers", order 7, prefix `io-`. Lessons:
  1. Interrupts, DMA, drivers
  2. The five I/O models
  3. select/poll/epoll/kqueue, C10K
  4. io_uring
  5. Event loops (libuv, nginx, Redis)
  6. The kernel network stack, NAPI, RSS, DPDK, eBPF/XDP
- **08-virtualisation**, `os-virtualisation`, "Virtualisation & Containers", order 8, prefix `virt-`. Lessons:
  1. Hypervisors, trap-and-emulate, Popek–Goldberg
  2. VT-x, EPT, virtio, SR-IOV, live migration
  3. Namespaces, cgroups v2, overlayfs
  4. OCI images, runc/containerd, Docker
  5. Isolation (seccomp, capabilities, gVisor, Firecracker)
  6. How Kubernetes uses these primitives

### Computer Networks (`networks`)
The System Design subject covers networking at the design level, so these modules go lower-level.
- **01-foundations** (INTERRUPTED), `net-foundations`, "Network Foundations & the Link Layer", order 1, prefix `nf-`. Lessons:
  1. OSI vs TCP/IP and encapsulation
  2. Delay types, bandwidth-delay product
  3. The physical layer in brief
  4. Ethernet, switches, VLANs, MTU
  5. ARP, spoofing, spanning tree
  6. Error detection (CRC) and sliding-window ARQ maths
- **02-ip-routing** (INTERRUPTED), `net-ip`, "IP, Addressing & Routing", order 2, prefix `ip-`. Lessons:
  1. IPv4 header, fragmentation, ICMP, traceroute
  2. CIDR and subnetting maths
  3. NAT, STUN/TURN/ICE, IPv6
  4. Forwarding and longest-prefix match
  5. RIP vs OSPF
  6. BGP, hijacks, RPKI
  7. DHCP and joining a network end to end
- **03-tcp** (INTERRUPTED), `net-tcp`, "Transport Layer: TCP & UDP in Depth", order 3, prefix `tcp-`. Lessons:
  1. UDP, ports, 5-tuples
  2. Handshake, SYN cookies, close, TIME_WAIT, state machine
  3. Sequence numbers/ACKs, SACK, RTO, fast retransmit
  4. Flow control, window scaling, Nagle and delayed ACK
  5. Congestion control (Reno, CUBIC, BBR) with cwnd traces
  6. Performance (bufferbloat, Mathis formula, QUIC in user space)
  7. The sockets API and a Python server
- **04-application** (not started), `net-application`, "Application-Layer Protocols", order 4, prefix `app-`. Lessons:
  1. HTTP on the wire (chunked encoding, cookies and their attributes)
  2. HTTP/2 framing and HPACK, QUIC packets and connection migration
  3. DNS message format, DNSSEC, DoH/DoT, cache poisoning
  4. Email (SMTP, IMAP, SPF/DKIM/DMARC)
  5. NTP, SSH, SFTP, gRPC on the wire
  6. P2P (BitTorrent, Kademlia), WebRTC, RTP
- **05-network-security** (INTERRUPTED, empty), `net-security`, "Network Security", order 5, prefix `nsec-`. Lessons:
  1. Threats and DDoS amplification maths
  2. Firewalls, segmentation, zero trust
  3. TLS 1.3 in depth, certificate chains, ECH, mTLS
  4. IPsec, WireGuard, tunnels, VXLAN
  5. Wi-Fi security (WEP, WPA2/KRACK, WPA3, 802.1X)
  6. IDS/IPS, tcpdump/Wireshark, flow logs
- **06-wireless-modern** (INTERRUPTED, empty), `net-modern`, "Wireless, Mobile & Modern Networks", order 6, prefix `wm-`. Lessons:
  1. Wi-Fi generations, CSMA/CA, hidden terminals
  2. 4G/5G architecture and what it means for apps
  3. Data-centre leaf-spine, ECMP, oversubscription maths
  4. SDN, OpenFlow, VPCs
  5. Network debugging tools and method
  6. Internet structure (cables, IXPs, tiers, last mile, LEO vs GEO)

### Computer Architecture (`architecture`)
- **01-data-representation** (INTERRUPTED, no question files), `arch-data`, "Data Representation", order 1, prefix `rep-`. Lessons:
  1. Number bases
  2. Two's complement and overflow
  3. Bitwise operations
  4. IEEE 754 floating point
  5. Unicode and UTF-8/16
  6. Endianness, alignment, struct padding
- **02-digital-logic**, `arch-logic`, "Digital Logic", order 2, prefix `logic-`. Lessons:
  1. Boolean algebra
  2. Gates and CMOS
  3. Karnaugh maps
  4. Combinational circuits and adders, ALU
  5. Latches, flip-flops, FSMs
  6. Datapath, SRAM vs DRAM, Verilog intro
- **03-isa**, `arch-isa`, "Instruction Sets & Assembly", order 3, prefix `isa-`. Lessons:
  1. The stored-program computer and fetch–decode–execute
  2. RISC vs CISC, encoding, addressing modes
  3. Reading x86-64/ARM64 assembly
  4. Calling conventions and stack frames
  5. Loops, jump tables, arrays and structs in assembly
  6. Compile, assemble, link (ELF, PLT/GOT) and load, plus security (NX, ASLR, canaries)
- **04-pipelining**, `arch-pipeline`, "Pipelining & CPU Performance", order 4, prefix `pipe-`. Lessons:
  1. The iron law, CPI/IPC
  2. 5-stage pipeline
  3. Hazards and forwarding
  4. Branch prediction
  5. Superscalar, out-of-order, Tomasulo
  6. Spectre/Meltdown
  7. The power wall and multicore
- **05-memory-hierarchy**, `arch-memory`, "Caches & the Memory Hierarchy", order 5, prefix `cache-arch-`. Lessons:
  1. Locality and the hierarchy
  2. Cache organisation (direct-mapped, set-associative, address breakdown maths)
  3. Write policies and AMAT calculations
  4. Cache-friendly code (loop order, blocking, structure of arrays)
  5. Coherence (MESI) and false sharing
  6. DRAM, NUMA, prefetching
- **06-parallelism**, `arch-parallel`, "Parallel Hardware", order 6, prefix `par-`. Lessons:
  1. Flynn's taxonomy, Amdahl vs Gustafson
  2. Multicore and memory consistency models (x86-TSO vs ARM)
  3. SIMD and vectorisation (SSE/AVX/NEON)
  4. GPU architecture (SIMT, warps, memory)
  5. Accelerators (TPUs, FPGAs)
  6. Measuring performance (perf, roofline model)

### Programming Languages & Compilers (`languages`)
- **01-paradigms**, `lang-paradigms`, order 1, prefix `para-`. Lessons:
  1. Imperative vs declarative
  2. OOP (encapsulation, inheritance vs composition, polymorphism, dispatch)
  3. Functional basics
  4. Logic and dataflow languages in brief
  5. Multi-paradigm languages and choosing one
  6. Scope, binding, closures, evaluation strategies
- **02-types**, `lang-types`, order 2, prefix `type-`. Lessons:
  1. Static vs dynamic, strong vs weak
  2. Type inference (Hindley–Milner intuition)
  3. Generics and parametric polymorphism
  4. Subtyping and variance
  5. Algebraic data types and pattern matching
  6. Gradual typing (TypeScript, Python hints), soundness
- **03-memory-management**, `lang-memory`, order 3, prefix `gc-`. Lessons:
  1. Stack vs heap
  2. Manual memory and its bugs
  3. Reference counting and cycles
  4. Tracing GC (mark-sweep, copying, generational)
  5. Modern GCs (G1, ZGC, Go's), pause times
  6. Rust ownership and borrowing
- **04-functional**, `lang-functional`, order 4, prefix `fp-`. Lessons:
  1. Pure functions and immutability
  2. Higher-order functions, map/filter/reduce
  3. Recursion and tail calls
  4. Laziness
  5. Functors and monads, explained practically
  6. Persistent data structures
- **05-compilers**, `lang-compilers`, order 5, prefix `comp-`. Lessons:
  1. Compiler pipeline overview
  2. Lexing (regex to DFA)
  3. Parsing (grammars, recursive descent, precedence climbing, LL vs LR)
  4. ASTs, semantic analysis, symbol tables
  5. IR, SSA, optimisations
  6. Code generation and register allocation
  7. Interpreters, bytecode VMs, JIT (V8, HotSpot)
- **06-concurrency-models**, `lang-concurrency`, order 6, prefix `conc-`. Lessons:
  1. Threads and shared memory
  2. async/await and event loops (Python asyncio, JavaScript)
  3. Coroutines and green threads
  4. CSP and goroutines/channels
  5. Actors (Erlang, Akka)
  6. Structured concurrency and data-race freedom (Rust Send/Sync)

### Security & Cryptography (`security`)
- **01-fundamentals**, `sec-fundamentals`, order 1, prefix `secf-`. Lessons:
  1. CIA triad, AAA
  2. Threat modelling (STRIDE, attack trees)
  3. Security principles (least privilege, defence in depth, fail-safe defaults)
  4. Authentication factors and passwords
  5. Access control models
  6. Common attacker techniques and the kill chain
- **02-crypto-basics**, `sec-crypto`, order 2, prefix `crypto-`. Lessons:
  1. Symmetric encryption (AES, modes, why ECB is bad, AEAD/GCM)
  2. Hash functions and their properties
  3. MACs and HMAC
  4. Asymmetric encryption (RSA maths walkthrough, ECC intuition)
  5. Key exchange (Diffie–Hellman with small-number maths)
  6. Randomness, KDFs, password hashing (bcrypt, scrypt, Argon2)
- **03-applied-crypto**, `sec-applied`, order 3, prefix `pki-`. Lessons:
  1. Digital signatures
  2. Certificates and PKI, chains of trust, revocation
  3. How TLS uses all of it
  4. Key management, HSMs, envelope encryption
  5. End-to-end encryption (Signal protocol at a high level)
  6. Common crypto mistakes and post-quantum crypto
- **04-web-security**, `sec-web`, order 4, prefix `web-`. Lessons:
  1. The same-origin policy and CORS
  2. XSS (stored, reflected, DOM) and CSP
  3. CSRF and SameSite
  4. Injection (SQL, command, template)
  5. SSRF, path traversal, deserialisation
  6. Authentication and session flaws, the OWASP Top 10 tour
- **05-systems-security**, `sec-systems`, order 5, prefix `sys-`. Lessons:
  1. Memory-safety bugs (buffer overflows, use-after-free)
  2. Exploit mitigations (ASLR, DEP, canaries, CFI)
  3. Privilege escalation and sandboxing
  4. Malware types
  5. Side channels
  6. Memory-safe languages
- **06-security-practice**, `sec-practice`, order 6, prefix `secp-`. Lessons:
  1. Secure SDLC, SAST/DAST
  2. Supply-chain security (SBOMs, SLSA, dependency attacks)
  3. Secrets management
  4. Logging, detection, incident response
  5. Cloud security basics (IAM)
  6. Pen-testing and bug bounties (ethics, process)

### Software Engineering (`software-engineering`)
- **01-principles**, `se-principles`, order 1, prefix `sep-`. Lessons:
  1. Clean code (naming, functions)
  2. Coupling and cohesion
  3. SOLID with examples
  4. DRY, KISS, YAGNI and their limits
  5. Error handling
  6. Writing code for others (comments, docs, APIs)
- **02-design-patterns**, `se-patterns`, order 2, prefix `dp-`. Lessons:
  1. Why patterns
  2. Creational patterns
  3. Structural patterns
  4. Behavioural patterns I (strategy, observer, command)
  5. Behavioural patterns II (state, template, iterator, visitor)
  6. Anti-patterns
- **03-testing**, `se-testing`, order 3, prefix `test-`. Lessons:
  1. Why test, and the test pyramid
  2. Unit testing well
  3. Test doubles (mocks, stubs, fakes)
  4. Integration and end-to-end tests, contract testing
  5. TDD and property-based testing
  6. Flaky tests, coverage, mutation testing
- **04-git-cicd**, `se-git`, order 4, prefix `git-`. Lessons:
  1. Git's object model
  2. Branching, merging vs rebasing
  3. Workflows (trunk-based, GitFlow)
  4. Code review
  5. CI pipelines
  6. CD, release engineering, semantic versioning
- **05-code-architecture**, `se-architecture`, order 5, prefix `sea-`. Lessons:
  1. Layered architecture
  2. Hexagonal / ports and adapters, clean architecture
  3. Domain-driven design (entities, value objects, aggregates, bounded contexts)
  4. Modularity and dependency management
  5. API and library design
  6. Architecture decision records and evolutionary architecture
- **06-practices**, `se-practices`, order 6, prefix `sepr-`. Lessons:
  1. Refactoring techniques
  2. Technical debt
  3. Debugging methodically
  4. Profiling and performance work
  5. Agile, Scrum and Kanban, estimation
  6. Working in teams (docs, on-call, postmortems)

### Theory & Discrete Maths (`theory`)
- **01-logic-proofs**, `th-logic`, order 1, prefix `logp-`. Lessons:
  1. Propositional logic
  2. Predicate logic and quantifiers
  3. Proof techniques (direct, contrapositive, contradiction)
  4. Induction (weak, strong, structural)
  5. Invariants for proving algorithms correct
  6. Boolean satisfiability intro
- **02-discrete-structures**, `th-discrete`, order 2, prefix `disc-`. Lessons:
  1. Sets and functions
  2. Relations and equivalence classes, partial orders
  3. Counting (permutations, combinations, pigeonhole)
  4. Inclusion–exclusion, recurrences, generating functions intro
  5. Graph theory essentials (trees, Euler/Hamilton paths, colouring, planarity)
  6. Number theory for CS (modular arithmetic, gcd, primes, modular inverse; links to RSA)
- **03-probability**, `th-probability`, order 3, prefix `prob-`. Lessons:
  1. Probability basics and conditional probability
  2. Bayes' theorem (base-rate fallacy)
  3. Random variables, expectation, linearity of expectation
  4. Distributions (binomial, geometric, Poisson, normal)
  5. Probability in algorithms (hashing collisions, birthday problem, randomised quicksort)
  6. Statistics for engineers (mean vs median, percentiles, confidence intervals, A/B testing)
- **04-automata**, `th-automata`, order 4, prefix `auto-`. Lessons:
  1. DFAs
  2. NFAs and subset construction
  3. Regular expressions to NFA (Thompson)
  4. The pumping lemma
  5. Minimisation
  6. Practical regex engines (backtracking vs DFA, ReDoS)
- **05-computability**, `th-computability`, order 5, prefix `compu-`. Lessons:
  1. Context-free grammars
  2. Pushdown automata, the CFL pumping lemma
  3. Turing machines
  4. The Church–Turing thesis
  5. The halting problem and diagonalisation
  6. Reductions, Rice's theorem
- **06-complexity**, `th-complexity`, order 6, prefix `cplx-`. Lessons:
  1. P and NP
  2. NP-completeness and Cook–Levin
  3. Reductions (3-SAT, vertex cover, etc.)
  4. Coping with NP-hardness (approximation, heuristics, parameterised algorithms)
  5. Space complexity, PSPACE
  6. Randomised and quantum complexity classes in brief

### Databases & SQL (`databases`)
- **01-sql-fundamentals**, `dbs-sql`, order 1, prefix `sql-`. Lessons:
  1. SELECT, WHERE, ORDER BY
  2. Joins (inner, outer, self, cross) with result tables
  3. GROUP BY, HAVING, aggregates
  4. NULL semantics
  5. INSERT/UPDATE/DELETE, constraints
  6. Schema design and DDL
- **02-advanced-sql**, `dbs-advanced`, order 2, prefix `asql-`. Lessons:
  1. Subqueries and correlated subqueries
  2. CTEs and recursive CTEs
  3. Window functions (ROW_NUMBER, RANK, LAG, running totals)
  4. Set operations, pivoting
  5. Common interview SQL problems
  6. JSON in SQL, upserts
- **03-relational-theory**, `dbs-theory`, order 3, prefix `rel-th-`. Lessons:
  1. The relational model
  2. Relational algebra
  3. Functional dependencies, closure, keys
  4. Normal forms 1NF to BCNF with decomposition examples
  5. Denormalisation trade-offs
  6. ER modelling
- **04-query-processing**, `dbs-query`, order 4, prefix `qp-`. Lessons:
  1. How a query executes
  2. Join algorithms (nested loop, hash, merge) with costs
  3. Statistics and the cost-based optimiser
  4. Reading EXPLAIN plans (Postgres)
  5. Index tuning
  6. Common performance anti-patterns

### AI & Machine Learning (`ml`)
- **01-fundamentals**, `ml-fundamentals`, order 1, prefix `mlf-`. Lessons:
  1. What ML is: supervised, unsupervised, reinforcement learning
  2. Train, validation and test splits, overfitting
  3. Bias–variance
  4. Evaluation metrics (precision/recall, ROC-AUC, RMSE)
  5. Feature engineering
  6. Regularisation and cross-validation
- **02-classical**, `ml-classical`, order 2, prefix `mlc-`. Lessons:
  1. Linear regression and gradient descent
  2. Logistic regression
  3. Decision trees
  4. Ensembles (random forests, gradient boosting/XGBoost)
  5. k-NN, SVM
  6. Clustering (k-means), PCA
- **03-neural-networks**, `ml-nn`, order 3, prefix `nn-`. Lessons:
  1. Perceptrons and MLPs
  2. Backpropagation worked by hand
  3. Optimisers (SGD, momentum, Adam), learning rates
  4. Regularisation (dropout, batch normalisation)
  5. CNNs
  6. RNNs and LSTMs
- **04-transformers-llms**, `ml-llm`, order 4, prefix `llm-`. Lessons:
  1. Embeddings and tokenisation
  2. Attention and self-attention maths
  3. The transformer architecture
  4. Pre-training, fine-tuning, RLHF
  5. Inference (KV cache, sampling, quantisation)
  6. RAG, agents, evaluation
- **05-ml-systems**, `ml-systems`, order 5, prefix `mls-`. Lessons:
  1. The ML lifecycle
  2. Data pipelines and feature stores
  3. Training at scale (data and model parallelism)
  4. Serving (batch vs online, latency)
  5. Monitoring and drift
  6. Responsible AI (bias, privacy)

## Removed content

- 2026-10-04: the AI & Machine Learning subject (`content/ml`, 5 modules) was removed at the user's request to keep the
  focus narrower. The files were moved to the macOS Trash (`cs-study-ml-20261004`).

## Skipped lessons

A safety check stopped the writer partway through each of these, so they were left out on purpose. Don't retry them:
- architecture/04-pipelining: `pipe-spectre-meltdown`
- security/04-web-security: `web-injection`, `web-ssrf-traversal-deser`, `web-auth-owasp`. The module ships with
  3 lessons. Injection is still covered at a high level in System Design's security lesson.
- security/05-systems-security: `sys-privesc-sandboxing`, `sys-malware`, `sys-side-channels`,
  `sys-memory-safe-languages`. The module ships with 2 lessons (memory bugs, mitigations).
- security/06-security-practice: `secp-cloud-iam`, `secp-pentesting`. The module ships with 4 lessons.


## Continued review: pipeline author pass (2026-10-05)

Architecture04 now fully read: 6 lessons, 66 questions. Author corrections and evidence: `docs/audit-architecture-pipeline.json`. Seven Python fences and both C loop forms checked (68,525 assertions including two compiled targets). Independent review queued with audit_synth after architecture05. Missing-verification errors expected; no root stamp. Helpers fix-root51 through55 applied: do not rerun exact replacement scripts. Digital-logic diagrams have no matching shared override by source or ID, so no reconciliation edit needed. ISA03 independent report now complete. Continue all remaining modules and shared-content review before final report.

## Continued review: networking (2026-10-05)

Network01 author pass complete (6 lessons/70 questions): `docs/audit-networks-foundations.json`; independent queue with audit_synth after pipeline04 and architecture06. Eight lesson Python fences and one contextual quiz fence exercised, 88,472 assertions. No live network/PHY testing. Scoped build only expected missing-verification errors. Root now owns network02: IPv4, subnetting and NAT/IPv6 pairs fully read/corrected; routing-basics pair fully read, corrections pending; remaining interior-routing/BGP/DHCP need full review. Helpers fix-root56–68 applied, **do not rerun** exact-replacement scripts. Next run per-module execution and release to independent review; no root stamping. Latest report generator: 402/482 lesson reads and 4607/5565 question reads (before adding network02 coverage). Parallel OS06, architecture05 and DSA07 now completed/stamped; OS07 and DSA08 active, pipeline04 independent active.

## Continued review: networking02 author completion (2026-10-05)

Network02 all seven lessons/84 questions fully read and corrected. Report: `docs/audit-networks-ip-routing.json`. Ten lesson and three contextual quiz Python fences run; 466,172 assertions pass. Shell policy-route fence not executed (Linux audit image lacks iproute2). Scoped build only expected verification errors. Source closure/independent verification pending; root has not stamped. fix-root64 through76 applied: do not rerun exact replacements. Root moves network03 while verifier queue is arranged. OS07 and DSA08 now complete/stamped; OS08, DSA09 and architecture06 active. No matching Node phase shared override found.

## Continued review: transport03 checkpoint (2026-10-05)

Root fully read/corrected first four transport03 lesson/quiz pairs (45 questions): UDP/ports, connections, reliability, flow control. docs/audit-networks-transport.json is partial; congestion/performance/sockets unread. fix-root77–84 applied, do not rerun. Need execute all examples and finish primary closure before release. Algorithms all10 and architecture all6 independently complete. audit_synth now independent network01 then application04; audit_system_design independent network02 then network-security05; audit_systems OS08 then security subject. Root will finish TCP03 then wireless06. Shared glossary/diagram/app-text review and final build/links/mobile/offline/tests remain.
