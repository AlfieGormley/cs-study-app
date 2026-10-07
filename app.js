import { render as md, plainText } from './markdown.js';
import { installExampleTools } from './examples.js';
import { loadDiagrams } from './diagrams.js';
import { installGlossary, searchGlossary, glossary } from './glossary.js';
installGlossary();
installExampleTools();

// ---------- Utilities ----------
const $ = (sel, el = document) => el.querySelector(sel);
const $$ = (sel, el = document) => [...el.querySelectorAll(sel)];
const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]);
const LEVELS = ['basic', 'intermediate', 'advanced'];
const today = () => new Date().toISOString().slice(0, 10);
const shuffle = (a) => {
  const arr = [...a];
  for (let i = arr.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [arr[i], arr[j]] = [arr[j], arr[i]];
  }
  return arr;
};
const pct = (a, b) => (b ? Math.round((a / b) * 100) : 0);
const plural = (n, word) => `${n} ${word}${n === 1 ? '' : 's'}`;
const chevron = '<svg class="chev" width="10" height="16" viewBox="0 0 10 16" aria-hidden="true"><path d="M2 2l6 6-6 6" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>';
const tick = '<svg width="14" height="14" viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12.5l4.5 4.5L19 7.5" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/></svg>';
const bookmarkIcon = (on) => `<svg width="22" height="22" viewBox="0 0 24 24" aria-hidden="true"><path d="M6 4h12v17l-6-4.5L6 21z" fill="${on ? 'currentColor' : 'none'}" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/></svg>`;
const badge = (level) => `<span class="badge ${esc(level)}">${esc(level)}</span>`;

// ---------- Persistent state (per device) ----------
const STORE_KEY = 'csstudy.v1';
const defaults = () => ({ done: {}, answers: {}, bookmarks: {}, pos: {}, last: null, days: [], fontScale: 1, session: null });
let state = defaults();
try {
  state = { ...defaults(), ...JSON.parse(localStorage.getItem(STORE_KEY) || '{}') };
} catch { /* private mode or corrupted: start fresh */ }
let saveTimer;
const save = (now = false) => {
  clearTimeout(saveTimer);
  const write = () => {
    try { localStorage.setItem(STORE_KEY, JSON.stringify(state)); } catch { /* storage unavailable */ }
  };
  now ? write() : (saveTimer = setTimeout(write, 300));
};
const markDay = () => {
  const d = today();
  if (state.days[state.days.length - 1] !== d) state.days = [...state.days, d].slice(-400);
};
const streak = () => {
  const days = new Set(state.days);
  let n = 0;
  const d = new Date();
  if (!days.has(today())) d.setDate(d.getDate() - 1); // streak survives until the end of today
  while (days.has(d.toISOString().slice(0, 10))) {
    n++;
    d.setDate(d.getDate() - 1);
  }
  return n;
};
const applyFont = () => document.documentElement.style.setProperty('--font-scale', state.fontScale);
applyFont();

const lessonKey = (s, l) => `${s}/${l}`;
const qKey = (s, q) => `${s}/${q}`;

// ---------- Data ----------
let index = null;
const modules = new Map();
async function getIndex() {
  if (!index) index = await (await fetch('data/index.json')).json();
  return index;
}
async function getModule(s, m) {
  const k = `${s}/${m}`;
  if (!modules.has(k)) {
    modules.set(k, fetch(`data/${s}/${m}.json`).then((r) => {
      if (!r.ok) throw new Error(`Couldn't load ${k}`);
      return r.json();
    }));
  }
  const [mod] = await Promise.all([modules.get(k), loadDiagrams()]);
  return mod;
}
async function getAllModules(subjectId) {
  const idx = await getIndex();
  const subs = subjectId ? idx.subjects.filter((s) => s.id === subjectId) : idx.subjects;
  return Promise.all(subs.flatMap((s) => s.modules.map((m) => getModule(s.id, m.id))));
}
let searchIdx = null;
let qIdx = null;
const getSearch = async () => (searchIdx ??= await (await fetch('data/search.json')).json());
const getQIndex = async () => (qIdx ??= await (await fetch('data/questions.json')).json());
// Question key "subject/qid" -> session item, using the prebuilt index.
const qItem = (key, idx) => {
  const [m, l, level, prompt, lessonTitle] = idx[key];
  const s = key.slice(0, key.indexOf('/'));
  return { s, m, l, qid: key.slice(s.length + 1), level, prompt, lessonTitle };
};

const findSubject = (s) => index.subjects.find((x) => x.id === s);
const findModuleMeta = (s, m) => findSubject(s)?.modules.find((x) => x.id === m);

function allQuestions(mods) {
  return mods.flatMap((mod) => mod.lessons.flatMap((l) =>
    l.questions.map((q) => ({ s: mod.subject, m: mod.id, l: l.id, qid: q.id, q, lessonTitle: l.title }))));
}

// ---------- Progress helpers ----------
function moduleProgress(s, mod) {
  const total = mod.lessons.length;
  const done = mod.lessons.filter((l) => state.done[lessonKey(s, l.id)]).length;
  return { done, total };
}
function subjectProgress(sub) {
  let done = 0, total = 0, questions = 0;
  for (const m of sub.modules) {
    const p = moduleProgress(sub.id, m);
    done += p.done;
    total += p.total;
    questions += m.lessons.reduce((n, l) => n + l.questionCount, 0);
  }
  return { done, total, questions };
}
function answerStats() {
  const vals = Object.values(state.answers);
  const right = vals.reduce((n, a) => n + a.c, 0);
  const wrong = vals.reduce((n, a) => n + a.w, 0);
  return { answered: vals.length, attempts: right + wrong, right, mistakes: vals.filter((a) => !a.last).length };
}

// ---------- Chrome (top bar, tab bar) ----------
const view = $('#view');
$('.skip-link').addEventListener('click', (event) => { event.preventDefault(); view.focus(); });
const topbar = $('#topbar');
function chrome({ title = '', back = null, backLabel = 'Back', tab = null, focus = false }) {
  document.title = title ? `${title} · CS Study` : 'CS Study';
  $('#topbar-title').textContent = title;
  const b = $('#back');
  b.hidden = !back;
  b.onclick = () => { location.hash = back; };
  $('#back-label').textContent = backLabel;
  $$('.tabbar a').forEach((a) => {
    const active = a.dataset.tab === tab;
    a.classList.toggle('active', active);
    if (active) a.setAttribute('aria-current', 'page');
    else a.removeAttribute('aria-current');
  });
  document.body.dataset.page = focus ? 'quiz' : title.toLowerCase();
  document.body.classList.toggle('focus', focus);
}
addEventListener('scroll', () => topbar.classList.toggle('scrolled', scrollY > 40), { passive: true });

function toast(text, action, onAction) {
  const t = $('#toast');
  t.innerHTML = `<span>${esc(text)}</span>${action ? `<button type="button">${esc(action)}</button>` : ''}`;
  t.hidden = false;
  if (action) $('button', t).onclick = () => { t.hidden = true; onAction(); };
  clearTimeout(toast.timer);
  toast.timer = setTimeout(() => { t.hidden = true; }, action ? 10000 : 2500);
}

// ---------- Views ----------
async function homeView() {
  const idx = await getIndex();
  chrome({ title: 'Learn', tab: 'learn' });
  const st = answerStats();
  const totalLessons = idx.subjects.reduce((n, s) => n + subjectProgress(s).total, 0);
  const doneLessons = idx.subjects.reduce((n, s) => n + subjectProgress(s).done, 0);
  let cont = '';
  if (state.last) {
    const [s, m, l] = state.last.split('/');
    const lm = findModuleMeta(s, m)?.lessons.find((x) => x.id === l);
    if (lm) {
      cont = `<div class="section-label">Continue</div>
        <a class="tile" href="#/l/${s}/${m}/${l}">
          <div class="row-meta" style="margin:0 0 6px">${badge(lm.level)}<span class="meta">${esc(findModuleMeta(s, m).title)}</span></div>
          <h3>${esc(lm.title)}</h3><p>${esc(lm.summary)}</p></a>`;
    }
  }
  view.innerHTML = `
    <div class="page-heading"><div><div class="eyebrow">YOUR COMPUTER SCIENCE COMPANION</div><h1 class="large-title">Make room for learning.</h1>
    <p class="subtitle">${streak() ? `🔥 ${plural(streak(), 'day')} streak` : 'Big ideas. Small steps. Build your understanding, one lesson at a time.'}</p></div><a class="settings-link" href="#/settings" aria-label="Settings">Settings <span aria-hidden="true">↗</span></a></div>
    <div class="stats">
      <div class="stat"><b>${doneLessons}<small style="font-size:13px;color:var(--muted)">/${totalLessons}</small></b><span>Lessons</span></div>
      <div class="stat"><b>${st.answered}</b><span>Questions</span></div>
      <div class="stat"><b>${st.attempts ? pct(st.right, st.attempts) + '%' : '–'}</b><span>Accuracy</span></div>
    </div>
    ${cont}
    <div class="section-label section-heading"><span>Explore subjects</span><span class="meta">${idx.subjects.length} subjects · ${totalLessons} lessons</span></div>
    <div class="subject-grid">
    ${idx.subjects.map((s, i) => {
      const p = subjectProgress(s);
      return `<a class="tile subject-tile" href="#/s/${s.id}" style="--subject-hue:${[245,170,210,280,30,335,155,225,265,195,315][i % 11]}">
        <div class="tile-top"><span class="subject-icon" aria-hidden="true">${['⌘','{ }','▤','⇄','▦','λ','◇','&lt;/&gt;','∀','≡','✧'][i % 11]}</span><span class="tile-arrow" aria-hidden="true">↗</span></div><h3>${esc(s.title)}</h3><p>${esc(s.description)}</p>
        <div class="row-meta"><span class="meta">${plural(s.modules.length, 'module')} · ${plural(p.total, 'lesson')} · ${plural(p.questions, 'question')}</span></div>
        <div class="tile-footer"><span>${p.done ? `${p.done} completed` : 'Ready when you are'}</span><span>${pct(p.done, p.total)}%</span></div><div class="progress" aria-label="${pct(p.done, p.total)}% complete"><div style="width:${pct(p.done, p.total)}%"></div></div></a>`;
    }).join('')}</div>
    <div class="section-label">More</div>
    <div class="list"><a class="row" href="#/dictionary"><div class="row-main"><div class="row-title">Technical dictionary</div><div class="row-sub">${glossary.length} quick definitions, from Redis to recursion</div></div>${chevron}</a><a class="row" href="#/settings"><div class="row-main"><div class="row-title">Settings</div><div class="row-sub">Text size, progress, offline</div></div>${chevron}</a></div>`;
}

async function subjectView(s) {
  await getIndex();
  const sub = findSubject(s);
  if (!sub) return notFound();
  chrome({ title: sub.title, back: '#/', backLabel: 'Learn', tab: 'learn' });
  view.innerHTML = `
    <h1 class="large-title">${esc(sub.title)}</h1>
    <p class="subtitle">${esc(sub.description)}</p>
    <div class="list">
    ${sub.modules.map((m, i) => {
      const p = moduleProgress(s, m);
      const q = m.lessons.reduce((n, l) => n + l.questionCount, 0);
      return `<a class="row" href="#/m/${s}/${m.id}">
        <div class="num">${p.done === p.total && p.total ? tick : i + 1}</div>
        <div class="row-main"><div class="row-title">${esc(m.title)}</div>
          <div class="row-sub">${esc(m.summary)}</div>
          <div class="row-meta"><span class="meta">${p.done}/${plural(p.total, 'lesson')} · ${plural(q, 'question')}</span></div>
          <div class="progress"><div style="width:${pct(p.done, p.total)}%"></div></div>
        </div>${chevron}</a>`;
    }).join('')}
    </div>
    <div class="btn-row"><button class="btn secondary" id="mix">Practise all of ${esc(sub.title)}</button></div>`;
  $('#mix').onclick = () => { location.hash = `#/practice?s=${s}`; };
}

async function moduleView(s, m) {
  await getIndex();
  const sub = findSubject(s);
  const meta = findModuleMeta(s, m);
  if (!meta) return notFound();
  chrome({ title: meta.title, back: `#/s/${s}`, backLabel: sub.title, tab: 'learn' });
  const q = meta.lessons.reduce((n, l) => n + l.questionCount, 0);
  view.innerHTML = `
    <h1 class="large-title">${esc(meta.title)}</h1>
    <p class="subtitle">${esc(meta.summary)}</p>
    <div class="list">
    ${meta.lessons.map((l) => {
      const done = state.done[lessonKey(s, l.id)];
      return `<a class="row" href="#/l/${s}/${m}/${l.id}">
        <div class="check ${done ? 'done' : ''}">${done ? tick : ''}</div>
        <div class="row-main"><div class="row-title">${esc(l.title)}</div>
          <div class="row-sub">${esc(l.summary)}</div>
          <div class="row-meta">${badge(l.level)}<span class="meta">${l.minutes} min · ${plural(l.questionCount, 'question')}</span></div>
        </div>${chevron}</a>`;
    }).join('')}
    </div>
    <div class="btn-row"><button class="btn" id="quiz-mod">Quiz this module (${q})</button></div>`;
  $('#quiz-mod').onclick = async () => {
    const mod = await getModule(s, m);
    startSession(allQuestions([mod]), `${meta.title} quiz`, `#/m/${s}/${m}`, { shuffle: true });
  };
}

async function lessonView(s, m, l) {
  await getIndex();
  const meta = findModuleMeta(s, m);
  const mod = await getModule(s, m).catch(() => null);
  const lesson = mod?.lessons.find((x) => x.id === l);
  if (!lesson) return notFound();
  const key = lessonKey(s, l);
  chrome({ title: lesson.title, back: `#/m/${s}/${m}`, backLabel: meta.title, tab: 'learn' });
  state.last = `${s}/${m}/${l}`;
  save();
  const i = mod.lessons.indexOf(lesson);
  const next = mod.lessons[i + 1];
  const done = !!state.done[key];
  view.innerHTML = `
    <div class="lesson-head">
      <div class="row-meta">${badge(lesson.level)}<span class="meta">${esc(meta.title)} · ${lesson.minutes} min read</span></div>
      <h1 class="large-title">${esc(lesson.title)}</h1>
    </div>
    <p class="term-help">Tap dotted-underlined terms for a quick definition. <a href="#/dictionary">Browse dictionary</a></p>
    <article class="prose">${md(lesson.body)}</article>
    <div class="section-label">Check your understanding</div>
    <button class="btn" id="practise" ${lesson.questions.length ? '' : 'disabled'}>Practise ${plural(lesson.questions.length, 'question')}</button>
    <div class="btn-row"><button class="btn ${done ? 'plain' : 'secondary'}" id="done">${done ? '✓ Completed' : 'Mark as complete'}</button></div>
    ${next ? `<div class="section-label">Up next</div>
      <div class="list"><a class="row" href="#/l/${s}/${m}/${next.id}"><div class="row-main">
        <div class="row-title">${esc(next.title)}</div><div class="row-meta">${badge(next.level)}<span class="meta">${next.minutes} min</span></div>
      </div>${chevron}</a></div>` : ''}`;
  const headings = $$('article.prose h2', view);
  if (headings.length > 2) {
    const contents = document.createElement('details');
    contents.className = 'lesson-contents';
    contents.innerHTML = '<summary>In this lesson <span class="meta">' + headings.length + ' sections</span></summary><div>' + headings.map((h, n) => `<button type="button" data-section="${n}">${esc(h.textContent)}</button>`).join('') + '</div>';
    $('.lesson-head').after(contents);
    contents.addEventListener('click', (event) => {
      const button = event.target.closest('[data-section]');
      if (!button) return;
      const heading = headings[Number(button.dataset.section)];
      contents.open = false;
      heading.tabIndex = -1;
      heading.focus({ preventScroll: true });
      heading.scrollIntoView({ block: 'start' });
    });
  }
  $('#practise').onclick = () => {
    startSession(allQuestions([{ ...mod, lessons: [lesson] }]), lesson.title, `#/l/${s}/${m}/${l}`, {});
  };
  $('#done').onclick = (e) => {
    if (state.done[key]) delete state.done[key];
    else { state.done[key] = Date.now(); markDay(); }
    save();
    const on = !!state.done[key];
    e.currentTarget.textContent = on ? '✓ Completed' : 'Mark as complete';
    e.currentTarget.className = `btn ${on ? 'plain' : 'secondary'}`;
  };
  // Restore the reading position (handy when you get interrupted mid-lesson).
  const y = state.pos[key];
  if (y) requestAnimationFrame(() => scrollTo(0, y));
  onScrollSave = () => { state.pos[key] = Math.round(scrollY); save(); };
}
let onScrollSave = null;
addEventListener('scroll', () => onScrollSave?.(), { passive: true });

// ---------- Quiz sessions ----------
function startSession(items, title, back, { shuffle: mix = false, limit = 0 } = {}) {
  let list = items.map(({ s, m, l, qid }) => ({ s, m, l, qid }));
  if (mix) list = shuffle(list);
  if (limit) list = list.slice(0, limit);
  if (!list.length) return toast('No questions match that selection.');
  state.session = { id: Date.now().toString(36), title, back, items: list, i: 0, picked: [], checked: false, results: [] };
  save(true);
  location.hash = `#/quiz/${state.session.id}`;
}

async function resolveItem(item) {
  const mod = await getModule(item.s, item.m);
  const lesson = mod.lessons.find((x) => x.id === item.l);
  return { lesson, q: lesson?.questions.find((x) => x.id === item.qid) };
}

function isCorrect(q, picked) {
  if (q.type === 'multi') {
    const want = new Set(q.answer);
    return picked.length === want.size && picked.every((p) => want.has(p));
  }
  return picked[0] === q.answer;
}

async function quizView(id) {
  await getIndex();
  const ses = state.session;
  if (!ses || ses.id !== id) {
    location.replace('#/practice');
    return;
  }
  if (ses.i >= ses.items.length) return quizSummary(ses);
  const item = ses.items[ses.i];
  const { lesson, q } = await resolveItem(item);
  if (!q) { // content changed since the session was saved: skip it
    ses.items.splice(ses.i, 1);
    save();
    return quizView(id);
  }
  chrome({ title: ses.title, back: ses.back, backLabel: 'Exit', focus: true });
  const key = qKey(item.s, q.id);
  const multi = q.type === 'multi';
  const answers = new Set(multi ? q.answer : [q.answer]);
  const letters = 'ABCDEF';

  const draw = () => {
    const { picked, checked } = ses;
    const right = checked && isCorrect(q, picked);
    const marked = !!state.bookmarks[key];
    view.innerHTML = `
      <div class="quiz-progress">
        <span class="meta">${ses.i + 1} / ${ses.items.length}</span>
        <div class="progress"><div style="width:${pct(ses.i + (checked ? 1 : 0), ses.items.length)}%"></div></div>
        <button class="icon-btn" id="bm" aria-pressed="${marked}" aria-label="Bookmark question">${bookmarkIcon(marked)}</button>
      </div>
      <div class="row-meta" style="margin:0 0 10px">${badge(q.level)}<span class="meta">${esc(lesson.title)}</span></div>
      <div class="quiz-prompt prose">${md(q.prompt)}</div>
      ${multi ? '<div class="quiz-hint">Select all that apply.</div>' : ''}
      ${checked ? `<div role="status" tabindex="-1" class="verdict ${right ? 'good' : 'bad'}">${right ? 'Correct!' : multi ? 'Not quite. Compare your picks with the correct answers below.' : 'Not quite. See why below.'}</div>` : ''}
      <div class="options">
        ${q.options.map((o, i) => {
          const isAns = answers.has(i);
          const sel = picked.includes(i);
          let cls = '';
          let tag = '';
          if (checked) {
            if (isAns) { cls = 'correct'; tag = sel ? 'Your answer · Correct' : 'Correct answer'; }
            else if (sel) { cls = 'wrong'; tag = 'Your answer · Incorrect'; }
            else { cls = 'dim'; tag = 'Incorrect'; }
          } else if (sel) cls = 'selected';
          return `<div class="answer-card ${cls}"><button class="option ${multi ? 'multi' : ''} ${cls}" data-i="${i}" aria-pressed="${sel}" ${checked ? 'disabled' : ''}>
            <span class="key">${checked && isAns ? tick : letters[i]}</span>
            <span class="opt-body">
              <span class="opt-text prose">${md(o.text, { interactive: false })}</span>
            </span></button>
            ${checked ? `<div class="opt-why prose"><span class="opt-tag">${tag}</span>${md(o.explanation)}</div>` : ''}</div>`;
        }).join('')}
      </div>
      ${checked ? `
        <div class="card worked prose"><h3>Worked example</h3>${md(q.workedExample)}</div>
        <a class="link-card" href="${esc(q.link.url)}" target="_blank" rel="noopener">
          <span class="ic"><svg width="18" height="18" viewBox="0 0 24 24" aria-hidden="true"><path d="M14 4h6v6M20 4l-9 9M18 14v5a1 1 0 01-1 1H5a1 1 0 01-1-1V7a1 1 0 011-1h5" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg></span>
          <span><b>Learn more: ${esc(q.link.title)}</b><small>${esc(new URL(q.link.url).hostname)}</small></span></a>
        <a class="link-card" href="#/l/${item.s}/${item.m}/${item.l}">
          <span class="ic"><svg width="18" height="18" viewBox="0 0 24 24" aria-hidden="true"><path d="M4 5.5A1.5 1.5 0 015.5 4H11v16H5.5A1.5 1.5 0 014 18.5zM13 4h5.5A1.5 1.5 0 0120 5.5v13a1.5 1.5 0 01-1.5 1.5H13z" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/></svg></span>
          <span><b>Revisit the lesson</b><small>${esc(lesson.title)}</small></span></a>` : ''}
      <div class="sticky-actions">
        ${checked
          ? `<button class="btn" id="next">${ses.i + 1 < ses.items.length ? 'Next question' : 'See results'}</button>`
          : `<button class="btn" id="check" ${picked.length ? '' : 'disabled'}>Check answer</button>`}
      </div>`;

    $$('.option', view).forEach((b) => (b.onclick = () => {
      const i = Number(b.dataset.i);
      if (multi) ses.picked = ses.picked.includes(i) ? ses.picked.filter((x) => x !== i) : [...ses.picked, i];
      else ses.picked = [i];
      save();
      draw();
      $(`.option[data-i="${i}"]`, view)?.focus({ preventScroll: true });
    }));
    $('#bm').onclick = () => {
      if (state.bookmarks[key]) delete state.bookmarks[key];
      else state.bookmarks[key] = Date.now();
      save();
      draw();
      $('#bm').focus({ preventScroll: true });
    };
    $('#check')?.addEventListener('click', () => {
      const ok = isCorrect(q, ses.picked);
      const a = state.answers[key] || { c: 0, w: 0 };
      state.answers[key] = { c: a.c + (ok ? 1 : 0), w: a.w + (ok ? 0 : 1), last: ok, t: Date.now() };
      ses.checked = true;
      ses.results.push({ ...item, ok, level: q.level });
      markDay();
      save(true);
      draw();
      $('.verdict', view)?.focus({ preventScroll: true });
      $('.verdict', view)?.scrollIntoView({ behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'instant' : 'smooth', block: 'center' });
    });
    $('#next')?.addEventListener('click', () => {
      ses.i++;
      ses.picked = [];
      ses.checked = false;
      save(true);
      quizView(id).then(() => { scrollTo(0, 0); view.focus({ preventScroll: true }); });
    });
  };
  draw();
}

async function quizSummary(ses) {
  chrome({ title: 'Results', back: ses.back, backLabel: 'Done', focus: true });
  const total = ses.results.length;
  const right = ses.results.filter((r) => r.ok).length;
  const p = pct(right, total);
  const byLevel = LEVELS.map((lv) => {
    const rs = ses.results.filter((r) => r.level === lv);
    return rs.length ? `<div class="setting"><span>${badge(lv)}</span><span>${rs.filter((r) => r.ok).length} / ${rs.length}</span></div>` : '';
  }).join('');
  const wrong = ses.results.filter((r) => !r.ok);
  const wrongRows = await Promise.all(wrong.map(async (r) => {
    const { q, lesson } = await resolveItem(r);
    return q ? `<a class="row" href="#/l/${r.s}/${r.m}/${r.l}"><div class="row-main"><div class="row-title">${esc(plainText(q.prompt).slice(0, 110))}</div><div class="row-sub">${esc(lesson.title)}</div></div>${chevron}</a>` : '';
  }));
  const C = 2 * Math.PI * 54;
  view.innerHTML = `
    <h1 class="large-title center">Session complete</h1>
    <p class="subtitle center" style="margin-inline:auto">Every question is another step forward.</p>
    <svg class="score-ring" role="img" viewBox="0 0 120 120" aria-label="${p}% correct">
      <circle cx="60" cy="60" r="54" fill="none" stroke="var(--surface-2)" stroke-width="10"/>
      ${p ? '' : '<!--'}<circle cx="60" cy="60" r="54" fill="none" stroke="${p >= 70 ? 'var(--good)' : p >= 40 ? 'var(--intermediate)' : 'var(--bad)'}" stroke-width="10"
        stroke-linecap="round" stroke-dasharray="${(C * p) / 100} ${C}" transform="rotate(-90 60 60)"/>${p ? '' : '-->'}
      <text x="60" y="68" text-anchor="middle" font-size="26" font-weight="700" fill="var(--text)">${p}%</text>
    </svg>
    <p class="center" style="margin:0 0 20px"><b>${right} of ${total}</b> correct · ${esc(ses.title)}</p>
    ${byLevel ? `<div class="list">${byLevel}</div>` : ''}
    ${wrong.length ? `<div class="section-label">To revisit</div><div class="list">${wrongRows.join('')}</div>` : ''}
    <div class="btn-row">${wrong.length ? '<button class="btn" id="retry">Retry the ones I got wrong</button>' : ''}</div>
    <div class="btn-row"><a class="btn plain" href="${esc(ses.back)}">Done</a></div>`;
  $('#retry')?.addEventListener('click', () => startSession(wrong, `${ses.title} (retry)`, ses.back, {}));
}

// ---------- Practice ----------
async function practiceView(params) {
  const idx = await getIndex();
  chrome({ title: 'Practice', tab: 'practice' });
  const p = practiceView.prefs ??= { s: idx.subjects[0]?.id, mods: null, levels: new Set(LEVELS), n: 10, filter: 'all' };
  if (params.get('s') && params.get('s') !== p.s) { p.s = params.get('s'); p.mods = null; }
  const sub = findSubject(p.s) ?? idx.subjects[0];
  if (!sub) return (view.innerHTML = '<div class="empty"><b>No content yet</b></div>');
  p.mods ??= new Set(sub.modules.map((m) => m.id));
  const all = allQuestions(await getAllModules(sub.id));

  const pool = () => all.filter(({ s, m, q }) => {
    if (!p.mods.has(m) || !p.levels.has(q.level)) return false;
    const a = state.answers[qKey(s, q.id)];
    if (p.filter === 'new') return !a;
    if (p.filter === 'wrong') return a && !a.last;
    return true;
  });
  const chip = (group, val, label, on) => `<button class="chip" data-g="${group}" data-v="${esc(val)}" aria-pressed="${on}">${esc(label)}</button>`;
  const draw = () => {
    const n = pool().length;
    view.innerHTML = `
      <h1 class="large-title">Practice</h1>
      <p class="subtitle">Build a custom quiz from any mix of topics and levels.</p>
      ${idx.subjects.length > 1 ? `<div class="section-label"><label for="practice-subject">Subject</label></div><select class="subject-select" id="practice-subject">${idx.subjects.map((s) => `<option value="${esc(s.id)}" ${s.id === sub.id ? 'selected' : ''}>${esc(s.title)}</option>`).join('')}</select>` : ''}
      <div class="section-label">Modules <button class="chip" data-g="allmods" style="float:right;padding:2px 10px;font-size:12px">${p.mods.size === sub.modules.length ? 'None' : 'All'}</button></div>
      <div class="chips">${sub.modules.map((m) => chip('m', m.id, m.title, p.mods.has(m.id))).join('')}</div>
      <div class="section-label">Difficulty</div>
      <div class="chips">${LEVELS.map((l) => chip('l', l, l[0].toUpperCase() + l.slice(1), p.levels.has(l))).join('')}</div>
      <div class="section-label">Questions</div>
      <div class="chips">${[['all', 'Any'], ['new', 'Not yet answered'], ['wrong', 'Got wrong last time']].map(([v, t]) => chip('f', v, t, p.filter === v)).join('')}</div>
      <div class="section-label">How many</div>
      <div class="chips">${[5, 10, 20, 50, 0].map((v) => chip('n', v, v ? String(v) : 'All', p.n === v)).join('')}</div>
      <div class="sticky-actions"><button class="btn" id="go" ${n ? '' : 'disabled'}>Start · ${p.n && p.n < n ? p.n : n} of ${plural(n, 'question')}</button></div>`;
    $('#practice-subject')?.addEventListener('change', (event) => { location.hash = `#/practice?s=${event.target.value}`; });
    $$('.chip', view).forEach((c) => (c.onclick = () => {
      const { g, v } = c.dataset;
      if (g === 's') { location.hash = `#/practice?s=${v}`; return; }
      if (g === 'allmods') p.mods = p.mods.size === sub.modules.length ? new Set() : new Set(sub.modules.map((m) => m.id));
      if (g === 'm') p.mods.has(v) ? p.mods.delete(v) : p.mods.add(v);
      if (g === 'l') p.levels.has(v) ? p.levels.delete(v) : p.levels.add(v);
      if (g === 'f') p.filter = v;
      if (g === 'n') p.n = Number(v);
      draw();
      $$('.chip', view).find((el) => el.dataset.g === g && el.dataset.v === v)?.focus({ preventScroll: true });
    }));
    $('#go').onclick = () => startSession(pool(), `${sub.title} practice`, '#/practice', { shuffle: true, limit: p.n });
  };
  draw();
}

// ---------- Review ----------
async function reviewView() {
  chrome({ title: 'Review', tab: 'review' });
  const idx = await getQIndex();
  const keys = (obj) => Object.keys(obj).filter((k) => idx[k]);
  const mistakes = keys(state.answers).filter((k) => state.answers[k].last === false).map((k) => qItem(k, idx));
  const marked = keys(state.bookmarks).map((k) => qItem(k, idx));
  // Spaced review: answered correctly, longest ago first.
  const stale = keys(state.answers).filter((k) => state.answers[k].last)
    .sort((a, b) => state.answers[a].t - state.answers[b].t).map((k) => qItem(k, idx));
  const row = (x) => `<a class="row" href="#/l/${x.s}/${x.m}/${x.l}"><div class="row-main">
      <div class="row-title">${esc(x.prompt)}</div>
      <div class="row-meta">${badge(x.level)}<span class="meta">${esc(x.lessonTitle)}</span></div></div>${chevron}</a>`;
  view.innerHTML = `
    <h1 class="large-title">Review</h1>
    <p class="subtitle">Go back over the questions you missed and the ones you saved.</p>
    <div class="stats">
      <div class="stat"><b>${mistakes.length}</b><span>To fix</span></div>
      <div class="stat"><b>${marked.length}</b><span>Bookmarked</span></div>
      <div class="stat"><b>${streak()}</b><span>Day streak</span></div>
    </div>
    <div class="btn-row"><button class="btn" id="r-mis" ${mistakes.length ? '' : 'disabled'}>Retry mistakes (${mistakes.length})</button></div>
    <div class="btn-row"><button class="btn secondary" id="r-bm" ${marked.length ? '' : 'disabled'}>Bookmarked (${marked.length})</button>
      <button class="btn secondary" id="r-old" ${stale.length ? '' : 'disabled'}>Refresh oldest (${Math.min(stale.length, 10)})</button></div>
    ${mistakes.length ? `<div class="section-label">Mistakes</div><div class="list">${mistakes.slice(0, 30).map(row).join('')}</div>` : ''}
    ${marked.length ? `<div class="section-label">Bookmarked</div><div class="list">${marked.map(row).join('')}</div>` : ''}
    ${!mistakes.length && !marked.length ? `<div class="empty"><span class="empty-icon" aria-hidden="true">↺</span><b>Your next breakthrough starts here</b>Questions you miss or save will appear here.<a class="btn secondary" href="#/practice">Try a practice quiz</a></div>` : ''}`;
  $('#r-mis').onclick = () => startSession(mistakes.slice(0, 30), 'Mistakes', '#/review', { shuffle: true });
  $('#r-bm').onclick = () => startSession(marked, 'Bookmarked', '#/review', { shuffle: true });
  $('#r-old').onclick = () => startSession(stale.slice(0, 10), 'Refresher', '#/review', { shuffle: true });
}

// ---------- Search ----------
let searchText = '';
async function searchView() {
  await getIndex();
  chrome({ title: 'Search', tab: 'search' });
  view.innerHTML = `
    <h1 class="large-title">Search</h1>
    <p class="subtitle">Find an idea, revisit a concept, or discover something new. <a href="#/dictionary">Look up a technical term ↗</a></p>
    <label class="sr-only" for="q">Search lessons</label><input class="search-input" id="q" type="search" placeholder="e.g. consistent hashing, Raft, LRU" autocomplete="off" value="${esc(searchText)}">
    <p class="meta" id="search-status" role="status"></p><div id="results"></div>`;
  const docs = (await getSearch()).map((d) => ({
    s: d.s, m: d.m, modTitle: d.mt, text: d.x,
    l: { id: d.l, title: d.t, summary: d.sum, level: d.lv },
    hay: `${d.t} ${d.sum} ${d.x}`.toLowerCase(),
  }));
  const input = $('#q');
  const run = () => {
    searchText = input.value;
    const terms = searchText.toLowerCase().split(/\s+/).filter((t) => t.length > 1);
    const out = $('#results');
    if (!terms.length) { $('#search-status').textContent = ''; out.innerHTML = '<div class="empty">Search every lesson by keyword.</div>'; return; }
    const hits = docs
      .map((d) => {
        if (!terms.every((t) => d.hay.includes(t))) return null;
        const title = d.l.title.toLowerCase();
        const score = terms.reduce((n, t) => n + (title.includes(t) ? 10 : 0) + d.hay.split(t).length, 0);
        return { d, score };
      })
      .filter(Boolean)
      .sort((a, b) => b.score - a.score)
      .slice(0, 40);
    const pattern = new RegExp(terms.map((t) => t.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')).join('|'), 'gi');
    const mark = (s) => {
      let html = '', last = 0;
      for (const match of s.matchAll(pattern)) {
        html += esc(s.slice(last, match.index)) + `<mark>${esc(match[0])}</mark>`;
        last = match.index + match[0].length;
      }
      return html + esc(s.slice(last));
    };
    $('#search-status').textContent = hits.length === 40 ? 'Showing the top 40 matches' : plural(hits.length, 'matching lesson');
    out.innerHTML = hits.length ? `<div class="list">${hits.map(({ d }) => {
      const at = d.text.toLowerCase().indexOf(terms[0]);
      const snip = at >= 0 ? (at > 40 ? '…' : '') + d.text.slice(Math.max(0, at - 40), at + 110) + '…' : d.l.summary;
      return `<a class="row" href="#/l/${d.s}/${d.m}/${d.l.id}"><div class="row-main">
        <div class="row-title">${mark(d.l.title)}</div><div class="row-sub">${mark(snip)}</div>
        <div class="row-meta">${badge(d.l.level)}<span class="meta">${esc(d.modTitle)}</span></div></div>${chevron}</a>`;
    }).join('')}</div>` : '<div class="empty"><b>No matches</b>Try fewer or different words.</div>';
  };
  input.oninput = run;
  run();
}

// ---------- Technical dictionary ----------
function dictionaryView(params) {
  chrome({ title: 'Dictionary', back: '#/', backLabel: 'Learn', tab: 'learn' });
  view.innerHTML = `<h1 class="large-title">Technical dictionary</h1>
    <p class="subtitle">Plain-language explanations for the terms you meet while studying. You can also tap dotted-underlined terms in lessons.</p>
    <label class="sr-only" for="dictionary-query">Search the technical dictionary</label>
    <input class="search-input" id="dictionary-query" type="search" placeholder="Try Redis, DNS, or binary search" autocomplete="off" value="${esc(params.get('q') || '')}">
    <p class="meta" id="dictionary-status" role="status"></p><div id="dictionary-results" class="dictionary-results"></div>`;
  const input = $('#dictionary-query');
  const draw = () => {
    const results = searchGlossary(input.value);
    $('#dictionary-status').textContent = `${plural(results.length, 'term')}${input.value.trim() ? ' found' : ' to explore'}`;
    $('#dictionary-results').innerHTML = results.length ? results.map((entry) => `<article class="card dictionary-entry">
      <div class="term-category">${esc(entry.category)}</div><h2>${esc(entry.term)}</h2>
      <p>${esc(entry.definition)}</p>${entry.example ? `<p class="term-example"><b>Example</b> ${esc(entry.example)}</p>` : ''}
      ${entry.aliases.length ? `<p class="meta">Also called: ${entry.aliases.map(esc).join(', ')}</p>` : ''}
      ${entry.source ? `<a class="dictionary-source" href="${esc(entry.source)}" target="_blank" rel="noopener">Official documentation ↗</a>` : ''}</article>`).join('') : '<div class="empty"><b>No matching terms</b>Try a shorter term or an abbreviation, such as DNS.</div>';
  };
  input.addEventListener('input', draw); draw();
}

// ---------- Settings ----------
async function settingsView() {
  const idx = await getIndex();
  chrome({ title: 'Settings', back: '#/', backLabel: 'Learn', tab: 'learn' });
  const st = answerStats();
  const offline = 'serviceWorker' in navigator && navigator.serviceWorker.controller;
  view.innerHTML = `
    <h1 class="large-title">Settings</h1>
    <div class="section-label">Reading</div>
    <div class="list">
      <div class="setting"><span>Text size <span class="meta" id="fs">${Math.round(state.fontScale * 100)}%</span></span>
        <span class="stepper"><button id="fs-down" aria-label="Smaller text">A−</button><button id="fs-up" aria-label="Larger text">A+</button></span></div>
    </div>
    <div class="section-label">Progress</div>
    <div class="list">
      <div class="setting"><span>Lessons completed</span><b>${Object.keys(state.done).length}</b></div>
      <div class="setting"><span>Questions answered</span><b>${st.answered}</b></div>
      <div class="setting"><span>Total attempts</span><b>${st.attempts}</b></div>
      <div class="setting"><button class="danger" id="reset">Reset all progress</button></div>
    </div>
    <div class="section-label">App</div>
    <div class="list">
      <div class="setting"><span>Offline ready</span><b>${offline ? 'Yes' : 'Not yet'}</b></div>
      <div class="setting"><span>Content</span><span class="meta">${idx.subjects.map((s) => `${esc(s.title)}: ${plural(subjectProgress(s).total, 'lesson')}`).join('<br>')}</span></div>
    </div>
    <p class="meta" style="margin:16px 4px">Your progress is stored only on this device.</p>`;
  const setFs = (d) => {
    state.fontScale = Math.min(1.4, Math.max(0.85, Math.round((state.fontScale + d) * 100) / 100));
    applyFont();
    save();
    $('#fs').textContent = `${Math.round(state.fontScale * 100)}%`;
  };
  $('#fs-down').onclick = () => setFs(-0.05);
  $('#fs-up').onclick = () => setFs(0.05);
  $('#reset').onclick = () => {
    if (!confirm('Reset all lessons, answers and bookmarks? This cannot be undone.')) return;
    state = { ...defaults(), fontScale: state.fontScale };
    save(true);
    toast('Progress reset');
    settingsView();
  };
}

function notFound() {
  chrome({ title: 'Not found', back: '#/', backLabel: 'Learn' });
  view.innerHTML = '<div class="empty"><b>Page not found</b>This content may have moved.</div>';
}

// ---------- Router ----------
const routes = [
  [/^\/?$/, homeView],
  [/^\/s\/([\w-]+)$/, subjectView],
  [/^\/m\/([\w-]+)\/([\w-]+)$/, moduleView],
  [/^\/l\/([\w-]+)\/([\w-]+)\/([\w-]+)$/, lessonView],
  [/^\/quiz\/(\w+)$/, quizView],
  [/^\/practice$/, practiceView, true],
  [/^\/review$/, reviewView],
  [/^\/search$/, searchView],
  [/^\/dictionary$/, dictionaryView, true],
  [/^\/settings$/, settingsView],
];
async function route() {
  onScrollSave = null;
  const [path, query = ''] = location.hash.replace(/^#/, '').split('?');
  scrollTo(0, 0);
  for (const [re, fn, wantsParams] of routes) {
    const m = path.match(re);
    if (m) {
      try {
        await (wantsParams ? fn(new URLSearchParams(query)) : fn(...m.slice(1)));
      } catch (e) {
        console.error(e);
        view.innerHTML = `<div class="empty"><b>Something went wrong</b>${esc(e.message)}<br><br>If you're offline, open the app once with a connection so it can save the content.</div>`;
      }
      view.focus({ preventScroll: true });
      return;
    }
  }
  notFound();
}
addEventListener('hashchange', route);
addEventListener('pagehide', () => save(true));
document.addEventListener('visibilitychange', () => document.hidden && save(true));
route();

// ---------- Offline support ----------
if ('serviceWorker' in navigator && (location.protocol === 'https:' || location.hostname === 'localhost')) {
  const hadController = !!navigator.serviceWorker.controller;
  navigator.serviceWorker.register('sw.js').catch((e) => console.warn('SW registration failed', e));
  navigator.serviceWorker.addEventListener('controllerchange', () => {
    if (hadController) toast('New content is available.', 'Reload', () => location.reload());
  });
}
