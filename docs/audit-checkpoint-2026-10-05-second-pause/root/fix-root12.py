exec(open('/tmp/cs-study-audit-2026-10-04/fix-root.py').read().split("go=['https:")[0])
report=json.loads(Path('docs/audit-root.json').read_text());findings=report['findings']
b='content/software-engineering/04-git-cicd/'
src=['https://git-scm.com/docs/git-init','https://git-scm.com/docs/git-gc','https://git-scm.com/docs/git-reset','https://git-scm.com/docs/gitattributes','https://git-scm.com/docs/BreakingChanges','https://git-scm.com/book/en/v2/Git-Internals-Git-Objects']
patch(b+'git-object-model.md',[
('why "lost" commits are almost never lost.', 'how reflogs can recover commits while their objects are retained.'),
('Older systems such as CVS and Subversion think in terms of changes to files over time. Git thinks in **snapshots**.', 'Git models committed project state as **snapshots**. This logical model is separate from delta compression used to store or transfer objects.'),
('| tree | A directory listing | Blobs, trees |', '| tree | A directory listing | Blobs, trees, submodule commit IDs |'),
('The first commit in a repository has **no parent**.', 'A root commit has **no parent**; a repository can contain multiple roots.'),
("They differ after a rebase or cherry-pick, when someone else (or you, later) replays the change.", 'Rebase and cherry-pick normally preserve authorship while recording the current committer and time; the two identities can still be the same person.'),
("An object's name is the SHA-1 hash", "In a SHA-1-format repository, an object's name is the SHA-1 hash"),
('a repository containing just that file.', 'a SHA-1 repository whose index contains just that file, with the shown mode and no content-conversion filters.'),
('In a fresh repository it is literally a 41-byte file: `.git/refs/heads/main` contains a hash and a newline.', 'With the files backend and a loose SHA-1 ref, .git/refs/heads/main is a 40-hex-digit object ID plus a newline. Packed refs, SHA-256 and the reftable backend use different representations; an unborn branch has no commit ref yet.'),
('Creating a branch is therefore instant and nearly free: it writes one small file.', 'Creating a branch records a ref rather than copying the project or its history, so it is normally inexpensive.'),
("Git is also introducing a newer **reftable** ref storage format.", 'Git also supports the **reftable** ref storage backend; use Git commands rather than depending on its on-disk representation.'),
('`git add f` hashes `f`, writes the blob into the store and records its hash in the index.', '`git add f` applies configured content conversions (such as line-ending or clean filters), stores the resulting blob and records its hash in the index.'),
('The **reflog** records every position a ref has held locally:', 'When enabled and retained, a **reflog** records local updates to a ref:'),
('Loose unreachable objects are pruned only when older than two weeks (`gc.pruneExpire`).', 'The usual prune grace period is two weeks (gc.pruneExpire), including expiry when using modern cruft packs. These are configurable age thresholds, not an extra guaranteed two weeks after a reflog entry expires.'),
('support across hosting services is still uneven.', 'check the intended Git clients and hosting service for SHA-256 interoperability before choosing it.'),
("Git's published plan for 3.0 is", "As checked on 2026-10-04, Git's published plan for 3.0 is"),
('Every version of a 200 MB asset is a separate blob in every clone forever.', 'Each distinct version is a blob, and a full clone normally retains reachable versions. Compression, partial/shallow clones and deliberate history removal affect actual disk use and retention.'),
('The reflog almost always has what you need, as long as you act within a few weeks.', 'A retained reflog may recover committed work. It is not a backup and does not recover arbitrary uncommitted changes discarded by a hard reset.'),
('- Objects are immutable; amend, rebase and reset create new objects and move refs rather than editing anything.', '- Objects are immutable. Amend and replaying rebase create commits; commit-level reset moves a ref and may update the index and working tree without creating a replacement commit.'),
('- A branch is a file containing a commit hash; HEAD usually names the current branch.', '- A branch is a ref naming a commit, with backend-dependent storage; HEAD usually names the current branch.'),
('unreachable objects survive for weeks thanks to the reflog and prune grace periods.', 'reflogs and configurable prune grace periods can retain otherwise unreachable work, but provide no universal recovery guarantee.')], 'Correct ref/hash backend assumptions, content filters, reset semantics and non-additive garbage-collection retention.',src)
def model(q):
 q[0]['options'][0]['text']='A ref naming one commit; its physical representation depends on the ref-storage backend'
 q[0]['options'][0]['explanation']='A loose SHA-1 ref in the files backend holds 40 hex digits plus a newline. Packed refs, reftable and SHA-256 use other representations.'
 q[0]['workedExample']=q[0]['workedExample'].replace('in a fresh repo', 'in a SHA-1 repository with an existing loose main ref and the files backend').replace('This is why branching in Git is O(1) and nearly free.', 'Creating the ref does not copy the project or walk its entire history; exact storage and hook costs depend on configuration.')
 q[2]['prompt']=q[2]['prompt'].replace('without changing any files.', 'on an attached branch, changing the message but no files.')
 q[2]['options'][2]['explanation']='Correct. Amend builds a replacement commit and moves the branch. The old object remains and may also be retained by other refs or reflogs.'
 q[3]['workedExample']=q[3]['workedExample'].replace('`count` rises by 5.', 'with automatic housekeeping disabled and ordinary loose-object storage, count rises by 5. Counting loose files during repacking is not a reliable total-object measurement.')
 q[4]['workedExample']=q[4]['workedExample'].replace('This is why a file saved with or without a final newline (or with CRLF instead of LF) shows up as a change in Git.', 'Different stored bytes normally produce different blobs. Configured clean filters and line-ending normalization can map different working-tree bytes to the same stored content.')
 q[5]['prompt']+=' Assume an existing commit, no staged changes except where explicitly stated, distinct new tag names, and no clean filter that maps the new file to existing stored content.'
 q[5]['options'][0]['explanation']='A branch command creates a ref to an existing commit, not a new content object.'
 q[5]['workedExample']=q[5]['workedExample'].replace('Check each with `git count-objects -v` before and after:', 'In separate controlled fixtures, with housekeeping disabled and the index otherwise unchanged, compare git count-objects -v before and after:')
 q[6]['options'][0]['text']='Inspect git reflog and create git branch rescue <old-tip> while that commit is still available'
 q[6]['options'][0]['explanation']='A rescue branch preserves the recovered commit without overwriting current working files. Reflogs and objects must still be retained.'
 q[6]['workedExample']=q[6]['workedExample'].replace('git reset --hard 9f8e7d6\n# or keep both:\ngit branch rescue 9f8e7d6','git branch rescue 9f8e7d6\n# inspect it before changing your current branch').replace('so act within weeks, not months.', 'but configuration and explicit expiry can shorten retention; recover promptly.')
 q[7]['options'][0]['explanation']='A normal full clone includes the relevant reachable history. Shallow or filtered clones may omit objects, but deletion from the current tree does not revoke the exposed credential.'
 q[7]['workedExample']=q[7]['workedExample'].replace('Anything reachable from the branch tip is kept and transferred:', 'In a normal full clone, the reachable chain includes:')
 q[9]['prompt']=q[9]['prompt'].replace('effectively vouch for', 'bind to the contents of').replace('Select all that apply.', 'Assume collision resistance; this does not establish author identity or code safety. Select all that apply.')
 q[10]['workedExample']=q[10]['workedExample'].replace('Under default settings you would have had 30 days (unreachable reflog expiry), plus up to two weeks for loose objects.', 'Default reflog and object expiry thresholds are independent, not additive: after a reflog expires, the old objects can already be old enough to prune. No extra two-week recovery window is guaranteed.')
questions(b+'git-object-model.questions.json',model,'Correct quiz recovery guarantees, ref formats, index-state assumptions and line-ending conversion.',src)
src=['https://git-scm.com/docs/git-rebase','https://git-scm.com/docs/git-merge','https://git-scm.com/docs/git-branch','https://git-scm.com/docs/git-push','https://git-scm.com/docs/git-reset','https://git-scm.com/docs/git-merge-base']
patch(b+'git-merge-rebase.md',[
('Both end with the same files, if the conflicts are resolved the same way.', 'For straightforward independent changes, both often produce the same final files. This is not guaranteed: rebase replays intermediate commits, may skip already-applied patches and can expose different conflicts.'),
('Everything starts with the **merge base**: the best common ancestor of the two branches', 'In this simple history there is one **merge base**, the best common ancestor of the two branches'),
('That is why it is called a **three-way merge**.', 'That is why it is called a **three-way merge**. Complex histories can have multiple best bases; recursive strategies can combine them into a virtual base.'),
('The originals still exist and are recorded in the reflog and in `ORIG_HEAD`.', 'The originals can be found via retained reflogs. ORIG_HEAD initially records the old branch tip, but other commands during the rebase can overwrite it.'),
("gives you **main's** version", 'gives you the upstream side **including commits already replayed**'),
('it also checks that the remote tip is something your local branch has actually incorporated.', 'it checks whether the remote-tracking tip is reachable from an entry in the local branch reflog used for the rewrite. This prevents the illustrated unseen-update overwrite; it does not prove the rewritten code preserved every remote change.'),
('`git branch -d feat` then refuses with "not fully merged",', 'git branch -d feat may refuse if checking against main; if feat has an upstream it checks that upstream instead,'),
('| Anything local | `git reflog`, reset to it |', '| Lost local committed history | Inspect git reflog and create a rescue branch at a retained commit |'),
('| Bad local merge/rebase | `git reset --hard ORIG_HEAD` |', '| Bad local merge/rebase | Inspect ORIG_HEAD/reflog, preserve current work, then choose a recovery commit |'),
('Reverting a merge commit needs `-m 1`', 'A hard reset discards tracked working-tree and staged changes, so it is not a general undo operation. Reflogs record ref changes, not every edit.\n\nReverting a merge commit needs `-m 1`'),
('| History | True, branchy | Linear, edited |', '| History | Original ancestry retained | Replayed ancestry; normally linear |'),
('giving a clean "one entry per merged change" view', 'giving a view that skips merged side-branch internals while retaining direct mainline commits'),
("Since Git 2.34 the default merge strategy is **ort**", 'Since Git 2.34 the default two-head merge strategy is **ort**')], 'Qualify merge/rebase equivalence, reflog-based force protection, branch deletion and safe recovery instructions.',src)
def merge(q):
 q[0]['prompt']+=' Assume merge.ff=true and no branch-specific options or hooks changing this behavior.'
 q[2]['prompt']=q[2]['prompt'].replace('runs `git rebase -i` over', 'reorders and rewrites commits with git rebase -i over')
 q[2]['options'][3]['explanation']='Replaying onto changed parents or rewriting content changes hashes. A rebase that has nothing to change can instead be a no-op.'
 q[4]['options'][0]['explanation']='During a rebase, ours is the upstream plus already replayed commits; in this conflict it has 45.'
 q[5]['options'][1]['explanation']='The original branch commits are not made ancestors by a squash. Local branch deletion checks the configured upstream if present, otherwise HEAD; it does not always refuse.'
 q[6]['prompt']+=' Assume force updates are permitted, the fetched tip has never been incorporated into this local branch, and nobody pushes again during the command.'
 q[6]['workedExample']=q[6]['workedExample'].replace('Y is gone from the remote.', 'Y is no longer the remote branch tip; the object can still exist.').replace("Git checks that Y appears in your local branch's reflog history", "Git checks whether Y is reachable from an entry in the local branch's reflog used for the rewrite")
 q[7]['prompt']+=' Assume a simple linear feature branch, no patch-equivalent commits already upstream, merge.ff=true, and no branch-specific merge options.'
 q[8]['prompt']=q[8]['prompt'].replace('What does `main` now contain?', 'The new commit adds a separate file, so this merge is clean. What does main now contain?')
 q[8]['options'][2]['explanation']='Conflicts depend on the edits; a fix modifying a file deleted by the revert may conflict. The question explicitly makes the new file independent.'
 q[8]['workedExample']=q[8]['workedExample'].replace('Only F\'s change is new, so only F is applied.', 'Here F adds an independent file, so that addition merges cleanly; edits to reverted feature files could instead conflict.')
 q[9]['workedExample']=q[9]['workedExample'].replace('`git merge-base --fork-point api` (which uses the remote-tracking reflog)', 'git merge-base --fork-point api ui if the local api reflog retained X; for a fetched remote branch use the appropriate origin/api ref')
 q[11]['options'][0]['text']='With merge commits, git log --first-parent main skips merged branch internals while retaining direct mainline commits'
 q[11]['options'][4]['text']='A merge commit preserves the existing parent relationships; this records ancestry, not a trustworthy wall-clock chronology'
 q[11]['options'][4]['explanation']='Correct. Commits carry editable author/committer timestamps, and independent branches have no intrinsic total time order. A merge preserves their existing ancestry.'
 q[11]['workedExample']=q[11]['workedExample'].replace('So `--first-parent` is a list of merges.', 'So --first-parent shows merges and any direct mainline commits, omitting side-branch internals.').replace('Rebase rewrites hashes, by definition.', 'Replaying commits onto changed parents rewrites hashes; a no-op rebase need not.')
questions(b+'git-merge-rebase.questions.json',merge,'Make merge configuration explicit, correct re-merge conflict example and separate ancestry from chronology.',src)
for name in ['git-object-model','git-merge-rebase']:
 for ext in ['.md','.questions.json']:
  if b+name+ext not in report['reviewed_files']:report['reviewed_files'].append(b+name+ext)
Path('docs/audit-root.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
