<template>
  <div
    class="flex min-h-8 min-w-0 items-center"
    :class="spaceBetween ? 'justify-between gap-3' : ''"
  >
    <div v-if="showLabel && !labelRight" class="me-3" :class="labelClasses">
      {{ df.label }}
    </div>
    <FrappeCheckbox
      ref="input"
      :model-value="getChecked(value)"
      :label="showLabel && labelRight ? df.label : undefined"
      :required="isRequired"
      :disabled="isReadOnly"
      size="sm"
      :class="['min-w-0', labelClass, showMandatory ? 'text-ink-red-7' : '']"
      @update:model-value="onChange"
      @focus="onFocus"
    />
  </div>
</template>

<script lang="ts">
import { Checkbox as FrappeCheckbox } from 'frappe-ui';
import { defineComponent } from 'vue';
import Base from './Base.vue';

export default defineComponent({
  name: 'Check',
  components: { FrappeCheckbox },
  extends: Base,
  props: {
    spaceBetween: {
      default: false,
      type: Boolean,
    },
    labelRight: {
      default: true,
      type: Boolean,
    },
    labelClass: String,
  },
  emits: ['focus'],
  computed: {
    labelClasses(): string {
      return this.labelClass || 'text-ink-gray-6 text-base';
    },
  },
  methods: {
    getChecked(value: unknown) {
      return Boolean(value);
    },
    onChange(value: boolean | 0 | 1) {
      if (!this.isReadOnly) {
        this.triggerChange(Boolean(value));
      }
    },
  },
});
</script>
