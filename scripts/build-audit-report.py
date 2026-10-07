#!/usr/bin/env python3
"""Summarise recorded evidence without treating inventory as fact verification."""
from pathlib import Path
import hashlib
import html
import json

ROOT = Path(__file__).resolve().parent.parent
reports = {}
for path in sorted((ROOT / 'docs').glob('audit-*.json')):
    if path.name not in {'audit-links.json', 'audit-manifest.json'}:
        reports[path.name] = json.loads(path.read_text())

reviewed = {}
review_hashes = {}
targeted = set()
findings = []
missing = set()
for name, report in reports.items():
    coverage_record = report.get('coverage', {})
    declared_reads = report.get('reviewed_files', []) + report.get('full_read_files', [])
    if isinstance(coverage_record, dict):
        full_read_files = coverage_record.get('full_read_files', [])
        if isinstance(full_read_files, list):
            declared_reads += full_read_files
    for item in declared_reads:
        path = item if isinstance(item, str) else item.get('file')
        if path:
            reviewed.setdefault(path, []).append(name)
            if not (ROOT / path).exists():
                missing.add(path)
    coverage = report.get('coverage', [])
    for item in coverage if isinstance(coverage, list) else []:
        if not isinstance(item, dict):
            continue
        path = item.get('file')
        scope = str(item.get('reviewScope', item.get('scope', item.get('review', '')))).lower()
        if path and any(label in scope for label in ['full-file', 'read in full', 'full semantic read']):
            reviewed.setdefault(path, []).append(name)
            if item.get('sha256'):
                review_hashes.setdefault(path, []).append(dict(report=name, sha256=item['sha256']))
        elif path and 'targeted' in scope:
            targeted.add(path)
    for finding in report.get('findings', []):
        finding = dict(finding)
        finding['report'] = name
        findings.append(finding)

files = []
modules = []
for module_file in sorted((ROOT / 'content').glob('*/*/module.json')):
    module = json.loads(module_file.read_text())
    directory = module_file.parent
    rel_dir = directory.relative_to(ROOT).as_posix()
    record = dict(path=rel_dir, title=module['title'], lessons=0,
                  lessons_read=0, questions=0, questions_read=0,
                  correction_records=0)
    verification_path = directory / 'verification.json'
    verification = json.loads(verification_path.read_text()) if verification_path.exists() else {}
    record['verification_summary'] = verification.get('summary')
    record['confidence'] = sorted(set(item.get('confidence', 'unrecorded')
                                     for item in verification.get('lessons', {}).values()))
    record['verification_gaps'] = verification.get('gaps', [])
    record['low_confidence'] = verification.get('lowConfidence', [])
    record['verification_current'] = bool(verification)
    record['stale_or_unrecorded_lessons'] = []
    for lesson in module['lessons']:
        record['lessons'] += 1
        lesson_hash = hashlib.sha256()
        for suffix in ['.md', '.questions.json']:
            filename = lesson + suffix
            source = directory / filename
            lesson_hash.update(filename.encode())
            lesson_hash.update(source.read_bytes() if source.exists() else b'')
        if verification.get('lessons', {}).get(lesson, {}).get('hash') != lesson_hash.hexdigest()[:16]:
            record['verification_current'] = False
            record['stale_or_unrecorded_lessons'].append(lesson)
        for suffix in ['.md', '.questions.json']:
            path = directory / (lesson + suffix)
            relative = path.relative_to(ROOT).as_posix()
            if not path.exists():
                missing.add(relative)
                continue
            full = relative in reviewed
            count = len(json.loads(path.read_text())) if suffix.endswith('json') else 0
            if suffix == '.md':
                record['lessons_read'] += full
            else:
                record['questions'] += count
                record['questions_read'] += count if full else 0
            files.append(dict(file=relative, sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                              review='full semantic read with selected verification' if full
                              else 'targeted review' if relative in targeted else 'inventory only; semantic review pending',
                              evidence=reviewed.get(relative, []),
                              recorded_review_hashes=[dict(item, matches_current_file=item['sha256'] == hashlib.sha256(path.read_bytes()).hexdigest())
                                                      for item in review_hashes.get(relative, [])]))
    for finding in findings:
        paths = finding.get('files', []) + [finding.get('file', ''), finding.get('scope', '')]
        if any(isinstance(p, str) and p.startswith(rel_dir + '/') for p in paths):
            record['correction_records'] += 1
    modules.append(record)

# Explicit historical removal, documented in docs/RESUME.md; do not hide other missing paths.
archived = sorted(p for p in missing if p.startswith('content/ml/'))
missing.difference_update(archived)

integration_path = ROOT / 'docs/audit-integration.json'
integration = json.loads(integration_path.read_text()) if integration_path.exists() else {}
complete = integration.get('status') == 'complete' and all(
    m['verification_current'] and m['lessons_read'] == m['lessons']
    and m['questions_read'] == m['questions'] for m in modules)
status = ('Current-corpus review complete; evidence and limitations recorded below' if complete
          else 'Audit in progress; not a certification of the entire corpus')
manifest = dict(status=status,
                confidence='No numeric confidence probabilities. A full semantic read does not mean every claim was externally corroborated.',
                counting='Correction records have different granularity across agents; they are not an exact count of distinct false claims.',
                modules=modules, files=files, missing_reviewed_paths=sorted(missing),
                intentionally_removed_reviewed_paths=archived,
                removal_evidence='docs/RESUME.md: Removed content (2026-10-04 user-requested removal of content/ml)',
                read_evidence_scope='Read counts are historical path-based declarations. Recorded review hashes may predate later corrections; current module verification hashes are shown separately.',
                evidence_reports=list(reports), findings=findings)
(ROOT / 'docs/audit-manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
esc = html.escape
rows = ''.join(f'<tr><td><a href="../{esc(m["path"])}/verification.json">{esc(m["path"])}</a></td><td>{m["lessons_read"]}/{m["lessons"]}</td>'
               f'<td>{m["questions_read"]}/{m["questions"]}</td><td>{m["correction_records"]}</td>'
               f'<td>{esc(str((m["verification_summary"] or {}).get("claimsChecked", "pending")))}</td>'
               f'<td>{esc(str((m["verification_summary"] or {}).get("errorsCorrected", "pending")))}</td>'
               f'<td>{esc(", ".join(m["confidence"]) or "unreviewed")}'
               f'{" — stale or incomplete record" if not m["verification_current"] else " — hashes current"}</td></tr>'
               for m in modules)
gap_sections = ''
for m in modules:
    entries = m['verification_gaps'] + m['low_confidence']
    if entries:
        items = ''.join('<li>' + esc(item if isinstance(item, str) else json.dumps(item, ensure_ascii=False)) + '</li>' for item in entries)
        gap_sections += f'<details><summary>{esc(m["path"])} — gaps and confidence limits</summary><ul>{items}</ul></details>'
links = ''.join(f'<li><a href="{esc(name)}">{esc(name)}</a></li>' for name in reports)
totals = {key: sum(m[key] for m in modules) for key in ['lessons','lessons_read','questions','questions_read']}
page = f'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Content audit evidence</title><style>body{{font:16px/1.6 system-ui;margin:2rem auto;padding:0 1rem;max-width:1100px;color:#172033;background:#f7f9fc}}h1{{line-height:1.2}}table{{border-collapse:collapse;width:100%;font-size:.9rem}}th,td{{padding:.65rem;text-align:left;border-bottom:1px solid #cbd5e1}}th{{background:#e5ebf4}}td:first-child{{overflow-wrap:anywhere}}.scroll{{overflow:auto}}a{{color:#164b9a}}.notice{{padding:1rem;background:#fff1d6;border-left:4px solid #ab6500}}</style>
<h1>Content audit evidence</h1><p class="notice">{esc(manifest['status'])}. This report separates recorded semantic reads from inventory-only files. It does not claim that every statement has been source-verified.</p>
<p>{totals['lessons_read']} of {totals['lessons']} current lessons and {totals['questions_read']} of {totals['questions']} current questions have recorded full semantic reads.</p>
<p>{esc(manifest['read_evidence_scope'])}</p>
<p>Confidence is evidence-based, not a numerical probability. Corrections, primary sources, omitted material, tests and limitations are recorded in the reports below. Missing benchmark or hardware evidence is explicitly distinguished from proof that a claim is false.</p>
<ul>{links}<li><a href="audit-links.json">Link retrieval evidence</a></li><li><a href="audit-manifest.json">File hashes, coverage and combined finding records</a></li></ul>
<h2>Priority findings</h2>
<ul><li><strong>System design:</strong> corrected availability arithmetic and independence assumptions, HTTP redirect caching claims, and database/consistency guarantees. Removed unsupported universal database throughput ceilings. Detailed case-study reviews include actual PostgreSQL concurrency and recovery checks.</li>
<li><strong>Synth building:</strong> corrected one-sided FFT endpoint scaling, strict Nyquist harmonic limits, quantisation/clipping explanations, control-to-audio concurrency examples and MIDI handling. Electrical and hearing-related advice was narrowed to the supported conditions.</li>
<li><strong>Missing project evidence:</strong> there is no verified project-specific wiring, parts compatibility, voice-count or end-to-end latency result without selected hardware and bench measurements. These omissions are stated in the synth lessons. Unsupported universal performance, latency and population statistics were removed elsewhere too.</li>
<li><strong>Across the app:</strong> corrected quiz answers and ambiguous distractors, obsolete or overbroad protocol/product statements, example code and arithmetic, dictionary definitions and diagram labels. A correction record may be a clarification or repeated field correction; it is not necessarily a distinct false fact.</li></ul>
<h2>Module coverage</h2><p>Read counts include selected source, arithmetic and code checks; they are not counts of individually corroborated claims. Correction-record granularity varies across reviewers.</p>
<p>The claims column reproduces each module verifier’s recorded counter, whose scope may be claim groups rather than individual assertions. See the module verification record for its definition; it is not an exhaustive count of verified facts. Confidence reflects recorded verification, not a fresh guarantee for subsequent edits.</p>
<div class="scroll"><table><thead><tr><th>Module</th><th>Lessons read</th><th>Questions read</th><th>Correction records</th><th>Recorded claims checked</th><th>Recorded corrections</th><th>Recorded confidence</th></tr></thead><tbody>{rows}</tbody></table></div>
<h2>Omitted material and confidence limits</h2><p>These are the verifier’s recorded limitations. Unexecuted hardware or deployment tests are not evidence that the teaching model is false. Unsupported claims were corrected, scoped or removed in the lessons.</p>{gap_sections}
<h2>Workspace changes requiring reconciliation</h2><p>{esc(', '.join(sorted(missing)) or 'No unexpected reviewed source paths are missing.')}</p>
<h2>Intentionally removed historical content</h2><p>The AI &amp; Machine Learning subject was removed at the user's request on 4 October 2026, as recorded in <a href="RESUME.md">RESUME.md</a>. Historical review evidence is retained; these paths are excluded from current coverage and do not require restoration.</p><p>{esc(', '.join(archived) or 'No removed paths appear in the review evidence.')}</p></html>'''
(ROOT / 'docs/content-audit.html').write_text(page)
print(json.dumps(totals))
