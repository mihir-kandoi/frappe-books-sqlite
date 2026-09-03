<template>
  <div
    class="
      flex
      h-full
      min-h-0
      min-w-0
      w-full
      bg-gray-25
      dark:bg-gray-875
      overflow-x-auto
      custom-scroll custom-scroll-thumb1
    "
  >
    <div class="flex min-w-0 flex-1 flex-col">
      <!-- Page Header (Title, Buttons, etc) -->
      <PageHeader
        v-if="showHeader"
        :title="title"
        :border="false"
        :searchborder="searchborder"
      >
        <template #left>
          <slot name="header-left" />
        </template>
        <slot name="header" />
      </PageHeader>

      <!-- Common Form -->
      <div
        class="
          flex flex-col
          self-center
          flex-1
          min-h-0
          overflow-auto
          bg-white
          dark:bg-gray-890
        "
        :class="
          useFullWidth
            ? 'w-full border-t dark:border-gray-800'
            : 'w-form border dark:border-gray-800 rounded-lg shadow-lg m-4'
        "
      >
        <slot name="body" />
      </div>
    </div>

    <!-- Invoice Quick Edit -->
    <slot name="quickedit" />
  </div>
</template>
<script lang="ts">
import { defineComponent } from 'vue';
import PageHeader from './PageHeader.vue';

export default defineComponent({
  components: { PageHeader },
  props: {
    title: { type: String, default: '' },
    useFullWidth: { type: Boolean, default: false },
    showHeader: { type: Boolean, default: true },
    searchborder: { type: Boolean, default: true },
  },
});
</script>
