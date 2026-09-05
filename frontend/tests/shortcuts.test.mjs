import assert from 'node:assert/strict';
import test from 'node:test';
import { Shortcuts } from '../src/utils/shortcuts.ts';

test('component-consumed keys do not trigger a page shortcut', () => {
  const shortcuts = new Shortcuts(false);
  let called = false;
  shortcuts.set('page', ['Escape'], () => (called = true));
  const event = keyEvent('Escape');
  event.preventDefault();
  assert.equal(shortcuts.handleKeydown(event), false);
  assert.equal(called, false);
});

test('popup Escape belongs to the popup and page Escape still works', () => {
  const shortcuts = new Shortcuts(false);
  let calls = 0;
  shortcuts.set('page', ['Escape'], () => calls++);
  const popupEvent = keyEvent('Escape', { closest: () => ({}) });
  assert.equal(shortcuts.handleKeydown(popupEvent), false);
  assert.equal(popupEvent.defaultPrevented, false);
  assert.equal(calls, 0);

  assert.equal(shortcuts.handleKeydown(keyEvent('Escape')), true);
  assert.equal(calls, 1);
});

test('modifier shortcuts remain available inside editable controls', () => {
  const shortcuts = new Shortcuts(false);
  let calls = 0;
  shortcuts.ctrl.set('page', ['KeyS'], () => calls++);
  const event = keyEvent('KeyS', { tagName: 'INPUT' }, { ctrlKey: true });
  assert.equal(shortcuts.handleKeydown(event), true);
  assert.equal(calls, 1);
  assert.equal(event.defaultPrevented, true);
});

function keyEvent(code, target = null, modifiers = {}) {
  const event = new Event('keydown', { cancelable: true });
  Object.assign(event, { code, ...modifiers });
  Object.defineProperty(event, 'target', { value: target });
  return event;
}
