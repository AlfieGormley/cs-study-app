// Keep the current question with a paused quiz. Option positions only make sense
// for the exact question the reader saw, not a later editorial revision.
export function sessionQuestion(session, item, question, lessonTitle) {
  const key = `${item.s}/${item.qid}`;
  const saved = session.currentQuestion;
  if (saved?.key === key && saved.index === session.i) {
    return { kind: 'question', ...saved };
  }
  // Older sessions saved selections and a result, but not the question. Keep
  // that result without grading its option numbers against today's content.
  if (session.checked) {
    const result = [...session.results].reverse().find(r => r.s === item.s && r.qid === item.qid);
    return { kind: 'recorded', result };
  }
  if (!question) return { kind: 'missing' };
  const selectionReset = session.picked.length > 0;
  session.picked = [];
  session.currentQuestion = {
    key, index: session.i, question: structuredClone(question), lessonTitle, selectionReset,
  };
  return { kind: 'question', ...session.currentQuestion };
}

export function advanceSession(session) {
  session.i++;
  session.picked = [];
  session.checked = false;
  delete session.currentQuestion;
}
