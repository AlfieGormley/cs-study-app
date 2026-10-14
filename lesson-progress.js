const key = (subject, lesson) => `${subject}/${lesson}`;

export function migrationProblems(module) {
  const migrations = module.migrations ?? {};
  if (!migrations || Array.isArray(migrations) || typeof migrations !== 'object') return ['migrations must map original lesson ids to ordered new ids'];
  const active = new Set(module.lessons), targets = new Set(), problems = [];
  for (const [original, ids] of Object.entries(migrations)) {
    if (active.has(original)) problems.push(`migration ${original} must retire its original lesson id`);
    if (!Array.isArray(ids) || !ids.length) { problems.push(`migration ${original} needs an ordered array of new ids`); continue; }
    const positions = ids.map((id) => module.lessons.indexOf(id));
    if (positions.some((position, i) => i > 0 && position <= positions[i - 1])) problems.push(`migration ${original} must follow the curriculum order`);
    for (const id of ids) {
      if (typeof id !== 'string' || !active.has(id)) problems.push(`migration ${original} contains an inactive lesson id`);
      if (id === original || targets.has(id)) problems.push(`migration ${original} must use distinct new ids`);
      targets.add(id);
    }
  }
  return problems;
}

// Expand a completed original into its short lessons once. Retain the original
// timestamp so both saved progress and completion-age filters survive the split.
export function migrateLessonProgress(state, index) {
  let changed = false;
  const migrations = state.lessonMigrations ??= {};
  for (const subject of index.subjects) for (const module of subject.modules) {
    for (const [original, lessons] of Object.entries(module.migrations ?? {})) {
      const originalKey = key(subject.id, original);
      if (!migrations[originalKey]) {
        const completedAt = state.done[originalKey];
        if (completedAt) for (const id of lessons) state.done[key(subject.id, id)] ??= completedAt;
        migrations[originalKey] = true;
        changed = true;
      }
      if (state.last === `${subject.id}/${module.id}/${original}`) {
        const resume = lessons.find((id) => !state.done[key(subject.id, id)]) ?? lessons[0];
        state.last = `${subject.id}/${module.id}/${resume}`;
        changed = true;
      }
    }
  }
  return changed;
}

export function migratedLessonId(subject, module, lesson, done) {
  const lessons = module.migrations?.[lesson];
  return lessons ? lessons.find((id) => !done[key(subject, id)]) ?? lessons[0] : lesson;
}

export function updateOriginalCompletion(subject, module, lesson, done) {
  const original = lesson.sourceLesson;
  const lessons = module.migrations?.[original];
  if (!lessons) return;
  const dates = lessons.map((id) => done[key(subject, id)]);
  if (dates.every(Boolean)) done[key(subject, original)] = Math.max(...dates);
  else delete done[key(subject, original)];
}
