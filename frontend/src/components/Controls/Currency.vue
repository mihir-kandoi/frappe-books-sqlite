<template>
  <div>
    <FrappeTextInput
      v-if="showInput"
      ref="input"
      class="[&_input]:text-end"
      :type="inputType"
      :model-value="round(value)"
      :label="showLabel ? df.label : undefined"
      :description="showLabel ? df.sub_label : undefined"
      :placeholder="inputPlaceholder"
      :disabled="isReadOnly"
      :required="isRequired"
      :size="frappeSize"
      :variant="frappeVariant"
      :tabindex="isReadOnly ? '-1' : '0'"
      @blur="onBlur"
      @focus="onFocus"
      @input="(e:Event) => $emit('input', e)"
    />
    <div v-else>
      <label v-if="showLabel" :class="labelClasses">
        {{ df.label }}
        <span v-if="isRequired" class="text-red-500">*</span>
      </label>
      <div
        class="whitespace-nowrap overflow-x-auto no-scrollbar"
        :class="[inputClasses, containerClasses]"
        tabindex="0"
        @click="activateInput"
        @focus="activateInput"
      >
        {{ formattedValue }}
      </div>
    </div>
  </div>
</template>
<script lang="ts">
import { isPesa } from 'fyo/utils';
import { TextInput as FrappeTextInput } from 'frappe-ui';
import { Money } from 'pesa';
import { fyo } from 'src/initFyo';
import { safeParsePesa } from 'utils/index';
import { defineComponent, nextTick } from 'vue';
import Float from './Float.vue';

export default defineComponent({
  name: 'Currency',
  components: { FrappeTextInput },
  extends: Float,
  emits: ['input', 'focus'],
  data() {
    return {
      showInput: false,
      currencySymbol: '',
    };
  },
  props: {
    focusInput: Boolean,
  },
  created() {
    if (this.focusInput) {
      this.showInput = true;
      nextTick(() => {
        this.focus();
      });
    }
  },
  computed: {
    formattedValue() {
      const value = this.parse(this.value);
      return fyo.format(value, this.df, this.doc);
    },
  },
  methods: {
    onFocus(e: FocusEvent) {
      const target = e.target;
      if (!(target instanceof HTMLInputElement)) {
        return;
      }

      target.select();
      this.showInput = true;
      this.$emit('focus', e);
    },
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
    onBlur(e: FocusEvent) {
      const target = e.target;
      if (!(target instanceof HTMLInputElement)) {
        return;
      }

      this.showInput = false;
      this.triggerChange(target.value);
    },
    activateInput() {
      if (this.isReadOnly) {
        return;
      }

      this.showInput = true;
      nextTick(() => {
        this.focus();
      });
    },
  },
});
</script>
