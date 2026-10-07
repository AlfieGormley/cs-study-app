exec(open('/tmp/cs-study-audit-2026-10-04/fix-root.py').read().split("go=['https:")[0])
p_report=Path('docs/audit-theory-automata.json');report=json.loads(p_report.read_text());findings=report['findings'];b='content/theory/04-automata/'
src=['https://swtch.com/~rsc/regexp/regexp1.html','https://swtch.com/~rsc/regexp/regexp3.html','https://www.pcre.org/current/doc/html/pcre2matching.html','https://github.com/google/re2','https://docs.rs/regex/latest/regex/','https://pkg.go.dev/regexp','https://docs.python.org/3/library/re.html','https://v8.dev/blog/non-backtracking-regexp','https://blog.cloudflare.com/details-of-the-cloudflare-outage-on-july-2-2019/','https://www.ruby-lang.org/en/news/2022/12/25/ruby-3-2-0-released/']
p=Path(b+'auto-regex-engines.md');old=p.read_text();s=old
start=s.index('Two regex engines can');end=s.index('## How backtracking works')
s=s[:start]+'''Two engines can recognize the same language while doing very different amounts of work. A path-enumerating backtracker can revisit the same state and input position exponentially many times; a set-based simulation merges those repeated situations.

## Matching strategies and guarantees

| Strategy | Idea | Important limit |
|---|---|---|
| Unmemoized backtracking | Try choices depth-first and revisit alternatives after failure | Ambiguous patterns can take exponential time |
| Thompson/Pike simulation | Merge equivalent active states at each input position | Bounded-out-degree machines use O(m·(n + 1)) work |
| Lazy DFA | Cache sets of active states and their transitions | Full determinisation can require exponentially many states |

Here m is compiled pattern size, including expansions such as counted repetition, and n is input length. For a fixed pattern, a documented O(m·n) single-search guarantee is linear in input size.

Production libraries combine strategies. Python re, Java's standard engine and default PCRE2 matching use backtracking; RE2, Go regexp and Rust regex provide input-linear single-search guarantees for their supported syntax. A bounded memoized backtracking implementation can also avoid repeated state/position work. Ruby 3.2 added memoization for many patterns; PCRE2 has a separate DFA-style API; GNU grep chooses methods according to options and syntax. Engine names alone do not specify every mode's behavior.

''' +s[end:]
start=s.index('When there is a match,');end=s.index('### Why it explodes')
s=s[:start]+'''This teaching function requires a supplied delta and accepting state. It has no memoization, recursion limit handling or epsilon-cycle guard; do not use it as a production matcher. A successful path may be found early, but other patterns can do extensive work before eventually succeeding. Failure may require exploring all remaining choices.

> [!note] Evidence gap
> Previous exact call counts and laptop timings are omitted: the original machine fixture and reproducible benchmark configuration were unavailable. The following combinatorial analysis explains growth without claiming measured runtime.

'''+s[end:]
start=s.index('## Measured in Python');end=s.index('## The danger patterns')
s=s[:start]+'''## Growth without a timing claim

For a path-enumerating matcher without memoization or simplifying optimizations, (a|aa)* on a failing run has Fibonacci-many decompositions: the first part has length one or two. This grows asymptotically by a factor approaching 1.618 per additional a. It is a count of possible decompositions, not an exact CPU-instruction count or a universal runtime prediction.

'''+s[end:]
start=s.index('- `\\s+$` used');end=s.index('> [!example] Cloudflare')
s=s[:start]+'''- An unoptimized search for \\s+$ on n spaces followed by x can try n starting positions. Scanning the remaining spaces at each position produces a triangular sum n + (n−1) + … + 1, hence quadratic work. Actual engine optimizations and constants determine runtime.

## Real outage

> [!note] Evidence gap
> Detailed Stack Overflow outage timings and remediation claims are omitted because its original postmortem could not be retrieved during this review. This is a source-access limitation, not evidence that the event did not happen.

'''+s[end:]
s=s.replace("RE2 (Google, 2010), Go's `regexp` and Rust's `regex` never search paths individually.", "RE2, Go regexp and Rust regex prevent unrestricted repeated exploration for their supported single searches. Implementations can combine several methods, including bounded memoized path exploration.")
s=s.replace('Most characters then cost one table lookup.', 'A cached transition can be followed with a table lookup; the hit rate is workload-dependent.')
s=s.replace('These match non-regular languages;', 'General backreferences can express non-regular languages, although individual backreference patterns can still be regular;')
s=s.replace('Matching with backreferences is NP-complete in general, so no linear-time engine can support them.', 'General backreferences cannot be implemented by ordinary finite automata. This does not mean every individual backreference pattern is slow or non-regular.')
s=s.replace('**Atomic groups and possessive quantifiers** have no meaning without backtracking.', '**Atomic groups and possessive quantifiers** can change which strings match. They have meaning beyond a particular execution algorithm: PCRE2’s DFA-style matcher supports them with documented semantics. RE2, Go and Rust regex omit this syntax.')
s=s.replace('V8 has an experimental linear engine (`--enable-experimental-regexp-engine` and the `/l` flag).', 'V8 described an experimental linear engine and /l flag in a 2021 article; availability depends on runtime version and build flags, so this is not a portable JavaScript feature. Bound pattern size, compilation resources and input volume even with linear matching.')
s=s.replace('matches the same strings as', 'has the same full-match language as')
s=s.replace('On 22 a\'s and a `!`, Python takes about 0.15 s on the first and microseconds on the second.', 'Captured-group results can differ. Unanchored searches also need separate complexity analysis.')
s=s.replace('fail instantly on the input that made `(a+)+$` take a second, because the engine is forbidden to give back characters.', 'eliminate that nested pattern’s repeated splitting because the inner group cannot give back characters. Atomicity does not make every surrounding search safe and can change accepted input.')
s=s.replace('20,000 spaces cannot reach a regex that only sees the first 200 characters.', 'Reject overlong values rather than validating only a truncated prefix: truncation can hide an invalid suffix.')
s=s.replace('isolate risky matching in a worker with a deadline.', 'use a killable process or an execution boundary that actually stops the work on deadline. Timing out a waiting thread does not necessarily stop the underlying match.')
s=s.replace('Lesson 4 showed it cannot be done correctly; attempts with recursion or long alternations are where catastrophic patterns breed.', 'Formal regular expressions cannot recognize arbitrary nesting. Bounded nesting and richer engine features are different cases; use a suitable parser for general structured formats.')
s=s.replace('This covers most application code.', 'Check the chosen implementation, input limits and required features; developer-authored patterns can also be vulnerable.')
s=s.replace('when latency must be predictable.', 'when predictable scaling matters. This still requires resource limits and workload testing.')
s=s.replace('- Failure is the slow case: `(a+)+$` doubles in cost per character on non-matching input but is instant on matching input.', '- Long almost-matching failures expose many vulnerabilities; success can also require substantial backtracking in other patterns.')
s=s.replace('- Nested quantifiers, overlapping alternatives and adjacent overlapping quantifiers cause ReDoS; `\\s+$` with search is quadratic.', '- Ambiguous repetition can cause excessive work in path-enumerating engines. A naive repeated-start search for \\s+$ has quadratic work on a failing whitespace run.')
s=s.replace('- Stack Overflow (2016, 34 minutes) and Cloudflare (2019, 27 minutes) were both taken down by regex backtracking.', '- Cloudflare’s primary postmortem documents a 27-minute regex-related outage in July2019.')
s=s.replace('- [Outage postmortem, July 20, 2016 — Stack Exchange status](https://stackstatus.tumblr.com/post/147710624694/outage-postmortem-july-20-2016)\n','')
assert s!=old;p.write_text(s)
findings.append({'files':[str(p)],'reason':'Replace unsupported benchmark tables with combinatorial analysis; correct engine families, atomic semantics, resource limits, truncation and timeout advice; mark unavailable outage evidence.','sources':src,'confidence':'medium'})
def regex(q):
 q[0]['prompt']=q[0]['prompt'].replace('* 30','* 12')
 q[0]['options'][0]['explanation']='With12 a characters and nothing else, the first greedy attempt succeeds.'
 q[0]['options'][1]['explanation']='Correct. The failing suffix forces repeated attempts; the12 a characters have2¹¹ possible nonempty-block decompositions. No fixed wall-clock time is claimed.'
 q[0]['workedExample']='A succeeds on its first greedy attempt. B fails after exploring ambiguous splits;12 characters have2¹¹ decompositions into positive-length blocks. C and D fail immediately. The smaller runnable example illustrates the behavior without requiring an expensive30-character failing match. Successful matches in other patterns can also require extensive backtracking.'
 q[1]['prompt']+=' Consider a single search with a fixed pattern and the standard APIs listed.'
 q[1]['workedExample']='Go regexp documents a bound linear in input length. Python re, Java’s standard matcher and PCRE’s default matcher do not offer that general guarantee. Production libraries can mix methods; PCRE2 also offers a separate DFA-style matcher, and recent Ruby versions memoize many patterns.'
 q[2]['options'][1]['text']='This particular backreference pattern describes a non-regular language outside RE2’s supported syntax'
 q[2]['options'][1]['explanation']='Correct. Arbitrarily long word-copy matching here exceeds finite-automaton expressiveness. Not every pattern containing a backreference is non-regular.'
 q[2]['options'][3]['explanation']='RE2 accepts many regular patterns that would cause excessive backtracking elsewhere. It excludes backreference syntax; its matching guarantee does not remove all resource-exhaustion risks.'
 q[2]['workedExample']=q[2]['workedExample'].replace("Supporting it would break RE2's linear-time guarantee, so RE2 leaves it out.", 'Ordinary finite automata cannot recognize this language, and RE2 excludes this syntax.').replace('Backtracking engines can test primality; finite automata cannot.', 'This pattern recognizes composite unary lengths, not primes; rejecting it does not by itself classify0 and1 as prime. A finite automaton cannot recognize the unbounded composite-length language.')
 q[3]['prompt']=q[3]['prompt'].replace('tries `(a+)+` against', 'requires a full-string match of `(a+)+` against')
 q[4]['prompt']='Suppose a benchmark of re.search(r"\\s+$", s) takes0.23seconds for10,000spaces followed by x. Assuming quadratic scaling with negligible fixed overhead, roughly how long for40,000spaces followed by x? This is hypothetical data, not a measured runtime claim.'
 q[4]['workedExample']='A naive search starts at each space and revisits remaining spaces, producing a triangular work sum. Under the explicitly assumed quadratic timing model, multiplying input length by4 multiplies time by16:0.23×16=3.68seconds, or about3.7seconds. Actual measurements depend on engine, optimization and hardware.'
 q[4]['link']={'title':'Regular expression matching — Russ Cox','url':src[0]}
 q[5]['prompt']='In an anchored, path-enumerating backtracker without memoization or pattern simplification, which patterns have exponentially many ambiguous paths on a run of a characters followed by !? Select all that apply.'
 q[5]['workedExample']='The nested quantifiers in (a+)+ and (\\w+\\s?)* allow2ⁿ⁻¹ complete decompositions of the a run. Duplicate alternatives in (a|a)* allow2ⁿ branch sequences. The single-run a+ and mandatory-separator rewrite do not have that exponential ambiguity. These are conceptual path counts, not measured timings; optimizations may collapse duplicate alternatives.'
 q[6]['options'][0]['explanation']='A bounded cache prevents unlimited DFA-cache growth. It does not guarantee that the entire application can never exhaust memory.'
 q[6]['options'][1]['text']='It falls back to unrestricted, unmemoized backtracking'
 q[6]['options'][1]['explanation']='That would lose the guarantee. Bounded memoized backtracking is a different technique that RE2 can use for suitable searches.'
 q[6]['workedExample']=q[6]['workedExample'].replace('Usually only a few hundred distinct sets occur, so the cache gives near-DFA speed.', 'Cached transitions are cheap when reused; distinct-set count depends on the pattern and input.')
 q[7]['prompt']+=' Compare full-match acceptance, not capture contents.'
 q[7]['options'][1]['explanation']='Correct. (\\w+\\s)*\\w* preserves full-match acceptance, including empty and trailing-whitespace cases; captured groups can differ.'
 q[7]['options'][3]['explanation']='The mandatory separator removes this nested ambiguity, but the rewrite accepts a different language. Do not infer a universal safety guarantee for every search mode.'
 q[7]['workedExample']=q[7]['workedExample'].replace('confirms `(\\w+\\s)*\\w*` is exactly equivalent to the original.', 'supports the full-match equivalence on that finite set. The general argument groups each non-final word with its following whitespace; capture results are not claimed equivalent.')
 q[8]['workedExample']=q[8]['workedExample'].replace('That is exactly why atomic groups cure ReDoS:', 'This is how atomic groups remove this particular repeated-splitting problem:')
 q[9]['prompt']='A hypothetical benchmark gives1ms,7ms and47ms when input length doubles from200to400to800. Which proposed scaling model is most consistent with those three measurements? These illustrative data are not a verified Cloudflare or Python benchmark.'
 q[9]['options'][2]['explanation']='Three timings cannot rule out every exponential model, but among these coarse candidate descriptions, roughly cubic growth best fits the observed doubling ratios.'
 q[9]['options'][3]['explanation']='Correct among the proposed models: ratios7 and47/7≈6.7 are closer to8 than to2 or4. More evidence is needed to establish asymptotic complexity.'
 q[9]['workedExample']='The observed ratios are7 andabout6.7. Cubic scaling predicts2³=8 per input doubling, so it is the closest proposed model, not a proof. Separately, a naive unanchored search for .*.*=.*; on x= followed by a long x suffix can take cubic work: at starts after the only equals sign, two leading stars try a quadratic number of allocations before failing to find =; summing over starts gives cubic work. Exact engine optimizations can alter observed behavior.'
 q[10]['options'][0]['explanation']+=' Also bound compiled pattern size and total work.'
 q[10]['options'][2]['text']='An existing full-match operation requiring (\\w+)=\\1 on explicitly bounded, vetted local input, without rewriting the operation'
 q[10]['options'][2]['explanation']='The listed engines reject backreferences. Use a suitably constrained supporting engine, or redesign as capture plus an ordinary equality check. Source files are not automatically trusted, especially from external contributions.'
 q[10]['workedExample']='For untrusted or large workloads, documented scaling guarantees are useful alongside input, pattern and compilation budgets. RE2, Go regexp and Rust regex reject the listed backreference. A supporting engine or capture-and-compare redesign is needed. Lookaround is not exclusive to backtracking: PCRE2’s separate DFA-style matcher supports it.'
 q[11]['prompt']+=' Assume full-string matching by a path-enumerating implementation without memoization or simplifying optimizations.'
 q[11]['workedExample']=q[11]['workedExample'].split('4. W(30)')[0]+'4. W(30)=1,346,269. These are decomposition counts, not measured timings.\n\nThis overlap produces exponential path counts in the assumed matcher; it is not a theorem that every overlap defeats every optimized engine.'
questions(b+'auto-regex-engines.questions.json',regex,'Correct unsupported measurements, full-match premises, blanket security claims and engine feature explanations; keep answer indices stable.',src)
report['omissions'] += [{'lesson':'auto-regex-engines','claim':'Exact laptop timings, NFA work table and Stack Overflow outage details','reason':'No reproducible benchmark fixture supplied; original Stack postmortem inaccessible via web and curl (403). Replaced with explicit evidence-gap notes, theoretical counts and hypothetical timing exercise.'}]
report['status']='All six lesson and72question pairs corrected; execution and independent review pending.'
p_report.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
