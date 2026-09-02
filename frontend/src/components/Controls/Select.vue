<template>
  <FrappeSelect
    ref="input"
    :model-value="selectValue"
    :open="dropdownVisible"
    :options="options"
    :label="showLabel ? df.label : undefined"
    :description="showLabel ? df.sub_label : undefined"
    :placeholder="inputPlaceholder"
    :disabled="isReadOnly"
    :required="isRequired"
    :size="frappeSize"
    :variant="frappeVariant"
    :class="controlClasses"
    :style="containerStyles"
    side="bottom"
    align="start"
    @update:model-value="selectOption"
    @update:open="onOpenChange"
    @focus="onFocus"
  />
</template>

<script lang="ts">
import { Select as FrappeSelect } from 'frappe-ui';
import { SelectOption } from 'schemas/types';
import { defineComponent, nextTick } from 'vue';
import Base from './Base.vue';

export default defineComponent({
  name: 'Select',
  components: { FrappeSelect },
  extends: Base,
  emits: ['focus'],
  props: {
    closeDropDown: {
      type: Boolean,
      default: true,
    },
  },
  data() {
    return {
      dropdownVisible: false,
    };
  },
  computed: {
    options(): SelectOption[] {
      if (this.df.fieldtype !== 'Select') {
        return [];
      }

      return this.df.options;
    },
    selectValue(): string | number | undefined {
      if (typeof this.value === 'string' || typeof this.value === 'number') {
        return this.value;
      }

      return undefined;
    },
  },
  methods: {
    onOpenChange(open: boolean) {
      this.dropdownVisible = open;
    },
    selectOption(value: string | number | undefined) {
      this.triggerChange(value);

      if (!this.closeDropDown) {
        nextTick(() => {
          this.dropdownVisible = true;
        });
      }
    },
  },
});
</script>
