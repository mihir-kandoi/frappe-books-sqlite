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
    :text-right="true"
  />
  <FrappeTextInput
    v-else
    ref="input"
    :type="inputType"
    :model-value="round(value)"
    :label="df.label"
    :description="df.sub_label"
    :placeholder="inputPlaceholder"
    :required="isRequired"
    :max="isNumeric(df) ? df.maxvalue : undefined"
    :min="isNumeric(df) ? df.minvalue : undefined"
    :size="size === 'large' ? 'lg' : 'md'"
    variant="outline"
    class="[&_input]:font-medium [&_input]:text-end"
    tabindex="0"
    @blur="onBlur"
    @focus="onFocus"
  >
    <template #prefix>
      <span class="text-sm text-ink-gray-5">
        {{ currency ? fyo.currencySymbols[currency] : '' }}
      </span>
    </template>
  </FrappeTextInput>
</template>

<script lang="ts">
import { TextInput as FrappeTextInput } from 'frappe-ui';
import FloatingLabelInputBase from './FloatingLabelInputBase.vue';
import { safeParsePesa } from 'utils/index';
import { isPesa } from 'fyo/utils';
import { fyo } from 'src/initFyo';
import { defineComponent } from 'vue';
import { Money } from 'pesa';
import ReadOnlyValue from '../Controls/ReadOnlyValue.vue';

export default defineComponent({
  name: 'FloatingLabelCurrencyInput',
  components: { FrappeTextInput, ReadOnlyValue },
  extends: FloatingLabelInputBase,
  computed: {
    currency(): string | undefined {
      if (this.value) {
        return (this.value as Money).getCurrency();
      }
    },
  },
  methods: {
    round(v: unknown) {
      if (!isPesa(v)) {
        v = this.parse(v);
      }

      if (isPesa(v)) {
        return v.round();
      }

      return fyo.pesa(0).round();
    },
    parse(value: unknown): Money {
      return safeParsePesa(value, this.fyo);
    },
  },
});
</script>
