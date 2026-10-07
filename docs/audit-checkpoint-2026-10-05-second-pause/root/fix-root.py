from pathlib import Path
import json
findings=[]
def patch(path,changes,reason,sources):
 p=Path(path);s=p.read_text();before=s
 for a,b in changes:
  if a not in s: raise ValueError((path,a[:100]))
  s=s.replace(a,b)
 p.write_text(s)
 findings.append(dict(files=[path],reason=reason,corrections=[{'before':a,'after':b} for a,b in changes],sources=sources,confidence='high'))
def questions(path,edit,reason,sources):
 p=Path(path);q=json.loads(p.read_text());before=json.loads(p.read_text());edit(q);p.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n')
 findings.append(dict(files=[path],reason=reason,changed_question_ids=[b['id'] for a,b in zip(before,q) if a!=b],sources=sources,confidence='high'))
go=['https://go.dev/doc/gc-guide']
zgc=['https://docs.oracle.com/en/java/javase/24/migrate/significant-changes-jdk-24.html','https://inside.java/2023/11/28/gen-zgc-explainer/']
patch('content/languages/03-memory-management/gc-modern.md',[
('**Parallel** means several GC threads work at once, but the application is paused.', '**Parallel** means several GC threads work at once. That work may be stop-the-world or concurrent; the JVM collector named Parallel GC is stop-the-world.'),
('The result is that pauses do not grow with the heap or the live set. ZGC targets pauses under a millisecond on heaps up to 16 TB. Since JDK 21 it is also **generational** (JEP 439), which made it far better at handling high allocation rates; from JDK 23 that became its default mode.', 'ZGC is designed for very short pauses that do not scale with heap size; this is a design goal, not a latency guarantee for your service. Generational ZGC arrived in JDK 21, became the default ZGC mode in JDK 23, and the non-generational mode was removed in JDK 24. Generational ZGC uses **store barriers as well as load barriers**; the simplified load-barrier description above explains concurrent relocation, not its entire barrier design.'),
("After a cycle, the next one starts when the heap has grown by `GOGC`% of the live heap:","Ignoring roots for a moment, `GOGC` sets a heap-size **goal** based on growth since the last live-heap measurement. The pacer starts collection before reaching that goal so concurrent marking has time to finish:"),
('(Since Go 1.18 the calculation also counts goroutine stacks and globals, but the idea is the same.)', '(Since Go 1.18 the formula is live heap + (live heap + GC roots) × GOGC/100; roots include scannable stacks and globals. The examples above neglect roots.)'),
('as the total approaches it', 'as Go-runtime-managed memory approaches it'),
('so the process collects harder instead of being killed by the OOM killer', 'to leave headroom for memory outside the runtime; this soft limit cannot guarantee avoidance of an OOM kill'),
("keeping pauses under a millisecond whatever the heap size.","targeting very short pauses without guaranteeing a particular application latency.")], 'Correct parallel/concurrent terminology, outdated ZGC mode/barrier coverage and a heap goal incorrectly described as the GC start threshold; qualify latency and OOM guarantees.',go+zgc)
def fixgc(q):
 q[0]['options'][3]['text']='Parallel means multiple GC threads work at once; concurrent means GC work overlaps application execution'
 q[0]['options'][3]['explanation']='These are independent properties. A concurrent collector may also use parallel workers; the JVM collector named Parallel GC uses stop-the-world collection.'
 q[2]['prompt']='A Go service has 300 MB of live heap and GOGC=100. Ignoring GC roots and a binding memory limit, what is its approximate heap-size goal (not the collection-start threshold)?'
 q[2]['options'][0]['explanation']='The goal includes an allocation allowance in addition to the measured live heap.'
 q[2]['workedExample']=q[2]['workedExample'].replace('So the program can allocate about 300 MB of new objects before the next cycle.', 'This gives a 300 MB allocation allowance in the simplified model. The pacer starts marking before the goal; the goal is not the trigger threshold.')
 q[5]['options'][0]['text']='ZGC targets much shorter pauses through concurrent relocation, but CPU costs and required headroom must be measured'
 q[5]['options'][0]['explanation']='This is a design trade-off, not a guarantee of sub-millisecond application latency or a fixed throughput penalty.'
 q[5]['workedExample']='1. G1 evacuates young and mixed collection sets during pauses.\n2. ZGC relocates concurrently and targets very short pauses.\n3. Generational ZGC uses load and store barriers.\n4. Measure CPU cost, allocation stalls and tail latency on the actual workload; a collector choice does not guarantee an SLO.'
 q[6]['options'][4]['explanation']='GOGC sets the heap growth goal; the pacer starts earlier. GOMEMLIMIT is a soft limit on memory managed by the Go runtime, not on all process memory.'
 q[8]['prompt']='A Go service has a 2 GiB container limit, and live heap can grow from 600 MiB to 1.2 GiB. Measurements show little memory outside the Go runtime. Which is a reasonable configuration to test, rather than a guaranteed OOM fix?'
 q[8]['options'][2]['explanation']='A soft runtime memory limit below the container limit can restrain growth, but headroom must cover memory the runtime does not track. It can still exceed its soft limit.'
 q[8]['workedExample']='1. Ignoring roots, 600 MiB live gives a 1200 MiB heap goal at GOGC=100.\n2. A 1.2 GiB live heap gives a 2.4 GiB goal, beyond the container limit.\n3. For example, GOMEMLIMIT=1800MiB (about 1.76 GiB) lowers the runtime memory budget; measure the margin required by this process.\n4. The budget includes runtime-managed stacks and metadata, but excludes C allocations and other untracked memory.\n5. It is soft: under GC pressure the runtime can exceed it, so it does not guarantee avoidance of an OOM kill.'
 q[9]['options'][2]['explanation']='ZGC still marks objects. Generational ZGC also uses store barriers; load barriers are not its only barrier mechanism.'
 q[9]['workedExample']+='\n\nThis explanation focuses on relocation. Modern generational ZGC also uses store barriers for marking and remembered-set work.'
 q[10]['options'][1]['explanation']='G1 is a reasonable baseline to measure. Its 200 ms soft pause goal does not guarantee a 200 ms request latency budget.'
 q[10]['options'][2]['explanation']='ZGC is a reasonable candidate because it targets low pause times with concurrent relocation. Benchmark it: the collector cannot guarantee a 2 ms p99.9 end-to-end latency.'
questions('content/languages/03-memory-management/gc-modern.questions.json',fixgc,'Align quiz with corrected Go pacing, memory accounting, parallelism and ZGC guarantees.',go+zgc)
inf=['https://arxiv.org/abs/2211.17192','https://arxiv.org/abs/2309.06180','https://huggingface.co/docs/transformers/kv_cache']
patch('content/ml/04-transformers-llms/llm-inference.md',[
('so it is mostly **compute-bound**. It determines', 'so it is often **compute-bound** for sufficiently long prompts. It strongly influences'),
('Each step must read every weight in the model to do a small amount of maths for one token per sequence, so it is **memory-bandwidth-bound**.', 'For a dense model at small batch size, reading its active weights often makes this phase **memory-bandwidth-bound**. Large batches, long-context attention, sparse architectures and hardware choices can change the bottleneck.'),
('So a single sequence cannot decode faster than about 150 tokens per second, however many FLOPs the chip has.', 'This gives about 150 tokens per second as an idealised bandwidth ceiling when each ordinary dense decode step reads that weight volume from device memory. It excludes speculative decoding, compression, cached weights and multi-device execution.'),
('Throughput rises almost linearly with batch size until compute or memory runs out.', 'Batching can improve throughput by sharing weight reads, but scaling also depends on attention work, cache traffic, scheduling and kernel efficiency; measure it rather than assuming linear growth.'),
('**Beam search** keeps the b most likely partial sequences. It suits tasks with one right answer (translation, speech recognition) but makes open-ended text bland, and it multiplies cost by b.', '**Beam search** keeps a bounded set of promising partial sequences under a scoring rule. It is often used for translation and speech recognition, which can have multiple valid outputs. Wider beams increase work and memory; the exact cost depends on batching, pruning and cache sharing, and a wider beam does not guarantee a better answer.'),
('Decode is memory-bound, so verifying several tokens in one forward pass costs about the same as generating one.', 'When decode is bandwidth-bound and spare compute is available, verifying several proposed tokens in one pass can cost less than generating them in separate passes. The benefit depends on proposal length, acceptance rate, context, batching and hardware.'),
('at the first rejection, a corrected token is sampled from the target and the rest discarded.', 'at the first rejection, a token is sampled from the normalised positive part of (target probabilities − draft probabilities), and later proposals are discarded. If all proposals are accepted, the target supplies a bonus token.'),
('- Prefill is compute-bound; decode is memory-bandwidth-bound, so batching is the main lever for throughput.', '- Prefill often has higher arithmetic intensity; dense-model decode at small batch is often bandwidth-bound. Measure the bottleneck and the throughput/latency trade-off of batching.')], 'Bound performance claims to their assumptions, correct beam-search framing and specify the necessary residual distribution for exact speculative sampling.',inf)
def fixinf(q):
 q[2]['prompt']='For a dense autoregressive transformer with a long prompt and small decode batch, what is a common inference bottleneck pattern?'
 q[2]['options'][3]['explanation']='Prefill can reuse weights across many prompt tokens. Small-batch dense decode often has low arithmetic intensity. These are common regimes, not universal guarantees.'
 q[6]['prompt']='A dense 13-billion-parameter FP16 model reads all its weights from device memory once per ordinary decode step at batch size 1. With 2 TB/s memory bandwidth, ignoring all other costs, what is its bandwidth ceiling?'
 q[7]['workedExample']=q[7]['workedExample'].replace('Decode reads all weights each step, so fewer bytes → faster.', 'In bandwidth-bound dense decoding, fewer weight bytes can help; speed also depends on kernels, dequantisation and other memory traffic.')
 q[11]['options'][0]['explanation']='Parallel verification can amortise target weight reads when spare compute is available; its cost is not universally equal to one decode step.'
 q[11]['workedExample']=q[11]['workedExample'].replace('Decode is bandwidth-bound: reading the target\'s weights dominates, whether you score 1 position or 5.', 'In a bandwidth-bound serving regime, scoring several positions together can amortise target weight reads; the actual cost is workload-dependent.').replace('with identical outputs.', 'with the same output distribution, not necessarily the same sampled token sequence.')
questions('content/ml/04-transformers-llms/llm-inference.questions.json',fixinf,'Make quiz assumptions explicit and distinguish equal sampling distributions from identical generated outputs.',inf)
Path('docs/audit-root.json').write_text(json.dumps({'date':'2026-10-04','reviewed_files':['content/languages/03-memory-management/gc-modern.md','content/languages/03-memory-management/gc-modern.questions.json','content/ml/04-transformers-llms/llm-inference.md','content/ml/04-transformers-llms/llm-inference.questions.json'],'findings':findings,'limitations':['Focused semantic review; other root-owned subjects remain under review. No universal guarantee that every factual statement is externally verified.']},indent=2)+'\n')
