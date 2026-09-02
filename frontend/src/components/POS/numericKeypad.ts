export type NumericKey =
  | '0'
  | '1'
  | '2'
  | '3'
  | '4'
  | '5'
  | '6'
  | '7'
  | '8'
  | '9'
  | '.'
  | '-'
  | '+'
  | 'backspace'
  | 'clear';

export type NumericDraft = {
  value: string;
  replaceOnEntry: boolean;
};

export function applyNumericKey(
  draft: NumericDraft,
  key: NumericKey
): NumericDraft {
  if (key === 'clear') {
    return { value: '', replaceOnEntry: false };
  }

  if (key === 'backspace') {
    return {
      value: draft.replaceOnEntry ? '' : draft.value.slice(0, -1),
      replaceOnEntry: false,
    };
  }

  if (key === '-' || key === '+') {
    return applySign(draft, key);
  }

  if (key === '.') {
    return appendDecimal(draft);
  }

  return appendDigit(draft, key);
}

export function normalizeNumericDraft(rawValue: string): string | null {
  let value = rawValue.trim().replaceAll(',', '');
  if (value.startsWith('+')) {
    value = value.slice(1);
  }

  if (value === '.') {
    return '0.';
  }

  if (value === '-.') {
    return '-0.';
  }

  return /^-?\d*(?:\.\d*)?$/.test(value) ? value : null;
}

export function parseNumericDraft(value: string): number | null {
  if (!/^-?(?:\d+\.?\d*|\.\d+)$/.test(value)) {
    return null;
  }

  const number = Number(value);
  return Number.isFinite(number) ? number : null;
}

function appendDigit(draft: NumericDraft, digit: string): NumericDraft {
  if (draft.replaceOnEntry) {
    return { value: digit, replaceOnEntry: false };
  }

  if (draft.value === '' || draft.value === '-') {
    return { value: draft.value + digit, replaceOnEntry: false };
  }

  if (/^-?0$/.test(draft.value)) {
    const sign = draft.value.startsWith('-') ? '-' : '';
    return { value: sign + digit, replaceOnEntry: false };
  }

  return { value: draft.value + digit, replaceOnEntry: false };
}

function appendDecimal(draft: NumericDraft): NumericDraft {
  if (draft.replaceOnEntry) {
    return { value: '0.', replaceOnEntry: false };
  }

  if (draft.value.includes('.')) {
    return { ...draft, replaceOnEntry: false };
  }

  if (draft.value === '' || draft.value === '-') {
    return {
      value: draft.value.startsWith('-') ? '-0.' : '0.',
      replaceOnEntry: false,
    };
  }

  return { value: draft.value + '.', replaceOnEntry: false };
}

function applySign(draft: NumericDraft, sign: '-' | '+'): NumericDraft {
  if (sign === '-') {
    return {
      value: draft.value.startsWith('-') ? draft.value : `-${draft.value}`,
      replaceOnEntry: false,
    };
  }

  return {
    value: draft.value.startsWith('-') ? draft.value.slice(1) : draft.value,
    replaceOnEntry: false,
  };
}
