exec(open('/tmp/cs-study-audit-2026-10-04/fix-root.py').read().split("go=['https:")[0])
report=json.loads(Path('docs/audit-root.json').read_text());findings=report['findings']
h=['https://raw.githubusercontent.com/openjdk/jdk/jdk-21%2B35/src/java.base/share/classes/java/util/HashMap.java','https://raw.githubusercontent.com/python/cpython/v3.14.0/Objects/dictobject.c','https://go.dev/blog/swisstable','https://abseil.io/about/design/swisstables']
p='content/dsa/03-hashing/hash-resizing'
patch(p+'.md',[
('changing m changes almost every key\'s bucket','changing m can change a key\'s bucket (doubling moves about half under uniform hashing)'),
('Count the copying work for n inserts into a table that starts with one slot and doubles when full:', 'Count the copying work for n inserts into a table that starts with one slot and doubles when full. First assume n is a power of two:'),
('Fewer than n copies in total, plus n ordinary inserts, makes fewer than 2n units of work: O(1) per insert on average. This is **amortised** O(1): a guarantee about any sequence of operations, not about each one.', 'For powers of two this is fewer than n copies. For arbitrary n, the last copied capacity can exceed n/2, but the total is still fewer than 2n copies, or fewer than 3n units including placements. Thus **resizing overhead** is amortised O(1) per insert for every sequence. Overall hash-table insertion also depends on collision costs: the usual bound is expected amortised O(1), assuming well-distributed hashes and constant-time key operations.'),
('Rehashing a 10-million-key table can take tens or hundreds of milliseconds, which a latency-sensitive server notices.', 'The pause depends on the implementation, key count, allocator and hardware; measure it against the server\'s latency budget.'),
('briefly, twice the memory', 'temporarily retaining both bucket arrays (m + 2m buckets when doubling, excluding entries and other overhead)'),
('There are two arrays:', 'The simplified description below covers an ordinary combined table with general keys. Split/key-sharing tables and Unicode-only entries have different layouts. There are two arrays:'),
('The space is only reclaimed on the next resize.', 'A rebuild compacts empty entries. In GIL-enabled builds a later insertion can reuse a dummy index slot; free-threaded builds avoid that reuse for lookup safety.'),
('When a bucket\'s chain reaches **8** entries (`TREEIFY_THRESHOLD`), it is converted into a red–black tree, so lookups in it are O(log n) rather than O(n). Two conditions apply:', 'In OpenJDK 21, ordinary `put` invokes treeification when adding a ninth node to a chain of eight (`TREEIFY_THRESHOLD` is 8). Other insertion paths can reach the threshold differently. A tree bin gives logarithmic lookup when hashes or a consistent comparable-key order distinguish keys. Two conditions apply:'),
('with random hash codes and α ≈ 0.75', 'with random hash codes and a default maximum load factor of 0.75'),
('The probability of a bucket reaching 8 entries is about 0.00000006.', 'Under that approximate model, the probability of exactly 8 entries is about 0.00000006; this is not a measured treeification rate.'),
('Growing by a constant factor makes inserts amortised O(1); growing by a constant amount makes them O(n).', 'Growing by a constant factor makes resizing overhead amortised O(1); constant increments give O(n) amortised copying cost. Hash collision costs are a separate assumption.'),
('converts chains of 8+ into red–black trees once the table has at least 64 buckets.', 'can convert long chains into red–black trees once the table has at least 64 buckets; ordinary OpenJDK 21 `put` invokes this on adding to a chain of eight.')], 'Correct geometric-series bound for arbitrary n, Java put treeification off-by-one, CPython layout scope and dummy reuse, and unsupported timing/memory generalisations.', h)
def fq(q):
 q[0]['prompt']+=' Assume well-distributed hashes, so collisions do not trigger an earlier resize.'
 q[1]['options'][0]['text']='A key\'s bucket depends on table size, so some keys may need a different bucket'
 q[2]['prompt']='For a doubling hash table, what does amortised O(1) resizing overhead guarantee, considering only entry-copying work?'
 q[2]['options'][2]['text']='Any sequence of n inserts from an empty table incurs O(n) total copying, although individual resizes can be expensive'
 q[2]['workedExample']='1. Start with one slot and double when full.\n2. For arbitrary n, copied capacities sum to less than 2n.\n3. Adding n placements gives less than 3n units.\n4. This amortises resizing only; hash collisions and key operations still affect overall insertion cost. Incremental work or pre-sizing reduces resize pauses but does not alone guarantee real-time deadlines.'
 q[5]['prompt']+=' Assume no collision-triggered early resizes; initial bucket allocation is lazy.'
 q[5]['workedExample']=q[5]['workedExample'].replace('12 + 24 + … + 768 = 1,524', '13 + 25 + 49 + 97 + 193 + 385 + 769 = 1,531')
 q[8]['prompt']='In OpenJDK 21, a HashMap has 32 buckets and a chain of eight entries. An ordinary put adds a ninth distinct key to that chain. What happens?'
 q[8]['workedExample']=q[8]['workedExample'].replace("On insert, if a bin's length reaches `TREEIFY_THRESHOLD` (8), Java calls `treeifyBin`.", 'The ordinary putVal path invokes treeifyBin when appending to a chain that already has eight nodes.')
 q[10]['prompt']='Which statements about the ordinary combined-table layout with general keys in CPython 3.14 are true? Select all that apply.'
 q[10]['options'][4]['text']='Deleting a key leaves a dummy marker so lookups can continue along the probe sequence'
 q[10]['workedExample']=q[10]['workedExample'].replace('space is recovered when the dict is next rebuilt.', 'rebuilding compacts entries, while GIL-enabled builds can also reuse dummy index slots during insertion.')
questions(p+'.questions.json',fq,'Align amortisation, Java ninth-node trigger and post-insertion resize copy count; scope CPython implementation questions.',h)
r=['https://swtch.com/~rsc/regexp/regexp2.html']
p='content/theory/04-automata/auto-nfa'
patch(p+'.md',[
('S, todo = set(S), list(S)', 'S = set(S)\n    todo = list(S)'),
('Here ε is the empty string `""`. Each step touches at most m states (m = |Q|) and their edges, so the run is **O(n · m)** time for a string of length n, with O(m) memory.', 'Here ε is the empty string `""`. With m states and e transitions, each step takes O(m + e), giving O(n · (m + e)) time and O(m) working memory, excluding the stored automaton. For a Thompson-style NFA, bounded out-degree gives e = O(m), hence **O(n · m)** time.'),
('An m-state NFA can need 2ᵐ DFA states, and for this family it does.', 'The general subset bound is 2ᵐ states for an m-state NFA. This particular family has m = n + 1 NFA states and 2ⁿ = 2^(m−1) minimal DFA states: exponential, but not exactly 2ᵐ.'),
('| Build cost | O(m) | up to O(2ᵐ) |', '| Build cost | O(m) for a Thompson-style NFA | potentially exponential, including transition computation |'),
('| Time per symbol | O(m) | O(1) |','| Time per symbol | O(m) for bounded out-degree | O(1) with a precomputed transition table |'),
('| Memory | O(m) | up to O(2ᵐ) |','| Memory | O(m + e), including transitions | O(2ᵐ) states; transition storage also depends on alphabet size |'),
('with ε-closure after each step: O(n · m) time.', 'with ε-closure after each step: O(n · (m + e)) time, or O(n · m) for bounded out-degree.'),
('Real engines build the DFA lazily, getting DFA speed without the worst-case blow-up.', 'Practical engines can build DFA states lazily and bound cache memory, falling back when necessary; this trades some matching speed for control of memory growth.')], 'Account for NFA edge count and correct the example exponential state bound; handle one-shot iterables in closure.',r)
def fn(q):
 q[4]['workedExample']='1. Each DFA state is a subset of the ten NFA states.\n2. There are 2¹⁰ = 1,024 such subsets, giving the general upper bound.\n3. The lesson\'s nth-from-end family is a different example: n = 10 uses eleven NFA states, not ten, so it does not establish tightness for this ten-state case.'
 q[7]['prompt']=q[7]['prompt'].replace('200-state NFA', '200-state Thompson-style NFA with bounded out-degree')
 q[10]['prompt']=q[10]['prompt'].replace('A regex engine uses', 'For a Thompson-style NFA with bounded out-degree, a regex engine uses')
questions(p+'.questions.json',fn,'Do not use an eleven-state example as proof for the ten-state upper bound; state bounded-degree complexity assumptions.',r)
p='content/theory/02-discrete-structures/disc-counting'
patch(p+'.md',[
('At 10¹⁰ guesses per second (a plausible GPU rig against a fast unsalted hash), that\'s about 6 hours.', 'At an assumed 10¹⁰ guesses per second, exhausting the space takes about 6 hours; this is arithmetic, not a measured hardware benchmark.'),
('Length beats complexity because it sits in the exponent.', 'For independently and uniformly chosen symbols, adding length multiplies the search space exponentially. Human-chosen passwords need a different model.'),
('is hopeless beyond about a dozen cities', 'quickly becomes impractical as n grows (the cutoff depends on the implementation and hardware)'),
('In any group of people, two have the same number of friends within the group', 'In a group of at least two people with mutual friendships and no self-friendships, two have the same number of friends within the group'),
('Every lossless compressor makes some inputs bigger;', 'A compressor defined on all finite bit strings that shrinks some inputs must expand others (an identity encoding need not expand anything);'),
('If mirror images also count as the same, halve it again.', 'For n ≥ 3 distinct people, if mirror images also count as the same, halve it again.')], 'Remove unsupported hardware rate attribution and add missing assumptions to compressor, friendship and circular-counting claims.', ['https://courses.csail.mit.edu/6.042/spring18/mcs.pdf'])
# All 12 quiz items read; arithmetic independently recomputed, no corrections needed.
for stem in ['content/dsa/03-hashing/hash-resizing','content/theory/04-automata/auto-nfa',p]:
 for ext in ['.md','.questions.json']:
  if stem+ext not in report['reviewed_files']: report['reviewed_files'].append(stem+ext)
report['findings']=findings
Path('docs/audit-root.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
