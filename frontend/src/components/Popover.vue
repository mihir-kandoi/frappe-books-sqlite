<template>
  <FrappePopover
    :open="isOpen"
    :side="side"
    :align="align"
    :offset="8"
    bare
    @update:open="setOpen"
  >
    <template #trigger>
      <div class="flex h-full items-center">
        <slot
          name="target"
          :toggle-popover="togglePopover"
          :handle-blur="handleBlur"
        ></slot>
      </div>
    </template>
    <div
      :class="popoverClass"
      class="
        relative
        z-10
        rounded-md
        border border-outline-gray-1
        bg-surface-elevation-2
        shadow-lg
      "
      :style="{ 'transition-delay': `${isOpen ? entryDelay : exitDelay}ms` }"
    >
      <slot name="content" :toggle-popover="togglePopover"></slot>
    </div>
  </FrappePopover>
</template>

<script lang="ts">
import { Popover as FrappePopover } from 'frappe-ui';
import { defineComponent, PropType } from 'vue';

type PopoverSide = 'top' | 'right' | 'bottom' | 'left';
type PopoverAlign = 'start' | 'center' | 'end';

export default defineComponent({
  name: 'BooksPopover',
  components: { FrappePopover },
  props: {
    disabled: {
      type: Boolean,
      default: false,
    },
    showPopup: {
      type: [Boolean, null] as PropType<boolean | null>,
      default: null,
    },
    right: Boolean,
    entryDelay: { type: Number, default: 0 },
    exitDelay: { type: Number, default: 0 },
    placement: {
      type: String,
      default: 'bottom-start',
    },
    popoverClass: [String, Object, Array],
  },
  emits: ['open', 'close'],
  data() {
    return {
      isOpen: false,
    };
  },
  computed: {
    side(): PopoverSide {
      const side = this.placement.split('-')[0];
      return ['top', 'right', 'bottom', 'left'].includes(side)
        ? (side as PopoverSide)
        : 'bottom';
    },
    align(): PopoverAlign {
      const align = this.placement.split('-')[1];
      return ['start', 'center', 'end'].includes(align)
        ? (align as PopoverAlign)
        : 'center';
    },
  },
  watch: {
    showPopup: {
      immediate: true,
      handler(value: boolean | null) {
        if (value !== null) {
          this.setOpen(value);
        }
      },
    },
  },
  methods: {
    togglePopover(flag?: boolean | Event) {
      if (flag instanceof Event) {
        flag = undefined;
      }

      this.setOpen(flag ?? !this.isOpen);
    },
    setOpen(open: boolean) {
      if (this.disabled && open) {
        return;
      }

      if (open === this.isOpen) {
        return;
      }

      this.isOpen = open;
      this.$emit(open ? 'open' : 'close');
    },
    open() {
      this.setOpen(true);
    },
    close() {
      this.setOpen(false);
    },
    handleBlur({ relatedTarget }: FocusEvent) {
      if (relatedTarget) {
        this.close();
      }
    },
  },
});
</script>
