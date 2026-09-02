<template>
  <div>
    <div v-if="showLabel" :class="labelClasses">
      {{ df.label }}
    </div>
    <Popover :disabled="isReadOnly" placement="bottom-end">
      <template #target>
        <div tabindex="0" :class="[inputClasses, containerClasses]">
          <div class="flex items-center">
            <div
              v-if="value"
              class="w-3 h-3 rounded me-1"
              :style="{ backgroundColor: value }"
            ></div>
            <span v-if="value">
              {{ selectedColorLabel }}
            </span>
            <span v-else class="text-gray-400 dark:text-gray-600">
              {{ inputPlaceholder }}
            </span>
          </div>
        </div>
      </template>
      <template #content>
        <div class="w-48 p-3">
          <div class="grid grid-cols-5 gap-2">
            <button
              v-for="color in colors"
              :key="color.value"
              type="button"
              class="
                h-7
                w-7
                rounded-md
                border border-gray-200
                dark:border-gray-700
                focus:outline-none
                focus-visible:ring-2 focus-visible:ring-blue-400
              "
              :class="
                normalizedColor.toLowerCase() === color.value.toLowerCase()
                  ? 'ring-2 ring-blue-500 ring-offset-2 dark:ring-offset-gray-850'
                  : ''
              "
              :style="{ backgroundColor: color.value }"
              :title="color.label"
              :aria-label="color.label"
              @click="setColorValue(color.value)"
            />
          </div>

          <div
            class="
              mt-3
              flex
              items-center
              gap-2
              rounded-md
              border border-gray-200
              bg-gray-25
              p-1.5
              dark:border-gray-700 dark:bg-gray-875
            "
          >
            <input
              type="color"
              class="color-swatch h-7 w-7 flex-shrink-0 cursor-pointer"
              :value="normalizedColor"
              :title="t`Choose color`"
              :aria-label="t`Choose color`"
              @input="setColorFromEvent"
            />
            <input
              type="text"
              class="
                min-w-0
                flex-1
                bg-transparent
                px-1
                py-1
                font-mono
                text-sm text-gray-900
                uppercase
                focus:outline-none
                dark:text-gray-100
              "
              :value="normalizedColor"
              :placeholder="t`Custom Hex`"
              :aria-label="t`Custom Hex`"
              maxlength="7"
              spellcheck="false"
              @change="setColorFromEvent"
              @keydown.enter.prevent="setColorFromEvent"
            />
          </div>
        </div>
      </template>
    </Popover>
  </div>
</template>

<script>
import Popover from 'src/components/Popover.vue';
import Base from './Base.vue';

export default {
  name: 'Color',
  components: {
    Popover,
  },
  extends: Base,
  computed: {
    colors() {
      if (Array.isArray(this.df.options) && this.df.options.length) {
        return this.df.options.filter(
          (color) => color && typeof color.value === 'string'
        );
      }

      return defaultColors;
    },
    normalizedColor() {
      if (typeof this.value !== 'string') {
        return '#000000';
      }

      const value = this.value.startsWith('#') ? this.value : `#${this.value}`;
      return isValidColor(value) ? value : '#000000';
    },
    selectedColorLabel() {
      const color = this.colors.find(
        (candidate) =>
          candidate.value.toLowerCase() === this.normalizedColor.toLowerCase()
      );
      return color ? color.label : this.value;
    },
  },
  methods: {
    setColorValue(value) {
      if (typeof value !== 'string') {
        return;
      }

      if (!value.startsWith('#')) {
        value = '#' + value;
      }

      if (isValidColor(value)) {
        this.triggerChange(value);
      }
    },
    setColorFromEvent(event) {
      if (!(event.target instanceof HTMLInputElement)) {
        return;
      }

      this.setColorValue(event.target.value);
    },
  },
};

const defaultColors = [
  { label: 'Red', value: '#f98080' },
  { label: 'Orange', value: '#fbbf70' },
  { label: 'Yellow', value: '#fde047' },
  { label: 'Green', value: '#86efac' },
  { label: 'Teal', value: '#5eead4' },
  { label: 'Blue', value: '#60a5fa' },
  { label: 'Indigo', value: '#818cf8' },
  { label: 'Purple', value: '#a78bfa' },
  { label: 'Pink', value: '#f472b6' },
  { label: 'Black', value: '#000000' },
];

function isValidColor(value) {
  return /^#[0-9A-F]{6}$/i.test(value);
}
</script>

<style scoped>
.color-swatch {
  appearance: none;
  border: 0;
  border-radius: 0.375rem;
  overflow: hidden;
  padding: 0;
}

.color-swatch::-webkit-color-swatch-wrapper {
  padding: 0;
}

.color-swatch::-webkit-color-swatch,
.color-swatch::-moz-color-swatch {
  border: 0;
}
</style>
