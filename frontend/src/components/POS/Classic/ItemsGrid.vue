<template>
  <div
    class="
      gap-4
      py-3
      w-full
      flex flex-col
      items-center
      rounded-t-md
      text-black
      min-h-0
      flex-1
      overflow-y-auto
      custom-scroll custom-scroll-thumb2
    "
  >
    <!-- Items Grid -->
    <div
      class="grid w-full gap-3"
      style="grid-template-columns: repeat(auto-fill, minmax(10rem, 1fr))"
    >
      <div
        class="
          min-h-[15rem]
          p-3
          rounded-md
          border border-gray-300
          flex flex-col
          text-sm text-center
          cursor-pointer
          bg-white
          hover:bg-gray-25
          focus:outline-none
          focus-visible:ring-2 focus-visible:ring-blue-500
          dark:border-gray-800 dark:bg-gray-875 dark:hover:bg-gray-850
        "
        @click="handleChange(item as POSItem)"
        @keydown.enter.prevent="handleChange(item as POSItem)"
        @keydown.space.prevent="handleChange(item as POSItem)"
        v-for="item in items as POSItem[]"
        :key="item.name"
        role="button"
        tabindex="0"
        :aria-label="`Add ${item.name}`"
      >
        <div class="relative h-28 w-full overflow-hidden rounded-md">
          <img
            v-if="item.image"
            :src="item.image"
            alt=""
            class="h-full w-full object-cover"
          />

          <div
            v-else
            class="
              rounded-md
              w-full
              h-full
              bg-gray-100
              flex
              justify-center
              items-center
              dark:bg-gray-850
            "
          >
            <p class="text-4xl font-semibold text-gray-400 select-none">
              {{ getExtractedWords(item.name) }}
            </p>
          </div>
          <p
            class="
              absolute
              top-1
              right-1
              rounded-full
              w-6
              h-6
              flex
              justify-center
              items-center
            "
            :class="
              item.availableQty > 0
                ? 'bg-green-100 text-green-900'
                : 'bg-red-100 text-red-900'
            "
          >
            {{ item.availableQty }}
          </p>
        </div>
        <div class="mt-3 flex flex-1 flex-col gap-1">
          <h3
            class="
              flex
              min-h-[3rem]
              items-center
              justify-center
              break-words
              text-base
              font-medium
              leading-6
              dark:text-white
            "
          >
            {{ item.name }}
          </h3>

          <p class="mt-auto text-base font-medium dark:text-white">
            {{
              item.rate
                ? fyo.currencySymbols[item.rate.getCurrency()]
                : undefined
            }}
            {{ item.rate }}
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import { POSItem } from '../types';

export default defineComponent({
  name: 'ItemsGrid',
  emits: ['addItem', 'updateValues'],
  props: {
    items: {
      type: Array,
    },
    itemQtyMap: {
      type: Object,
    },
    itemVisibility: {
      type: String,
      default: 'Inventory Items',
    },
  },
  methods: {
    getExtractedWords(item: string) {
      const initials = item.split(' ').map((word) => {
        return word[0].toUpperCase();
      });
      return initials.join('');
    },
    handleChange(value: POSItem) {
      this.$emit('addItem', value);
      this.$emit('updateValues');
    },
  },
});
</script>
