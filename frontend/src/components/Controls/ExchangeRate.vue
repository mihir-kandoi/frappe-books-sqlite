<template>
  <div
    class="
      flex
      items-center
      bg-gray-50
      dark:bg-gray-890 dark:border-gray-800
      rounded-md
      text-sm
      p-1
      border
    "
  >
    <div
      class="rate-container gap-2"
      :class="
        disabled
          ? 'bg-gray-100 dark:bg-gray-850'
          : 'bg-gray-25 dark:bg-gray-890'
      "
    >
      <FrappeTextInput
        :model-value="fromValue"
        type="number"
        :disabled="disabled"
        :min="0"
        size="sm"
        variant="ghost"
        class="w-16 [&_input]:text-end"
        @update:model-value="setFromValue"
      />

      <span class="dark:text-gray-400">{{ left }}</span>
    </div>

    <p class="mx-1 text-gray-600 dark:text-gray-400">=</p>

    <div
      class="rate-container gap-2"
      :class="
        disabled
          ? 'bg-gray-100 dark:bg-gray-850'
          : 'bg-gray-25 dark:bg-gray-890'
      "
    >
      <FrappeTextInput
        type="number"
        :model-value="
          isSwapped ? fromValue / exchangeRate : exchangeRate * fromValue
        "
        :disabled="disabled"
        :min="0"
        size="sm"
        variant="ghost"
        class="w-16 [&_input]:text-end"
        @change="rightChange"
      />
      <span class="dark:text-gray-400">{{ right }}</span>
    </div>

    <FrappeButton
      v-if="!disabled"
      theme="green"
      variant="subtle"
      size="xs"
      class="ms-1"
      :tooltip="t`Swap currencies`"
      @click="swap"
    >
      <feather-icon
        name="refresh-cw"
        class="w-3 h-3 text-gray-600 dark:text-gray-400"
      />
    </FrappeButton>
  </div>
</template>
<script lang="ts">
import {
  Button as FrappeButton,
  TextInput as FrappeTextInput,
} from 'frappe-ui';
import { safeParseFloat } from 'utils/index';
import { defineComponent } from 'vue';

export default defineComponent({
  components: { FrappeButton, FrappeTextInput },
  props: {
    disabled: { type: Boolean, default: false },
    fromCurrency: { type: String, default: 'USD' },
    toCurrency: { type: String, default: 'INR' },
    exchangeRate: { type: Number, default: 75 },
  },
  emits: ['change'],
  data() {
    return { fromValue: 1, isSwapped: false };
  },
  computed: {
    left(): string {
      if (this.isSwapped) {
        return this.toCurrency;
      }

      return this.fromCurrency;
    },
    right(): string {
      if (this.isSwapped) {
        return this.fromCurrency;
      }

      return this.toCurrency;
    },
  },
  methods: {
    setFromValue(value: string) {
      this.fromValue = Math.max(safeParseFloat(value), 0);
    },
    swap() {
      this.isSwapped = !this.isSwapped;
    },
    rightChange(e: Event) {
      let value: string | number = 1;
      if (e.target instanceof HTMLInputElement) {
        value = e.target.value;
      }

      value = safeParseFloat(value);

      let exchangeRate = value / this.fromValue;
      if (this.isSwapped) {
        exchangeRate = this.fromValue / value;
      }

      this.$emit('change', exchangeRate);
    },
  },
});
</script>
<style scoped>
.rate-container {
  @apply flex items-center rounded-md  border-gray-100 text-gray-900 text-sm  px-1  focus-within:border-gray-200 bg-transparent;
}

.rate-container > p {
  @apply text-xs text-gray-600;
}
</style>
