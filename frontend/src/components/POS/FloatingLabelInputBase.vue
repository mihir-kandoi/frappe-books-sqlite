<template>
  <FrappeTextInput
    ref="input"
    :type="inputType"
    :model-value="inputValue"
    :label="df.label"
    :description="df.sub_label"
    :placeholder="inputPlaceholder"
    :disabled="isReadOnly"
    :required="isRequired"
    :max="isNumeric(df) ? df.maxvalue : undefined"
    :min="isNumeric(df) ? df.minvalue : undefined"
    :size="size === 'large' ? 'lg' : 'md'"
    variant="outline"
    class="[&_input]:font-medium"
    :tabindex="isReadOnly ? '-1' : '0'"
    @blur="onBlur"
    @focus="onFocus"
  />
</template>
<script lang="ts">
import { TextInput as FrappeTextInput } from 'frappe-ui';
import { defineComponent } from 'vue';
import Base from '../Controls/Base.vue';

export default defineComponent({
  name: 'FloatingLabelInputBase',
  components: { FrappeTextInput },
  extends: Base,
});
</script>
