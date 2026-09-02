<template>
  <FrappeDialog
    :open="openModal"
    bare
    :size="size"
    :dismissible="true"
    @close="$emit('closemodal')"
  >
    <div
      class="
        books-modal
        min-w-0
        max-h-[calc(100vh-2rem)]
        overflow-hidden
        rounded-lg
        border border-outline-gray-1
        bg-surface-elevation-1
        text-gray-900
        dark:text-gray-100
        shadow-2xl
      "
      v-bind="$attrs"
    >
      <slot></slot>
    </div>
  </FrappeDialog>
</template>

<script lang="ts">
import { Dialog as FrappeDialog } from 'frappe-ui';
import { defineComponent, PropType } from 'vue';

type DialogSize =
  | 'xs'
  | 'sm'
  | 'md'
  | 'lg'
  | 'xl'
  | '2xl'
  | '3xl'
  | '4xl'
  | '5xl'
  | '6xl'
  | '7xl';

export default defineComponent({
  name: 'BooksModal',
  components: { FrappeDialog },
  inheritAttrs: false,
  props: {
    openModal: {
      default: false,
      type: Boolean,
    },
    size: {
      default: '2xl',
      type: String as PropType<DialogSize>,
    },
  },
  emits: ['closemodal'],
});
</script>

<style scoped>
.books-modal :deep(label) {
  @apply text-gray-600 dark:text-gray-300;
}
</style>
