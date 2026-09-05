<script setup lang="ts">
import { showSidebar } from 'src/utils/refs';
</script>
<template>
  <div class="flex overflow-hidden">
    <Transition name="sidebar">
      <!-- eslint-disable vue/require-explicit-emits -->
      <Sidebar
        v-show="showSidebar"
        class="
          flex-shrink-0
          border-e
          border-outline-gray-1
          whitespace-nowrap
          w-sidebar
        "
        :dark-mode="darkMode"
        @change-db-file="$emit('change-db-file')"
      />
    </Transition>

    <div
      class="
        flex flex-1
        min-w-0
        overflow-y-hidden
        custom-scroll custom-scroll-thumb1
        bg-surface-base
      "
    >
      <router-view v-slot="{ Component }">
        <keep-alive>
          <component
            :is="Component"
            :key="$route.path"
            :dark-mode="darkMode"
            class="min-w-0 flex-1"
          />
        </keep-alive>
      </router-view>

      <router-view v-slot="{ Component, route }" name="edit">
        <Transition name="quickedit">
          <div v-if="route?.query?.edit">
            <component
              :is="Component"
              :key="
                String(route.query.schemaName ?? '') +
                String(route.query.name ?? '')
              "
              :dark-mode="darkMode"
            />
          </div>
        </Transition>
      </router-view>
    </div>
  </div>
</template>
<script lang="ts">
import { defineComponent } from 'vue';
import Sidebar from '../components/Sidebar.vue';
export default defineComponent({
  name: 'Desk',
  components: {
    Sidebar,
  },
  props: {
    darkMode: { type: Boolean, default: false },
  },
  emits: ['change-db-file'],
});
</script>

<style scoped>
.sidebar-enter-from,
.sidebar-leave-to {
  opacity: 0;
  transform: translateX(calc(-1 * var(--w-sidebar)));
  width: 0px;
}
[dir='rtl'] .sidebar-leave-to {
  opacity: 0;
  transform: translateX(calc(1 * var(--w-sidebar)));
  width: 0px;
}

.sidebar-enter-to,
.sidebar-leave-from {
  opacity: 1;
  transform: translateX(0px);
  width: var(--w-sidebar);
}

.sidebar-enter-active,
.sidebar-leave-active {
  transition: all 150ms ease-out;
}
</style>
