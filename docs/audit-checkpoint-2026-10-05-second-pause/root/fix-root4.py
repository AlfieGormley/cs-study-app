exec(open('/tmp/cs-study-audit-2026-10-04/fix-root.py').read().split("go=['https:")[0])
report=json.loads(Path('docs/audit-root.json').read_text());findings=report['findings']
sources=['https://scikit-learn.org/stable/auto_examples/ensemble/plot_bias_variance.html','https://www.statlearning.com/']
p='content/ml/01-fundamentals/mlf-bias-variance.md';s=Path(p).read_text();a=s[s.index('The same experiment averaged'):s.index('```\nerror')]
patch(p,[(a, '> [!note] Content gap: polynomial simulation results\n> The previous exact polynomial bias/variance table is omitted because its fitting procedure, evaluation grid and reproducible run record were not supplied. The k-NN code and output above have been rerun successfully; they do not verify a separate polynomial experiment.\n\n'),
('| More training data | Same | Down |', '| More training data | Can change | Often down |'),
('**More data** reduces variance but not bias.', '**More data** often reduces sampling variance and can also change finite-sample estimator bias. It cannot by itself make a fixed straight-line model represent an arbitrary sine curve.'),
('But training and validation errors tell you which term dominates:', 'Training and validation errors offer diagnostic clues, not a numerical decomposition into bias and variance:'),
('Very large neural networks can fit their training data perfectly, even random labels, yet still generalise well.', 'Very large neural networks can interpolate training data and still generalise when there is learnable structure. Their ability to memorise independently random labels does not imply they generalise to new random labels.'),
('- More data cuts variance but never bias; averaging models (bagging) cuts variance; boosting cuts bias.', '- More data, averaging and boosting can change bias and variance; their effects depend on the estimator and data. Treat common trends as diagnostics, not universal laws.')], 'Remove unsupported simulation table; qualify universal bias claims and distinguish classification heuristics from squared-error decomposition.', sources)
def bias(q):
 q[0]['options'][0]['explanation']='More data cannot remove the approximation error of a straight-line family fitted to a sine curve, even though finite-sample estimator bias can change.'
 q[0]['options'][2]['explanation']='More data usually stabilises the fitted line; it cannot remove this model-family mismatch. Bias is not universally independent of sample size.'
 q[2]['prompt']='On the same image task and information, reliable human labels give about 1% error. Your model has 8% training and 9% validation error. Which issue is the most reasonable first investigation (not an exact bias–variance decomposition)?'
 q[2]['options'][0]['explanation']='The small observed generalisation gap makes fit, features and optimisation natural first checks. It is not an exact measurement of variance.'
 q[2]['options'][1]['explanation']='Similar training and validation errors do not establish model adequacy; the gap to the comparable human benchmark deserves investigation.'
 q[2]['options'][2]['explanation']='Investigate inadequate fit or optimisation first, using the comparable human result as a benchmark rather than a measured noise floor.'
 q[2]['options'][3]['explanation']='The comparable human benchmark suggests lower error is attainable. Human error is not necessarily the irreducible error.'
 q[2]['workedExample']='1. Training error is 7 percentage points above the comparable human benchmark.\n2. The observed validation gap is only 1 point.\n3. Investigate features, optimisation and model capacity, while checking labels and distribution differences.\n4. These classification-error gaps are heuristics: they do not imply bias is exactly seven times variance, or that more data cannot help.'
 q[3]['options'][3]['explanation']='The correct components are 0.09 squared bias and 0.81 variance, summing to 0.90, not 0.99.'
 q[7]['prompt']=q[7]['prompt'].replace('over repeated training sets', 'over repeated independent label-noise draws at the same fixed training x values')
 q[7]['workedExample']=q[7]['workedExample'].replace('Between the training points it is far worse: the lesson\'s simulation found average variance 0.269 across the interval.', 'Between those points the variance can be much larger. The separate polynomial simulation table was removed because its exact experimental setup could not be verified.')
questions('content/ml/01-fundamentals/mlf-bias-variance.questions.json',bias,'Correct exact bias/variance inference from classification errors and remove dependent unverified experiment claims.',sources)
sources=['https://scikit-learn.org/stable/modules/generated/sklearn.metrics.average_precision_score.html','https://developers.google.com/machine-learning/crash-course/classification/roc-and-auc']
patch('content/ml/01-fundamentals/mlf-metrics.md',[
('p, r = tp / (tp + fp), tp / (tp + fn)\n    return p, r, 2 * p * r / (p + r)', 'p = tp / (tp + fp) if tp + fp else 0.0\n    r = tp / (tp + fn) if tp + fn else 0.0\n    f = 2*p*r/(p+r) if p+r else 0.0\n    return p, r, f'),
('**the probability that a randomly chosen positive scores higher than a randomly chosen negative.**','**the probability that a randomly chosen positive scores higher than a randomly chosen negative, plus half the probability of a tie.**'),
('any monotonic rescaling', 'any strictly increasing rescaling'),
('the mean of the precision values at the rank of each positive.', 'a recall-increment-weighted sum of precision values. With distinct scores, this equals the mean precision at each positive\'s rank; tied scores must be grouped consistently.'),
("A random classifier's AP equals the positive rate, so always compare AP against that baseline.", 'The positive rate is a useful no-skill precision baseline; a random finite ranking\'s realised AP, and even its finite-sample expectation, need not equal it exactly.'),
('ROC-AUC is the probability a random positive outranks a random negative;', 'ROC-AUC counts positive–negative ranking wins, with ties receiving half credit;')], 'Handle undefined metric denominators, AUC ties and monotonicity, and the finite-sample average-precision baseline.',sources)
def metrics(q):
 q[2]['options'][0]['text']='A random positive beats a random negative with probability 0.80 when ties receive half credit'
 q[2]['options'][0]['explanation']='AUC equals P(positive score > negative score) plus half of P(equal scores). Without ties this is the ordinary probability of correct ranking.'
 q[7]['prompt']='A defect occurs in 0.1% of parts. Which metrics directly assess rare-positive detection and inspector workload rather than being dominated by majority-class correctness? Select all that apply.'
 q[7]['options'][0]['explanation']='Accuracy is a real metric, but alone is dominated here by non-defective parts. Report it with metrics that expose missed defects and false alarms.'
 q[7]['workedExample']=q[7]['workedExample'].replace("A random classifier's AP equals the prevalence, 0.001, so even AP = 0.2 is a 200-fold lift.", 'The prevalence, 0.001, is a useful no-skill precision baseline, but not an exact expected AP for every finite random ranking.')
 q[8]['options'][3]['explanation']='The mean negative log probability of the true class is about 0.415. For the negative example use 1 - 0.2 = 0.8.'
 q[11]['prompt']='You add negatives whose scores are all strictly below every positive score, increasing negatives tenfold while keeping positives unchanged. What happens to ROC-AUC and average precision?'
questions('content/ml/01-fundamentals/mlf-metrics.questions.json',metrics,'Make metric tie and dataset assumptions explicit and correct misleading explanations.',sources)
report['findings']=findings
for stem in ['content/ml/01-fundamentals/mlf-bias-variance','content/ml/01-fundamentals/mlf-metrics']:report['reviewed_files'] += [stem+'.md',stem+'.questions.json']
report['omissions'].append({'file':'content/ml/01-fundamentals/mlf-bias-variance.md','detail':'Polynomial simulation table removed because setup/provenance could not be reproduced from the supplied material; explicit gap note replaces it. Supplied k-NN simulation verified.'})
Path('docs/audit-root.json').write_text(json.dumps(report,indent=2)+'\n')
