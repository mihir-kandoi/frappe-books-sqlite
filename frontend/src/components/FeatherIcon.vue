<template>
  <FrappeIcon :name="iconName" v-bind="$attrs" />
</template>

<script lang="ts">
import { Icon as FrappeIcon } from 'frappe-ui';
import { defineComponent } from 'vue';

export default defineComponent({
  name: 'FeatherIcon',
  components: { FrappeIcon },
  inheritAttrs: false,
  props: {
    name: {
      type: String,
      required: true,
    },
  },
  computed: {
    iconName(): string {
      return `lucide-${this.name}`;
    },
  },
});
</script>
