from pathlib import Path
import json
base=Path('content/theory/03-probability');p=base/'prob-algorithms.md';s=p.read_text()
def r(a,b):
 global s
 assert a in s,a
 s=s.replace(a,b)
r('A random pivot defeats adversarial inputs to quicksort. A random hash seed defeats hash-flooding attacks. A random sample answers a question about a billion rows in milliseconds.', 'Independent uniform pivots give quicksort good expected performance on fixed distinct-key inputs. Secret keyed hashing makes precomputed collision attacks harder. Random sampling can reduce the data needed for an estimate, with accuracy and runtime depending on the task.')
r('per round.', 'per round for an odd composite input when the base is sampled uniformly from the required range.')
r('That is far smaller than the chance of a hardware fault during the computation.', 'This bounds acceptance of a fixed composite under the sampling model; it is not directly the posterior probability that a returned candidate is composite.\n\n> [!note] Evidence gap\n> The previous comparison with hardware-fault probability is omitted because no hardware error model or measured execution exposure supported it.')
r("Python's `dict` resizes when it is about two-thirds full, and Java's `HashMap` at a load factor of 0.75.", "CPython's dictionary implementation uses a usable-entry fraction of about two-thirds; deletions and table layout complicate a simple occupancy trigger. Java `HashMap` has a configurable load factor, default 0.75. These are implementation/default details, not universal rules for all hash tables.")
r('with linear probing, an unsuccessful search costs about', 'in the classical large-table model with uniform independent home positions and no deletions, linear probing has expected unsuccessful-search cost about')
r('The fix was **randomised hashing**: Python (since 3.3) salts string hashes with a random per-process key, and now uses SipHash. Randomness is again the defence against a worst-case input.', 'Defences include input limits and secret keyed hashing. Python enables hash randomisation for str and bytes by default since 3.3; CPython commonly uses SipHash, with the active algorithm visible in sys.hash_info. Configuration can disable randomisation, and custom or non-string hashes need separate consideration. A random seed alone is not a guarantee against every adaptive attack.')
r('Most guess around 180. The answer is **23**.', 'Under independent uniform birthdays over 365 days, the first group size with a collision probability above 50% is **23**.')
r('P(collision) ≈ 1 − e^(−n²/2m)', 'P(collision) ≈ 1 − e^(−n(n−1)/(2m))')
r('Using 1 − x ≈ e^(−x), for n items in m slots:', 'For n independent uniform draws from m slots, approximating the no-collision product gives (accurate in the birthday regime n on the order of √m for large m):')
r('def p_collision(n, m):\n    p_unique', 'def p_collision(n, m):\n    if not isinstance(n, int) or not isinstance(m, int) or n < 0 or m < 1:\n        raise ValueError("need integer n >= 0 and m >= 1")\n    if n > m:\n        return 1.0\n    p_unique')
r('a repository with tens of thousands of objects has ambiguous short hashes.', 'a repository with tens of thousands of objects has a material probability of ambiguous fixed-length abbreviations under an ideal uniform-hash model.')
r('Finding *some* collision in an n-bit hash takes about 2^(n/2) attempts,', 'For an ideal n-bit hash under a classical generic attack, finding *some* collision takes on the order of 2^(n/2) evaluations,')
r('This is part of why MD5 (128-bit) and SHA-1 (160-bit) were retired for signatures, and why SHA-256 is the modern default.', 'MD5 and SHA-1 also have cryptanalytic collision weaknesses beyond this generic bound; their history cannot be explained by output length alone. SHA-256 offers a generic 128-bit classical collision bound, assuming no better attack.')
r('**Choosing the pivot uniformly at random** makes every input behave like a random one.', 'For distinct keys, standard pivot partitioning that compares the pivot once with every other element, and fresh independent uniform pivots, the comparison-count distribution does not depend on the initial order.')
r('i.e. O(n log n), for every input.', 'i.e. O(n log n), for every fixed distinct-key input.')
a=s.index('def qs(a):');b=s.index('\nprint(qs(',a)
s=s[:a]+'''def qs(a):
    # Count actual pivot comparisons for distinct, totally ordered keys.
    if len(a) <= 1:
        return 0
    i = random.randrange(len(a))
    p = a[i]
    lo, hi = [], []
    for j, x in enumerate(a):
        if j == i:
            continue
        if x < p:
            lo.append(x)
        else:
            hi.append(x)
    return (len(a) - 1) + qs(lo) + qs(hi)
''' + s[b:]
r('The worst case is still possible but astronomically unlikely, and no input can trigger it reliably.', 'The quadratic worst case remains possible. The expectation guarantee assumes the input is fixed independently of the random choices and comparisons obey a total order; an adaptive adversary or predictable pivots needs separate analysis. A naive two-way implementation can also be quadratic on equal keys.')
r("Rust's unstable sort descends from pdqsort", "Rust's documented current unstable sort uses ipnsort")
r("Python and Java (for objects) use stable merge-based sorts (Timsort and its successors) instead.", "Python's list sort and Java's object-array sort are stable; implementation details can change by version. These library algorithms have additional safeguards and are not identical to the teaching function above.")
r('It never gives false negatives,', 'A correctly implemented, insert-only filter with consistent hashing and no lost updates gives no false negatives for inserted keys,')
r('Cassandra, HBase, RocksDB and LevelDB put Bloom filters in front of on-disk files so most reads for absent keys skip the disk entirely.', 'Storage engines can use Bloom filters to skip files that cannot contain a key; RocksDB documents this use. Whether an absent-key read avoids physical I/O depends on filter configuration, cache state and the other files or metadata examined.')
r('Use a keyed hash (SipHash) for untrusted keys.', 'Use an appropriate secret keyed hash and bound untrusted input size; check which key types actually use that hash.')
r('Randomised quicksort is expected O(n log n) for every input; deterministic quicksort is O(n log n) only on average over inputs, which an adversary or a sorted file can defeat.', 'The stated randomised comparison bound assumes distinct keys, suitable partitioning and independent uniform pivots. Simple deterministic pivot rules can have quadratic inputs; deterministic algorithms with stronger pivot guarantees or fallback strategies can avoid that worst case.')
r('A predictable PRNG (`random` in Python) is fine for pivots', 'a PRNG (`random` in Python) can serve non-adversarial pivot selection')
r('Monte Carlo algorithms have bounded time and a small error that repetition shrinks exponentially.', 'Monte Carlo algorithms permit error; independent repetition with an appropriate decision rule can amplify a suitable per-run bound.')
r('an n-bit hash has n/2-bit collision resistance.', 'an ideal n-bit hash has a generic classical collision bound of about n/2 bits.')
r('comparisons in expectation on every input;', 'comparisons in expectation under the distinct-key pivot model;')
s+='\n- [UUIDv4 random-bit layout — RFC 9562](https://www.rfc-editor.org/rfc/rfc9562.html#section-5.4)\n- [Miller–Rabin — Handbook of Applied Cryptography, chapter 4](https://cacr.uwaterloo.ca/hac/about/chap4.pdf)\n- [RocksDB Bloom filters](https://github.com/facebook/rocksdb/wiki/RocksDB-Bloom-Filter)\n'
p.write_text(s)
p=base/'prob-algorithms.questions.json';qs=json.loads(p.read_text());q={x['id'].split('-q')[-1]:x for x in qs}
q['1']['workedExample']=q['1']['workedExample'].replace('fixed time, small chance', 'bounded time for a fixed round count, small chance')
q['2']['prompt']=q['2']['prompt'].replace('birthdays uniform', 'independent birthdays uniform')
q['3']['options'][3]['explanation']='This question specifies a chained table scanned linearly within a bucket. A tree-backed bucket is a different implementation.'
q['3']['workedExample']=q['3']['workedExample'].replace('Java resizes at 0.75', 'Java HashMap defaults to load factor 0.75')
q['4']['prompt']=q['4']['prompt'].replace('a random **32-bit** ID', 'an independently uniform **32-bit** ID')
q['4']['options'][0]['explanation']='10,000 / 2³² approximates the chance that one further uniform ID hits any of 10,000 distinct existing IDs. The question asks about all pairs among the issued IDs.'
q['4']['workedExample']=q['4']['workedExample'].replace('is why random IDs should be 64 bits at minimum and preferably 122+ (UUIDv4).', 'shows why ID width must be chosen from the expected population and tolerated collision risk, with collision detection where required. No single bit width is a universal minimum.')
q['5']['prompt']+=' Assume an odd composite input and bases sampled independently and uniformly from the required range.'
q['6']['prompt']=q['6']['prompt'].replace('birthdays uniform', 'independent birthdays uniform')
q['8']['prompt']+=' Assume distinct keys, one pivot comparison per other element, and a fixed input independent of fresh uniform pivot choices.'
q['8']['options'][2]['explanation']='Under the stated fixed-input and independent-uniform-pivot assumptions, no fixed ordering forces quadratic work on every run. Predictable randomness or adaptive comparisons falls outside that model.'
q['9']['prompt']=q['9']['prompt'].replace('a 128-bit content hash', 'an ideal 128-bit content hash').replace('generic birthday attack','classical generic birthday attack')
q['9']['workedExample']=q['9']['workedExample'].replace(', which is within reach of large-scale computation.', '. Actual feasibility depends on the implementation and resource budget.').replace('This is why SHA-256 (128-bit collision resistance) replaced 128-bit MD5 and 160-bit SHA-1, both of which also have practical collision attacks that beat even the birthday bound.', 'SHA-256 has a generic classical 128-bit collision bound. MD5 and SHA-1 have demonstrated cryptanalytic collisions that beat their generic birthday bounds; these weaknesses are separate from output length.')
q['11']['options'][1]['text']='Secret keyed hashing makes precomputed collision attacks against covered key types harder'
q['11']['options'][1]['explanation']='Correct. A suitable secret keyed hash frustrates precomputation, but randomisation configuration, key types and adaptive attacks still matter; input limits remain useful.'
q['11']['workedExample']=q['11']['workedExample'].replace("balanced-tree buckets (Java 8's HashMap turns long chains into trees, bounding each operation to O(log n)).", 'balanced-tree buckets where the key ordering supports logarithmic lookup; Java HashMap treeification is not an unconditional O(log n) guarantee for every same-hash, non-comparable key set.')
q['12']['prompt']+=' Count one comparison between the pivot and each other element per partition; version B uses fresh independent pivot choices.'
p.write_text(json.dumps(qs,ensure_ascii=False,indent=2)+'\n')
