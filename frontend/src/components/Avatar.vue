<template>
  <FrappeAvatar
    :image="imageURL"
    :label="label"
    :size="frappeSize"
    shape="circle"
  />
</template>

<script lang="ts">
import { Avatar as FrappeAvatar } from 'frappe-ui';
import { defineComponent, PropType } from 'vue';

export default defineComponent({
  name: 'BooksAvatar',
  components: { FrappeAvatar },
  props: {
    imageURL: String,
    label: String,
    size: {
      type: String as PropType<'sm' | 'md' | 'lg'>,
      default: 'md',
    },
  },
  computed: {
    frappeSize(): 'sm' | 'lg' | '2xl' {
      return {
        sm: 'sm',
        md: 'lg',
        lg: '2xl',
      }[this.size] as 'sm' | 'lg' | '2xl';
    },
  },
});
</script>
