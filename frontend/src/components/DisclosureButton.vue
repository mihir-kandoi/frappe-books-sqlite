<template>
  <FrappeButton
    variant="ghost"
    size="md"
    class="!h-auto min-h-8 w-full !justify-between !px-2 !py-2 text-start [&>span]:min-w-0 [&>span]:whitespace-normal [&>svg]:shrink-0"
    :icon-right="expanded ? 'lucide-chevron-up' : 'lucide-chevron-down'"
    :aria-expanded="expanded"
    @click="$emit('toggle')"
  >
    <slot></slot>
  </FrappeButton>
</template>

<script setup lang="ts">
import { Button as FrappeButton } from 'frappe-ui';

defineProps<{ expanded: boolean }>();
defineEmits<{ toggle: [] }>();
</script>
