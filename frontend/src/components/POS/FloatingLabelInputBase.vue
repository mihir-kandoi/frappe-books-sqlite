<template>
  <ReadOnlyValue
    v-if="isReadOnly"
    :df="df"
    :value="value"
    :doc="doc"
    :border="true"
    :show-label="true"
    :required="isRequired"
    :size="size"
  />
  <FrappeTextInput
    v-else
    ref="input"
    :type="inputType"
    :model-value="inputValue"
    :label="df.label"
    :description="df.sub_label"
    :placeholder="inputPlaceholder"
    :required="isRequired"
    :max="isNumeric(df) ? df.maxvalue : undefined"
    :min="isNumeric(df) ? df.minvalue : undefined"
    :size="size === 'large' ? 'lg' : 'md'"
    variant="outline"
    class="[&_input]:font-medium"
    tabindex="0"
    @blur="onBlur"
    @focus="onFocus"
  />
</template>
<script lang="ts">
import { TextInput as FrappeTextInput } from 'frappe-ui';
import { defineComponent } from 'vue';
import Base from '../Controls/Base.vue';
import ReadOnlyValue from '../Controls/ReadOnlyValue.vue';

export default defineComponent({
  name: 'FloatingLabelInputBase',
  components: { FrappeTextInput, ReadOnlyValue },
  extends: Base,
});
</script>
