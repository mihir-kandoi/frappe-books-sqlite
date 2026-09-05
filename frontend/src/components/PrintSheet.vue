<template>
  <div class="overflow-hidden" :style="outerContainerStyle">
    <iframe
      class="block border-0"
      :title="t`Print preview`"
      :srcdoc="previewDocument"
      :style="innerContainerStyle"
      @load="onLoad"
    />
    <Teleport v-if="frameBody" :to="frameBody">
      <div class="h-full w-full">
        <slot />
      </div>
    </Teleport>
  </div>
</template>

<script lang="ts">
import { constructPrintDocument } from 'src/utils/printDocument';
import { defineComponent } from 'vue';

export default defineComponent({
  props: {
    height: { type: Number, default: 29.7 },
    width: { type: Number, default: 21 },
    scale: { type: Number, default: 0.65 },
  },
  data() {
    return { frameBody: null as HTMLElement | null };
  },
  computed: {
    previewDocument(): string {
      // Use the printed document's styles, isolated from the app's theme.
      return constructPrintDocument(
        this.t`Print preview`,
        '',
        this.width,
        this.height
      );
    },
    innerContainerStyle(): Record<string, string> {
      return {
        width: `${this.width}cm`,
        height: `${this.height}cm`,
        transform: `scale(${this.scale})`,
        transformOrigin: 'top left',
      };
    },
    outerContainerStyle(): Record<string, string> {
      // Transforms do not change layout dimensions.
      return {
        height: `calc(${this.scale} * ${this.height}cm)`,
        width: `calc(${this.scale} * ${this.width}cm)`,
      };
    },
  },
  methods: {
    onLoad(event: Event) {
      const frame = event.target as HTMLIFrameElement;
      this.frameBody = frame.contentDocument?.body ?? null;
    },
    getHTML(): string | undefined {
      return this.frameBody?.innerHTML;
    },
  },
});
</script>
