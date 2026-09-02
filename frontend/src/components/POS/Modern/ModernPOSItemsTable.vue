<template>
  <div class="flex min-h-0 flex-1 gap-2">
    <div
      class="min-h-0 w-1/2 overflow-y-auto custom-scroll custom-scroll-thumb2"
    >
      <Row
        :ratio="ratio"
        class="
          mt-2
          px-2
          w-full
          flex
          items-center
          border
          rounded-t-md
          text-gray-600
          dark:border-gray-800 dark:text-gray-400
        "
      >
        <div
          v-for="df in tableFields"
          :key="df.fieldname"
          class="flex items-center p-2 text-lg"
          :class="{
        'ms-auto': isNumeric(df as Field),
      }"
        >
          {{ df.label }}
        </div>
      </Row>

      <Row
        v-for="row in firstColumnItems as POSItem[]"
        :key="row.name"
        :ratio="ratio"
        :border="true"
        class="
          px-2
          w-full
          border
          flex
          items-center
          justify-center
          group
          h-row-mid
          cursor-pointer
          hover:bg-gray-25
          dark:border-gray-800 dark:bg-gray-890
        "
        role="button"
        tabindex="0"
        :aria-label="`Add ${row.name}`"
        @click="handleChange(row)"
        @keydown.enter.prevent="handleChange(row)"
        @keydown.space.prevent="handleChange(row)"
      >
        <FormControl
          v-for="df in tableFields"
          :key="df.fieldname"
          size="large"
          class="pointer-events-none select-none"
          :df="df"
          :value="(row as POSItem)[df.fieldname as keyof POSItem]"
          :readOnly="true"
        />
      </Row>
    </div>

    <div
      class="min-h-0 w-1/2 overflow-y-auto custom-scroll custom-scroll-thumb2"
    >
      <Row
        :ratio="ratio"
        class="
          mt-2
          px-2
          w-full
          flex
          items-center
          border
          rounded-t-md
          text-gray-600
          dark:border-gray-800 dark:text-gray-400
        "
      >
        <div
          v-for="df in tableFields"
          :key="df.fieldname"
          class="flex items-center p-2 text-lg"
          :class="{
        'ms-auto': isNumeric(df as Field),
      }"
        >
          {{ df.label }}
        </div>
      </Row>
      <Row
        v-for="row in secondColumnItems as POSItem[]"
        :key="row.name"
        :ratio="ratio"
        :border="true"
        class="
          px-2
          w-full
          border
          flex
          items-center
          justify-center
          group
          h-row-mid
          cursor-pointer
          hover:bg-gray-25
          dark:bg-gray-890 dark:border-gray-800
        "
        role="button"
        tabindex="0"
        :aria-label="`Add ${row.name}`"
        @click="handleChange(row)"
        @keydown.enter.prevent="handleChange(row)"
        @keydown.space.prevent="handleChange(row)"
      >
        <FormControl
          v-for="df in tableFields"
          :key="df.fieldname"
          size="large"
          class="pointer-events-none select-none"
          :df="df"
          :value="(row as POSItem)[df.fieldname as keyof POSItem]"
          :readOnly="true"
        />
      </Row>
    </div>
  </div>
</template>

<script lang="ts">
import FormControl from 'src/components/Controls/FormControl.vue';
import Row from 'src/components/Row.vue';
import { isNumeric } from 'src/utils';
import { t } from 'fyo';
import { defineComponent } from 'vue';
import { Field } from 'schemas/types';
import { POSItem } from '../types';

export default defineComponent({
  name: 'ModernPOSItemsTable',
  components: { FormControl, Row },
  emits: ['addItem', 'updateValues'],
  props: {
    items: Array,
    itemQtyMap: Object,
    itemVisibility: {
      type: String,
      default: 'Inventory Items',
    },
  },
  computed: {
    ratio() {
      return [1.6, 0.9, 0.8, 0.7];
    },
    tableFields() {
      const fields = [
        {
          fieldname: 'name',
          fieldtype: 'Data',
          label: t`Item`,
          placeholder: 'Item',
          readOnly: true,
        },
        {
          fieldname: 'rate',
          label: t`Rate`,
          placeholder: 'Rate',
          fieldtype: 'Currency',
          readOnly: true,
        },
        {
          fieldname: 'unit',
          label: t`Unit`,
          placeholder: 'Unit',
          fieldtype: 'Data',
          target: 'UOM',
          readOnly: true,
        },
      ] as Field[];

      fields.splice(2, 0, {
        fieldname: 'availableQty',
        label: t`Qty`,
        placeholder: 'Available Qty',
        fieldtype: 'Float',
        readOnly: true,
      });

      return fields;
    },
    firstColumnItems() {
      return this.items?.slice(0, Math.ceil(this.items.length / 2));
    },
    secondColumnItems() {
      return this.items?.slice(Math.ceil(this.items.length / 2));
    },
  },
  methods: {
    handleChange(value: POSItem) {
      this.$emit('addItem', value);
      this.$emit('updateValues');
    },
    isNumeric,
  },
});
</script>
