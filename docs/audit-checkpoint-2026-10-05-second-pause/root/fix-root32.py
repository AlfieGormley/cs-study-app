from pathlib import Path
import json
base=Path('content/theory/03-probability');p=base/'prob-expectation.md';s=p.read_text()
def r(a,b):
 global s
 assert a in s,a
 s=s.replace(a,b)
r('The **expectation** E[X] is the probability-weighted average of its values:', 'For a discrete variable with finite E[|X|], the **expectation** E[X] is the probability-weighted average of its values:')
r('It is the long-run average over many repetitions.', 'For independent, identically distributed repetitions with finite absolute expectation, sample averages converge to it by the law of large numbers. Some distributions have no finite expectation.')
r('probability p on each independent attempt', 'the same probability 0 < p ≤ 1 on each independent attempt')
r('The mean says where values centre; **variance** says how spread out they are:', 'For a variable with finite second moment, the mean says where values centre; **variance** says how spread out they are:')
r('For any random variables X and Y,', 'For random variables X and Y with finite absolute expectations,')
r('> - E[XY] = E[X] E[Y] needs independence (strictly, uncorrelatedness).\n> - Var(X + Y) = Var(X) + Var(Y) needs it too.\n> - E[f(X)] = f(E[X]) is false for non-linear f.', '> - For finite-second-moment variables, E[XY] = E[X] E[Y] holds exactly when covariance is zero. Independence is sufficient but not necessary.\n> - Var(X + Y) = Var(X) + Var(Y) + 2 Cov(X,Y), so uncorrelatedness suffices for variances to add.\n> - E[f(X)] = f(E[X]) does not hold in general for non-linear f, though it can hold in particular cases.')
r('n people check their hats;', 'n ≥ 1 people check their hats;')
r('1 for every n,', '1 for every positive n,')
r('assigns n jobs to n servers,', 'assigns n jobs to n servers (n ≥ 1),')
r('about 36.6 servers sit idle while others take two or three jobs.', 'the expected number of idle servers is about 36.6; other servers may receive one or several jobs.')
r('picking the less loaded of two random servers dramatically reduces the maximum load.', 'in the sequential model with n unit jobs, n initially empty servers, independent uniform candidate choices and current load information, picking the less loaded of two candidates dramatically reduces the maximum load with high probability as n grows. Real scheduling systems need their own workload and measurement assumptions.')
r('Insertion sort performs exactly one swap per inversion. For a random permutation,', 'The adjacent-swap version of insertion sort performs exactly one swap per inversion; the usual shifting version instead performs one rightward shift per inversion. For a uniformly random permutation of distinct values,')
r('For a random permutation of distinct values,', 'For a uniformly random permutation of distinct finite numbers,')
r('You send requests to random shards out of n until every shard has been hit at least once.', 'You independently choose a shard uniformly from n ≥ 1 shards on each request, with replacement, until every shard has been hit at least once.')
r('Real latency tails are usually far smaller, but Markov needs no assumptions beyond non-negativity.', 'The true tail can be smaller or attain this bound. For a useful finite bound, Markov needs a nonnegative variable and a known finite mean.')
r("Chebyshev's inequality, P(|X − μ| ≥ kσ) ≤ 1/k², tightens this using the variance.", "Chebyshev's inequality, P(|X − μ| ≥ kσ) ≤ 1/k² for k > 0 and finite σ > 0, bounds deviations using the variance. It need not improve every Markov bound at every threshold.")
r('A link runs at 10 MB/s half the time and 90 MB/s the other half.', 'Each download independently selects a speed of 10 MB/s or 90 MB/s with equal probability and keeps that speed for the entire transfer.')
r('= 5 + 1.11 ≈ 5.6 s', '= 5 + 0.556 ≈ 5.6 s')
r('The slow periods dominate.', 'The slower transfers contribute more to the mean duration. This model differs from a single transfer whose speed fluctuates rapidly with equal time spent at each rate.')
r('E[X] = Σ x P(X = x) is its long-run average.', 'for a discrete integrable variable E[X] = Σ x P(X = x), and iid sample averages converge to it.')
r('it adds over independent variables only.', 'finite variances add over pairwise uncorrelated variables; independence is sufficient.')
s+='\n- [Balanced Allocations — Azar, Broder, Karlin and Upfal](https://cs.brown.edu/research/pubs/pdfs/1994/Azar-1994-BA.pdf)\n'
p.write_text(s)
p=base/'prob-expectation.questions.json';qs=json.loads(p.read_text());q={x['id'].split('-q')[-1]:x for x in qs}
q['1']['workedExample']=q['1']['workedExample'].replace('This is the mean of a binomial distribution, np, derived without any binomial coefficients.','With independent flips the count is binomial with mean np. Linearity gives the same expectation even without independence, provided each flip has marginal head probability 0.3.')
q['3']['workedExample']=q['3']['workedExample'].replace('will be very close','is very likely to be close').replace('Roll a die a million times','Roll a fair die independently a million times')
q['5']['workedExample']=q['5']['workedExample'].replace('for any n.', 'for any positive n.')
q['6']['prompt']=q['6']['prompt'].replace('4 distinct numbers','4 distinct finite numbers')
q['7']['prompt']=q['7']['prompt'].replace('that are **not** independent', 'with finite second moments that are **not** independent')
q['7']['options'][0]['explanation']='Correct. With finite expectations, linearity does not require independence.'
q['7']['options'][4]['explanation']='Not guaranteed. The equality holds exactly when X is constant almost surely (variance zero).'
q['7']['workedExample']=q['7']['workedExample'].replace('Sort the identities by what they need:', 'Under the finite-second-moment assumption, sort the identities by the additional conditions they need:').replace('| nothing |','| no independence assumption |').replace('| X constant |','| X constant almost surely |')
q['9']['prompt']=q['9']['prompt'].replace('from a uniformly random shard','from an independently chosen uniformly random shard')
q['11']['prompt']='Each 100 MB download selects 10 MB/s or 90 MB/s with equal probability and keeps that speed throughout. Ignoring overhead, what is its expected duration?'
q['11']['options'][0]['explanation']=q['11']['options'][0]['explanation'].replace('5 + 1.11','5 + 0.556')
q['12']['options'][3]['explanation']='The maximum is at least the average, and some assignments produce a maximum greater than 1, so its expectation is strictly greater than 1. In the n-keys/n-buckets model the maximum grows on the scale ln n / ln ln n with high probability as n grows.'
q['12']['workedExample']+='\n\nThe earlier numerical simulation average for the maximum is omitted: no reproducible simulation setup accompanied that figure.'
p.write_text(json.dumps(qs,ensure_ascii=False,indent=2)+'\n')
