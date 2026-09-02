<template>
  <FrappeBadge :theme="theme" variant="subtle" size="md">
    <slot></slot>
  </FrappeBadge>
</template>

<script lang="ts">
import { Badge as FrappeBadge } from 'frappe-ui';
import { defineComponent } from 'vue';

type BadgeTheme = 'gray' | 'blue' | 'green' | 'amber' | 'red' | 'violet';

const themeMap: Record<string, BadgeTheme> = {
  amber: 'amber',
  blue: 'blue',
  gray: 'gray',
  green: 'green',
  indigo: 'violet',
  orange: 'amber',
  pink: 'red',
  purple: 'violet',
  red: 'red',
  violet: 'violet',
  yellow: 'amber',
};

export default defineComponent({
  name: 'BooksBadge',
  components: { FrappeBadge },
  props: {
    color: {
      type: String,
      default: 'gray',
    },
  },
  computed: {
    theme(): BadgeTheme {
      return themeMap[this.color] ?? 'gray';
    },
  },
});
</script>
