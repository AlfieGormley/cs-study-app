import test from 'node:test';
import assert from 'node:assert/strict';
import { daysSinceCompletion, normalizeCompletionRange } from '../practice.js';

test('completion age counts calendar days rather than elapsed 24-hour periods', () => {
  const now = new Date(2026, 9, 12, 9).getTime();
  assert.equal(daysSinceCompletion(new Date(2026, 9, 12, 1).getTime(), now), 0);
  assert.equal(daysSinceCompletion(new Date(2026, 9, 11, 23, 59).getTime(), now), 1);
  assert.equal(daysSinceCompletion(new Date(2026, 9, 2, 23, 59).getTime(), now), 10);
  assert.equal(daysSinceCompletion(new Date(2026, 8, 27, 23, 59).getTime(), now), 15);
});

test('calendar age stays accurate across daylight saving changes', () => {
  const previous = process.env.TZ;
  process.env.TZ = 'Europe/London';
  try {
    assert.equal(daysSinceCompletion(new Date(2026, 2, 28, 23, 30).getTime(), new Date(2026, 2, 29, 9).getTime()), 1);
    assert.equal(daysSinceCompletion(new Date(2026, 9, 24, 1).getTime(), new Date(2026, 9, 25, 23).getTime()), 1);
  } finally {
    if (previous === undefined) delete process.env.TZ;
    else process.env.TZ = previous;
  }
});

test('invalid dates have no age; a clock set back never produces a negative age', () => {
  for (const value of [undefined, null, true, '123', 0, -1, NaN, Infinity, 1e20]) {
    assert.equal(daysSinceCompletion(value), null);
  }
  const now = new Date(2026, 9, 12).getTime();
  assert.equal(daysSinceCompletion(now + 86400000, now), 0);
  assert.equal(daysSinceCompletion(now, NaN), null);
});

test('existing progress gets an optional 1–10 day range without enabling it', () => {
  assert.deepEqual(normalizeCompletionRange(), { enabled: false, min: 1, max: 10 });
  assert.deepEqual(normalizeCompletionRange({ enabled: true, min: 0, max: 0 }), { enabled: true, min: 0, max: 0 });
  assert.deepEqual(normalizeCompletionRange({ enabled: true, min: 7, max: 365 }), { enabled: true, min: 7, max: 365 });
});

test('saved ranges recover from invalid values and keep the upper limit above the lower', () => {
  assert.deepEqual(normalizeCompletionRange({ enabled: 'true', min: -1, max: Infinity }), { enabled: false, min: 1, max: 10 });
  assert.deepEqual(normalizeCompletionRange({ enabled: true, min: 15, max: 10 }), { enabled: true, min: 15, max: 15 });
  assert.deepEqual(normalizeCompletionRange({ min: 1.5, max: '10' }), { enabled: false, min: 1, max: 10 });
});
