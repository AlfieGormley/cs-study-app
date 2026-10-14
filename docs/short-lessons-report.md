# Short lessons and code comments

Verified modules: 6/76. Updated 2026-10-14.

Each converted lesson has its own completion status, completion date and focused questions. Original completed lessons carry their exact dates into all new parts. Existing question IDs, saved answers, bookmarks and quiz sessions remain compatible; old lesson links open the new units.

The material is divided by concept while retaining substantive explanations, examples, caveats, equations and diagrams. Most lessons take 3–5 minutes; a few naturally small units have honest shorter estimates. Useful code comments explain operations and outputs; incomplete examples remain clearly labelled.

| Subject/module | Original lessons | Short lessons | Questions | Formulas | Glossary | Review items | Corrections |
|---|---:|---:|---:|---:|---:|---:|---:|
| system-design/Fundamentals | 7 | 27 | 84 | 107 | 379 | 252 | 37 |
| system-design/Networking & Traffic | 8 | 34 | 96 | 62 | 433 | 192 | 12 |
| system-design/Caching | 7 | 39 | 84 | 75 | 352 | 200 | 65 |
| system-design/Databases & Storage | 8 | 37 | 98 | 55 | 311 | 239 | 33 |
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

## system-design: Networking & Traffic

[Independent verification record](../content/system-design/02-networking/verification.json)

Corrections and qualifications in this conversion:

- The DNS arrow row names the hierarchy, rather than messages passed from root to TLD to authoritative servers: the recursive resolver queries each server itself. Roughly, the steps are:
- [object Object]
- [object Object]
- - **Load balancing:** migration needs packets to keep reaching the endpoint with connection state. A balancer that hashes only the changing 4-tuple can send them to another backend; connection-ID-aware routing or equivalent forwarding support avoids that failure.
- [object Object]
- [object Object]
- [object Object]
- [object Object]
- [object Object]
- As checked on 14 October 2026, its classic profile is scheduled
- maximum for newly issued publicly trusted TLS certificates became 200 days on 15 March 2026 and is scheduled to become 100 days on 15 March 2027 and 47 days on 15 March 2029.
- [object Object]
- [object Object]
- Whether partial service is preferable to rejection depends on the workload and the kinds of errors it could return.
- [object Object]
- [object Object]
- One rate-based retry budget caps retries per second at a fixed fraction of original request traffic. The calculation below uses that policy. Product accounting differs: Envoy’s retry budget instead limits concurrent retries relative to active and pending requests, with a default percentage of 20% when that budget is configured.
- 0.1 to 0.2 (10–20%) are illustrative choices, not universal defaults
- [object Object]
- [object Object]
- Ensure CDN configuration honours those headers. In CloudFront, a positive minimum TTL can override `private` or `no-store`; use an appropriate zero-minimum-TTL or cache-disabled policy for these paths. Also beware *web cache deception*:
- - [Cache expiry and minimum TTL (Amazon CloudFront)](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/Expiration.html)
- [HTTP caching (RFC 9111)]
- [object Object]
- [object Object]
- [object Object]
- [object Object]
- with deployment-dependent delay as routers propagate withdrawals and try alternatives. No convergence measurement or universal time bound is provided here.
- [object Object]
- [object Object]
- 3. **Encrypted application traffic.** QUIC encrypts application data and protects parts of its transport headers, reducing middlebox dependence on protocol details. Some routing fields stay visible. The first setup packets use publicly derivable keys, so their TLS ClientHello is observable unless ECH protects it.
- [object Object]
- Google's Maglev and Meta's Katran use software packet forwarding designed for high throughput; their achieved rates depend on hardware, packet sizes and configuration.
- - **Weighted:** choose DNS answers with 90:10 relative weights for a `v1`/`v2` canary. Resolver caching and connection reuse mean request traffic need not follow those exact percentages.
- Providers offer ALIAS/ANAME records or CNAME flattening to return address records without an ordinary apex CNAME. Supported targets differ: Route 53 alias records support selected AWS resources such as CloudFront, and eligible records in the same hosted zone; they are not aliases to arbitrary external hostnames.
- - [Alias versus CNAME targets (Amazon Route 53)](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/resource-record-sets-choosing-alias-non-alias.html)
- [Choosing a routing policy (Amazon Route 53)]
- [object Object]

Remaining gaps:

- No live TCP/TLS/QUIC, DNS/CDN, cloud-balancer, mesh or multi-region deployment; no packet capture, signature throughput, purge, BGP convergence or failover benchmark. All timing/capacity arithmetic is a stated model, not a measurement.
- Existing content depth is divided rather than removed. Cache-header details, partitioning/hash analysis and write coordination remain in later modules as before.
- The unchanged 433-term glossary retains the prior 2026-10-11 audit/reconciliation provenance; this scoped split pass checks preservation and coverage, not a new 433-definition audit. packet-loss and bgp-convergence remain medium.
- Inherited glossary annotation limitation: PoPs has no ordinary-word pops alias; point of presence is defined. The inherited round trip alias can also match serialization wording elsewhere; no shared glossary edits are made here.
- No new runnable programs: 18 conceptual drawings plus one illustrative HTTP fragment and two incomplete DNS zone fragments were source-reviewed. The DNS record lines match the archive after removing native explanatory comments and the old visual TTL annotation.
- Project-wide generated data/diagram integration, tests and 390 px browser render checks remain the coordinating agent’s responsibility under docs/short-lessons-brief.md. No shared diagram override defect was found.

Low-confidence areas:

- **medium** — net-url-dns-start: Deployment-specific timing, throughput, routing, configuration or workload heuristics in the retained examples. Core factual mechanisms source-checked; keep inherited medium confidence for qualified performance, deployment/product and heuristic examples. No live deployment benchmarks were run.
- **medium** — net-connection-handshakes: Deployment-specific timing, throughput, routing, configuration or workload heuristics in the retained examples. Core factual mechanisms source-checked; keep inherited medium confidence for qualified performance, deployment/product and heuristic examples. No live deployment benchmarks were run.
- **medium** — net-first-byte-latency: Deployment-specific timing, throughput, routing, configuration or workload heuristics in the retained examples. Core factual mechanisms source-checked; keep inherited medium confidence for qualified performance, deployment/product and heuristic examples. No live deployment benchmarks were run.
- **medium** — net-rendering-error-layers: Deployment-specific timing, throughput, routing, configuration or workload heuristics in the retained examples. Core factual mechanisms source-checked; keep inherited medium confidence for qualified performance, deployment/product and heuristic examples. No live deployment benchmarks were run.
- **medium** — net-dns-resolution-transport: Deployment-specific timing, throughput, routing, configuration or workload heuristics in the retained examples. Core factual mechanisms source-checked; keep inherited medium confidence for qualified performance, deployment/product and heuristic examples. No live deployment benchmarks were run.
- **medium** — net-dns-records-aliases: Deployment-specific timing, throughput, routing, configuration or workload heuristics in the retained examples. Core factual mechanisms source-checked; keep inherited medium confidence for qualified performance, deployment/product and heuristic examples. No live deployment benchmarks were run.
- **medium** — net-dns-cache-lifetimes: Deployment-specific timing, throughput, routing, configuration or workload heuristics in the retained examples. Core factual mechanisms source-checked; keep inherited medium confidence for qualified performance, deployment/product and heuristic examples. No live deployment benchmarks were run.
- **medium** — net-dns-steering-resilience: Deployment-specific timing, throughput, routing, configuration or workload heuristics in the retained examples. Core factual mechanisms source-checked; keep inherited medium confidence for qualified performance, deployment/product and heuristic examples. No live deployment benchmarks were run.
- **medium** — net-tcp-slow-start: Deployment-specific timing, throughput, routing, configuration or workload heuristics in the retained examples. Core factual mechanisms source-checked; keep inherited medium confidence for qualified performance, deployment/product and heuristic examples. No live deployment benchmarks were run.
- **medium** — net-udp-http1-concurrency: Deployment-specific timing, throughput, routing, configuration or workload heuristics in the retained examples. Core factual mechanisms source-checked; keep inherited medium confidence for qualified performance, deployment/product and heuristic examples. No live deployment benchmarks were run.
- **medium** — net-http2-streams-pools: Deployment-specific timing, throughput, routing, configuration or workload heuristics in the retained examples. Core factual mechanisms source-checked; keep inherited medium confidence for qualified performance, deployment/product and heuristic examples. No live deployment benchmarks were run.
- **medium** — net-quic-http3-migration: Deployment-specific timing, throughput, routing, configuration or workload heuristics in the retained examples. Core factual mechanisms source-checked; keep inherited medium confidence for qualified performance, deployment/product and heuristic examples. No live deployment benchmarks were run.
- **medium** — net-tls13-key-exchange: Deployment-specific timing, throughput, routing, configuration or workload heuristics in the retained examples. Core factual mechanisms source-checked; keep inherited medium confidence for qualified performance, deployment/product and heuristic examples. No live deployment benchmarks were run.
- **medium** — net-certificate-trust-renewal: Deployment-specific timing, throughput, routing, configuration or workload heuristics in the retained examples. Core factual mechanisms source-checked; keep inherited medium confidence for qualified performance, deployment/product and heuristic examples. No live deployment benchmarks were run.
- **medium** — net-tls-termination-mtls: Deployment-specific timing, throughput, routing, configuration or workload heuristics in the retained examples. Core factual mechanisms source-checked; keep inherited medium confidence for qualified performance, deployment/product and heuristic examples. No live deployment benchmarks were run.
- **medium** — net-tls-resumption-replay: Deployment-specific timing, throughput, routing, configuration or workload heuristics in the retained examples. Core factual mechanisms source-checked; keep inherited medium confidence for qualified performance, deployment/product and heuristic examples. No live deployment benchmarks were run.
- **medium** — net-l4-l7-routing: Deployment-specific timing, throughput, routing, configuration or workload heuristics in the retained examples. Core factual mechanisms source-checked; keep inherited medium confidence for qualified performance, deployment/product and heuristic examples. No live deployment benchmarks were run.
- **medium** — net-balancing-load-choices: Deployment-specific timing, throughput, routing, configuration or workload heuristics in the retained examples. Core factual mechanisms source-checked; keep inherited medium confidence for qualified performance, deployment/product and heuristic examples. No live deployment benchmarks were run.
- **medium** — net-hash-affinity-resizing: Deployment-specific timing, throughput, routing, configuration or workload heuristics in the retained examples. Core factual mechanisms source-checked; keep inherited medium confidence for qualified performance, deployment/product and heuristic examples. No live deployment benchmarks were run.
- **medium** — net-health-check-policies: Deployment-specific timing, throughput, routing, configuration or workload heuristics in the retained examples. Core factual mechanisms source-checked; keep inherited medium confidence for qualified performance, deployment/product and heuristic examples. No live deployment benchmarks were run.
- **medium** — net-session-affinity-draining: Deployment-specific timing, throughput, routing, configuration or workload heuristics in the retained examples. Core factual mechanisms source-checked; keep inherited medium confidence for qualified performance, deployment/product and heuristic examples. No live deployment benchmarks were run.
- **medium** — net-reverse-proxy-buffering: Deployment-specific timing, throughput, routing, configuration or workload heuristics in the retained examples. Core factual mechanisms source-checked; keep inherited medium confidence for qualified performance, deployment/product and heuristic examples. No live deployment benchmarks were run.
- **medium** — net-api-gateway-bff: Deployment-specific timing, throughput, routing, configuration or workload heuristics in the retained examples. Core factual mechanisms source-checked; keep inherited medium confidence for qualified performance, deployment/product and heuristic examples. No live deployment benchmarks were run.
- **medium** — net-mesh-planes-costs: Deployment-specific timing, throughput, routing, configuration or workload heuristics in the retained examples. Core factual mechanisms source-checked; keep inherited medium confidence for qualified performance, deployment/product and heuristic examples. No live deployment benchmarks were run.
- **medium** — net-retry-budgets-deadlines: Deployment-specific timing, throughput, routing, configuration or workload heuristics in the retained examples. Core factual mechanisms source-checked; keep inherited medium confidence for qualified performance, deployment/product and heuristic examples. No live deployment benchmarks were run.
- **medium** — net-cdn-hits-distribution: Deployment-specific timing, throughput, routing, configuration or workload heuristics in the retained examples. Core factual mechanisms source-checked; keep inherited medium confidence for qualified performance, deployment/product and heuristic examples. No live deployment benchmarks were run.
- **medium** — net-cdn-cache-key-safety: Deployment-specific timing, throughput, routing, configuration or workload heuristics in the retained examples. Core factual mechanisms source-checked; keep inherited medium confidence for qualified performance, deployment/product and heuristic examples. No live deployment benchmarks were run.
- **medium** — net-cdn-purges-origin-shields: Deployment-specific timing, throughput, routing, configuration or workload heuristics in the retained examples. Core factual mechanisms source-checked; keep inherited medium confidence for qualified performance, deployment/product and heuristic examples. No live deployment benchmarks were run.
- **medium** — net-cdn-dynamic-data-locality: Deployment-specific timing, throughput, routing, configuration or workload heuristics in the retained examples. Core factual mechanisms source-checked; keep inherited medium confidence for qualified performance, deployment/product and heuristic examples. No live deployment benchmarks were run.
- **medium** — net-global-dns-policy: Deployment-specific timing, throughput, routing, configuration or workload heuristics in the retained examples. Core factual mechanisms source-checked; keep inherited medium confidence for qualified performance, deployment/product and heuristic examples. No live deployment benchmarks were run.
- **medium** — net-anycast-bgp-routing: Deployment-specific timing, throughput, routing, configuration or workload heuristics in the retained examples. Core factual mechanisms source-checked; keep inherited medium confidence for qualified performance, deployment/product and heuristic examples. No live deployment benchmarks were run.
- **medium** — net-anycast-connections-capacity: Deployment-specific timing, throughput, routing, configuration or workload heuristics in the retained examples. Core factual mechanisms source-checked; keep inherited medium confidence for qualified performance, deployment/product and heuristic examples. No live deployment benchmarks were run.
- **medium** — net-region-data-headroom: Deployment-specific timing, throughput, routing, configuration or workload heuristics in the retained examples. Core factual mechanisms source-checked; keep inherited medium confidence for qualified performance, deployment/product and heuristic examples. No live deployment benchmarks were run.
- **medium** — net-region-failover-operations: Deployment-specific timing, throughput, routing, configuration or workload heuristics in the retained examples. Core factual mechanisms source-checked; keep inherited medium confidence for qualified performance, deployment/product and heuristic examples. No live deployment benchmarks were run.
- **medium** — net-dns-records-aliases: ALIAS/flattening target lookup can change the location signal used by a DNS-steered CDN. A conditional inference from provider target resolution and ECS behaviour; no provider/CDN apex comparison was executed. Question now states its assumptions.
- **medium** — net-certificate-trust-renewal: Public certificate and Let’s Encrypt lifetime milestones. Current primary schedule/profile checked on 2026-10-14. Future milestones can change; lesson is explicitly dated and limited to new public certificates.
- **medium** — net-tls-resumption-replay: Certificate size, signing cost and handshake throughput. Algorithm/key-size and transport mechanisms source-reviewed; chain fields, hardware and implementation require benchmarking. Universal RSA speed/cost assertions removed.
- **medium** — net-balancing-load-choices: 5.3 versus 3.8 from asymptotic leading load terms. Original theorem and numerical values checked; additive constants and finite-size terms omitted, so these remain illustrations rather than maximum-load predictions.
- **medium** — net-retry-budgets-deadlines: Rate-based 20% retry budget versus product-specific concurrency budgets. Rate model and separate Envoy accounting checked. The illustrative 10–20% range is not a universal default.
- **medium** — net-anycast-bgp-routing: BGP convergence duration. No routing experiment; unsupported often-seconds numerical guidance removed. Routing depends on detection, topology, timers and policy. Inherited bgp-convergence glossary confidence remains medium.
- **medium** — net-anycast-connections-capacity: 30-second failover objective and established-connection movement. Requires tested health detection and client reconnect/timeout handling. Question states the no-shared-state/forwarding failure model; anycast itself gives no time guarantee.
- **medium** — net-cdn-purges-origin-shields: One origin fetch/refresh from shielding and collapsing. Ideal one-key cacheable request model and successful coalescing are explicit; bypasses, partitioned shields, headers and failure policy can add origin requests.
- **medium** — net-http2-streams-pools: 87% loss-round probability. Correct only for independent 2% packet losses among 100 packets. Correlation and real windows differ. Inherited packet-loss glossary confidence remains medium.

## system-design: Caching

[Independent verification record](../content/system-design/03-caching/verification.json)

Corrections and qualifications in this conversion:

- {"lesson":"cache-hit-ratios-and-latency","kind":"hedge","before":"for a remote cache such as Redis typically around 1 ms including the network trip","after":"use a measured value for your deployment; the worked example assumes a 1 ms Redis round trip"}
- {"lesson":"cache-layered-misses-and-break-even","kind":"hedge","before":"Redis's *own* hit ratio looks lower than it would without the in-process layer","after":"Redis's *own* hit ratio can be lower than it would without the in-process layer"}
- {"lesson":"cache-layered-misses-and-break-even","kind":"correction","before":"With one, the average is the formula above.","after":"With one, every read pays the cache lookup and only misses also pay the backend, using the sequential model from the preceding latency unit."}
- {"lesson":"cache-application-and-buffer-caches","kind":"hedge","before":"Fastest possible, with no network hop and no serialisation.","after":"Avoids a network hop and can avoid serialisation; actual lookup cost depends on the implementation."}
- {"lesson":"cache-application-and-buffer-caches","kind":"correction","before":"recently used 8 KB pages","after":"recently used pages, normally 8 KiB (8,192 bytes)"}
- {"lesson":"cache-application-and-buffer-caches","kind":"correction","before":"at about 25% of RAM on a dedicated server","after":"at about 25% of RAM on a dedicated server with at least 1 GB of RAM"}
- {"lesson":"cache-write-behind-durability","kind":"correction","before":"This is how CPU caches, the operating system page cache, and database buffer pools work: a \"dirty\" page is written to disk later.","after":"Many CPU caches, the operating system page cache and database buffer pools use write-back: dirty data is written to the next storage layer later. A database can first make a transaction durable in its write-ahead log, so delayed buffer-page writes do not imply the same loss window as an unlogged application cache."}
- {"lesson":"cache-redis-capacity-policies","kind":"correction","before":"a pointer update on every read, which also means a lock or atomic operation","after":"list updates on hits; shared concurrent implementations also need synchronisation"}
- {"lesson":"cache-redis-capacity-policies","kind":"hedge","before":"With 5 samples, Redis's eviction is close to true LRU; with 10 it is nearly indistinguishable, at a little more CPU.","after":"Redis's documented comparison found five samples close to true LRU and ten closer, at extra CPU cost. Accuracy still depends on the access pattern; measure your workload."}
- {"lesson":"cache-redis-capacity-policies","kind":"hedge","before":"Many evictions with a falling hit ratio means the cache is too small for the working set.","after":"Many evictions with a falling hit ratio can indicate insufficient working-set capacity or a poor eviction policy."}
- {"lesson":"cache-redis-lfu-counters","kind":"correction","before":"New keys start at 5 rather than 0, so they are not evicted instantly.","after":"New keys start at 5 rather than 0, giving them a chance to establish popularity; they can still be evicted immediately."}
- {"lesson":"cache-redis-lfu-counters","kind":"correction","before":"Decay works the other way. Each time Redis looks at a key, it subtracts one for every whole decay period the key has sat untouched:","after":"Decay works the other way. For a positive decay-time setting, Redis computes a lower score for elapsed idle periods when considering a key. Ordinary accesses store the decayed-and-incremented score and a new timestamp; eviction sampling computes the score without updating that stored timestamp:"}
- {"lesson":"cache-redis-lfu-counters","kind":"correction","before":"Setting `lfu-decay-time` to 0 turns decay off.","after":"Setting `lfu-decay-time` to 0 turns decay off and is outside the division formula. The 16-bit minute clock wraps after about 45.5 days, so the simple idle-time model must not be extrapolated to arbitrarily long gaps."}
- {"lesson":"cache-redis-lfu-counters","kind":"correction","before":"[Redis eviction implementation (8.0)](https://raw.githubusercontent.com/redis/redis/8.0/src/evict.c)","after":"[Redis eviction implementation (8.6)](https://raw.githubusercontent.com/redis/redis/8.6/src/evict.c)"}
- {"lesson":"cache-slabs-and-admission","kind":"correction","before":"Memcached allocates memory in 1 MB **pages**","after":"Memcached 1.6.39 defaults to 1 MiB (1,048,576-byte) **pages**"}
- {"lesson":"cache-slabs-and-admission","kind":"correction","before":"S_{k+1} = S_k × g","after":"S_{k+1} ≈ S_k × g"}
- {"lesson":"cache-slabs-and-admission","kind":"correction","before":"the first class, S_1, is 96 B by default","after":"the illustrative first class, S_1, is 96 B; its actual size depends on item-header size and configuration"}
- {"lesson":"cache-slabs-and-admission","kind":"correction","before":"→: \"is rounded up to\"; Memcached aligns chunk sizes to a multiple of 8 bytes","after":"→: \"is rounded up to\"; the usual 64-bit build aligns chunk sizes to a multiple of 8 bytes\n≈: approximately equal; alignment changes the exact next-class size"}
- {"lesson":"cache-slabs-and-admission","kind":"correction","before":"a header of roughly 50 bytes","after":"a build-dependent header, roughly 50 bytes in this illustrative sizing"}
- {"lesson":"cache-slabs-and-admission","kind":"correction","before":"To enter the main cache, a candidate must have a higher estimated frequency than the item it would evict.","after":"The main-cache admission decision compares the candidate’s estimated frequency with the victim’s. In Caffeine 3.2.3 a higher frequency is accepted; warmer candidates can also be accepted with a small random probability to resist hash-collision attacks."}
- {"lesson":"cache-slabs-and-admission","kind":"hedge","before":"It achieves near-optimal hit ratios across many traces.","after":"Its authors report strong hit ratios across their benchmark traces; results depend on workload and implementation."}
- {"lesson":"cache-slabs-and-admission","kind":"correction","before":"- [Caffeine efficiency (W-TinyLFU)]","after":"- [Caffeine 3.2.3 admission implementation](https://raw.githubusercontent.com/ben-manes/caffeine/v3.2.3/caffeine/src/main/java/com/github/benmanes/caffeine/cache/BoundedLocalCache.java)\n- [Memcached 1.6.39 slab implementation](https://raw.githubusercontent.com/memcached/memcached/1.6.39/slabs.c)\n- [Caffeine efficiency (W-TinyLFU)]"}
- {"lesson":"cache-clock-page-replacement","kind":"hedge","before":", and many distributions now enable it.","after":". Whether it is enabled depends on kernel configuration and runtime settings."}
- {"lesson":"cache-delete-on-write-races","kind":"correction","before":"**indefinitely** (until TTL)","after":"for a whole freshly started TTL, or longer if later refills are also stale"}
- {"lesson":"cache-stale-refills-and-double-delete","kind":"correction","before":"**Leases** (covered in the following units) fix it properly.","after":"**Leases** (covered in the following units) reject fills whose token was revoked by an invalidation, when the cache enforces that protocol."}
- {"lesson":"cache-http-conditional-validation","kind":"correction","before":"the cache resets the freshness clock on its stored copy.","after":"the cache updates the stored response headers and recomputes its age and freshness under RFC 9111. A 304 does not unconditionally grant a new fixed lifetime."}
- {"lesson":"cache-http-conditional-validation","kind":"hedge","before":"revalidation fails half the time behind a load balancer.","after":"switching servers can cause unnecessary full responses even when the file is unchanged."}
- {"lesson":"cache-http-variants-and-shared-caches","kind":"correction","before":"Now a gzip copy and a Brotli copy are stored separately, and a client asking for Brotli never gets the gzip body.","after":"Reuse must match the nominated Accept-Encoding request header, allowing the cache to distinguish encoding variants. Header normalisation and the encodings a client accepts determine which variant is eligible."}
- {"lesson":"cache-http-variants-and-shared-caches","kind":"hedge","before":"`Vary: Accept-Encoding` is normal and harmless.","after":"`Vary: Accept-Encoding` is common and usually necessary when encoding changes the representation; it still adds variants."}
- {"lesson":"cache-http-stale-serving","kind":"hedge","before":"Major browsers support `stale-while-revalidate`, but `stale-if-error` is mainly honoured by CDNs and proxies, and each CDN documents its own behaviour.","after":"Browser versions and CDN products differ in which directives and failure cases they support. Use your deployed cache’s documentation and an integration check."}
- {"lesson":"cache-distributed-engine-choice","kind":"correction","before":"| 512 MiB string |","after":"| 512 MiB default string limit |"}
- {"lesson":"cache-distributed-engine-choice","kind":"hedge","before":"for system design purposes they behave largely the same.","after":"shared ancestry does not guarantee identical versioned features, threading, durability or managed-service behaviour. Check the chosen engine and service version."}
- {"lesson":"cache-modulo-and-consistent-hashing","kind":"correction","before":"(for example, the range 0 to 2³²)","after":"(for example, a 32-bit hash space with 4,294,967,296 possible positions)"}
- {"lesson":"cache-modulo-and-consistent-hashing","kind":"hedge","before":"each physical node is placed on the ring at 100–200 points.","after":"each physical node is placed at many ring positions, perhaps 150 in an illustrative design; choose and measure the count for the implementation."}
- {"lesson":"cache-replication-and-gutter","kind":"correction","before":"`min-replicas-to-write` limits the damage by making the primary refuse writes if too few replicas are connected.","after":"`min-replicas-to-write` with `min-replicas-max-lag` refuses writes when too few connected replicas meet the lag threshold; it still cannot prove receipt of each write."}
- {"lesson":"cache-restart-persistence","kind":"correction","before":"A 26 GB dataset on a 32 GB machine fits normally,","after":"This first-order estimate excludes non-dataset allocations, buffers, allocator fragmentation, page-size effects and other process overhead. A 26 GB dataset on a 32 GB machine may fit normally,"}
- {"lesson":"cache-stampede-and-coalescing","kind":"correction","before":"With 50 servers, you get at most 50 rebuilds instead of 1,000.","after":"With one coalescing group per server and no explicit forgetting, 50 servers allow at most 50 simultaneous rebuilds for the key; later calls can start new flights."}
- {"lesson":"cache-stampede-and-coalescing","kind":"correction","before":"Facebook's **leases** (the later invalidation units)","after":"Facebook's **leases** (the earlier invalidation units)"}
- {"lesson":"cache-stampede-and-coalescing","kind":"correction","before":"This handles lease expiry but does not by itself order concurrent database invalidations.","after":"The atomic ownership check rejects publication after lease expiry on that Redis state. An asynchronously replicated lock can be lost during failover, allowing overlapping owners; this is duplicate-work mitigation, not a fault-tolerant mutual-exclusion proof. It also does not by itself order concurrent database invalidations."}
- {"lesson":"cache-background-and-early-refresh","kind":"correction","before":"uniformly between 0 and 1, fresh for every request","after":"uniformly above 0 and at most 1, fresh for every request"}
- {"lesson":"cache-background-and-early-refresh","kind":"correction","before":"P = e^(−2 / (0.5 × 1)) = e^(−4) ≈ 0.018","after":"P = e^(−2 s / (0.5 s × 1))\nP = e^(−4) ≈ 0.018"}
- {"lesson":"cache-background-and-early-refresh","kind":"correction","before":"β: the tuning knob, here 1\n≈:","after":"β: the positive tuning knob, here 1\ns: seconds\n≈:"}
- {"lesson":"cache-hot-key-relief","kind":"hedge","before":"A celebrity with 100 million followers tweets.","after":"As an illustrative workload, suppose a celebrity with 100 million followers posts."}
- {"lesson":"cache-hot-key-relief","kind":"hedge","before":"Systems like this keep hot objects in process-local caches on every front-end server, precisely because one cache shard cannot serve that traffic.","after":"Process-local caches can absorb repeated reads of the object when the allowed staleness fits; this is a design illustration, not a measured description of Twitter’s deployed system."}
- {"lesson":"cache-negative-cache-and-penetration","kind":"correction","before":"Otherwise readers can continue seeing the cached absence until that entry expires.","after":"Otherwise readers can continue seeing the cached absence until that entry expires. A delayed negative fill can still race with creation and deletion; strict immediate visibility needs the same leases or retained version safeguards as positive values."}
- {"lesson":"cache-cold-start-warming","kind":"correction","before":"With a database sized for 2% of full traffic, 5% of traffic just fits once the new cache reaches a 60% hit ratio.","after":"If spare database capacity is 2% of full traffic, the new cluster alone uses that allowance at 5% traffic and a 60% hit ratio. Include the old cluster’s misses, warming work and other queries when comparing total load with capacity."}
- {"lesson":"cache-layered-misses-and-break-even","question":"cache-fundamentals-q11","field":"workedExample","option":null,"kind":"correction","before":"1 + (1 − h) × 10 = 10\n(1 − h) × 10 = 9","after":"1 ms + (1 − h) × 10 ms = 10 ms\n(1 − h) × 10 ms = 9 ms"}
- {"lesson":"cache-layered-misses-and-break-even","question":"cache-fundamentals-q11","field":"workedExample","option":null,"kind":"correction","before":"T_b: the database time, 10 ms\nIn words:","after":"T_b: the database time, 10 ms\nms: milliseconds\nIn words:"}
- {"lesson":"cache-aside-and-read-through","question":"cache-strategies-q7","field":"prompt","option":null,"kind":"correction","before":"Under a sudden spike, Within one process,","after":"Under a sudden spike, within one process,"}
- {"lesson":"cache-aside-and-read-through","question":"cache-strategies-q7","field":"workedExample","option":null,"kind":"correction","before":"as lesson 7 shows","after":"as the later stampede and coalescing unit shows"}
- {"lesson":"cache-synchronous-and-bypass-writes","question":"cache-strategies-q10","field":"workedExample","option":null,"kind":"correction","before":"Lesson 4 covers","after":"The later stale-refill unit covers"}
- {"lesson":"cache-redis-lfu-counters","question":"cache-eviction-q5","field":"explanation","option":4,"kind":"correction","before":"Redis also actively samples keys with TTLs about 10 times a second and deletes expired ones, so unread keys are reclaimed too.","after":"Redis also runs budgeted active-expiry cycles, so unread keys are reclaimed too; timing depends on version and hz/dynamic-hz settings."}
- {"lesson":"cache-slabs-and-admission","question":"cache-eviction-q6","field":"workedExample","option":null,"kind":"correction","before":"1 MB pages","after":"1 MiB (1,048,576-byte) pages"}
- {"lesson":"cache-slabs-and-admission","question":"cache-eviction-q7","field":"text","option":1,"kind":"correction","before":"When the cache is full, a new item only displaces the victim if its estimated access frequency is higher than the victim's","after":"Its main-cache admission decision compares the newcomer’s estimated frequency with the victim’s and can reject a less popular newcomer"}
- {"lesson":"cache-slabs-and-admission","question":"cache-eviction-q7","field":"explanation","option":1,"kind":"correction","before":"if the newcomer is less popular, it is dropped instead, which protects the cache from one-hit wonders.","after":"low-frequency newcomers can be dropped, protecting against one-hit wonders. Caffeine 3.2.3 also admits warmer candidates randomly with probability 1/128 as a hash-attack defence."}
- {"lesson":"cache-slabs-and-admission","question":"cache-eviction-q7","field":"workedExample","option":null,"kind":"correction","before":"6. The sketch is periodically halved so frequencies reflect recent behaviour.","after":"6. The sketch is periodically halved so frequencies reflect recent behaviour.\n7. The frequency comparison describes the main policy, not an absolute invariant: Caffeine 3.2.3 randomly admits some warmer candidates to resist hash-collision attacks."}
- {"lesson":"cache-delete-on-write-races","question":"cache-invalidation-q1","field":"explanation","option":0,"kind":"hedge","before":"The speed difference is negligible.","after":"The speed difference depends on value size and workload; it is not the reason for this default."}
- {"lesson":"cache-delete-on-write-races","question":"cache-invalidation-q6","field":"explanation","option":2,"kind":"hedge","before":"TTLs reduce hit ratio slightly, since entries expire and must be reloaded.","after":"TTLs can reduce hit ratio by expiring useful entries; the effect depends on reuse and the chosen lifetime."}
- {"lesson":"cache-invalidation-leases","question":"cache-invalidation-q3","field":"workedExample","option":null,"kind":"correction","before":"5. The next reader misses, gets a fresh token T2, reads £12, and sets it successfully.","after":"5. A later eligible reader obtains a fresh token T2, reads £12, and can set it if no further invalidation revokes T2. Clients may have to wait for the token-issuance interval."}
- {"lesson":"cache-change-log-and-own-writes","question":"cache-invalidation-q4","field":"explanation","option":2,"kind":"hedge","before":"(often tens to hundreds of ms)","after":"(whose size depends on the capture and delivery pipeline)"}
- {"lesson":"cache-change-log-and-own-writes","question":"cache-invalidation-q12","field":"workedExample","option":null,"kind":"hedge","before":"(tens of ms)","after":"(with deployment-dependent latency)"}
- {"lesson":"cache-http-lifetimes-and-assets","question":"cache-http-q9","field":"workedExample","option":null,"kind":"hedge","before":"The typical heuristic is a fraction","after":"One possible heuristic is a fraction"}
- {"lesson":"cache-restart-persistence","question":"cache-distributed-q6","field":"workedExample","option":null,"kind":"hedge","before":"keep `maxmemory` around 50–65% of RAM when snapshotting under write-heavy load","after":"set `maxmemory` below RAM by enough measured headroom for copy-on-write, buffers and fragmentation"}
- {"lesson":"cache-proxy-topologies","question":"cache-distributed-q12","field":"workedExample","option":null,"kind":"hedge","before":"(tens to hundreds of µs)","after":"(measure its latency under the actual load)"}
- {"lesson":"cache-background-and-early-refresh","question":"cache-failure-modes-q2","field":"prompt","option":null,"kind":"correction","before":"U: a fresh random number between 0 and 1","after":"U: a fresh random number above 0 and at most 1"}
- {"lesson":"cache-background-and-early-refresh","question":"cache-failure-modes-q2","field":"workedExample","option":null,"kind":"correction","before":"P = e^(−2 / (0.5 × 1)) = e^(−4)","after":"P = e^(−2 s / (0.5 s × 1))\nP = e^(−4)"}
- {"lesson":"cache-cold-start-warming","question":"cache-failure-modes-q6","field":"workedExample","option":null,"kind":"correction","before":"6. Pre-warming","after":"6. Include other database work and any old-region misses sharing this capacity; the equation counts only the new cluster. Each step needs measured headroom rather than a fixed schedule.\n7. Pre-warming"}
- {"lesson":"cache-fifo-and-lru","kind":"correction","before":"a **victim**","after":"an **eviction victim**"}
- {"lesson":"cache-slabs-and-admission","question":"cache-eviction-q7","field":"prompt","option":null,"kind":"correction","before":"an **admission** policy","after":"an **admission policy**"}
- {"lesson":"cache-delete-on-write-races","kind":"correction","before":"**Invalidation** is how","after":"**Cache invalidation** is how"}
- {"lesson":"cache-background-and-early-refresh","kind":"correction","before":"a **soft** expiry","after":"a **soft expiry**"}
- {"lesson":"cache-background-and-early-refresh","kind":"correction","before":"a longer **hard** TTL","after":"a longer **hard TTL**"}
- {"lesson":"cache-stampede-and-coalescing","kind":"correction","before":"atomic ownership check","after":"atomic lock-token comparison"}
- {"lesson":"cache-write-behind-durability","kind":"correction","before":"next storage layer","after":"next memory or storage level"}
- {"lesson":"cache-http-variants-and-shared-caches","kind":"correction","before":"remove shared copies after publication","after":"remove shared responses after publication"}
- {"lesson":"cache-http-freshness-policy","kind":"correction","before":"(covered below)","after":"(covered in the later stale-serving unit)"}
- {"lesson":"cache-http-conditional-validation","kind":"correction","before":"Some servers, Nginx among them,","after":"Some servers, including the Nginx 1.26.3 gzip filter,"}
- {"lesson":"cache-change-log-and-own-writes","kind":"correction","before":"after a write in a non-primary region, a marker tells subsequent reads to go to the primary database until replication catches up.","after":"before a write from a non-primary region, the client sets a marker that redirects subsequent misses to the primary until replication delivers its removal. The paper notes that concurrent updates can remove a marker too early and eviction can lose it, so this reduces stale-read probability rather than guaranteeing read-your-writes."}
- {"lesson":"cache-change-log-and-own-writes","kind":"correction","before":"TTL on everything (with TTL jitter) + delete after commit + leases or versioning for correctness + CDC for writes that bypass the app. Each layer catches the failures of the one above it.","after":"TTLs on disposable cached values (with TTL jitter) + delete after commit + invalidation-aware leases or retained version metadata + CDC for writes that bypass the app. These address different failure modes under their stated assumptions."}
- {"lesson":"cache-change-log-and-own-writes","kind":"correction","before":"Remote markers redirect reads to an authoritative primary until regional replication catches up.","after":"Remote markers redirect misses to the primary while present; concurrent removal and eviction remain consistency risks."}
- {"lesson":"cache-change-log-and-own-writes","question":"cache-invalidation-q12","field":"workedExample","option":null,"kind":"correction","before":"The cost is a cross-region round trip (with deployment-dependent latency) on those misses only.","after":"The cost is a cross-region round trip (with deployment-dependent latency) on those misses only. Concurrent modifications can remove a marker needed by another write, and eviction can lose it: the paper describes reduced stale-read probability, not an unconditional consistency guarantee."}
- {"lesson":"cache-http-freshness-policy","question":"cache-http-q8","field":"workedExample","option":null,"kind":"correction","before":"Contrast `stale-if-error=600`, which would explicitly permit the stale copy during an outage.","after":"An alternative policy with `stale-if-error=600` and without `must-revalidate` can explicitly permit the stale copy during an eligible outage in a supporting cache."}
- {"lesson":"glossary","term":"soft-expiry","kind":"correction","before":"Soft expiry 60 s, hard TTL 10 minutes: readers wait only if nobody read the key for 9 minutes.","after":"Soft expiry 60 s, hard TTL 10 minutes: retained stale data can serve during refresh, but failed refreshes, hard expiry or eviction can still make readers wait."}
- {"lesson":"glossary","term":"w-tinylfu","kind":"correction","before":"An item must have a higher estimated frequency to reach Caffeine’s main cache.","after":"Caffeine 3.2.3 compares frequencies but permits small random admissions of warmer candidates as a hash-attack defence; source pinned to the implementation."}
- {"lesson":"cache-fifo-and-lru","kind":"hedge","before":"FIFO is rarely used on its own for application caches, but variants like **CLOCK** and **SIEVE** build on its cheapness.","after":"Variants such as **CLOCK** and **SIEVE** build on cheap queues and reference bits without maintaining exact recency order."}
- {"lesson":"cache-clock-page-replacement","kind":"hedge","before":"Since Linux 6.1 the kernel also offers","after":"Current Linux kernels also offer"}
- {"lesson":"cache-modulo-and-consistent-hashing","kind":"hedge","before":"Memcached clients typically use the **ketama** consistent hashing algorithm.","after":"Memcached clients and proxies can use the **ketama** consistent hashing algorithm; check the client’s configured distribution policy."}
- {"lesson":"cache-response-cache-layers","kind":"hedge","before":"A CDN keeps copies in hundreds of points of presence (PoPs) worldwide, so a user in Sydney fetches from Sydney rather than from Virginia.","after":"Large CDNs can keep copies in hundreds of points of presence (PoPs) worldwide, allowing an Australian user to fetch from a nearby edge rather than a distant origin. Actual placement and routing depend on the provider and request."}
- {"lesson":"cache-redis-capacity-policies","question":"cache-eviction-q3","kind":"correction","before":"You deploy a fresh Redis instance as a cache with default settings and `maxmemory 4gb`. Your app never sets TTLs. What happens when memory reaches 4 GB?","after":"You deploy a fresh Redis instance as a cache with default settings and `maxmemory 4gb`. Your app never sets TTLs. What happens when accounted memory exceeds this configured 4 GiB (4,294,967,296-byte) limit?","detail":"Redis gb configuration suffix is binary; threshold uses accounted memory and is checked above its configured limit."}
- {"lesson":"cache-slabs-and-admission","kind":"correction","before":"a compact **Count-Min Sketch** (a few bits per key)","after":"a compact **Count-Min Sketch** (few-bit counters in shared hashed buckets)"}

Remaining gaps:

- No substantive topic intentionally removed: original bodies were read alongside all successors; author range coverage independently recomputed, executable statements/diagram traces retained, and all14 original archival files independently match the Git baseline. Source-proven factual corrections and hedges replace inaccurate originals.
- Naturally compact units remain1–2minutes and some have1question; all39 active units have their own content, stable completion ID,1–5 questions and a local objective. Reported reading minutes exclude quiz time.
- Controlled Python adapter checks and Redis8.6.7 Lua tests do not prove production atomic adapters, failover, partitions, persistence durability, performance, or HTTP/browser/CDN integration behaviour.
- 350 unchanged glossary entries rely on their inherited verification; their records and genuine confidence levels are preserved. Complete fresh per-entry primary-source review is outside this short-lesson split pass.
- Whole-project generated build, application tests and390px browser checks belong to the coordinating agent; this scoped verifier did not edit generated data or shared app/compiler files.

Low-confidence areas:

- **medium** — cache-purpose-and-locality: Conservative evidence scope and inherited factual detail. Full semantic pass and fetched primary-source groups support core claims; no complete separate citation ledger for every inherited sentence or deployment experiment. Original medium lesson confidence has not been upgraded.
- **medium** — cache-response-cache-layers: Conservative evidence scope and inherited factual detail. Full semantic pass and fetched primary-source groups support core claims; no complete separate citation ledger for every inherited sentence or deployment experiment. Original medium lesson confidence has not been upgraded.
- **medium** — cache-application-and-buffer-caches: Conservative evidence scope and inherited factual detail. Full semantic pass and fetched primary-source groups support core claims; no complete separate citation ledger for every inherited sentence or deployment experiment. Original medium lesson confidence has not been upgraded.
- **medium** — cache-hit-ratios-and-latency: Conservative evidence scope and inherited factual detail. Full semantic pass and fetched primary-source groups support core claims; no complete separate citation ledger for every inherited sentence or deployment experiment. Original medium lesson confidence has not been upgraded.
- **medium** — cache-layered-misses-and-break-even: Conservative evidence scope and inherited factual detail. Full semantic pass and fetched primary-source groups support core claims; no complete separate citation ledger for every inherited sentence or deployment experiment. Original medium lesson confidence has not been upgraded.
- **medium** — cache-working-set-sizing: Conservative evidence scope and inherited factual detail. Full semantic pass and fetched primary-source groups support core claims; no complete separate citation ledger for every inherited sentence or deployment experiment. Original medium lesson confidence has not been upgraded.
- **medium** — cache-aside-and-read-through: Conservative evidence scope and inherited factual detail. Full semantic pass and fetched primary-source groups support core claims; no complete separate citation ledger for every inherited sentence or deployment experiment. Original medium lesson confidence has not been upgraded.
- **medium** — cache-synchronous-and-bypass-writes: Conservative evidence scope and inherited factual detail. Full semantic pass and fetched primary-source groups support core claims; no complete separate citation ledger for every inherited sentence or deployment experiment. Original medium lesson confidence has not been upgraded.
- **medium** — cache-write-behind-durability: Conservative evidence scope and inherited factual detail. Full semantic pass and fetched primary-source groups support core claims; no complete separate citation ledger for every inherited sentence or deployment experiment. Original medium lesson confidence has not been upgraded.
- **medium** — cache-refresh-ahead: Conservative evidence scope and inherited factual detail. Full semantic pass and fetched primary-source groups support core claims; no complete separate citation ledger for every inherited sentence or deployment experiment. Original medium lesson confidence has not been upgraded.
- **medium** — cache-fifo-and-lru: Conservative evidence scope and inherited factual detail. Full semantic pass and fetched primary-source groups support core claims; no complete separate citation ledger for every inherited sentence or deployment experiment. Original medium lesson confidence has not been upgraded.
- **medium** — cache-frequency-and-expiry: Conservative evidence scope and inherited factual detail. Full semantic pass and fetched primary-source groups support core claims; no complete separate citation ledger for every inherited sentence or deployment experiment. Original medium lesson confidence has not been upgraded.
- **medium** — cache-redis-capacity-policies: Conservative evidence scope and inherited factual detail. Full semantic pass and fetched primary-source groups support core claims; no complete separate citation ledger for every inherited sentence or deployment experiment. Original medium lesson confidence has not been upgraded.
- **medium** — cache-redis-lfu-counters: Conservative evidence scope and inherited factual detail. Full semantic pass and fetched primary-source groups support core claims; no complete separate citation ledger for every inherited sentence or deployment experiment. Original medium lesson confidence has not been upgraded.
- **medium** — cache-slabs-and-admission: Conservative evidence scope and inherited factual detail. Full semantic pass and fetched primary-source groups support core claims; no complete separate citation ledger for every inherited sentence or deployment experiment. Original medium lesson confidence has not been upgraded.
- **medium** — cache-clock-page-replacement: Conservative evidence scope and inherited factual detail. Full semantic pass and fetched primary-source groups support core claims; no complete separate citation ledger for every inherited sentence or deployment experiment. Original medium lesson confidence has not been upgraded.
- **medium** — cache-delete-on-write-races: Conservative evidence scope and inherited factual detail. Full semantic pass and fetched primary-source groups support core claims; no complete separate citation ledger for every inherited sentence or deployment experiment. Original medium lesson confidence has not been upgraded.
- **medium** — cache-stale-refills-and-double-delete: Conservative evidence scope and inherited factual detail. Full semantic pass and fetched primary-source groups support core claims; no complete separate citation ledger for every inherited sentence or deployment experiment. Original medium lesson confidence has not been upgraded.
- **medium** — cache-version-guards-and-tombstones: Conservative evidence scope and inherited factual detail. Full semantic pass and fetched primary-source groups support core claims; no complete separate citation ledger for every inherited sentence or deployment experiment. Original medium lesson confidence has not been upgraded.
- **medium** — cache-invalidation-leases: Conservative evidence scope and inherited factual detail. Full semantic pass and fetched primary-source groups support core claims; no complete separate citation ledger for every inherited sentence or deployment experiment. Original medium lesson confidence has not been upgraded.
- **medium** — cache-change-log-and-own-writes: Conservative evidence scope and inherited factual detail. Full semantic pass and fetched primary-source groups support core claims; no complete separate citation ledger for every inherited sentence or deployment experiment. Original medium lesson confidence has not been upgraded.
- **medium** — cache-http-freshness-policy: Conservative evidence scope and inherited factual detail. Full semantic pass and fetched primary-source groups support core claims; no complete separate citation ledger for every inherited sentence or deployment experiment. Original medium lesson confidence has not been upgraded.
- **medium** — cache-http-lifetimes-and-assets: Conservative evidence scope and inherited factual detail. Full semantic pass and fetched primary-source groups support core claims; no complete separate citation ledger for every inherited sentence or deployment experiment. Original medium lesson confidence has not been upgraded.
- **medium** — cache-http-conditional-validation: Conservative evidence scope and inherited factual detail. Full semantic pass and fetched primary-source groups support core claims; no complete separate citation ledger for every inherited sentence or deployment experiment. Original medium lesson confidence has not been upgraded.
- **medium** — cache-http-variants-and-shared-caches: Conservative evidence scope and inherited factual detail. Full semantic pass and fetched primary-source groups support core claims; no complete separate citation ledger for every inherited sentence or deployment experiment. Original medium lesson confidence has not been upgraded.
- **medium** — cache-http-stale-serving: Conservative evidence scope and inherited factual detail. Full semantic pass and fetched primary-source groups support core claims; no complete separate citation ledger for every inherited sentence or deployment experiment. Original medium lesson confidence has not been upgraded.
- **medium** — cache-distributed-engine-choice: Conservative evidence scope and inherited factual detail. Full semantic pass and fetched primary-source groups support core claims; no complete separate citation ledger for every inherited sentence or deployment experiment. Original medium lesson confidence has not been upgraded.
- **medium** — cache-modulo-and-consistent-hashing: Conservative evidence scope and inherited factual detail. Full semantic pass and fetched primary-source groups support core claims; no complete separate citation ledger for every inherited sentence or deployment experiment. Original medium lesson confidence has not been upgraded.
- **medium** — cache-redis-hash-slot-routing: Conservative evidence scope and inherited factual detail. Full semantic pass and fetched primary-source groups support core claims; no complete separate citation ledger for every inherited sentence or deployment experiment. Original medium lesson confidence has not been upgraded.
- **medium** — cache-replication-and-gutter: Conservative evidence scope and inherited factual detail. Full semantic pass and fetched primary-source groups support core claims; no complete separate citation ledger for every inherited sentence or deployment experiment. Original medium lesson confidence has not been upgraded.
- **medium** — cache-restart-persistence: Conservative evidence scope and inherited factual detail. Full semantic pass and fetched primary-source groups support core claims; no complete separate citation ledger for every inherited sentence or deployment experiment. Original medium lesson confidence has not been upgraded.
- **medium** — cache-proxy-topologies: Conservative evidence scope and inherited factual detail. Full semantic pass and fetched primary-source groups support core claims; no complete separate citation ledger for every inherited sentence or deployment experiment. Original medium lesson confidence has not been upgraded.
- **medium** — cache-stampede-and-coalescing: Conservative evidence scope and inherited factual detail. Full semantic pass and fetched primary-source groups support core claims; no complete separate citation ledger for every inherited sentence or deployment experiment. Original medium lesson confidence has not been upgraded.
- **medium** — cache-background-and-early-refresh: Conservative evidence scope and inherited factual detail. Full semantic pass and fetched primary-source groups support core claims; no complete separate citation ledger for every inherited sentence or deployment experiment. Original medium lesson confidence has not been upgraded.
- **medium** — cache-hot-key-relief: Conservative evidence scope and inherited factual detail. Full semantic pass and fetched primary-source groups support core claims; no complete separate citation ledger for every inherited sentence or deployment experiment. Original medium lesson confidence has not been upgraded.
- **medium** — cache-negative-cache-and-penetration: Conservative evidence scope and inherited factual detail. Full semantic pass and fetched primary-source groups support core claims; no complete separate citation ledger for every inherited sentence or deployment experiment. Original medium lesson confidence has not been upgraded.
- **medium** — cache-bloom-filter-sizing: Conservative evidence scope and inherited factual detail. Full semantic pass and fetched primary-source groups support core claims; no complete separate citation ledger for every inherited sentence or deployment experiment. Original medium lesson confidence has not been upgraded.
- **medium** — cache-avalanche-defences: Conservative evidence scope and inherited factual detail. Full semantic pass and fetched primary-source groups support core claims; no complete separate citation ledger for every inherited sentence or deployment experiment. Original medium lesson confidence has not been upgraded.
- **medium** — cache-cold-start-warming: Conservative evidence scope and inherited factual detail. Full semantic pass and fetched primary-source groups support core claims; no complete separate citation ledger for every inherited sentence or deployment experiment. Original medium lesson confidence has not been upgraded.
- **medium** — cache-restart-persistence: Copy-on-write peak memory model and AOF loss window. First-order M(1+f) excludes page/buffer/allocator effects. everysec is typical loss exposure, not a measured hard fault bound; sizing is qualified.
- **medium** — cache-http-lifetimes-and-assets: Ten-percent heuristic freshness. RFC9111 presents a possible typical fraction; browsers/CDNs choose their own policies.
- **medium** — cache-http-stale-serving: Actual support of optional stale-serving directives. Normative semantics checked against RFC5861; no browser/provider integration experiment. Unverified major-browser/general CDN support assertion removed.
- **medium** — cache-distributed-engine-choice: Version-dependent engine features, managed-service support and licences. Official docs fetched on2026-10-14; selected Redis8.6, Memcached1.6.39, Caffeine3.2.3 and Valkey ancestry sources reviewed. Re-check the deployed engine/service version.
- **medium** — cache-stampede-and-coalescing: Distributed lock safety. Adapter control flow checked; no production atomic publication client/failover/partition test. Async failover can lose a lock; ownership guards do not order database invalidations or guarantee latest returned values.
- **medium** — cache-change-log-and-own-writes: Historical remote markers. Primary paper explicitly permits stale-read risk from concurrent removal or marker eviction; added caveat. Historical distributed system not reproduced.
- **medium** — cache-cold-start-warming: Historical two-second warmup holdoff. Primary paper reread; delayed invalidations can still cause rare consistency issues. The timing safeguard is qualified as an operational trade-off.
- **medium** — glossary: Inherited unchanged glossary verification. 350 entry objects and their records remain unchanged;26 existing medium scores retained. This pass semantically reverified only the two corrected entries and cross-checked terms relevant to active lessons. Author’s additional236 glossary-source URL checks are inherited evidence, not claimed as independent semantic checks.

## system-design: Databases & Storage

[Independent verification record](../content/system-design/04-databases/verification.json)

Corrections and qualifications in this conversion:

- A text/integer comparison may error rather than silently force a cast; explain which cast preserves index use.
- InnoDB current writes do not invariably take gap locks; unique-key probes are a documented exception.
- SSI dependency tracking adds no blocking, but transactions can still wait on ordinary locks.
- The SSI/2PL comparison now refers specifically to plain read row locks.
- Physical WAL replication requires compatible formats; literal byte identity is too broad.
- Asynchronous replication specifies what acknowledgement waits for, not when transmission starts.
- remote_write requires the standby filesystem write rather than mere network receipt.
- The standby replay-delay budget is cumulative and is not a per-query timeout.
- State the fixed-membership, durability and non-concurrent assumptions before the quorum cards.
- A month can span many files or partitions; whole-file removal is an engine-specific retention strategy.
- The height/capacity estimate also needs the assumed leaf-key capacity and full occupancy.
- Key-value does not imply distributed; RocksDB is embedded.
- SQL traversal cost depends on branching and the chosen plan, rather than inevitably on depth alone.
- Do not imply Elasticsearch cannot read a just-written document by id.
- Removed an incorrect comment from a literal UPDATE; this statement has no old-value condition.
- The worked InnoDB read distinction includes the record-only locking exception.
- ALLOW FILTERING does not require reading every replica on every physical node.
- Clarify the filtering scope and avoid a universal every-node execution claim.
- Replica pinning needs a continuously advancing history and failover handling.
- Synchronous durability alone does not remove replay lag.
- The illustrative hash is not automatically stable when implemented with Python built-in string hash.
- Repeat the cumulative standby-delay caveat in the relevant question.
- Virtual-node transfers are not guaranteed equal across every old node.
- Virtual-node allocation reduces skew; it does not promise every node participates or perfect workload balance.
- Remove an unmeasured route-specific latency figure; the partition conflict already establishes the answer.
- Spanner quorum placement and latency are configuration-specific; unreachable quorum conflicts with every-region acceptance.
- Remove a universal RAM ceiling and explain the missing capacity/recovery evidence.
- A named store does not establish tested 200,000-write/s capacity.
- Remove an unsupported universal consensus-latency increment.
- Retain hardware-scale examples while marking their unmeasured, workload-dependent scope.
- Range work uses candidate runs; whole-key filters do not force every level to be read.
- Allocate three minutes to the dense explanation and code/caveats; naturally smaller units retain honest two-minute estimates.
- Allocate three minutes to the dense explanation and code/caveats; naturally smaller units retain honest two-minute estimates.
- Allocate three minutes to the dense explanation and code/caveats; naturally smaller units retain honest two-minute estimates.
- Allocate three minutes to the dense explanation and code/caveats; naturally smaller units retain honest two-minute estimates.
- Make durable local commit configuration explicit in the WAL-before-page question.
- Range scans merge candidate runs; bounds or other metadata can prune work.
- Qualify iterator work rather than requiring every file regardless of bounds.
- The SQL traversal cost model assumes an indexed nested-loop plan; other plans and pruning can differ.
- MySQL documentation explicitly says once-per-second flushing is not guaranteed.
- A composite index can be searched efficiently only on a leading part of its column list. An index on (a, b, c) serves conditions on a, or a and b, but not on b alone. → The conventional composite B-tree access rule: constraints on leading columns identify a contiguous index range. A predicate on a later column alone may require a broad scan, although skip scan can help when there are few distinct leading values.
- An index that contains every column a query needs, so the database can answer from the index alone without visiting the table. → An index containing every column needed by a query’s predicates, ordering and result, making an index-only access path possible. Engine visibility rules can still require table visits, such as PostgreSQL heap checks or InnoDB clustered-record checks.
- Heap-only tuple update: a Postgres optimisation where an UPDATE that changes no indexed column, and whose new version fits on the same page, needs no new index entries. Indexing the changed column prevents it. → PostgreSQL’s heap-only tuple optimisation: a new tuple version on the same heap page can avoid ordinary index entries when no column referenced by a non-summarising index changes. BRIN and other summarising indexes are an exception to that column-change restriction and may still need maintenance.
- Converting a value from one data type to another, such as text to integer. If a query forces a cast on an indexed column, the index on the raw column can no longer be used. → Converting a value from one data type to another, such as text to integer. Applying a cast to an indexed column can prevent an ordinary index seek; converting the query parameter to the column’s type can preserve it.
- A lock on every row that matches a condition, including rows that do not exist yet, which prevents phantoms. Real databases approximate it with index-range or next-key locks. → Tracking or protecting the set of rows matching a condition, including possible future rows. Lock-based serializable engines can use blocking key-range locks to prevent phantoms; PostgreSQL SSI instead uses non-blocking predicate markers to detect dependencies and abort unsafe executions.
- Postgres's built-in physical replication: the leader streams WAL records to standbys as they are written, and the standbys replay them byte for byte. → Postgres’s built-in physical replication: the primary streams WAL records as they are generated, and standbys replay the physical changes. Compatible server formats and major versions are required.
- Replicating by sending the raw storage-level log (such as Postgres WAL), so replicas are byte-identical. Leader and follower must run the same major version, and you cannot pick individual tables. → Replication by sending the raw storage-level log, such as PostgreSQL WAL, and replaying its physical changes on a compatible standby. PostgreSQL generally requires the same major version and compatible hardware architecture; physical replication covers the cluster rather than selected tables.
- A Postgres standby setting (30 s by default) for how long WAL replay may wait for a conflicting read query before cancelling it with "conflict with recovery". → A PostgreSQL standby setting, 30 seconds by default, that limits the total delay in applying WAL already received from the primary. Conflicting queries can be cancelled when that budget is exhausted; each query does not receive its own fresh 30-second allowance.
- B-tree fan-out prose, quiz and two card explanatory labels now use a precise local term instead of opening a messaging-fan-out definition; equations unchanged.
- Replaced atomic write/increment labels with direct SQL-increment wording so the glossary cannot open the pipe-writer non-interleaving definition.
- Storage examples and quiz use a new narrow storage-atomic-write term to distinguish all-or-nothing failure semantics from concurrent pipe writes.

Remaining gaps:

- No production benchmarks, storage-device crash tests, torn-page fault injection, watchdog/STONITH tests or cross-region partitions; no cloud DynamoDB, Aurora, InfluxDB or Elasticsearch deployment exercised.
- All lesson SQL/CQL/Cypher fences and relevant SQL question fragments were run with documented fixtures; statements with $1/$2 or <self> use declared substitutions. Retry code is a handler fragment with explicit application helpers, not a supplied library implementation.
- Cassandra and Redis checks use one-node fixtures. They verify syntax, ordering, rejection and key-slot behaviour, not replica repair, quorum failures, compaction workloads or cluster-scale latency.
- Major-version logical replication and tenant migration are documentation-reviewed workflows; complete cutover/failover deployments were not executed.
- Existing glossary confidence/source/alias records retained; 301 original definitions remain unchanged, eight corrected from fetched primary sources, two narrow new definitions checked. This split review does not claim a fresh per-entry fetch of all inherited glossary source pages.
- Six naturally small units are honestly estimated at two minutes; 31 units are 3–5 minutes. Every unit has its own completion id and 1–5 concept-matched questions.
- The ledger counts section/question/card review units, not every atomic factual assertion. Generic historical deployment anecdotes remain omitted and scenario throughput values remain illustrative.

Low-confidence areas:

- **medium** — db-schema-constraints: Inherited medium evidence scope. Primary-source core semantics and bounded fixtures checked; product/version/configuration choices and production/failure behaviour remain deployment-specific. No promotion of inherited medium confidence.
- **medium** — db-declarative-sql-joins: Inherited medium evidence scope. Primary-source core semantics and bounded fixtures checked; product/version/configuration choices and production/failure behaviour remain deployment-specific. No promotion of inherited medium confidence.
- **medium** — db-acid-transfer-guarantees: Inherited medium evidence scope. Primary-source core semantics and bounded fixtures checked; product/version/configuration choices and production/failure behaviour remain deployment-specific. No promotion of inherited medium confidence.
- **medium** — db-normalisation-read-models: Inherited medium evidence scope. Primary-source core semantics and bounded fixtures checked; product/version/configuration choices and production/failure behaviour remain deployment-specific. No promotion of inherited medium confidence.
- **medium** — db-key-value-access-durability: Inherited medium evidence scope. Primary-source core semantics and bounded fixtures checked; product/version/configuration choices and production/failure behaviour remain deployment-specific. No promotion of inherited medium confidence.
- **medium** — db-document-aggregate-bounds: Inherited medium evidence scope. Primary-source core semantics and bounded fixtures checked; product/version/configuration choices and production/failure behaviour remain deployment-specific. No promotion of inherited medium confidence.
- **medium** — db-wide-column-query-buckets: Inherited medium evidence scope. Primary-source core semantics and bounded fixtures checked; product/version/configuration choices and production/failure behaviour remain deployment-specific. No promotion of inherited medium confidence.
- **medium** — db-graph-traversal-locality: Inherited medium evidence scope. Primary-source core semantics and bounded fixtures checked; product/version/configuration choices and production/failure behaviour remain deployment-specific. No promotion of inherited medium confidence.
- **medium** — db-time-series-retention-cardinality: Inherited medium evidence scope. Primary-source core semantics and bounded fixtures checked; product/version/configuration choices and production/failure behaviour remain deployment-specific. No promotion of inherited medium confidence.
- **medium** — db-search-refresh-family-fit: Inherited medium evidence scope. Primary-source core semantics and bounded fixtures checked; product/version/configuration choices and production/failure behaviour remain deployment-specific. No promotion of inherited medium confidence.
- **medium** — db-index-scan-budgets: Inherited medium evidence scope. Primary-source core semantics and bounded fixtures checked; product/version/configuration choices and production/failure behaviour remain deployment-specific. No promotion of inherited medium confidence.
- **medium** — db-btree-clustered-layout: Inherited medium evidence scope. Primary-source core semantics and bounded fixtures checked; product/version/configuration choices and production/failure behaviour remain deployment-specific. No promotion of inherited medium confidence.
- **medium** — db-lsm-buffer-flush-compaction: Inherited medium evidence scope. Primary-source core semantics and bounded fixtures checked; product/version/configuration choices and production/failure behaviour remain deployment-specific. No promotion of inherited medium confidence.
- **medium** — db-composite-covering-indexes: Inherited medium evidence scope. Primary-source core semantics and bounded fixtures checked; product/version/configuration choices and production/failure behaviour remain deployment-specific. No promotion of inherited medium confidence.
- **medium** — db-index-maintenance-plans: Inherited medium evidence scope. Primary-source core semantics and bounded fixtures checked; product/version/configuration choices and production/failure behaviour remain deployment-specific. No promotion of inherited medium confidence.
- **medium** — db-isolation-anomaly-traces: Inherited medium evidence scope. Primary-source core semantics and bounded fixtures checked; product/version/configuration choices and production/failure behaviour remain deployment-specific. No promotion of inherited medium confidence.
- **medium** — db-isolation-engine-differences: Inherited medium evidence scope. Primary-source core semantics and bounded fixtures checked; product/version/configuration choices and production/failure behaviour remain deployment-specific. No promotion of inherited medium confidence.
- **medium** — db-mvcc-snapshot-conflicts: Inherited medium evidence scope. Primary-source core semantics and bounded fixtures checked; product/version/configuration choices and production/failure behaviour remain deployment-specific. No promotion of inherited medium confidence.
- **medium** — db-row-locks-race-fixes: Inherited medium evidence scope. Primary-source core semantics and bounded fixtures checked; product/version/configuration choices and production/failure behaviour remain deployment-specific. No promotion of inherited medium confidence.
- **medium** — db-ssi-whole-transaction-retries: Inherited medium evidence scope. Primary-source core semantics and bounded fixtures checked; product/version/configuration choices and production/failure behaviour remain deployment-specific. No promotion of inherited medium confidence.
- **medium** — db-leader-replication-acknowledgements: Inherited medium evidence scope. Primary-source core semantics and bounded fixtures checked; product/version/configuration choices and production/failure behaviour remain deployment-specific. No promotion of inherited medium confidence.
- **medium** — db-replica-lag-read-guarantees: Inherited medium evidence scope. Primary-source core semantics and bounded fixtures checked; product/version/configuration choices and production/failure behaviour remain deployment-specific. No promotion of inherited medium confidence.
- **medium** — db-failover-fencing-history: Inherited medium evidence scope. Primary-source core semantics and bounded fixtures checked; product/version/configuration choices and production/failure behaviour remain deployment-specific. No promotion of inherited medium confidence.
- **medium** — db-multi-leader-conflict-resolution: Inherited medium evidence scope. Primary-source core semantics and bounded fixtures checked; product/version/configuration choices and production/failure behaviour remain deployment-specific. No promotion of inherited medium confidence.
- **medium** — db-leaderless-quorums-repair: Inherited medium evidence scope. Primary-source core semantics and bounded fixtures checked; product/version/configuration choices and production/failure behaviour remain deployment-specific. No promotion of inherited medium confidence.
- **medium** — db-range-hash-placement: Inherited medium evidence scope. Primary-source core semantics and bounded fixtures checked; product/version/configuration choices and production/failure behaviour remain deployment-specific. No promotion of inherited medium confidence.
- **medium** — db-consistent-hash-hot-keys: Inherited medium evidence scope. Primary-source core semantics and bounded fixtures checked; product/version/configuration choices and production/failure behaviour remain deployment-specific. No promotion of inherited medium confidence.
- **medium** — db-sharded-secondary-indexes: Inherited medium evidence scope. Primary-source core semantics and bounded fixtures checked; product/version/configuration choices and production/failure behaviour remain deployment-specific. No promotion of inherited medium confidence.
- **medium** — db-rebalancing-tenant-cutovers: Inherited medium evidence scope. Primary-source core semantics and bounded fixtures checked; product/version/configuration choices and production/failure behaviour remain deployment-specific. No promotion of inherited medium confidence.
- **medium** — db-database-access-pattern-fit: Inherited medium evidence scope. Primary-source core semantics and bounded fixtures checked; product/version/configuration choices and production/failure behaviour remain deployment-specific. No promotion of inherited medium confidence.
- **medium** — db-scale-operational-budget: Inherited medium evidence scope. Primary-source core semantics and bounded fixtures checked; product/version/configuration choices and production/failure behaviour remain deployment-specific. No promotion of inherited medium confidence.
- **medium** — db-polyglot-outbox-handoff: Inherited medium evidence scope. Primary-source core semantics and bounded fixtures checked; product/version/configuration choices and production/failure behaviour remain deployment-specific. No promotion of inherited medium confidence.
- **medium** — db-pages-wal-crash-recovery: Inherited medium evidence scope. Primary-source core semantics and bounded fixtures checked; product/version/configuration choices and production/failure behaviour remain deployment-specific. No promotion of inherited medium confidence.
- **medium** — db-lsm-compaction-strategies: Inherited medium evidence scope. Primary-source core semantics and bounded fixtures checked; product/version/configuration choices and production/failure behaviour remain deployment-specific. No promotion of inherited medium confidence.
- **medium** — db-storage-amplification-accounting: Inherited medium evidence scope. Primary-source core semantics and bounded fixtures checked; product/version/configuration choices and production/failure behaviour remain deployment-specific. No promotion of inherited medium confidence.
- **medium** — db-bloom-filter-candidate-checks: Inherited medium evidence scope. Primary-source core semantics and bounded fixtures checked; product/version/configuration choices and production/failure behaviour remain deployment-specific. No promotion of inherited medium confidence.
- **medium** — db-column-store-analytical-work: Inherited medium evidence scope. Primary-source core semantics and bounded fixtures checked; product/version/configuration choices and production/failure behaviour remain deployment-specific. No promotion of inherited medium confidence.
- **medium** — db-pages-wal-crash-recovery: Indicative SSD/HDD IOPS and hardware throughput figures. Retained as explicitly indicative examples, not measurements from this review; selected device, queue depth, cache and workload determine results.
- **medium** — db-lsm-compaction-strategies: Roughly 90% last-level share. Fetched RocksDB primary documentation supports dynamic targeting; static or underfilled levels, L0, retained versions and workload can change the share. Conditional caveat retained.
- **medium** — glossary: innodb-flush-log confidence provenance. Original medium record retained without upgrading. This pass fetched the primary MySQL manual and checked values 0/1/2, including the non-guaranteed approximate one-second flush interval; this does not test physical crash behaviour.
- **medium** — glossary: resume-driven-development. Inherited informal industry term with no authoritative formal standard; original confidence and source retained.
- **medium** — glossary: io-optimized pricing description. Inherited pricing/configuration description remains time-sensitive; no current regional price comparison or billing benchmark performed.

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
