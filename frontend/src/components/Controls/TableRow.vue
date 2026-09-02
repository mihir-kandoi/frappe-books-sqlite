<template>
  <Row
    :ratio="ratio"
    class="w-full px-2 group flex items-center justify-center h-row-mid"
    :class="readOnly ? '' : 'hover:bg-gray-25 dark:hover:bg-gray-900'"
  >
    <!-- Index or Remove button -->
    <div
      class="flex items-center ps-2 text-gray-600 dark:text-gray-400"
      @mouseenter="isIndexHovered = true"
      @mouseleave="isIndexHovered = false"
    >
      <span v-if="readOnly">
        {{ row.idx + 1 }}
      </span>
      <FrappeButton
        v-else
        :icon="showDeleteButton ? 'lucide-x' : undefined"
        variant="ghost"
        size="xs"
        class="!size-5 !p-0"
        aria-label="Delete row"
        @focus="isDeleteFocused = true"
        @blur="isDeleteFocused = false"
        @click="$emit('remove')"
      >
        <span v-if="!showDeleteButton">
          {{ row.idx + 1 }}
        </span>
      </FrappeButton>
    </div>

    <!-- Data Input Form Control -->
    <FormControl
      v-for="df in tableFields"
      :key="df.fieldname"
      class="min-w-0 self-center"
      :size="size"
      :df="df"
      :value="row[df.fieldname]"
      @change="(value) => onChange(df, value)"
    />
    <Button
      v-if="canEditRow"
      :icon="true"
      :padding="false"
      :background="false"
      size="sm"
      @click="openRowQuickEdit"
    >
      <feather-icon name="edit" class="w-4 h-4 text-gray-600 dark:text-gray-400" />
    </Button>

    <!-- Error Display -->
    <div
      v-if="hasErrors"
      class="text-xs text-red-600 ps-2 col-span-full relative"
      style="bottom: 0.75rem; height: 0px"
    >
      {{ getErrorString() }}
    </div>
  </Row>
</template>
<script>
import { Doc } from 'fyo/model/doc';
import { Button as FrappeButton } from 'frappe-ui';
import Row from 'src/components/Row.vue';
import { getErrorMessage } from 'src/utils';
import { computed, nextTick } from 'vue';
import Button from '../Button.vue';
import FormControl from './FormControl.vue';

export default {
  name: 'TableRow',
  components: {
    Row,
    FormControl,
    Button,
    FrappeButton,
  },
  provide() {
    return {
      doc: computed(() => this.row),
    };
  },
  props: {
    row: Doc,
    tableFields: Array,
    size: String,
    ratio: Array,
    isNumeric: Function,
    readOnly: Boolean,
    canEditRow: {
      type: Boolean,
      default: false,
    },
  },
  emits: ['remove', 'change'],
  data: () => ({
    isIndexHovered: false,
    isDeleteFocused: false,
    errors: {},
  }),
  computed: {
    showDeleteButton() {
      return this.isIndexHovered || this.isDeleteFocused;
    },
    hasErrors() {
      return Object.values(this.errors).filter(Boolean).length;
    },
  },
  beforeCreate() {
    this.$options.components.FormControl = FormControl;
  },
  methods: {
    async onChange(df, value) {
      const fieldname = df.fieldname;
      this.errors[fieldname] = null;
      const oldValue = this.row[fieldname];
      try {
        await this.row.set(fieldname, value);
        this.$emit('change', df, value);
      } catch (e) {
        this.errors[fieldname] = getErrorMessage(e, this.row);
        this.row[fieldname] = '';
        nextTick(() => (this.row[fieldname] = oldValue));
      }
    },
    getErrorString() {
      return Object.values(this.errors).filter(Boolean).join(' ');
    },
    openRowQuickEdit() {
      if (!this.row) return;
      this.$parent.$emit('editrow', this.row);
    },
    focusFirstInput() {
      const firstControl = this.$el.querySelector('.form-control, input, textarea, select');
      if (firstControl) {
        firstControl.focus();
      }
    },
  },
};
</script>
