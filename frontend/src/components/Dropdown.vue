<template>
  <FrappeDropdown
    v-model:open="isShown"
    :align="right ? 'end' : 'start'"
    :disabled="disabled"
    :options="menuOptions"
  >
    <template #trigger>
      <slot
        :toggle-dropdown="toggleDropdown"
        :highlight-item-up="noop"
        :highlight-item-down="noop"
        :select-highlighted-item="noop"
      />
    </template>
    <template #empty>
      <span class="italic">{{ emptyMessage }}</span>
    </template>
  </FrappeDropdown>
</template>

<script lang="ts">
import { Doc } from 'fyo/model/doc';
import { Dropdown as FrappeDropdown, type DropdownOption, type DropdownOptions } from 'frappe-ui';
import { Field } from 'schemas/types';
import { fyo } from 'src/initFyo';
import { DropdownItem } from 'src/utils/types';
import { defineComponent, PropType } from 'vue';

export default defineComponent({
  name: 'Dropdown',
  components: { FrappeDropdown },
  props: {
    disabled: {
      type: Boolean,
      default: false,
    },
    items: {
      type: Array as PropType<DropdownItem[]>,
      default: () => [],
    },
    right: {
      type: Boolean,
      default: false,
    },
    isLoading: {
      type: Boolean,
      default: false,
    },
    df: {
      type: Object as PropType<Field | null>,
      default: null,
    },
    doc: {
      type: Object as PropType<Doc | null>,
      default: null,
    },
  },
  data() {
    return {
      isShown: false,
    };
  },
  computed: {
    emptyMessage(): string {
      const { schemaName, fieldname } = this.df ?? {};
      if (!schemaName || !fieldname || !this.doc) {
        return this.t`Empty`;
      }

      return fyo.models[schemaName]?.emptyMessages[fieldname]?.(this.doc) ?? this.t`Empty`;
    },
    menuOptions(): DropdownOptions {
      if (this.isLoading) {
        return [{ label: this.t`Loading...`, disabled: true }];
      }

      const groups = groupItems(this.items);
      const options: DropdownOptions = (groups.get('') ?? []).map(this.toMenuOption);

      for (const group of [...groups.keys()].filter(Boolean).sort()) {
        options.push({
          group,
          options: (groups.get(group) ?? []).map(this.toMenuOption),
        });
      }

      return options;
    },
  },
  methods: {
    noop(): void {},
    toggleDropdown(flag?: boolean): void {
      this.isShown = flag ?? !this.isShown;
    },
    toMenuOption(item: DropdownItem): DropdownOption {
      const option: DropdownOption = {
        label: item.label,
        theme: item.theme,
        onClick: () => this.selectItem(item),
      };

      return option;
    },
    async selectItem(item: DropdownItem): Promise<void> {
      if (!item.action) {
        return;
      }

      if (this.doc) {
        await item.action(this.doc, this.$router);
      } else {
        await (item.action as () => unknown)();
      }

      this.isShown = false;
    },
  },
});

function groupItems(items: DropdownItem[]): Map<string, DropdownItem[]> {
  const groups = new Map<string, DropdownItem[]>();
  for (const item of items) {
    const group = item.group ?? '';
    groups.set(group, [...(groups.get(group) ?? []), item]);
  }

  return groups;
}
</script>
