<template>
  <div
    class="
      grid grid-cols-3
      text-gray-800
      dark:text-gray-100
      text-sm
      select-none
      items-center
    "
    style="height: 50px"
  >
    <!-- Length Display -->
    <div class="justify-self-start">
      {{
        `${(pageNo - 1) * count + 1} - ${Math.min(pageNo * count, itemCount)}`
      }}
    </div>

    <!-- Pagination Selector -->
    <div class="flex gap-1 items-center justify-self-center">
      <FrappeButton
        variant="ghost"
        size="xs"
        :disabled="pageNo <= 1"
        aria-label="Previous page"
        @click="() => setPageNo(Math.max(1, pageNo - 1))"
      >
        <template #icon>
          <span class="lucide-chevron-left size-4 rtl-rotate-180" />
        </template>
      </FrappeButton>
      <div class="flex items-center gap-1 rounded bg-surface-gray-2">
        <FrappeTextInput
          type="number"
          class="w-12 [&_input]:text-end"
          variant="ghost"
          size="sm"
          :model-value="pageNo"
          min="1"
          :max="maxPages"
          @change="(e) => setPageNo(e.target.value)"
          @input="(e) => setPageNo(e.target.value)"
        />
        <p class="text-gray-600">/</p>
        <p class="w-7">
          {{ maxPages }}
        </p>
      </div>
      <FrappeButton
        variant="ghost"
        size="xs"
        :disabled="pageNo >= maxPages"
        aria-label="Next page"
        @click="() => setPageNo(Math.min(maxPages, pageNo + 1))"
      >
        <template #icon>
          <span class="lucide-chevron-right size-4 rtl-rotate-180" />
        </template>
      </FrappeButton>
    </div>

    <!-- Count Selector -->
    <div
      v-if="filteredCounts.length"
      class="
        border border-gray-100
        dark:border-gray-800
        rounded
        flex
        justify-self-end
      "
    >
      <template v-for="c in filteredCounts" :key="c + '-count'">
        <FrappeButton
          class="w-9"
          :variant="
            count === c || (count === itemCount && c === -1)
              ? 'subtle'
              : 'ghost'
          "
          size="sm"
          @click="setCount(c)"
        >
          {{ c === -1 ? t`All` : c }}
        </FrappeButton>
      </template>
    </div>
  </div>
</template>
<script>
import {
  Button as FrappeButton,
  TextInput as FrappeTextInput,
} from 'frappe-ui';
import { defineComponent } from 'vue';

export default defineComponent({
  components: { FrappeButton, FrappeTextInput },
  props: {
    itemCount: { type: Number, default: 0 },
    allowedCounts: { type: Array, default: () => [50, 100, 500, -1] },
  },
  emits: ['index-change'],
  data() {
    return {
      pageNo: 1,
      count: 0,
    };
  },
  computed: {
    maxPages() {
      return Math.ceil(this.itemCount / this.count);
    },
    filteredCounts() {
      return this.allowedCounts.filter(this.filterCount);
    },
  },
  mounted() {
    this.count = this.allowedCounts[0];
    this.emitIndices();
  },
  methods: {
    filterCount(count) {
      if (count !== -1 && this.itemCount < count) {
        return false;
      }

      if (count === -1 && this.itemCount < this.allowedCounts[0]) {
        return false;
      }

      return true;
    },
    setPageNo(value) {
      value = parseInt(value);
      if (isNaN(value)) {
        return;
      }

      this.pageNo = Math.min(Math.max(1, value), this.maxPages);
      this.emitIndices();
    },
    setCount(count) {
      this.pageNo = 1;
      if (count === -1) {
        count = this.itemCount;
      }
      this.count = count;
      this.emitIndices();
    },
    emitIndices() {
      const indices = this.getSliceIndices();
      this.$emit('index-change', indices);
    },
    getSliceIndices() {
      const start = (this.pageNo - 1) * this.count;
      const end = this.pageNo * this.count;
      return { start, end };
    },
  },
});
</script>
