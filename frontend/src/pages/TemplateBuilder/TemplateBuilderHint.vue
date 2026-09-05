<template>
  <div :class="level > 0 ? 'ms-2 ps-2 border-l border-outline-gray-1' : ''">
    <template v-for="r of rows" :key="r.key">
      <FrappeButton
        v-if="r.isCollapsible"
        class="!h-auto w-full !justify-start !px-0 text-start text-ink-gray-6"
        variant="ghost"
        size="sm"
        :icon-right="r.collapsed ? 'lucide-chevron-down' : 'lucide-chevron-up'"
        :aria-expanded="!r.collapsed"
        @click="r.collapsed = !r.collapsed"
      >
        <span class="min-w-0 overflow-auto whitespace-nowrap no-scrollbar">
          {{ getKey(r) }}
        </span>
        <FrappeBadge :theme="Array.isArray(r.value) ? 'blue' : 'red'" variant="subtle" size="sm">
          {{ Array.isArray(r.value) ? t`Array` : t`Object` }}
        </FrappeBadge>
      </FrappeButton>
      <div
        v-else
        class="flex gap-2 px-0 py-1.5 text-sm text-ink-gray-6 whitespace-nowrap overflow-auto no-scrollbar"
      >
        <div>{{ getKey(r) }}</div>
        <div class="font-semibold text-ink-gray-8">
          {{ r.value }}
        </div>
      </div>
      <div v-if="!r.collapsed && typeof r.value === 'object'">
        <TemplateBuilderHint
          :prefix="getKey(r)"
          :hints="Array.isArray(r.value) ? r.value[0] : r.value"
          :level="level + 1"
        />
      </div>
    </template>
  </div>
</template>
<script lang="ts">
import { PrintTemplateHint } from 'src/utils/printTemplates';
import { Badge as FrappeBadge, Button as FrappeButton } from 'frappe-ui';
import { PropType } from 'vue';
import { defineComponent } from 'vue';
type HintRow = {
  key: string;
  value: PrintTemplateHint[string];
  isCollapsible: boolean;
  collapsed: boolean;
};
export default defineComponent({
  name: 'TemplateBuilderHint',
  components: { FrappeBadge, FrappeButton },
  props: {
    prefix: { type: String, default: '' },
    hints: {
      type: Object as PropType<PrintTemplateHint>,
      required: true,
    },
    level: { type: Number, default: 0 },
  },
  data() {
    return { rows: [] } as {
      rows: HintRow[];
    };
  },
  mounted() {
    this.rows = Object.entries(this.hints)
      .map(([key, value]) => ({
        key,
        value,
        isCollapsible: typeof value === 'object',
        collapsed: this.level > 0,
      }))
      .sort((a, b) => Number(a.isCollapsible) - Number(b.isCollapsible));
  },
  methods: {
    getKey(row: HintRow) {
      const isArray = Array.isArray(row.value);
      if (isArray) {
        return `${this.prefix}.${row.key}[number]`;
      }

      if (this.prefix.length) {
        return `${this.prefix}.${row.key}`;
      }

      return row.key;
    },
  },
});
</script>
