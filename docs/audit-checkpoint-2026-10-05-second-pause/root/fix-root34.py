from pathlib import Path
import json
base=Path('content/theory/03-probability');p=base/'prob-bayes.md';s=p.read_text()
def r(a,b):
 global s
 assert a in s,a
 s=s.replace(a,b)
r('why accurate tests and alerts are still mostly false alarms when the thing they detect is rare','how rare events and false-positive rates affect the meaning of an alert')
r('Your fraud model is 98% accurate at catching fraud', 'In a hypothetical example, your fraud model detects 98% of fraud')
r('Most people say "about 98%". The real answer,', 'The 98% detection rate is not the answer. Under this model,')
r('Divide by P(B):','Divide by P(B), assuming P(B) > 0:')
r('A condition affects 1% of people. A test has:', 'In a hypothetical probability model, a condition affects 1% of people and a test has:')
r('despite the "99% accurate" test.', 'despite 99% sensitivity. Sensitivity and overall accuracy are different quantities.')
r('Imagine 10,000 people:', 'Use expected counts in a hypothetical group of 10,000 people:')
r('Research by Gigerenzer and others found that people (including doctors) reason far better with counts like these than with percentages. When you explain an alerting design to a team, use counts.', 'The count table makes the numerator and denominator explicit; its entries are expected counts, not guaranteed outcomes in every sample.\n\n> [!note] Evidence gap\n> The previous broad claim about how much better people reason with counts is omitted here because its study populations, tasks and effect sizes were not established in this review. No population-wide claim is needed for the arithmetic.')
r('> An analyst reviewing alerts will find fraud in fewer than 1 in 11.', '> Under these fixed rates, a randomly selected alert has fraud probability about 8.9%; a finite queue need not match that fraction exactly.')
r('Attacks are a tiny fraction of connections, so even a 0.1% false positive rate floods the SOC with noise. This "alert fatigue" leads people to ignore the real one.', 'When attacks are rare enough relative to the false positive rate, benign connections can generate most alerts. The operational effect depends on traffic volume and triage capacity.')
r('If 1 in 500 commits introduces a real bug but a flaky test fails on 2% of runs, most red builds are not your fault.', 'Suppose 1 in 500 builds contains a bug, the test detects every such bug, and it also fails on 2% of bug-free builds. Then P(bug | failure) = 0.002 / (0.002 + 0.998 × 0.02) ≈ 9.1%. This is a hypothetical model, not a judgement about a particular failed build.')
r('Bayes says precision depends on the base rate; recall does not.', 'Holding sensitivity and false positive rate fixed, changing the base rate changes precision. Recall is a conditional rate; it can also change if the population shift changes the mix of positive cases.')
r('Take the medical test', 'Take the hypothetical test')
r('and vary one thing at a time:', 'and vary one thing at a time, keeping the other conditional rates fixed:')
r('When the base rate is low, **the false positive rate dominates**. Improving sensitivity barely moves the posterior. The two powerful levers are cutting false positives and raising the prior, for example by only running the expensive check on traffic that a cheaper filter already found suspicious.', 'In this example, false positives dominate and sensitivity is already near 100%, so that small sensitivity increase barely helps. Reducing the false positive rate or testing a higher-prevalence population raises precision if other rates stay fixed. A real pre-filter can also change sensitivity and false positive rate; re-estimate them on the selected population. Low prevalence alone does not imply mostly false alerts: a detector with zero false positives is a counterexample.')
r('Independent pieces of evidence multiply their likelihood ratios. A second independent positive test', 'Likelihood ratios multiply when the evidence pieces are conditionally independent both given H and given not H. Under that assumption, a second positive test')
r('The independence assumption is plainly false ("Nigerian" and "prince" are not independent), yet naive Bayes works surprisingly well for ranking and was the basis of influential spam filters such as Paul Graham\'s 2002 "A Plan for Spam" and SpamAssassin\'s Bayes component.', 'Real words can remain correlated even within a class (for example, words in fixed phrases), so the naive assumption is an approximation and posterior scores may be poorly calibrated. Paul Graham’s 2002 "A Plan for Spam" describes a related Bayesian filter with token-selection and scoring choices beyond the simple model here.')
r('    # like[c][w] = P(w | c), smoothed\n', '    # Nonempty classes; strictly positive priors and\n    # smoothed likelihoods for every token in a fixed vocabulary.\n    words = tuple(words)  # reuse even when caller supplies a generator\n')
r('Summing logs is stable and gives the same ranking.', 'Summing finite logs avoids that product underflow and preserves the mathematical ranking; floating-point rounding can still affect close scores.')
r('adds 1 to every count so no probability is ever exactly zero.', 'adds 1 to each token count in a fixed vocabulary and normalises by the total count plus vocabulary size. Every token in that vocabulary then has positive probability in every class; out-of-vocabulary tokens need a separate policy.')
r('In a city of 10 million, about 10 innocent people would also match.', 'In a hypothetical population of 10 million innocent people each with that marginal match probability, the expected number of matches is 10; the actual count and posterior need further assumptions.')
r('Retesting only multiplies likelihood ratios if the errors are independent.', 'Using unchanged per-test likelihood ratios requires conditional independence both with and without the condition. Otherwise use the likelihood of the new evidence conditional on what was already observed.')
r('No evidence can move them. Leave a little room.', 'Within a fixed model, conditioning on positive-probability evidence preserves probability-zero and probability-one events. Evidence the model assigns probability zero makes the elementary update undefined; revise the model rather than dividing by zero.')
r('- When the base rate is low, most positives are false positives, even from an accurate detector.', '- With rare events, even a small false positive rate can make most alerts false; calculate the posterior from all three rates.')
r('- To improve precision on rare events, cut the false positive rate or raise the prior; raising sensitivity barely helps.', '- Reducing false positives or raising prevalence improves precision when the other rates stay fixed; the size of a sensitivity improvement matters too.')
r('independent evidence multiplies.', 'likelihood ratios multiply under the appropriate conditional-independence assumptions.')
s+='\n- [Naive Bayes — scikit-learn documentation](https://scikit-learn.org/stable/modules/naive_bayes.html)\n'
p.write_text(s)
p=base/'prob-bayes.questions.json';qs=json.loads(p.read_text());q={x['id'].split('-q')[-1]:x for x in qs}
q['2']['prompt']='In a hypothetical population, '+q['2']['prompt'][0].lower()+q['2']['prompt'][1:]
q['2']['workedExample']=q['2']['workedExample'].replace('Use natural frequencies with 10,000 people:', 'Use expected counts for 10,000 people in this model:')
q['5']['prompt']=q['5']['prompt'].replace('a patient takes a **second, independent** test of the same kind', 'a second test of the same kind is taken in the hypothetical model, with results **conditionally independent both given illness and given no illness**')
q['5']['options'][3]['explanation']='Under the specified conditional-independence model, another positive has likelihood ratio 19.8 and updates the odds. Correlated evidence requires a different conditional likelihood.'
q['5']['workedExample']=q['5']['workedExample'].replace('The caveat is *independent*:', 'The caveat is conditional independence in both classes:')
q['7']['prompt']='Start with prevalence 1%, sensitivity 99% and false positive rate 5%. Which hypothetical changes substantially raise precision, holding other rates fixed, with two-test results conditionally independent in both classes where stated? Select all that apply.'
q['7']['options'][2]['text']='Apply the same sensitivity and false positive rate to a pre-filtered population whose attack prevalence is 10%'
q['7']['options'][2]['explanation']='Correct under the fixed-rate premise: precision becomes 0.99 × 0.10 / (0.99 × 0.10 + 0.05 × 0.90) ≈ 68.8%. A real filter requires remeasuring both conditional rates.'
q['7']['options'][3]['text']='Require positive results from two identical detectors whose outputs are conditionally independent both for attacks and benign traffic'
q['7']['options'][3]['explanation']='Correct. Combined sensitivity is 0.99², false positive rate is 0.05², and precision is about 79.8%. The conditional-independence premise is essential.'
q['10']['options'][0]['explanation']='Underflow is possible when multiplying small probabilities; one or both class scores may underflow. But the stated zero count gives a direct zero-likelihood explanation for this word.'
q['10']['options'][3]['explanation']=q['10']['options'][3]['explanation'].replace('unseen words','words in the fixed vocabulary that were unseen in that class')
q['10']['workedExample']=q['10']['workedExample'].replace('Every word now', 'Every word in this fixed vocabulary now')
q['11']['prompt']+=' Interpret daily counts as expectations; when varying the false positive rate, hold sensitivity fixed.'
q['11']['options'][4]['explanation']='Under the fixed-sensitivity premise, halving the false positive rate leaves expected true detections at 99 and increases precision. In a real threshold change, sensitivity may also change.'
p.write_text(json.dumps(qs,ensure_ascii=False,indent=2)+'\n')
