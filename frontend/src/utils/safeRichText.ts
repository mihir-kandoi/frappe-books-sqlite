import { h, VNode } from 'vue';

const SAFE_TAGS = ['b', 'br', 'em', 'i', 'strong', 'u'] as const;

type SafeTag = typeof SAFE_TAGS[number];

export type SafeRichTextNode =
  | string
  | { tag: SafeTag; children: SafeRichTextNode[] };

type ParentNode = { tag?: SafeTag; children: SafeRichTextNode[] };

const SAFE_TAG_SET = new Set<string>(SAFE_TAGS);
const NAMED_ENTITIES: Record<string, string> = {
  amp: '&',
  apos: "'",
  gt: '>',
  lt: '<',
  nbsp: '\u00a0',
  quot: '"',
};

export function parseSafeRichText(value: string): SafeRichTextNode[] {
  const root: ParentNode = { children: [] };
  const stack: ParentNode[] = [root];
  const tokens = value.match(/<[^>]*>|[^<]+|</g) ?? [];

  for (const token of tokens) {
    if (!token.startsWith('<') || token === '<') {
      appendText(stack, token);
      continue;
    }

    const tagMatch = token.match(/^<\s*(\/?)\s*([a-zA-Z][\w:-]*)\b[^>]*>$/);
    if (!tagMatch) {
      continue;
    }

    const isClosing = Boolean(tagMatch[1]);
    const tag = tagMatch[2].toLowerCase();
    if (!SAFE_TAG_SET.has(tag)) {
      continue;
    }

    if (isClosing) {
      closeTag(stack, tag as SafeTag);
      continue;
    }

    const node: ParentNode = { tag: tag as SafeTag, children: [] };
    stack.at(-1)?.children.push(node as SafeRichTextNode);
    if (tag !== 'br' && !token.endsWith('/>')) {
      stack.push(node);
    }
  }

  return root.children;
}

export function renderSafeRichText(value: string): VNode {
  return h(
    'span',
    { class: 'whitespace-pre-line' },
    parseSafeRichText(value).map(renderNode)
  );
}

function appendText(stack: ParentNode[], value: string) {
  const text = decodeEntities(value);
  if (text) {
    stack.at(-1)?.children.push(text);
  }
}

function closeTag(stack: ParentNode[], tag: SafeTag) {
  const index = stack.findLastIndex((node) => node.tag === tag);
  if (index > 0) {
    stack.length = index;
  }
}

function renderNode(node: SafeRichTextNode): string | VNode {
  if (typeof node === 'string') {
    return node;
  }

  return h(node.tag, {}, node.children.map(renderNode));
}

function decodeEntities(value: string): string {
  return value.replace(
    /&(#(?:x[\da-f]+|\d+)|amp|apos|gt|lt|nbsp|quot);/gi,
    (entity, encoded: string) => {
      if (!encoded.startsWith('#')) {
        return NAMED_ENTITIES[encoded.toLowerCase()] ?? entity;
      }

      const isHex = encoded[1]?.toLowerCase() === 'x';
      const digits = encoded.slice(isHex ? 2 : 1);
      const codePoint = Number.parseInt(digits, isHex ? 16 : 10);
      if (!Number.isSafeInteger(codePoint) || codePoint > 0x10ffff) {
        return '\ufffd';
      }

      return String.fromCodePoint(codePoint);
    }
  );
}
