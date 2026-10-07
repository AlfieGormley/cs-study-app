exec(open('/tmp/cs-study-audit-2026-10-04/fix-root.py').read().split("go=['https:")[0])
p_report=Path('docs/audit-theory-automata.json');report=json.loads(p_report.read_text());findings=report['findings'];b='content/theory/04-automata/'
src=['https://ocw.mit.edu/courses/18-404j-theory-of-computation-fall-2020/a77711ed3d212bf472f3485883a121e0_MIT18_404f20_lec3.pdf','https://arxiv.org/abs/1102.3901','https://epubs.siam.org/doi/10.1137/0222067','https://people.eecs.berkeley.edu/~dawnsong/teaching/s10/papers/angluin87.pdf']
patch(b+'auto-pumping.md',[
('Pumping this directly is fiddly, because strings like (ab)ᵖ can be pumped (take y = ab). Instead:', 'The same aᵖbᵖ witness proves non-regularity directly. Closure gives another proof:'),
('intersect with `(*)*` to get (ⁿ)ⁿ', 'intersect with the regular language consisting of zero or more opening brackets followed by zero or more closing brackets to get (ⁿ)ⁿ'),
('They are no longer "regular expressions" in the theory sense, and they lose the linear-time guarantee.', 'These features go beyond formal regular expressions. Their performance depends on the engine and pattern; recognizing balanced brackets itself can be done in linear time with a parser.')], 'Clarify closure proof, bracket notation and extended-engine complexity.',src)
def pumping(q):
 q[4]['workedExample']=q[4]['workedExample'].replace('Pumping down (i = 0) is the move for "more than" languages; pumping up is the move for "fewer than".', 'For this language and witness, pumping down supplies the contradiction. Other languages and witnesses require their own argument.')
 q[5]['prompt']+=' Assume p ≥ 2, which an adversary may choose if any pumping length exists.'
 q[7]['workedExample']=q[7]['workedExample'].replace('which block (2 states)', 'two live states plus a dead state').replace('Bounded or modular counting is regular; comparing two unbounded quantities is not.', 'These bounded or modular conditions are regular. The exact unbounded comparisons above are non-regular, as the proofs show.')
 q[9]['prompt']=q[9]['prompt'].replace('every string in L can', 'every non-empty string in L can')
 q[9]['workedExample']=q[9]['workedExample'].replace('every string,', 'every non-empty string,')
 q[11]['options'][0]['explanation']='For p ≥ 2 the adversary can choose x = ε and y = aa. Pumping gives length 2p + 2(i − 1), an even nonnegative number, so every result remains some ww.'
questions(b+'auto-pumping.questions.json',pumping,'Fix dead-state count, empty-string exception and pumped-length arithmetic; scope witnesses.',src)
patch(b+'auto-minimisation.md',[
('for each regular language, the minimal DFA is **unique** up to renaming states.', 'for each regular language over a fixed alphabet, the minimal complete DFA is unique up to renaming states.'),
('their minimal DFAs are identical', 'their minimal complete DFAs agree up to a start- and transition-preserving renaming'),
('    # start: split accepting / non-accepting', '    states, alpha = tuple(states), tuple(alpha)\n    # start: split accepting / non-accepting'),
('The DFA must be **complete** (every transition defined), so add a dead state first if needed.', 'The DFA must be complete (every transition defined), so add a dead state first if needed. Remove unreachable states before calling this function. It returns state-to-block IDs; constructing the quotient transitions, start and accepting states is a separate step.'),
('Its trick: when a block splits into two, you only need to re-examine transitions into the *smaller* half. Each state can be in the smaller half only O(log n) times, which gives the n log n bound.', 'Its worklist rule matters: if a split block is already pending, replace it with both pieces; otherwise schedule only the smaller piece. Smaller-piece scheduling and reverse transition lists let each of the k·n transitions be charged O(log n) times.'),
('For `a*b*` versus `(ab)*` that search returns `a`.', 'For a*b* versus (ab)*, a and b are both shortest counterexamples; alphabet traversal order determines which is returned.'),
('Fewer states means fewer flip-flops and simpler next-state logic in synthesised controllers.', 'Fewer logical states may reduce storage or logic, but encoding and synthesis matter. The same binary bit count can cover several state counts, and next-state logic can become more complex.'),
("Angluin's L* algorithm learns a minimal DFA by asking membership queries, building the Myhill–Nerode classes directly.", "Angluin's L* algorithm learns a minimal DFA using membership queries and equivalence queries that return counterexamples when a hypothesis is wrong."),
('Finding a minimum NFA is PSPACE-complete in general, and minimal NFAs need not be unique.', 'The decision problem of whether an equivalent NFA with at most a given number of states exists is PSPACE-complete, even when the input is a DFA. Minimum NFAs need not be unique.'),
('Two states with identical rows are equivalent, but', 'Two states with identical rows and the same accepting status are equivalent, but'),
('The minimal DFA is unique, so it is a canonical form', 'The minimal complete DFA over a fixed alphabet is unique up to renaming, so it is a canonical form')], 'State minimisation preconditions and output, correct Hopcroft worklist account and hardware/L-star/NFA-complexity claims.',src)
def minimum(q):
 q[7]['prompt']+=' Explore a before b at each breadth-first-search step.'
 q[8]['options'][1]['text']='Its worklist uses smaller-piece scheduling, charging each transition only O(log n) times'
 q[8]['options'][1]['explanation']='Correct. A pending block is replaced by both pieces; otherwise only the smaller piece is added. The halving argument bounds charges per transition.'
 q[8]['workedExample']='1. Split B into B₁ and B₂. If B is already pending, replace it by both pieces; otherwise enqueue only the smaller piece.\n2. A state can belong to a newly scheduled smaller piece only O(log n) times.\n3. Reverse transition lists charge scans to transitions. A single state can have many incoming transitions, so the bound is not O(k) per state per scan.\n4. There are k·n transitions in a complete n-state DFA over k symbols, giving O(k n log n) total with suitable data structures.'
 q[9]['options'][3]['explanation']='The four length residue classes are pairwise distinguishable: append enough a characters to make one residue zero modulo4, and another residue remains nonzero. Four states are necessary.'
 q[9]['workedExample']=q[9]['workedExample'].replace('In general mod m ∩ mod n needs', 'For unary length divisibility by positive m and n, the intersection needs')
 q[10]['workedExample']=q[10]['workedExample'].replace('this DFA is minimal for the reversed language, but the reversed language may need exponentially many states.', 'the reachable DFA is minimal for the reversed language if A was an accessible DFA. For a general NFA input, this first determinisation need not be minimal. In either case its size may be exponential.')
 q[11]['prompt']+=' DFA uniqueness here uses complete machines over a fixed alphabet.'
questions(b+'auto-minimisation.questions.json',minimum,'Correct Hopcroft charging/worklist, BFS tie and general NFA reversal claims.',src)
p=Path(b+'auto-thompson.md');s=p.read_text();s=s.replace('## Further reading','> [!note] Evidence gap\n> A previous fixed grep throughput figure is omitted because no reproducible hardware, input and tool configuration was available.\n\n## Further reading');p.write_text(s)
report['reviewed_files']=[b+n+s for n in ['auto-dfa','auto-nfa','auto-thompson','auto-pumping','auto-minimisation','auto-regex-engines'] for s in ['.md','.questions.json']]
report['status']='All six lesson/question pairs read; last regex engine pair corrections and execution pending.'
p_report.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
