<template>
  <div :class="level > 0 ? 'ms-2 ps-2 border-l border-outline-gray-1' : ''">
    <template v-for="r of rows" :key="r.key">
      <DisclosureButton
        v-if="r.isCollapsible"
        class="text-ink-gray-6"
        :expanded="!r.collapsed"
        @toggle="r.collapsed = !r.collapsed"
      >
        <span class="flex min-w-0 flex-wrap items-center gap-2">
          <span class="min-w-0 break-all">{{ getKey(r) }}</span>
          <FrappeBadge :theme="Array.isArray(r.value) ? 'blue' : 'red'" variant="subtle" size="sm">
            {{ Array.isArray(r.value) ? t`Array` : t`Object` }}
          </FrappeBadge>
        </span>
      </DisclosureButton>
      <div
        v-else
        class="flex gap-2 px-2 py-1.5 text-sm text-ink-gray-6 whitespace-nowrap overflow-auto no-scrollbar"
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
import { Badge as FrappeBadge } from 'frappe-ui';
import DisclosureButton from 'src/components/DisclosureButton.vue';
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
  components: { FrappeBadge, DisclosureButton },
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
