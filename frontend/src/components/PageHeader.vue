<template>
  <FrappePageHeader
    class="h-row-largest w-full min-w-0 flex-shrink-0 !px-4"
    :class="[
      border ? '' : '!border-b-0',
      platform !== 'Windows' ? 'window-drag' : '',
    ]"
  >
    <Transition name="spacer" class="border-none">
      <div
        v-if="!showSidebar && platform === 'Mac' && languageDirection !== 'rtl'"
        class="h-full"
        :class="spacerClass"
      />
    </Transition>

    <div
      class="
        flex
        min-w-0
        flex-1
        items-center
        window-no-drag
        gap-4
        me-auto
        overflow-hidden
      "
      :class="platform === 'Mac' && languageDirection === 'rtl' ? 'me-18' : ''"
    >
      <Button
        v-if="!showSidebar"
        :background="false"
        :icon="true"
        :padding="false"
        class="!h-8 !w-8 !px-0 flex-shrink-0 rtl-rotate-180"
        :title="t`Show sidebar`"
        :aria-label="t`Show sidebar`"
        @click="toggleSidebar"
      >
        <Icon name="chevrons-right" class="h-4 w-4" />
      </Button>

      <!-- Nav Group -->
      <PageHeaderNavGroup />
      <h1
        v-if="title"
        class="text-xl font-semibold select-none truncate dark:text-white"
      >
        {{ title }}
      </h1>

      <!-- Left Slot -->
      <div class="flex min-w-0 items-stretch window-no-drag gap-4">
        <slot name="left" />
      </div>
    </div>

    <!-- Right (regular) Slot -->
    <div
      class="flex flex-shrink-0 items-stretch window-no-drag gap-2 ms-auto"
      :class="platform === 'Mac' && languageDirection === 'rtl' ? 'me-18' : ''"
    >
      <slot />
    </div>
  </FrappePageHeader>
</template>
<script lang="ts">
import { PageHeader as FrappePageHeader } from 'frappe-ui';
import { languageDirectionKey } from 'src/utils/injectionKeys';
import { showSidebar } from 'src/utils/refs';
import { toggleSidebar } from 'src/utils/ui';
import { defineComponent, inject, Transition } from 'vue';
import Button from './Button.vue';
import Icon from './Icon.vue';
import PageHeaderNavGroup from './PageHeaderNavGroup.vue';

export default defineComponent({
  components: { Button, FrappePageHeader, Icon, Transition, PageHeaderNavGroup },
  props: {
    title: { type: String, default: '' },
    border: { type: Boolean, default: true },
    searchborder: { type: Boolean, default: true },
  },
  setup() {
    return { showSidebar, languageDirection: inject(languageDirectionKey) };
  },
  methods: { toggleSidebar },
  computed: {
    showBorder() {
      return !!this.$slots.default && this.searchborder;
    },
    spacerClass() {
      if (this.showSidebar) {
        return '';
      }

      if (this.border) {
        return 'w-tl me-4 border-e';
      }

      return 'w-tl me-4';
    },
  },
});
</script>
<style scoped>
.w-tl {
  width: var(--w-trafficlights);
}

.spacer-enter-from,
.spacer-leave-to {
  opacity: 0;
  width: 0px;
  margin-right: 0px;
  border-right-width: 0px;
}

.spacer-enter-to,
.spacer-leave-from {
  opacity: 1;
  width: var(--w-trafficlights);
  margin-right: 1rem;
  border-right-width: 1px;
}

.spacer-enter-active,
.spacer-leave-active {
  transition: all 150ms ease-out;
}
</style>
