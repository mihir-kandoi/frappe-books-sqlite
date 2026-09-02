<template>
  <div
    class="relative bg-white dark:bg-gray-900 border dark:border-gray-800 flex-center overflow-hidden group"
    :class="{
      rounded: size === 'form',
      'w-20 h-20 rounded-full': size !== 'small' && size !== 'form',
      'w-12 h-12 rounded-full': size === 'small',
    }"
    :title="df?.label"
    :style="imageSizeStyle"
  >
    <img v-if="value" :src="value" />
    <div v-else :class="[!isReadOnly ? 'group-hover:opacity-90' : '']">
      <div
        v-if="letterPlaceholder"
        class="flex h-full items-center justify-center text-gray-400 dark:text-gray-600 font-semibold w-full text-4xl select-none"
      >
        {{ letterPlaceholder }}
      </div>
      <span v-else class="lucide-image size-6 text-ink-gray-4" aria-hidden="true" />
    </div>
    <div
      class="hidden w-full h-full absolute justify-center items-end"
      :class="[!isReadOnly ? 'group-hover:flex' : '']"
      style="background: rgba(0, 0, 0, 0.2); backdrop-filter: blur(2px)"
    >
      <FrappeButton
        size="xs"
        variant="subtle"
        class="mb-1"
        :aria-label="shouldClear ? t`Remove image` : t`Upload image`"
        @click="handleClick"
      >
        <template #icon>
          <span :class="shouldClear ? 'lucide-x' : 'lucide-upload'" class="size-4" />
        </template>
      </FrappeButton>
    </div>
  </div>
</template>
<script lang="ts">
import { Field } from 'schemas/types';
import { Button as FrappeButton } from 'frappe-ui';
import { fyo } from 'src/initFyo';
import { selectFile } from 'src/utils/browser';
import { getDataURL } from 'src/utils/misc';
import { defineComponent, PropType } from 'vue';
import Base from './Base.vue';

const mime_types: Record<string, string> = {
  png: 'image/png',
  jpg: 'image/jpeg',
  jpeg: 'image/jpeg',
  webp: 'image/webp',
  svg: 'image/svg+xml',
};

export default defineComponent({
  name: 'AttachImage',
  components: { FrappeButton },
  extends: Base,
  props: {
    letterPlaceholder: { type: String, default: '' },
    value: { type: String, default: '' },
    df: { type: Object as PropType<Field> },
  },
  computed: {
    imageSizeStyle() {
      if (this.size === 'form') {
        return { width: '135px', height: '135px' };
      }
      return {};
    },
    shouldClear() {
      return !!this.value;
    },
  },
  methods: {
    async handleClick() {
      if (this.value) {
        return await this.clearImage();
      }
      return await this.selectImage();
    },
    async clearImage() {
      // @ts-ignore
      this.triggerChange(null);
    },
    async selectImage() {
      if (this.isReadOnly) {
        return;
      }
      const options = {
        title: fyo.t`Select Image`,
        filters: [{ name: 'Image', extensions: Object.keys(mime_types) }],
      };

      const selectedFile = await selectFile(options);
      if (!selectedFile) {
        return;
      }
      const { name, data } = selectedFile;
      const extension = name.split('.').at(-1)?.toLowerCase();
      if (!extension) {
        return;
      }

      const type = mime_types[extension];
      if (!type) {
        return;
      }
      const dataURL = await getDataURL(type, Uint8Array.from(data));

      // @ts-ignore
      this.triggerChange(dataURL);
    },
  },
});
</script>
