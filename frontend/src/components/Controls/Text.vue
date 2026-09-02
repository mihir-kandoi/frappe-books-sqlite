<template>
  <FrappeTextarea
    ref="input"
    :rows="df.rows ?? rows"
    :class="controlClasses"
    :model-value="typeof value === 'string' ? value : ''"
    :label="showLabel ? df.label : undefined"
    :description="showLabel ? df.sub_label : undefined"
    :placeholder="inputPlaceholder"
    :disabled="isReadOnly"
    :required="isRequired"
    :size="frappeSize"
    :variant="frappeVariant"
    :tabindex="isReadOnly ? '-1' : '0'"
    @blur="(e) => triggerChange(e.target.value)"
    @focus="(e) => $emit('focus', e)"
    @input="(e) => $emit('input', e)"
  />
</template>

<script>
import { Textarea as FrappeTextarea } from 'frappe-ui';
import Base from './Base.vue';

export default {
  name: 'Text',
  components: { FrappeTextarea },
  extends: Base,
  props: { rows: { type: Number, default: 3 } },
  emits: ['focus', 'input'],
};
</script>
