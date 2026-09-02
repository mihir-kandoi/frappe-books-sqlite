<template>
  <ReadOnlyValue
    v-if="isReadOnly"
    :df="df"
    :value="value"
    :doc="doc"
    :border="border"
    :show-label="showLabel"
    :required="isRequired"
    :size="size"
    :text-right="textRight"
    :container-styles="containerStyles"
  />
  <FrappeTextarea
    v-else
    ref="input"
    :rows="df.rows ?? rows"
    :class="textControlClasses"
    :model-value="typeof value === 'string' ? value : ''"
    :label="showLabel ? df.label : undefined"
    :description="showLabel ? df.sub_label : undefined"
    :placeholder="inputPlaceholder"
    :required="isRequired"
    :size="frappeSize"
    :variant="frappeVariant"
    tabindex="0"
    @blur="(e) => triggerChange(e.target.value)"
    @focus="(e) => $emit('focus', e)"
    @input="(e) => $emit('input', e)"
  />
</template>

<script>
import { Textarea as FrappeTextarea } from 'frappe-ui';
import Base from './Base.vue';
import ReadOnlyValue from './ReadOnlyValue.vue';

export default {
  name: 'Text',
  components: { FrappeTextarea, ReadOnlyValue },
  extends: Base,
  props: { rows: { type: Number, default: 3 } },
  emits: ['focus', 'input'],
  computed: {
    textControlClasses() {
      return [
        this.controlClasses,
        "[&_[data-slot='control']]:!text-base",
      ];
    },
  },
};
</script>
