// Remove only explicitly retired subjects, never progress missing from a partial
// index. A saved question snapshot must not resurrect a removed course.
export function retireSubjects(state, subjects = []) {
  const retired = new Set(subjects);
  const removedKey = (key) => retired.has(String(key).split('/')[0]);
  let changed = false;
  for (const field of ['done', 'answers', 'bookmarks', 'pos', 'lessonMigrations']) {
    for (const key of Object.keys(state[field] ?? {})) {
      if (!removedKey(key)) continue;
      delete state[field][key];
      changed = true;
    }
  }
  if (state.last && removedKey(state.last)) {
    state.last = null;
    changed = true;
  }
  const session = state.session;
  if (session?.items.some((item) => retired.has(item.s))) {
    const oldIndex = session.i;
    const currentRemoved = retired.has(session.items[oldIndex]?.s);
    session.i = session.items.slice(0, oldIndex).filter((item) => !retired.has(item.s)).length;
    session.items = session.items.filter((item) => !retired.has(item.s));
    session.results = session.results.filter((item) => !retired.has(item.s));
    session.title = 'Practice';
    session.back = '#/practice';
    if (currentRemoved) {
      session.picked = [];
      session.checked = false;
      delete session.currentQuestion;
    } else if (session.currentQuestion) {
      session.currentQuestion.index = session.i;
    }
    if (!session.items.length) state.session = null;
    changed = true;
  }
  return changed;
}
