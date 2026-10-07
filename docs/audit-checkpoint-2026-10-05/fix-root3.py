exec(open('/tmp/cs-study-audit-2026-10-04/fix-root.py').read().split("go=['https:")[0])
report=json.loads(Path('docs/audit-root.json').read_text());findings=report['findings']
patch('glossary-data.js',[
('recording changes in a log before updating the main data pages', 'flushing change records to durable storage before the corresponding changed data pages are written there'),
("['cache stampedes', 'thundering herd']", "['cache stampedes']"),
('The data-carrying capacity of a connection, usually measured in bits per second. Actual useful throughput can be lower.', 'In networking, the capacity of a connection, usually measured in bits per second. In signal processing, the width of a frequency band, measured in hertz. The context determines the meaning.')], 'Clarify durable WAL ordering, avoid treating every thundering herd as a cache stampede, and disambiguate bandwidth for synth lessons.', ['https://www.postgresql.org/docs/current/wal-intro.html'])
sources=['https://scikit-learn.org/stable/modules/ensemble.html','https://arxiv.org/abs/2207.08815','https://xgboost.readthedocs.io/en/stable/tutorials/model.html']
patch('content/ml/02-classical/mlc-ensembles.md',[
('tree ensembles are still the strongest general-purpose models, routinely beating neural networks.', 'tree ensembles are strong baselines. Which model wins depends on the dataset, training budget and evaluation; a historical benchmark is not a universal ranking.'),
('More is never worse for accuracy, just slower; returns diminish after a few hundred. A random forest **does not overfit by adding trees**.', 'More trees reduce Monte Carlo variability and approach a limiting ensemble, but a particular validation score need not improve monotonically. Returns diminish, while memory and prediction cost grow. Individual tree complexity still matters.'),
('For squared error, the negative gradient is exactly the residual', 'For half squared error, the negative gradient is exactly the residual'),
('a split whose gain does not exceed γ is not worth making.', 'the unpenalised improvement must exceed γ, or equivalently the displayed gain after subtracting γ must be positive.'),
('| More trees | Never hurts | Can overfit |', '| More trees | Approaches a limit | Can overfit |'),
('Ensembles of trees still predict within the range of training targets.', 'A regression forest averaging leaf means stays within the training target range. A boosted sum of residual trees need not. Ordinary constant-leaf trees still do not extend a smooth trend beyond the training feature range.'),
('where neural networks treat every rotation of the feature space alike.', 'reflecting inductive biases of the neural architectures evaluated in that study, not a property of every neural network.'),
('adding trees never causes overfitting.', 'more trees reduce sampling variability but do not guarantee a monotonic improvement in test accuracy.')], 'Correct forest accuracy guarantee, boosted-regression target-range claim, loss normalisation and double-counted split penalty.', sources)
def ensemble(q):
 q[1]['options'][2]['text']='Not as a general rule: more averaged trees approach a limiting ensemble, but validation accuracy can fluctuate and resource use grows'
 q[1]['options'][2]['explanation']='The ensemble stabilises as more trees are averaged. That does not imply each additional tree can only improve every test-set metric.'
 q[1]['options'][0]['explanation']='Forest trees are not fitted sequentially to residuals, so boosting-style reasoning does not apply. A particular finite-forest score can still fluctuate.'
 q[1]['options'][1]['explanation']='Counting parameters alone is not enough: averaging changes prediction variability, and test error is not guaranteed to vary monotonically.'
 q[1]['workedExample']=q[1]['workedExample'].replace('Error therefore flattens out as B grows; it does not turn upwards.', 'Predictions converge as B grows. Finite-ensemble classification error or a particular validation score need not decrease monotonically.')
 q[11]['prompt']='You forecast sales using ordinary constant-leaf LightGBM trees with time as the only changing feature; other inputs stay fixed. Future times exceed all training times and forecasts are flat despite a continuing trend. What explains this?'
 q[11]['options'][1]['text']='Future time values pass every learned time threshold into the same leaves; model the trend separately or evaluate a suitable change-based target'
 q[11]['options'][1]['explanation']='The problem is piecewise-constant extrapolation in feature space. A boosted sum can exceed the training target range, but that does not make it extend a time trend.'
 q[11]['options'][0]['explanation']='Changing the learning rate does not create new time thresholds beyond the observed feature range.'
 q[11]['options'][2]['explanation']='More ordinary trees fitted to the same time range still cannot create time splits beyond that range.'
 q[11]['workedExample']='1. Each ordinary tree routes all times above its greatest time threshold to the same leaf when other features are fixed.\n2. A sum of those constant values stays flat as time continues increasing.\n3. This is not a target-range guarantee: boosted sums can exceed observed targets.\n4. Evaluate a trend component, or a transformed forecasting target with appropriate time-based validation. Differencing or ratios do not automatically make a series stationary.'
questions('content/ml/02-classical/mlc-ensembles.questions.json',ensemble,'Correct answers/explanations teaching universal forest monotonicity or a false bound on boosted predictions.',sources)
sources=['https://algs4.cs.princeton.edu/24pq/']
patch('content/dsa/05-sorting-searching/sort-heapsort-lower-bound.md',[
('In benchmarks it is typically 2 to 3 times slower on large arrays. The reason is memory:', 'Heapsort can be slower on large arrays, but the ratio depends on implementation, data and hardware. Memory access and comparison counts help explain why:'),
('Near the top of a large heap those indices are far apart, so almost every step is a cache miss.', 'Near the root, frequently reused nodes may remain cached. Deeper in the heap, larger index gaps and less reuse can hurt locality; a different cache line does not by itself imply a cache miss.'),
('It is usually 2 to 3 times slower than quicksort because sift-down jumps around memory, so it is used as a safety net', 'Its less sequential access pattern can hurt performance compared with quicksort; the speed ratio must be measured. It is often used as a safety net')], 'Remove unsourced universal benchmark multiplier and correct inverted cache-locality explanation.',sources)
def heap(q):
 q[5]['prompt']='Why can heapsort be slower than quicksort on large arrays despite its O(n log n) worst-case guarantee?'
 q[5]['options'][0]['explanation']='Top heap levels may remain cached; deeper sift-down steps have larger index gaps and lower reuse. Partition scans can have better locality. Actual cache misses and speed ratios depend on the workload.'
 q[5]['options'][1]['explanation']='Heapsort has O(n log n) worst-case work, not quadratic work. Some duplicate-heavy inputs may take less than Theta(n log n) in this implementation.'
 q[5]['workedExample']='1. Both have O(n log n)-scale comparison counts on typical distinct-key inputs.\n2. A sift path visits indices such as 0, 1, 3, 7; gaps grow deeper in the heap.\n3. Upper nodes are reused often, while deeper accesses may miss caches.\n4. Partition scans can exploit sequential locality.\n5. Benchmark specific implementations rather than assuming a universal 2–3 times speed ratio.'
questions('content/dsa/05-sorting-searching/sort-heapsort-lower-bound.questions.json',heap,'Remove unverified speed claim and false all-input Theta assertion.',sources)
report['findings']=findings;report['reviewed_files']+=['glossary-data.js']
for stem in ['content/ml/02-classical/mlc-ensembles','content/dsa/05-sorting-searching/sort-heapsort-lower-bound']:report['reviewed_files'] += [stem+'.md',stem+'.questions.json']
Path('docs/audit-root.json').write_text(json.dumps(report,indent=2)+'\n')
