<template>
  <FrappeScrollArea ref="scrollArea" orientation="both">
    <slot></slot>
  </FrappeScrollArea>
</template>
<script lang="ts">
import { ScrollArea as FrappeScrollArea, type ScrollAreaExposed } from 'frappe-ui';
import { defineComponent } from 'vue';

export default defineComponent({
  name: 'WithScroll',
  components: { FrappeScrollArea },
  emits: ['scroll'],
  data() {
    return { listener: undefined } as { listener?: () => void };
  },
  mounted() {
    this.listener = () => {
      const { scrollLeft, scrollTop } = this.scrollElement ?? {
        scrollLeft: 0,
        scrollTop: 0,
      };
      this.$emit('scroll', { scrollLeft, scrollTop });
    };
    this.scrollElement?.addEventListener('scroll', this.listener);
  },
  beforeUnmount() {
    if (!this.listener) {
      return;
    }

    this.scrollElement?.removeEventListener('scroll', this.listener);
    delete this.listener;
  },
  computed: {
    scrollElement(): HTMLElement | null {
      return (this.$refs.scrollArea as ScrollAreaExposed | undefined)?.viewportElement ?? null;
    },
  },
});
</script>
