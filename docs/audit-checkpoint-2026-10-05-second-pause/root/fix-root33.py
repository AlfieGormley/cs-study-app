from pathlib import Path
import json
base=Path('content/theory/03-probability')
p=base/'prob-expectation.md';p.write_text(p.read_text().replace('https://cs.brown.edu/research/pubs/pdfs/1994/Azar-1994-BA.pdf','https://www.cs.tau.ac.il/~azar/box.pdf'))
p=base/'prob-basics.md';s=p.read_text()
def r(a,b):
 global s
 assert a in s,a
 s=s.replace(a,b)
r('When every outcome is equally likely', 'In a finite nonempty sample space, when every outcome is equally likely')
r('Rolling two dice gives', 'Rolling two independent fair six-sided dice gives')
r("Kolmogorov's three axioms are all you need:", "In general probability spaces, events belong to a specified collection of measurable subsets. For finite examples here, every subset can be an event. Kolmogorov's axioms are:")
r('3. If A and B are **disjoint** (cannot both happen), P(A ∪ B) = P(A) + P(B).', '3. For any countable collection of pairwise **disjoint** events, the probability of their union equals the sum of their probabilities. For two events, this gives P(A ∪ B) = P(A) + P(B).')
r('four rolls of a die?', 'four independent rolls of a fair six-sided die?')
r('This exact problem was posed to Pascal and Fermat in 1654, and it is the same calculation as', 'This is the same calculation as')
r('The **conditional probability** of A given B is:', 'When P(B) > 0, the **conditional probability** of A given B is:')
r('Given that two dice sum to 8,', 'Given that two independent fair six-sided dice sum to 8,')
r('which is how you compute probabilities of sequences:', 'which is how you compute probabilities of sequences (the displayed conditional requires P(A) > 0):')
r('from a shuffled deck', 'from a uniformly shuffled standard 52-card deck')
r('split Ω into disjoint pieces, then:', 'form a countable partition of Ω into disjoint pieces, then (omitting any zero-probability pieces):')
r('equivalently  P(A | B) = P(A)', 'equivalently, if P(B) > 0: P(A | B) = P(A)')
r('With two dice,', 'With two independent fair six-sided dice,')
r('maximally *dependent*', '*dependent*')
r('each up 99.9% of the time:', 'each independently up 99.9% of the time, in a model with no other causes of failure:')
r('**In parallel** (any one is enough),', '**In parallel** (any one working replica is sufficient, with ideal routing and failover),')
r('That is why AWS spreads replicas across Availability Zones and why a bad deploy can defeat redundancy entirely.', 'Separating replicas across failure domains can reduce shared infrastructure risks, while a bad deployment across all replicas can still defeat redundancy.')
r('A Monte Carlo estimate converges on the true probability as the number of trials grows.', 'For independent trials from the specified model, the sample frequency converges to the model probability as the number of trials grows. This checks arithmetic against a simulation; it does not establish that the model describes the real system.')
r('Simulation error shrinks like 1/√n, so a million trials gives about three correct decimal places. That is plenty for checking a formula.', 'For n independent Bernoulli trials, the estimate has standard error √(p(1 − p)/n), at most 0.0005 for a million trials. This is not a guarantee of three correct decimal places. Rare events can require far more trials for small relative error; exact enumeration is preferable when feasible.')
r('are all correlated.', 'can be correlated.')
r('- With equally likely outcomes,', '- In a finite nonempty sample space with equally likely outcomes,')
r('restricts the sample space to B;', 'requires P(B) > 0 and restricts the sample space to B;')
s+='\n> [!note] Evidence gap\n> The previous precise attribution of the four-roll example to a particular 1654 exchange is omitted because that historical detail was not independently established in this review. The calculation is unchanged.\n'
p.write_text(s)
p=base/'prob-basics.questions.json';qs=json.loads(p.read_text());q={x['id'].split('-q')[-1]:x for x in qs}
for k in ['1','4','7']: q[k]['prompt']=q[k]['prompt'].replace('Two fair six-sided dice','Two independent fair six-sided dice').replace('Two fair dice','Two independent fair six-sided dice')
q['6']['prompt']+=' Assume these are the only failure causes and all three are required.'
q['6']['options'][1]['explanation']='The ideal parallel calculation is 1 − 0.001³ = 99.9999999%, not 99.9999%; either way, parallel redundancy is the wrong model when all three services are required.'
q['7']['options'][2]['explanation']='Correct under the stated independent-dice model: P(A ∩ D) = 3/36 = 1/12 = 1/2 × 1/6.'
q['10']['prompt']+=' The car is initially uniform over the three doors; when the host has two goat doors available, he chooses each with probability 1/2 and always offers the switch.'
q['10']['workedExample']+='\n\nThe 2/3 probability after observing a specific opened door uses the stated fair tie-break. The strategy of always switching wins 2/3 before observing the host’s door even with a different tie-break, provided the host always reveals a goat and offers the switch.'
q['11']['prompt']+=' Assume any one working replica suffices, with perfect routing and failover and no other failure causes.'
p.write_text(json.dumps(qs,ensure_ascii=False,indent=2)+'\n')
