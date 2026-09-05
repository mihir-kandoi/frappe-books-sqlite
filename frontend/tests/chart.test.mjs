import assert from 'node:assert/strict';
import test from 'node:test';
import { getYMax, getYMin } from '../src/utils/chart.ts';

test('chart axes include zero and have a finite range for sparse periods', () => {
  for (const points of [[], [[]], [[0]], [[12]], [[-12]], [[NaN, Infinity]]]) {
    const min = getYMin(points);
    const max = getYMax(points);
    assert.ok(Number.isFinite(min) && Number.isFinite(max));
    assert.ok(min <= 0 && max >= 0);
    assert.ok(min < max);
  }
});

test('chart axes contain every positive and negative balance', () => {
  const points = [[-121, 0, 345], [10, -2]];
  assert.ok(getYMin(points) <= -121);
  assert.ok(getYMax(points) >= 345);
});
