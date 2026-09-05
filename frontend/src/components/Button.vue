<template>
  <FrappeButton
    v-if="isIconOnly"
    :disabled="disabled"
    :size="size"
    :theme="resolvedTheme"
    :type="nativeType"
    :variant="variant"
    :class="buttonClasses"
    :style="buttonStyle"
    v-bind="buttonAttrs"
  >
    <template #icon>
      <slot></slot>
    </template>
  </FrappeButton>
  <FrappeButton
    v-else
    :disabled="disabled"
    :size="size"
    :theme="resolvedTheme"
    :type="nativeType"
    :variant="variant"
    :class="buttonClasses"
    :style="buttonStyle"
    v-bind="buttonAttrs"
  >
    <slot></slot>
  </FrappeButton>
</template>

<script lang="ts">
import { Button as FrappeButton } from 'frappe-ui';
import { getButtonTextColor } from 'src/utils/button';
import { defineComponent, PropType } from 'vue';

type ButtonTheme = 'gray' | 'blue' | 'green' | 'red';

const legacyThemeMap: Record<string, ButtonTheme> = {
  blue: 'blue',
  green: 'green',
  red: 'red',
  teal: 'green',
};

const legacyInlineThemeMap: Record<string, ButtonTheme> = {
  '#86efac': 'green',
  '#f98080': 'red',
  'rgb(134,239,172)': 'green',
  'rgb(249,128,128)': 'red',
};

export default defineComponent({
  name: 'BooksButton',
  components: { FrappeButton },
  inheritAttrs: false,
  props: {
    type: {
      type: String,
      default: 'secondary',
    },
    icon: {
      type: Boolean,
      default: false,
    },
    disabled: {
      type: Boolean,
      default: false,
    },
    padding: {
      type: Boolean,
      default: true,
    },
    background: {
      type: Boolean,
      default: true,
    },
    size: {
      type: String as PropType<'xs' | 'sm' | 'md' | 'lg'>,
      default: 'md',
    },
    theme: {
      type: String as PropType<ButtonTheme>,
      default: 'gray',
    },
  },
  computed: {
    buttonAttrs(): Record<string, unknown> {
      const attrs = { ...this.$attrs };
      delete attrs.style;
      if (typeof attrs.title === 'string') {
        attrs.tooltip ??= attrs.title;
        if (this.isIconOnly) attrs['aria-label'] ??= attrs.title;
        delete attrs.title;
      }
      return attrs;
    },
    buttonStyle(): unknown {
      if (this.customBackground) {
        return [
          removeBackgroundStyle(this.$attrs.style),
          {
            '--books-button-background': this.customBackground,
            '--books-button-foreground': getButtonTextColor(
              this.customBackground
            ),
          },
        ];
      }
      if (!this.legacyInlineTheme) {
        return this.$attrs.style;
      }

      return removeBackgroundStyle(this.$attrs.style);
    },
    isIconOnly(): boolean {
      if (!this.icon) {
        return false;
      }

      return !slotHasText(this.$slots.default?.() ?? []);
    },
    resolvedTheme(): ButtonTheme {
      return this.legacyTheme ?? this.legacyInlineTheme ?? this.theme;
    },
    variant(): 'solid' | 'subtle' | 'ghost' {
      if (!this.background) {
        return 'ghost';
      }

      if (
        this.type === 'primary' ||
        this.legacyTheme ||
        this.legacyInlineTheme ||
        hasBackgroundStyle(this.$attrs.style)
      ) {
        return 'solid';
      }

      return 'subtle';
    },
    nativeType(): 'button' | 'submit' | 'reset' {
      if (['button', 'submit', 'reset'].includes(this.type)) {
        return this.type as 'button' | 'submit' | 'reset';
      }

      return 'button';
    },
    buttonClasses(): string[] {
      const classes: string[] = [];
      if (this.customBackground) classes.push('books-custom-button');

      if (!this.isIconOnly && !this.padding && !this.hasCustomPadding) {
        classes.push('!px-0');
      }

      return classes;
    },
    hasCustomPadding(): boolean {
      return /(?:^|\s)!?p(?:[xysetrlb])?-\S+/.test(
        normalizeClasses(this.$attrs.class)
      );
    },
    legacyTheme(): ButtonTheme | undefined {
      const match = normalizeClasses(this.$attrs.class).match(
        /(?:^|\s)(?:dark:)?bg-(blue|green|red|teal)-\d+(?:\s|$)/
      );
      return match ? legacyThemeMap[match[1]] : undefined;
    },
    legacyInlineTheme(): ButtonTheme | undefined {
      const background = getBackgroundStyle(this.$attrs.style);
      return background
        ? legacyInlineThemeMap[normalizeColor(background)]
        : undefined;
    },
    customBackground(): string | undefined {
      const background = getBackgroundStyle(this.$attrs.style);
      return !this.legacyInlineTheme && /^#[0-9a-f]{6}$/i.test(background ?? '')
        ? background
        : undefined;
    },
  },
});

function hasBackgroundStyle(style: unknown): boolean {
  if (Array.isArray(style)) {
    return style.some(hasBackgroundStyle);
  }

  if (typeof style === 'string') {
    return /(?:^|;)\s*background(?:-color)?\s*:/.test(style);
  }

  if (!style || typeof style !== 'object') {
    return false;
  }

  return 'background' in style || 'backgroundColor' in style;
}

function getBackgroundStyle(style: unknown): string | undefined {
  if (Array.isArray(style)) {
    for (const entry of style) {
      const background = getBackgroundStyle(entry);
      if (background) {
        return background;
      }
    }

    return undefined;
  }

  if (typeof style === 'string') {
    return style.match(/(?:^|;)\s*background(?:-color)?\s*:\s*([^;]+)/i)?.[1];
  }

  if (!style || typeof style !== 'object') {
    return undefined;
  }

  if ('backgroundColor' in style && typeof style.backgroundColor === 'string') {
    return style.backgroundColor;
  }

  if ('background' in style && typeof style.background === 'string') {
    return style.background;
  }

  return undefined;
}

function normalizeColor(color: string): string {
  return color.toLowerCase().replace(/\s+/g, '');
}

function removeBackgroundStyle(style: unknown): unknown {
  if (Array.isArray(style)) {
    return style.map(removeBackgroundStyle);
  }

  if (typeof style === 'string') {
    return style
      .replace(/(?:^|;)\s*background(?:-color)?\s*:[^;]*/gi, '')
      .replace(/^\s*;|;\s*$/g, '');
  }

  if (!style || typeof style !== 'object') {
    return style;
  }

  const sanitizedStyle = { ...style } as Record<string, unknown>;
  delete sanitizedStyle.background;
  delete sanitizedStyle.backgroundColor;
  return sanitizedStyle;
}

function slotHasText(content: unknown): boolean {
  if (typeof content === 'string' || typeof content === 'number') {
    return String(content).trim().length > 0;
  }

  if (Array.isArray(content)) {
    return content.some(slotHasText);
  }

  if (!content || typeof content !== 'object' || !('children' in content)) {
    return false;
  }

  return slotHasText(content.children);
}

function normalizeClasses(classes: unknown): string {
  if (typeof classes === 'string') {
    return classes;
  }

  if (Array.isArray(classes)) {
    return classes.map(normalizeClasses).filter(Boolean).join(' ');
  }

  if (classes && typeof classes === 'object') {
    return Object.entries(classes)
      .filter(([, enabled]) => Boolean(enabled))
      .map(([className]) => className)
      .join(' ');
  }

  return '';
}
</script>

<style scoped>
.books-custom-button:not(:disabled) {
  background-color: var(--books-button-background);
  color: var(--books-button-foreground);
}

.books-custom-button:not(:disabled):hover {
  background-color: color-mix(
    in srgb,
    var(--books-button-background),
    black 8%
  );
}

.books-custom-button:not(:disabled):active {
  background-color: color-mix(
    in srgb,
    var(--books-button-background),
    black 14%
  );
}
</style>
