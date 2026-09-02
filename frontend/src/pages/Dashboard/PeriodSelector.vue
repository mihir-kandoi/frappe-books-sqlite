<template>
  <Dropdown ref="dropdown" class="text-sm" :items="periodOptions" right>
    <template
      #default="{ highlightItemUp, highlightItemDown, selectHighlightedItem }"
    >
      <div
        class="
          text-sm
          flex
          focus:outline-none
          hover:text-gray-800
          dark:hover:text-gray-100
          focus:text-gray-800
          dark:focus:text-gray-100
          items-center
          gap-1.5
          px-3
          py-1
          rounded-md
          leading-relaxed
          whitespace-nowrap
          cursor-pointer
        "
        :class="
          !value
            ? 'text-gray-600 dark:text-gray-500'
            : 'text-gray-900 dark:text-gray-300'
        "
        tabindex="0"
        @keydown.down="highlightItemDown"
        @keydown.up="highlightItemUp"
        @keydown.enter="selectHighlightedItem"
      >
        {{ periodSelectorMap?.[value] ?? value }}
        <feather-icon name="chevron-down" class="h-3 w-3 flex-shrink-0" />
      </div>
    </template>
  </Dropdown>
</template>

<script lang="ts">
import { t } from 'fyo';
import Dropdown from 'src/components/Dropdown.vue';
import { PeriodKey } from 'src/utils/types';
import { PropType } from 'vue';
import { defineComponent } from 'vue';

export default defineComponent({
  name: 'PeriodSelector',
  components: {
    Dropdown,
  },
  props: {
    value: { type: String as PropType<PeriodKey>, default: 'This Year' },
    options: {
      type: Array as PropType<PeriodKey[]>,
      default: () => ['This Year', 'This Quarter', 'This Month', 'YTD'],
    },
  },
  emits: ['change'],
  data() {
    return {
      periodSelectorMap: {} as Record<PeriodKey | '', string>,
      periodOptions: [] as { label: string; action: () => void }[],
    };
  },
  mounted() {
    this.periodSelectorMap = {
      '': t`Set Period`,
      'This Year': t`This Year`,
      YTD: t`Year to Date`,
      'This Quarter': t`This Quarter`,
      'This Month': t`This Month`,
    };

    this.periodOptions = this.options.map((option) => {
      let label = this.periodSelectorMap[option] ?? option;

      return {
        label,
        action: () => this.selectOption(option),
      };
    });
  },
  methods: {
    selectOption(value: PeriodKey) {
      this.$emit('change', value);
      (this.$refs.dropdown as InstanceType<typeof Dropdown>).toggleDropdown(
        false
      );
    },
  },
});
</script>
